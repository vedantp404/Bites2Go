"""Content-free request tracing. Never capture request bodies or arbitrary headers."""

import json
import logging
import os
import re
import time
import uuid

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("bites2go.requests")


class RequestDiagnosticsMiddleware:
    def __init__(self, app: ASGIApp, version: str) -> None:
        self.app = app
        self.version = version
        commit = os.getenv("RENDER_GIT_COMMIT", "")
        self.commit = commit if re.fullmatch(r"[a-fA-F0-9]{40}", commit) else "unknown"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        # Server-generated IDs cannot contain client-supplied health data or log injection.
        request_id = uuid.uuid4().hex
        scope.setdefault("state", {})["request_id"] = request_id
        started = time.perf_counter()
        status_code = 500
        response_started = False
        category = None

        async def traced_send(message: Message) -> None:
            nonlocal status_code, response_started, category
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_started = True
                headers = [(k, v) for k, v in message.get("headers", []) if k.lower() != b"x-request-id"]
                headers.append((b"x-request-id", request_id.encode("ascii")))
                message = {**message, "headers": headers}
                for key, value in headers:
                    if key.lower() == b"x-error-category":
                        candidate = value.decode("ascii", errors="ignore")
                        if re.fullmatch(r"[a-z_]{1,60}", candidate):
                            category = candidate
            await send(message)

        try:
            await self.app(scope, receive, traced_send)
        except Exception:
            category = "internal_error"
            if response_started:
                raise
            response = JSONResponse(
                {"detail": "An internal server error occurred. Please try again."},
                status_code=500,
            )
            await response(scope, receive, traced_send)
        finally:
            # A route template is safe; the raw URL, query, body and exception are not.
            route = getattr(scope.get("route"), "path", "unmatched")
            logger.info(json.dumps({
                "event": "request_completed", "request_id": request_id,
                "endpoint": route, "status": status_code,
                "status_class": f"{status_code // 100}xx",
                "error_category": category,
                "latency_ms": round((time.perf_counter() - started) * 1000, 1),
                "outcome": "success" if status_code < 400 else "error",
                "backend_version": self.version, "deployment_commit": self.commit,
            }, separators=(",", ":")))

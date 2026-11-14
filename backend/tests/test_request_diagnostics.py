"""Mock-only correlation and privacy regression coverage."""
import json
import logging
import re
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import create_app
from app.request_diagnostics import RequestDiagnosticsMiddleware


def events(caplog):
    return [json.loads(r.message) for r in caplog.records if r.name == "bites2go.requests"]


def test_success_validation_and_unknown_routes_have_safe_ids(caplog):
    caplog.set_level(logging.INFO, logger="bites2go.requests")
    client = TestClient(create_app())
    responses = [client.get("/health", headers={"X-Request-ID": "private-meal-description"}),
                 client.post("/api/v1/parse-voice-audio"),
                 client.get("/private-meal-description?token=secret")]
    assert responses[0].status_code == 200
    assert responses[1].status_code in (400, 503)
    assert responses[2].status_code == 404
    ids = [r.headers["x-request-id"] for r in responses]
    assert len(set(ids)) == 3
    assert all(re.fullmatch(r"[0-9a-f]{32}", value) for value in ids)
    records = events(caplog)
    assert [r["request_id"] for r in records] == ids
    assert records[-1]["endpoint"] == "unmatched"
    assert "private-meal-description" not in json.dumps(records)
    assert "secret" not in json.dumps(records)


def test_unexpected_exception_is_sanitized_and_correlated(caplog):
    caplog.set_level(logging.INFO, logger="bites2go.requests")
    app = FastAPI()
    app.add_middleware(RequestDiagnosticsMiddleware, version="test")

    @app.get("/broken")
    def broken():
        raise RuntimeError("secret transcript or token")

    response = TestClient(app).get("/broken")
    assert response.status_code == 500
    assert "secret" not in response.text
    record = events(caplog)[0]
    assert record["request_id"] == response.headers["x-request-id"]
    assert record["error_category"] == "internal_error"
    assert record["outcome"] == "error"
    assert "secret" not in json.dumps(record)


def test_framework_validation_errors_are_correlated(client, caplog):
    caplog.set_level(logging.INFO)
    response = client.post("/api/v1/parse-voice-meal", json={"transcript": ""})
    assert response.status_code == 422
    assert events(caplog)[-1]["request_id"] == response.headers["x-request-id"]

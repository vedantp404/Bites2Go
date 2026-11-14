"""Main FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.request_diagnostics import RequestDiagnosticsMiddleware

from app.config import get_settings
from app.routers.health import router as health_router
from app.routers.food import router as food_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("bites2go.backend")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Validate startup configuration safely."""
    settings = get_settings()
    configured_providers = []
    if settings.is_gemini_configured:
        configured_providers.append(f"Gemini ({settings.gemini_model})")
    if settings.is_openrouter_configured:
        configured_providers.append(f"OpenRouter ({settings.openrouter_model})")

    if configured_providers:
        logger.info(
            "AI recognition services ready: %s. Primary: %s, Fallback enabled: %s",
            ", ".join(configured_providers),
            settings.ai_primary_provider,
            settings.ai_fallback_enabled,
        )
    else:
        logger.warning(
            "Neither GEMINI_API_KEY nor OPENROUTER_API_KEY is configured in backend/.env. "
            "Health check will work, but recognition endpoints will return 503."
        )
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Secure Gemini AI Food Recognition Backend for Bites2Go",
        docs_url="/docs" if settings.environment == "development" else None,
        redoc_url=None,
        lifespan=lifespan,
    )

    app.add_middleware(RequestDiagnosticsMiddleware, version=settings.app_version)

    # Configure CORS for local development and mobile emulator access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Error-Category", "Retry-After"],
    )

    # Include routers
    app.include_router(health_router)
    app.include_router(food_router)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )

"""Health check endpoint."""

from fastapi import APIRouter
from app.config import get_settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check() -> dict:
    """Verify backend health, configuration status, and connectivity readiness.

    Never echoes API keys, tokens, or environment paths.
    """
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "ai_configured": settings.is_gemini_configured,
        "model": settings.gemini_model,
    }


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
        "ai_configured": settings.is_ai_configured,
        "primary_provider": settings.ai_primary_provider,
        "fallback_enabled": settings.ai_fallback_enabled,
        "gemini_configured": settings.is_gemini_configured,
        "openrouter_configured": settings.is_openrouter_configured,
        "model": settings.gemini_model,
        "fallback_model": settings.openrouter_model,
    }


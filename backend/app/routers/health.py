"""Health check endpoint."""

from fastapi import APIRouter
from app.config import get_settings
from app.services.ai_service import get_active_cooldowns_if_initialized

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
        "fallback_alternative_model": settings.openrouter_alternative_model,
        "photo_primary_provider": settings.photo_primary_provider,
        "photo_fallback_provider": settings.photo_fallback_provider,
        "photo_model": (
            settings.gemini_model
            if settings.photo_primary_provider == "gemini"
            else settings.photo_openrouter_model
        ),
        "photo_fallback_model": (
            settings.photo_openrouter_model
            if settings.photo_fallback_provider == "openrouter"
            else settings.gemini_model
        ),
        "voice_primary_provider": settings.voice_primary_provider,
        "voice_fallback_provider": settings.voice_fallback_provider,
        "voice_model": (
            settings.voice_openrouter_model
            if settings.voice_primary_provider == "openrouter"
            else settings.gemini_model
        ),
        "voice_fallback_model": (
            settings.gemini_model
            if settings.voice_fallback_provider == "gemini"
            else settings.voice_openrouter_model
        ),
        "voice_audio_primary_provider": getattr(settings, "voice_audio_primary_provider", "gemini"),
        "voice_audio_fallback_provider": getattr(settings, "voice_audio_fallback_provider", "none"),
        "voice_audio_model": getattr(settings, "voice_audio_model", settings.gemini_model),
        "voice_audio_supported_formats": [
            "audio/m4a",
            "audio/mp4",
            "audio/aac",
            "audio/mpeg",
            "audio/wav",
            "audio/ogg",
            "audio/webm",
            "audio/flac",
        ],
        "rate_limit_cooldowns": get_active_cooldowns_if_initialized(),
        "commit": settings.git_commit[:8],
    }

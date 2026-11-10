"""Application configuration and environment management."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Search locations for .env file:
# 1. backend/.env
# 2. Project root .env
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_ROOT_DIR = _BACKEND_DIR.parent

_ENV_LOCATIONS = [
    _BACKEND_DIR / ".env",
    _ROOT_DIR / ".env",
]

for _env_path in _ENV_LOCATIONS:
    if _env_path.is_file():
        load_dotenv(dotenv_path=_env_path, override=False)
        break


class ConfigurationError(RuntimeError):
    """Raised when critical configuration is missing or invalid."""
    pass


class Settings:
    """Runtime configuration container."""

    def __init__(self) -> None:
        self.app_name: str = "Bites2Go AI Service"
        self.app_version: str = "1.0.0"
        self.environment: str = os.getenv("ENVIRONMENT", "development")
        self.host: str = os.getenv("HOST", "127.0.0.1")
        self.port: int = int(os.getenv("PORT", "8000"))
        
        # Default to gemini-3.5-flash (benchmarked faster/more reliable than 3.8-flash and 3.5-flash-lite)
        self.gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash").strip()

        # Disable hidden Gemini thinking tokens by default (cut latency from ~17.5s to ~2.7-4.0s)
        self.gemini_thinking_budget: int = int(os.getenv("GEMINI_THINKING_BUDGET", "0"))
        self.gemini_max_output_tokens: int = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "1500"))
        
        # Image upload & in-memory preprocessing settings (preserve clarity while shrinking payload)
        self.max_image_size_bytes: int = int(os.getenv("MAX_IMAGE_SIZE_BYTES", str(10 * 1024 * 1024)))
        self.max_image_dimension: int = int(os.getenv("MAX_IMAGE_DIMENSION", "1024"))
        self.image_jpeg_quality: int = int(os.getenv("IMAGE_JPEG_QUALITY", "82"))
        
        # Request timeout in seconds per attempt (14.0s photo fits safely inside 35s deadline with 21s fallback headroom)
        self.gemini_timeout_seconds: float = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "14.0"))
        
        # Max automatic retries for transient failures when fallback is disabled
        self.gemini_max_retries: int = int(os.getenv("GEMINI_MAX_RETRIES", "2"))
        
        # Retry backoff initial delay and max delay in seconds
        self.gemini_retry_initial_delay: float = float(os.getenv("GEMINI_RETRY_INITIAL_DELAY", "1.0"))
        self.gemini_retry_max_delay: float = float(os.getenv("GEMINI_RETRY_MAX_DELAY", "3.0"))
        
        # Global server-side request deadline budgets (must finish ahead of mobile AbortControllers: 45s photo / 40s voice)
        self.server_deadline_seconds: float = float(os.getenv("SERVER_DEADLINE_SECONDS", "35.0"))
        self.voice_server_deadline_seconds: float = float(os.getenv("VOICE_SERVER_DEADLINE_SECONDS", "32.0"))

        # Master fallback switch
        self.ai_fallback_enabled: bool = os.getenv("AI_FALLBACK_ENABLED", "true").lower() in ("true", "1", "yes")

        # Task-specific Photo routing (Primary: Gemini vision, Fallback: verified OpenRouter vision free model)
        self.ai_primary_provider: str = os.getenv("AI_PRIMARY_PROVIDER", "gemini").strip().lower()
        self.photo_primary_provider: str = os.getenv("PHOTO_PRIMARY_PROVIDER", self.ai_primary_provider).strip().lower()
        default_photo_fallback = "gemini" if self.photo_primary_provider == "openrouter" else "openrouter"
        self.photo_fallback_provider: str = os.getenv("PHOTO_FALLBACK_PROVIDER", default_photo_fallback).strip().lower()

        # Task-specific Voice routing (Primary: Nemotron 3 Ultra on OpenRouter, Fallback: Gemini text parsing)
        self.voice_primary_provider: str = os.getenv("VOICE_PRIMARY_PROVIDER", "openrouter").strip().lower()
        default_voice_fallback = "gemini" if self.voice_primary_provider == "openrouter" else "openrouter"
        self.voice_fallback_provider: str = os.getenv("VOICE_FALLBACK_PROVIDER", default_voice_fallback).strip().lower()

        # Photo OpenRouter vision configuration (avoids legacy openrouter/free empty-content failures)
        legacy_or_model = os.getenv("OPENROUTER_MODEL", "").strip()
        photo_or_env = os.getenv("PHOTO_OPENROUTER_MODEL")
        if photo_or_env and photo_or_env.strip():
            self.photo_openrouter_model: str = photo_or_env.strip()
        elif legacy_or_model and legacy_or_model != "openrouter/free":
            self.photo_openrouter_model = legacy_or_model
        else:
            self.photo_openrouter_model = "nvidia/nemotron-3.5-super-vl:free"
        self.openrouter_model: str = self.photo_openrouter_model

        alt_model_env = os.getenv("PHOTO_OPENROUTER_ALTERNATIVE_MODEL")
        if alt_model_env is None:
            alt_model_env = os.getenv("OPENROUTER_ALTERNATIVE_MODEL")
        if alt_model_env is not None:
            cleaned_alt = alt_model_env.strip()
            self.photo_openrouter_alternative_model: Optional[str] = (
                None if cleaned_alt.lower() in ("", "none", "off") else cleaned_alt
            )
        else:
            if self.photo_openrouter_model == "nvidia/nemotron-3.5-super-vl:free":
                self.photo_openrouter_alternative_model = "dots-studio/dots-3-note-preview:free"
            else:
                self.photo_openrouter_alternative_model = "nvidia/nemotron-3.5-super-vl:free"
        self.openrouter_alternative_model: Optional[str] = self.photo_openrouter_alternative_model

        # Voice OpenRouter configuration (Nemotron 3 Ultra text-only model; never passed image data)
        self.voice_openrouter_model: str = os.getenv(
            "VOICE_OPENROUTER_MODEL",
            "nvidia/nemotron-3-ultra-550b-a55b:free",
        ).strip()
        voice_alt_env = os.getenv("VOICE_OPENROUTER_ALTERNATIVE_MODEL")
        if voice_alt_env is not None and voice_alt_env.strip().lower() not in ("", "none", "off"):
            self.voice_openrouter_alternative_model: Optional[str] = voice_alt_env.strip()
        else:
            self.voice_openrouter_alternative_model = None

        self.openrouter_base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
        self.openrouter_timeout_seconds: float = float(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "19.0"))
        # 14.0s enforceable wall-clock cap for voice primary reserves >=14.0s for Gemini fallback inside 32.0s deadline
        self.voice_primary_timeout_seconds: float = float(os.getenv("VOICE_PRIMARY_TIMEOUT_SECONDS", "14.0"))
        self.openrouter_max_retries: int = int(os.getenv("OPENROUTER_MAX_RETRIES", "1"))
        self.openrouter_max_tokens: int = int(os.getenv("OPENROUTER_MAX_TOKENS", "2000"))
        self.voice_openrouter_max_tokens: int = int(os.getenv("VOICE_OPENROUTER_MAX_TOKENS", "900"))

        # Bounded rate-limit cooldown settings (prevent hammering free-tier 429 endpoints)
        self.rate_limit_cooldown_enabled: bool = os.getenv("RATE_LIMIT_COOLDOWN_ENABLED", "true").lower() in ("true", "1", "yes")
        self.rate_limit_burst_cooldown_min_seconds: float = float(os.getenv("RATE_LIMIT_BURST_COOLDOWN_MIN_SECONDS", "15.0"))
        self.rate_limit_burst_cooldown_max_seconds: float = float(os.getenv("RATE_LIMIT_BURST_COOLDOWN_MAX_SECONDS", "60.0"))
        self.rate_limit_upstream_cooldown_seconds: float = float(os.getenv("RATE_LIMIT_UPSTREAM_COOLDOWN_SECONDS", "20.0"))
        self.rate_limit_daily_cooldown_max_seconds: float = float(os.getenv("RATE_LIMIT_DAILY_COOLDOWN_MAX_SECONDS", "300.0"))

        # Deployed git commit hash (populated on Render via RENDER_GIT_COMMIT)
        self.git_commit: str = os.getenv("RENDER_GIT_COMMIT", os.getenv("GIT_COMMIT", "dev"))

        # CORS origins (allow local development, emulator, and LAN)
        origins_str = os.getenv("ALLOWED_ORIGINS", "*")
        self.allowed_origins: list[str] = [o.strip() for o in origins_str.split(",") if o.strip()]

    @property
    def gemini_api_key(self) -> Optional[str]:
        """Fetch the Gemini API key without logging or exposing it."""
        key = os.getenv("GEMINI_API_KEY")
        if key and key.strip():
            return key.strip()
        return None

    def require_gemini_api_key(self) -> str:
        """Fetch the Gemini API key or raise ConfigurationError."""
        key = self.gemini_api_key
        if not key:
            raise ConfigurationError(
                "GEMINI_API_KEY is not configured. "
                "Please configure GEMINI_API_KEY in backend/.env before calling the recognition endpoint."
            )
        return key

    @property
    def is_gemini_configured(self) -> bool:
        """Boolean indicator for whether Gemini API key is available."""
        return self.gemini_api_key is not None

    @property
    def openrouter_api_key(self) -> Optional[str]:
        """Fetch the OpenRouter API key without logging or exposing it."""
        key = os.getenv("OPENROUTER_API_KEY")
        if key and key.strip():
            return key.strip()
        return None

    def require_openrouter_api_key(self) -> str:
        """Fetch the OpenRouter API key or raise ConfigurationError."""
        key = self.openrouter_api_key
        if not key:
            raise ConfigurationError(
                "OPENROUTER_API_KEY is not configured. "
                "Please configure OPENROUTER_API_KEY in backend/.env before calling the OpenRouter endpoint."
            )
        return key

    @property
    def is_openrouter_configured(self) -> bool:
        """Boolean indicator for whether OpenRouter API key is available."""
        return self.openrouter_api_key is not None

    @property
    def is_ai_configured(self) -> bool:
        """Indicate whether at least one AI provider is configured."""
        return self.is_gemini_configured or self.is_openrouter_configured


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Singleton getter for application settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

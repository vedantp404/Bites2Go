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
        
        # Default to gemini-3.5-flash for speed, high availability, multimodal accuracy, and active API tier
        self.gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
        
        # Max upload size: 10 MB
        self.max_image_size_bytes: int = int(os.getenv("MAX_IMAGE_SIZE_BYTES", str(10 * 1024 * 1024)))
        
        # Request timeout in seconds per attempt (default 12.0s so 3 bounded attempts fit within mobile timeout)
        self.gemini_timeout_seconds: float = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "12.0"))
        
        # Max automatic retries for transient failures (default 2 additional attempts = 3 attempts total)
        self.gemini_max_retries: int = int(os.getenv("GEMINI_MAX_RETRIES", "2"))
        
        # Retry backoff initial delay in seconds
        self.gemini_retry_initial_delay: float = float(os.getenv("GEMINI_RETRY_INITIAL_DELAY", "1.0"))
        
        # Retry backoff maximum delay in seconds
        self.gemini_retry_max_delay: float = float(os.getenv("GEMINI_RETRY_MAX_DELAY", "4.0"))
        
        # Provider architecture configuration
        self.ai_primary_provider: str = os.getenv("AI_PRIMARY_PROVIDER", "gemini").lower()
        self.ai_fallback_enabled: bool = os.getenv("AI_FALLBACK_ENABLED", "true").lower() in ("true", "1", "yes")

        # OpenRouter fallback configuration
        self.openrouter_model: str = os.getenv("OPENROUTER_MODEL", "openrouter/free")
        self.openrouter_base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
        self.openrouter_timeout_seconds: float = float(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "25.0"))
        self.openrouter_max_retries: int = int(os.getenv("OPENROUTER_MAX_RETRIES", "1"))

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

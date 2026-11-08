"""AI recognition providers package."""

from app.services.providers.base import (
    AIAllProvidersFailedError,
    AIAuthenticationError,
    AIRateLimitError,
    AIServiceError,
    AITimeoutError,
    AITransientError,
    AIUnavailableError,
    BaseAIProvider,
    GeminiServiceError,
    GeminiTimeoutError,
    GeminiUnavailableError,
    ModelOutputValidationError,
    RateLimitError,
    SYSTEM_INSTRUCTION,
    VOICE_PARSER_SYSTEM_INSTRUCTION,
)

__all__ = [
    "AIAllProvidersFailedError",
    "AIAuthenticationError",
    "AIRateLimitError",
    "AIServiceError",
    "AITimeoutError",
    "AITransientError",
    "AIUnavailableError",
    "BaseAIProvider",
    "GeminiServiceError",
    "GeminiTimeoutError",
    "GeminiUnavailableError",
    "ModelOutputValidationError",
    "RateLimitError",
    "SYSTEM_INSTRUCTION",
    "VOICE_PARSER_SYSTEM_INSTRUCTION",
]


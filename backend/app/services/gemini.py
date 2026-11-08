"""Gemini AI service and provider integration module.

Maintains backward-compatibility aliases for existing imports and tests.
"""

from typing import Optional
from google.genai import errors
import httpx

from app.models.food import FoodRecognitionResponse, VoiceMealParseResponse
from app.services.ai_service import DualProviderService, get_ai_service
from app.services.providers.base import (
    AIAllProvidersFailedError,
    AIAuthenticationError,
    AIRateLimitError,
    AIServiceError,
    AITimeoutError,
    AITransientError,
    AIUnavailableError,
    GeminiServiceError,
    GeminiTimeoutError,
    GeminiUnavailableError,
    ModelOutputValidationError,
    RateLimitError,
    SYSTEM_INSTRUCTION,
    VOICE_PARSER_SYSTEM_INSTRUCTION,
)
from app.services.providers.gemini_provider import (
    GeminiProvider,
)


def is_transient_gemini_error(exc: BaseException) -> bool:
    """Determine whether an error from the Gemini API is transient (for backward compatibility)."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        if code in {408, 429, 500, 502, 503, 504}:
            return True
        if isinstance(exc, errors.ServerError):
            return True
        return False

    if isinstance(
        exc,
        (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.RemoteProtocolError,
            TimeoutError,
        ),
    ):
        return True

    return False


# In previous versions, GeminiService was the direct Gemini client.
# To preserve test compatibility with GeminiService(client=mock_client, ...),
# GeminiService is an alias to GeminiProvider.
GeminiService = GeminiProvider

# In dependency injection, get_gemini_service provides the DualProviderService orchestrator.
get_gemini_service = get_ai_service

__all__ = [
    "AIAllProvidersFailedError",
    "AIAuthenticationError",
    "AIRateLimitError",
    "AIServiceError",
    "AITimeoutError",
    "AITransientError",
    "AIUnavailableError",
    "DualProviderService",
    "GeminiProvider",
    "GeminiService",
    "GeminiServiceError",
    "GeminiTimeoutError",
    "GeminiUnavailableError",
    "ModelOutputValidationError",
    "RateLimitError",
    "SYSTEM_INSTRUCTION",
    "VOICE_PARSER_SYSTEM_INSTRUCTION",
    "get_ai_service",
    "get_gemini_service",
    "is_transient_gemini_error",
]

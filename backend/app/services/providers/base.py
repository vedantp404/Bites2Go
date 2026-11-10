"""Base abstraction and exception definitions for AI recognition providers."""

import contextvars
import time
from abc import ABC, abstractmethod
from typing import Callable, Optional

from app.models.food import FoodRecognitionResponse, VoiceMealParseResponse


class AIServiceError(RuntimeError):
    """Base exception for all AI provider errors."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        code: Optional[int] = None,
        error_category: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.code = code
        self.error_category = error_category


class AITransientError(AIServiceError):
    """Base exception for transient/retryable AI failures (e.g. rate limits, 503, 504)."""
    pass


class AITimeoutError(AITransientError):
    """Raised when an AI request times out after retries."""
    pass


class AIUnavailableError(AITransientError):
    """Raised when an AI service is temporarily overloaded or unavailable (HTTP 500, 502, 503)."""
    pass


class AIRateLimitError(AITransientError):
    """Raised when API rate limits, upstream saturation, or daily quotas are reached."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        code: int = 429,
        is_quota_exhausted: bool = False,
        error_category: Optional[str] = "rate_limit",
        retry_after_seconds: Optional[float] = None,
        limit_scope: str = "model",
    ) -> None:
        super().__init__(message, provider=provider, code=code, error_category=error_category)
        self.is_quota_exhausted = is_quota_exhausted
        self.retry_after_seconds = retry_after_seconds
        self.limit_scope = limit_scope


class AIAuthenticationError(AIServiceError):
    """Raised when API authentication fails (HTTP 401/403)."""
    pass


class ModelOutputValidationError(AIServiceError):
    """Raised when model returns malformed, unparseable, or invalid structured data."""
    pass


class AIRequestCancelledError(AIServiceError):
    """Raised when the client disconnects or aborts the in-flight AI request."""
    pass


class AIAllProvidersFailedError(AIServiceError):
    """Raised when all configured providers (primary and fallback) have failed."""

    def __init__(
        self,
        message: str,
        primary_provider: str,
        primary_error: Optional[Exception] = None,
        fallback_provider: Optional[str] = None,
        fallback_error: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, provider=primary_provider)
        self.primary_provider = primary_provider
        self.primary_error = primary_error
        self.fallback_provider = fallback_provider
        self.fallback_error = fallback_error


# Backward compatibility aliases
GeminiServiceError = AIServiceError
GeminiTransientError = AITransientError
GeminiTimeoutError = AITimeoutError
GeminiUnavailableError = AIUnavailableError
RateLimitError = AIRateLimitError


current_cancellation_check: contextvars.ContextVar[Optional[Callable[[], bool]]] = (
    contextvars.ContextVar("current_cancellation_check", default=None)
)

current_request_id: contextvars.ContextVar[Optional[str]] = (
    contextvars.ContextVar("current_request_id", default=None)
)

# Monotonic timestamp (time.monotonic() + deadline_s) propagated from FastAPI endpoints
current_request_deadline: contextvars.ContextVar[Optional[float]] = (
    contextvars.ContextVar("current_request_deadline", default=None)
)


def get_current_request_id() -> str:
    """Return the active correlation/request ID or a default fallback."""
    req_id = current_request_id.get()
    return req_id if req_id else "req-local"


def get_remaining_request_deadline() -> Optional[float]:
    """Return remaining seconds until active request's server deadline, or None if unset."""
    deadline_ts = current_request_deadline.get()
    if deadline_ts is None:
        return None
    return max(0.0, deadline_ts - time.monotonic())


def is_request_cancelled(explicit_check: Optional[Callable[[], bool]] = None) -> bool:
    """Check whether the active request has been cancelled by client disconnect."""
    if explicit_check is not None and explicit_check():
        return True
    ctx_check = current_cancellation_check.get()
    if ctx_check is not None and ctx_check():
        return True
    return False


class BaseAIProvider(ABC):
    """Abstract interface defining required capabilities for food AI providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier: 'gemini' | 'openrouter'."""
        pass

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Whether this provider has necessary credentials/keys configured."""
        pass

    @abstractmethod
    def recognize_food(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        timeout_seconds: Optional[float] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> FoodRecognitionResponse:
        """Recognize food from image bytes and return normalized FoodRecognitionResponse."""
        pass

    @abstractmethod
    def parse_voice_meal(
        self,
        transcript: str,
        meal_context: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> VoiceMealParseResponse:
        """Parse voice transcript and return normalized VoiceMealParseResponse."""
        pass


SYSTEM_INSTRUCTION = (
    "You are an expert dietary analysis AI specializing in global, Indian, Asian, and Western cuisines. "
    "Identify each visually distinguishable food item separately on mixed plates or thalis.\n"
    "Guidelines:\n"
    "- Indian & mixed staples: Distinguish Roti/Chapati (~30-45g, 80-120 kcal), Naan (~100-130g), Paratha (~70-120g), Puri/Bhatura; Steamed Basmati Rice (~150-200g/bowl), Jeera Rice, Pulao, Biryani; Dal Tadka/Makhani/Chana Dal/Sambar/Rajma/Chole (~150-200g/katori); dry Sukhi Sabzi vs cream/oil curries and Paneer dishes; sides (Kachumber, Raita, Papad, Chutneys, Achar).\n"
    "- Separation & Grouping: Detect separate bowls/heaps distinctly. Group identical countable items into one entry (e.g. estimated_quantity=2.0, unit='rotis', estimated_grams=70.0) without duplicate items.\n"
    "- Grounded Honesty: Only report foods visually evidenced. Never invent unseen items; return empty items for non-food or empty plates. For ambiguous dishes, lower confidence_level to 'medium'/'low', note ambiguity, and add 2-3 uncertainty.alternatives.\n"
    "- Nutrition: Keep macros consistent (Calories ~= 4*Protein + 4*Carbohydrates + 9*Fat) using finite non-negative numbers."
)

VOICE_PARSER_SYSTEM_INSTRUCTION = (
    "Parse spoken meal transcripts (English/Indian/Hinglish) into compact itemized nutrition JSON.\n"
    "Rules:\n"
    "1. Split compound/Hinglish meals cleanly (e.g. 'do aloo paratha dahi ke saath, ek cup adrak chai' -> Aloo Paratha, Plain Dahi, Adrak Chai).\n"
    "2. Honor in-flight corrections ('one roti, actually make that two', 'no sugar') and note briefly in 'warnings'.\n"
    "3. Realistic weights: 1 roti~35g, 1 paratha~100g, 1 bowl dal/rice~160g, 1 tbsp ghee/oil~15g, 1 cup chai~150ml.\n"
    "4. Set state ('raw'|'cooked'|'unspecified'); adjust macros for raw vs cooked.\n"
    "5. Never invent unspoken foods; obey Calories~=4P+4C+9F with non-negative numbers. Keep text brief."
)


"""Dual-provider AI orchestration service with intelligent fallback between Gemini and OpenRouter."""

import logging
import time
from typing import Callable, Optional

from app.config import ConfigurationError, Settings, get_settings
from app.models.food import FoodRecognitionResponse, VoiceMealParseResponse
from app.services.providers.base import (
    AIAllProvidersFailedError,
    AIAuthenticationError,
    AIRateLimitError,
    AIRequestCancelledError,
    AIServiceError,
    AITimeoutError,
    AITransientError,
    AIUnavailableError,
    BaseAIProvider,
    ModelOutputValidationError,
    get_current_request_id,
    is_request_cancelled,
)
from app.services.providers.gemini_provider import GeminiProvider
from app.services.providers.openrouter_provider import OpenRouterProvider

logger = logging.getLogger("bites2go.ai_service")


class DualProviderService:
    """Orchestrates primary and fallback AI providers with bounded retries, deadline budgets, and failover."""

    def __init__(
        self,
        gemini_provider: Optional[BaseAIProvider] = None,
        openrouter_provider: Optional[BaseAIProvider] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        self._settings = settings or get_settings()
        fallback_active = bool(
            self._settings.ai_fallback_enabled and self._settings.is_openrouter_configured
        )
        gemini_retries = 1 if fallback_active else self._settings.gemini_max_retries
        self._gemini = gemini_provider or GeminiProvider(
            settings=self._settings,
            max_retries=gemini_retries,
            retry_on_rate_limit=not fallback_active,
        )
        self._openrouter = openrouter_provider or OpenRouterProvider(settings=self._settings)

    @property
    def gemini(self) -> BaseAIProvider:
        return self._gemini

    @property
    def openrouter(self) -> BaseAIProvider:
        return self._openrouter

    @property
    def primary_provider(self) -> BaseAIProvider:
        if self._settings.ai_primary_provider.lower() == "openrouter":
            return self._openrouter
        return self._gemini

    @property
    def fallback_provider(self) -> BaseAIProvider:
        if self._settings.ai_primary_provider.lower() == "openrouter":
            return self._gemini
        return self._openrouter

    @property
    def is_fallback_enabled(self) -> bool:
        return bool(self._settings.ai_fallback_enabled)

    def recognize_food(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        deadline_seconds: Optional[float] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> FoodRecognitionResponse:
        """Execute photo recognition with primary provider and intelligent failover to secondary."""
        if is_request_cancelled(is_cancelled):
            raise AIRequestCancelledError("Client disconnected / request cancelled.", provider="ai_service")

        primary = self.primary_provider
        fallback = self.fallback_provider
        fallback_available = self.is_fallback_enabled and fallback.is_configured

        total_budget = (
            deadline_seconds
            if deadline_seconds is not None
            else self._settings.server_deadline_seconds
        )
        start_time = time.perf_counter()
        logger.info(
            "[Timing][%s] AI Service [%s] started (budget: %.1fs, primary=%s, fallback=%s)",
            get_current_request_id(),
            "recognize_food",
            total_budget,
            primary.name,
            fallback.name if fallback_available else "none",
        )

        def remaining_budget() -> float:
            elapsed = time.perf_counter() - start_time
            return max(0.0, total_budget - elapsed)

        def _attempt_fallback(primary_err: Exception, reason: str) -> FoodRecognitionResponse:
            if not fallback_available:
                raise primary_err
            if is_request_cancelled(is_cancelled):
                raise AIRequestCancelledError("Client disconnected / request cancelled.", provider=fallback.name)

            rem = remaining_budget()
            if rem < 4.0:
                logger.warning(
                    "[Timing][%s] Remaining budget (%.2fs) insufficient for fallback AI provider [%s] (min 4.0s).",
                    get_current_request_id(),
                    rem,
                    fallback.name,
                )
                raise AITimeoutError(
                    f"Request deadline reached after primary attempt ({total_budget:.1f}s budget exhausted; {rem:.1f}s remaining).",
                    provider=primary.name,
                )

            logger.info(
                "[Timing][%s] Fallback start: switching from primary [%s] to fallback [%s] after %s (remaining budget: %.2fs).",
                get_current_request_id(),
                primary.name,
                fallback.name,
                reason,
                rem,
            )
            fallback_timeout = min(
                self._settings.openrouter_timeout_seconds
                if fallback.name == "openrouter"
                else self._settings.gemini_timeout_seconds,
                rem,
            )
            try:
                return fallback.recognize_food(
                    image_bytes,
                    mime_type=mime_type,
                    timeout_seconds=fallback_timeout,
                    is_cancelled=is_cancelled,
                )
            except AIRequestCancelledError:
                raise
            except Exception as fb_err:
                logger.error(
                    "Fallback provider [%s] also failed after primary %s: %s",
                    fallback.name,
                    reason,
                    str(fb_err),
                )
                raise AIAllProvidersFailedError(
                    message=f"Both AI providers failed. Primary [{primary.name}] {reason}; fallback [{fallback.name}] failed.",
                    primary_provider=primary.name,
                    primary_error=primary_err,
                    fallback_provider=fallback.name,
                    fallback_error=fb_err,
                ) from fb_err

        # Case 1: Primary provider is not configured
        if not primary.is_configured:
            if fallback_available:
                logger.warning(
                    "Primary AI provider [%s] is not configured. Routing directly to fallback [%s].",
                    primary.name,
                    fallback.name,
                )
                rem = remaining_budget()
                if rem < 4.0:
                    raise AITimeoutError(
                        f"Request deadline reached before fallback execution ({total_budget:.1f}s budget exhausted).",
                        provider=fallback.name,
                    )
                fallback_timeout = min(
                    self._settings.openrouter_timeout_seconds
                    if fallback.name == "openrouter"
                    else self._settings.gemini_timeout_seconds,
                    rem,
                )
                return fallback.recognize_food(
                    image_bytes,
                    mime_type=mime_type,
                    timeout_seconds=fallback_timeout,
                    is_cancelled=is_cancelled,
                )
            raise ConfigurationError(
                f"AI provider [{primary.name}] is not configured. "
                "Please configure GEMINI_API_KEY or OPENROUTER_API_KEY in backend/.env."
            )

        # Case 2: Attempt primary provider within budget
        primary_default_timeout = (
            self._settings.gemini_timeout_seconds
            if primary.name == "gemini"
            else self._settings.openrouter_timeout_seconds
        )
        rem = remaining_budget()
        primary_timeout = min(primary_default_timeout, rem)

        try:
            return primary.recognize_food(
                image_bytes,
                mime_type=mime_type,
                timeout_seconds=primary_timeout,
                is_cancelled=is_cancelled,
            )

        except AIRequestCancelledError:
            logger.info("Food recognition cancelled by client. Aborting without fallback.")
            raise

        except AIRateLimitError as rate_err:
            logger.warning(
                "Primary provider [%s] rate limited / quota exhausted: %s.",
                primary.name,
                str(rate_err),
            )
            return _attempt_fallback(rate_err, "rate limited")

        except (AITimeoutError, AIUnavailableError) as trans_err:
            logger.warning(
                "Primary provider [%s] failed with transient error after retries: %s.",
                primary.name,
                str(trans_err),
            )
            return _attempt_fallback(trans_err, "transient error")

        except AIAuthenticationError as auth_err:
            logger.error(
                "Primary provider [%s] authentication failed: %s.",
                primary.name,
                str(auth_err),
            )
            return _attempt_fallback(auth_err, "authentication failed")

        except ModelOutputValidationError as val_err:
            logger.warning(
                "Primary provider [%s] returned malformed output: %s.",
                primary.name,
                str(val_err),
            )
            return _attempt_fallback(val_err, "output malformed")

        except Exception as exc:
            logger.warning(
                "Primary provider [%s] encountered unexpected error: %s. Attempting fallback.",
                primary.name,
                str(exc),
            )
            return _attempt_fallback(exc, str(exc))

    def parse_voice_meal(
        self,
        transcript: str,
        meal_context: Optional[str] = None,
        deadline_seconds: Optional[float] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> VoiceMealParseResponse:
        """Execute spoken food parsing with primary provider and intelligent failover to secondary."""
        if is_request_cancelled(is_cancelled):
            raise AIRequestCancelledError("Client disconnected / request cancelled.", provider="ai_service")

        primary = self.primary_provider
        fallback = self.fallback_provider
        fallback_available = self.is_fallback_enabled and fallback.is_configured

        total_budget = (
            deadline_seconds
            if deadline_seconds is not None
            else self._settings.voice_server_deadline_seconds
        )
        start_time = time.perf_counter()
        logger.info(
            "[Timing][%s] AI Service [%s] started (budget: %.1fs, primary=%s, fallback=%s)",
            get_current_request_id(),
            "parse_voice_meal",
            total_budget,
            primary.name,
            fallback.name if fallback_available else "none",
        )

        def remaining_budget() -> float:
            elapsed = time.perf_counter() - start_time
            return max(0.0, total_budget - elapsed)

        def _attempt_fallback(primary_err: Exception, reason: str) -> VoiceMealParseResponse:
            if not fallback_available:
                raise primary_err
            if is_request_cancelled(is_cancelled):
                raise AIRequestCancelledError("Client disconnected / request cancelled.", provider=fallback.name)

            rem = remaining_budget()
            if rem < 4.0:
                logger.warning(
                    "[Timing][%s] Remaining budget (%.2fs) insufficient for fallback AI provider [%s] (min 4.0s).",
                    get_current_request_id(),
                    rem,
                    fallback.name,
                )
                raise AITimeoutError(
                    f"Request deadline reached after primary attempt ({total_budget:.1f}s budget exhausted; {rem:.1f}s remaining).",
                    provider=primary.name,
                )

            logger.info(
                "[Timing][%s] Fallback start: switching from primary [%s] to fallback [%s] after %s (remaining budget: %.2fs).",
                get_current_request_id(),
                primary.name,
                fallback.name,
                reason,
                rem,
            )
            fallback_timeout = min(
                self._settings.openrouter_timeout_seconds
                if fallback.name == "openrouter"
                else self._settings.gemini_timeout_seconds,
                rem,
            )
            try:
                return fallback.parse_voice_meal(
                    transcript=transcript,
                    meal_context=meal_context,
                    timeout_seconds=fallback_timeout,
                    is_cancelled=is_cancelled,
                )
            except AIRequestCancelledError:
                raise
            except Exception as fb_err:
                logger.error(
                    "Fallback provider [%s] also failed after primary %s: %s",
                    fallback.name,
                    reason,
                    str(fb_err),
                )
                raise AIAllProvidersFailedError(
                    message=f"Both AI providers failed. Primary [{primary.name}] {reason}; fallback [{fallback.name}] failed.",
                    primary_provider=primary.name,
                    primary_error=primary_err,
                    fallback_provider=fallback.name,
                    fallback_error=fb_err,
                ) from fb_err

        # Case 1: Primary provider is not configured
        if not primary.is_configured:
            if fallback_available:
                logger.warning(
                    "Primary AI provider [%s] is not configured. Routing directly to fallback [%s].",
                    primary.name,
                    fallback.name,
                )
                rem = remaining_budget()
                if rem < 4.0:
                    raise AITimeoutError(
                        f"Request deadline reached before fallback execution ({total_budget:.1f}s budget exhausted).",
                        provider=fallback.name,
                    )
                fallback_timeout = min(
                    self._settings.openrouter_timeout_seconds
                    if fallback.name == "openrouter"
                    else self._settings.gemini_timeout_seconds,
                    rem,
                )
                return fallback.parse_voice_meal(
                    transcript=transcript,
                    meal_context=meal_context,
                    timeout_seconds=fallback_timeout,
                    is_cancelled=is_cancelled,
                )
            raise ConfigurationError(
                f"AI provider [{primary.name}] is not configured. "
                "Please configure GEMINI_API_KEY or OPENROUTER_API_KEY in backend/.env."
            )

        # Case 2: Attempt primary provider within budget
        primary_default_timeout = (
            min(self._settings.gemini_timeout_seconds, 10.0)
            if primary.name == "gemini"
            else self._settings.openrouter_timeout_seconds
        )
        rem = remaining_budget()
        primary_timeout = min(primary_default_timeout, rem)

        try:
            return primary.parse_voice_meal(
                transcript=transcript,
                meal_context=meal_context,
                timeout_seconds=primary_timeout,
                is_cancelled=is_cancelled,
            )

        except AIRequestCancelledError:
            logger.info("Voice meal parsing cancelled by client. Aborting without fallback.")
            raise

        except AIRateLimitError as rate_err:
            logger.warning(
                "Primary provider [%s] rate limited / quota exhausted: %s.",
                primary.name,
                str(rate_err),
            )
            return _attempt_fallback(rate_err, "rate limited")

        except (AITimeoutError, AIUnavailableError) as trans_err:
            logger.warning(
                "Primary provider [%s] failed with transient error after retries: %s.",
                primary.name,
                str(trans_err),
            )
            return _attempt_fallback(trans_err, "transient error")

        except AIAuthenticationError as auth_err:
            logger.error(
                "Primary provider [%s] authentication failed: %s.",
                primary.name,
                str(auth_err),
            )
            return _attempt_fallback(auth_err, "authentication failed")

        except ModelOutputValidationError as val_err:
            logger.warning(
                "Primary provider [%s] returned malformed voice output: %s.",
                primary.name,
                str(val_err),
            )
            return _attempt_fallback(val_err, "output malformed")

        except Exception as exc:
            logger.warning(
                "Primary provider [%s] encountered unexpected error: %s. Attempting fallback.",
                primary.name,
                str(exc),
            )
            return _attempt_fallback(exc, str(exc))


_ai_service: Optional[DualProviderService] = None


def get_ai_service() -> DualProviderService:
    """Singleton getter for DualProviderService."""
    global _ai_service
    if _ai_service is None:
        _ai_service = DualProviderService()
    return _ai_service


# Backward compatibility aliases
AIService = DualProviderService

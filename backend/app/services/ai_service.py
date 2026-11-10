"""Dual-provider AI orchestration service with intelligent fallback between Gemini and OpenRouter."""

import logging
import time
from typing import Callable, Optional, TypeVar

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

T = TypeVar("T")


class DualProviderService:
    """Orchestrates task-specific primary/fallback AI providers with bounded deadlines and failover."""

    def __init__(
        self,
        gemini_provider: Optional[BaseAIProvider] = None,
        openrouter_provider: Optional[BaseAIProvider] = None,
        settings: Optional[Settings] = None,
        photo_openrouter_provider: Optional[BaseAIProvider] = None,
        voice_openrouter_provider: Optional[BaseAIProvider] = None,
    ) -> None:
        self._settings = settings or get_settings()

        photo_fallback_active = bool(
            self._settings.ai_fallback_enabled
            and (
                self._settings.is_openrouter_configured
                if self._settings.photo_primary_provider == "gemini"
                else self._settings.is_gemini_configured
            )
        )
        voice_fallback_active = bool(
            self._settings.ai_fallback_enabled
            and (
                self._settings.is_gemini_configured
                if self._settings.voice_primary_provider == "openrouter"
                else self._settings.is_openrouter_configured
            )
        )

        gemini_photo_retries = 0 if photo_fallback_active else self._settings.gemini_max_retries
        gemini_voice_retries = 0 if voice_fallback_active else self._settings.gemini_max_retries

        self._gemini = gemini_provider or GeminiProvider(
            settings=self._settings,
            max_retries=gemini_photo_retries,
            retry_on_rate_limit=not photo_fallback_active,
        )
        if gemini_provider is not None:
            self._voice_gemini = gemini_provider
        elif gemini_voice_retries == gemini_photo_retries and voice_fallback_active == photo_fallback_active:
            self._voice_gemini = self._gemini
        else:
            self._voice_gemini = GeminiProvider(
                settings=self._settings,
                max_retries=gemini_voice_retries,
                retry_on_rate_limit=not voice_fallback_active,
            )

        photo_or_retries = 0 if photo_fallback_active else self._settings.openrouter_max_retries
        voice_or_retries = 0 if voice_fallback_active else self._settings.openrouter_max_retries

        self._photo_openrouter = (
            photo_openrouter_provider
            or openrouter_provider
            or OpenRouterProvider(
                settings=self._settings,
                model=self._settings.photo_openrouter_model,
                alternative_model=self._settings.photo_openrouter_alternative_model,
                max_retries=photo_or_retries,
            )
        )
        self._voice_openrouter = (
            voice_openrouter_provider
            or openrouter_provider
            or OpenRouterProvider(
                settings=self._settings,
                model=self._settings.voice_openrouter_model,
                alternative_model=self._settings.voice_openrouter_alternative_model,
                timeout_seconds=self._settings.voice_primary_timeout_seconds,
                max_retries=voice_or_retries,
            )
        )
        # Preserve .openrouter attribute pointing to photo_openrouter for backward test compatibility
        self._openrouter = self._photo_openrouter

    @property
    def gemini(self) -> BaseAIProvider:
        return self._gemini

    @property
    def openrouter(self) -> BaseAIProvider:
        return self._openrouter

    @property
    def photo_openrouter(self) -> BaseAIProvider:
        return self._photo_openrouter

    @property
    def voice_openrouter(self) -> BaseAIProvider:
        return self._voice_openrouter

    def _resolve_task_providers(self, task: str) -> tuple[BaseAIProvider, BaseAIProvider]:
        """Return (primary_provider, fallback_provider) for 'photo' or 'voice' tasks."""
        if task == "voice":
            if self._settings.voice_primary_provider.lower() == "gemini":
                return self._voice_gemini, self._voice_openrouter
            return self._voice_openrouter, self._voice_gemini

        # Photo recognition: Gemini primary -> OpenRouter vision fallback by default
        primary_name = (
            self._settings.photo_primary_provider
            if self._settings.photo_primary_provider != "gemini"
            else self._settings.ai_primary_provider
        ).lower()
        if primary_name == "openrouter":
            return self._photo_openrouter, self._gemini
        return self._gemini, self._photo_openrouter

    @property
    def primary_provider(self) -> BaseAIProvider:
        return self._resolve_task_providers("photo")[0]

    @property
    def fallback_provider(self) -> BaseAIProvider:
        return self._resolve_task_providers("photo")[1]

    @property
    def voice_primary_provider(self) -> BaseAIProvider:
        return self._resolve_task_providers("voice")[0]

    @property
    def voice_fallback_provider(self) -> BaseAIProvider:
        return self._resolve_task_providers("voice")[1]

    @property
    def is_fallback_enabled(self) -> bool:
        return bool(self._settings.ai_fallback_enabled)

    def _default_provider_timeout(self, task: str, provider_name: str, is_fallback: bool) -> float:
        """Return configured timeout budget for the specific task/provider role."""
        if task == "voice":
            if provider_name == "openrouter":
                return (
                    self._settings.openrouter_timeout_seconds
                    if is_fallback
                    else self._settings.voice_primary_timeout_seconds
                )
            return self._settings.gemini_timeout_seconds

        if provider_name == "openrouter":
            return self._settings.openrouter_timeout_seconds
        return self._settings.gemini_timeout_seconds

    def _execute_with_failover(
        self,
        task: str,
        operation_name: str,
        total_budget: float,
        reserve_fallback_seconds: float,
        invoke_fn: Callable[[BaseAIProvider, float], T],
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> T:
        """Execute a task-specific primary AI call with bounded fallback and cancellation."""
        if is_request_cancelled(is_cancelled):
            raise AIRequestCancelledError("Client disconnected / request cancelled.", provider="ai_service")

        primary, fallback = self._resolve_task_providers(task)
        fallback_available = self.is_fallback_enabled and fallback.is_configured

        start_time = time.perf_counter()
        logger.info(
            "[Timing][%s] AI Service [%s] started (task=%s, budget=%.1fs, primary=%s, fallback=%s)",
            get_current_request_id(),
            operation_name,
            task,
            total_budget,
            primary.name,
            fallback.name if fallback_available else "none",
        )

        def remaining_budget() -> float:
            elapsed = time.perf_counter() - start_time
            return max(0.0, total_budget - elapsed)

        def _attempt_fallback(primary_err: Exception, reason: str) -> T:
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
                "[Timing][%s] Fallback start: switching from primary [%s] to fallback [%s] for task=[%s] after %s (remaining budget: %.2fs).",
                get_current_request_id(),
                primary.name,
                fallback.name,
                task,
                reason,
                rem,
            )
            fallback_timeout = min(
                self._default_provider_timeout(task, fallback.name, is_fallback=True),
                rem,
            )
            try:
                return invoke_fn(fallback, fallback_timeout)
            except AIRequestCancelledError:
                raise
            except Exception as fb_err:
                logger.error(
                    "[Timing][%s] Fallback provider [%s] also failed after primary [%s] %s: %s",
                    get_current_request_id(),
                    fallback.name,
                    primary.name,
                    reason,
                    type(fb_err).__name__,
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
                    "[Timing][%s] Primary AI provider [%s] for task=[%s] is not configured. Routing directly to fallback [%s].",
                    get_current_request_id(),
                    primary.name,
                    task,
                    fallback.name,
                )
                rem = remaining_budget()
                if rem < 4.0:
                    raise AITimeoutError(
                        f"Request deadline reached before fallback execution ({total_budget:.1f}s budget exhausted).",
                        provider=fallback.name,
                    )
                fallback_timeout = min(
                    self._default_provider_timeout(task, fallback.name, is_fallback=True),
                    rem,
                )
                return invoke_fn(fallback, fallback_timeout)
            raise ConfigurationError(
                f"AI provider [{primary.name}] is not configured. "
                "Please configure GEMINI_API_KEY or OPENROUTER_API_KEY in backend/.env."
            )

        # Case 2: Attempt primary provider within bounded budget reserving fallback headroom
        primary_default_timeout = self._default_provider_timeout(task, primary.name, is_fallback=False)
        rem = remaining_budget()
        max_primary_budget = (
            max(total_budget - reserve_fallback_seconds, 5.0)
            if fallback_available
            else rem
        )
        primary_timeout = min(primary_default_timeout, max_primary_budget, rem)

        try:
            return invoke_fn(primary, primary_timeout)

        except AIRequestCancelledError:
            logger.info("[Timing][%s] %s cancelled by client. Aborting without fallback.", get_current_request_id(), operation_name)
            raise

        except AIRateLimitError as rate_err:
            logger.warning(
                "[Timing][%s] Primary [%s] rate limited / quota exhausted (%s).",
                get_current_request_id(),
                primary.name,
                getattr(rate_err, "error_category", None) or "rate_limit",
            )
            return _attempt_fallback(rate_err, "rate limited")

        except (AITimeoutError, AIUnavailableError) as trans_err:
            logger.warning(
                "[Timing][%s] Primary [%s] failed with transient error (%s).",
                get_current_request_id(),
                primary.name,
                type(trans_err).__name__,
            )
            return _attempt_fallback(trans_err, "transient error")

        except AIAuthenticationError as auth_err:
            logger.error(
                "[Timing][%s] Primary [%s] authentication failed.",
                get_current_request_id(),
                primary.name,
            )
            return _attempt_fallback(auth_err, "authentication failed")

        except ModelOutputValidationError as val_err:
            logger.warning(
                "[Timing][%s] Primary [%s] returned malformed/empty output (%s).",
                get_current_request_id(),
                primary.name,
                getattr(val_err, "error_category", None) or "output_invalid",
            )
            return _attempt_fallback(val_err, "output malformed")

        except Exception as exc:
            logger.warning(
                "[Timing][%s] Primary [%s] encountered unexpected error (%s). Attempting fallback.",
                get_current_request_id(),
                primary.name,
                type(exc).__name__,
            )
            return _attempt_fallback(exc, type(exc).__name__)

    def recognize_food(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        deadline_seconds: Optional[float] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> FoodRecognitionResponse:
        """Execute photo recognition (Primary: Gemini Vision, Fallback: OpenRouter Vision)."""
        total_budget = (
            deadline_seconds
            if deadline_seconds is not None
            else self._settings.server_deadline_seconds
        )
        return self._execute_with_failover(
            task="photo",
            operation_name="recognize_food",
            total_budget=total_budget,
            reserve_fallback_seconds=16.0,
            invoke_fn=lambda provider, timeout_s: provider.recognize_food(
                image_bytes,
                mime_type=mime_type,
                timeout_seconds=timeout_s,
                is_cancelled=is_cancelled,
            ),
            is_cancelled=is_cancelled,
        )

    def parse_voice_meal(
        self,
        transcript: str,
        meal_context: Optional[str] = None,
        deadline_seconds: Optional[float] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> VoiceMealParseResponse:
        """Execute voice meal parsing (Primary: OpenRouter Nemotron Ultra, Fallback: Gemini)."""
        total_budget = (
            deadline_seconds
            if deadline_seconds is not None
            else self._settings.voice_server_deadline_seconds
        )
        return self._execute_with_failover(
            task="voice",
            operation_name="parse_voice_meal",
            total_budget=total_budget,
            reserve_fallback_seconds=10.0,
            invoke_fn=lambda provider, timeout_s: provider.parse_voice_meal(
                transcript=transcript,
                meal_context=meal_context,
                timeout_seconds=timeout_s,
                is_cancelled=is_cancelled,
            ),
            is_cancelled=is_cancelled,
        )


_ai_service: Optional[DualProviderService] = None


def get_ai_service() -> DualProviderService:
    """Singleton getter for DualProviderService."""
    global _ai_service
    if _ai_service is None:
        _ai_service = DualProviderService()
    return _ai_service


# Backward compatibility aliases
AIService = DualProviderService

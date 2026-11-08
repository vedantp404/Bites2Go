"""Dual-provider AI orchestration service with intelligent fallback between Gemini and OpenRouter."""

import logging
from typing import Optional

from app.config import ConfigurationError, Settings, get_settings
from app.models.food import FoodRecognitionResponse, VoiceMealParseResponse
from app.services.providers.base import (
    AIAllProvidersFailedError,
    AIAuthenticationError,
    AIRateLimitError,
    AIServiceError,
    AITimeoutError,
    AITransientError,
    AIUnavailableError,
    BaseAIProvider,
    ModelOutputValidationError,
)
from app.services.providers.gemini_provider import GeminiProvider
from app.services.providers.openrouter_provider import OpenRouterProvider

logger = logging.getLogger("bites2go.ai_service")


class DualProviderService:
    """Orchestrates primary and fallback AI providers with bounded retries and failover."""

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
        self._gemini = gemini_provider or GeminiProvider(
            settings=self._settings,
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
    ) -> FoodRecognitionResponse:
        """Execute photo recognition with primary provider and intelligent failover to secondary."""
        primary = self.primary_provider
        fallback = self.fallback_provider
        fallback_available = self.is_fallback_enabled and fallback.is_configured

        # Case 1: Primary provider is not configured
        if not primary.is_configured:
            if fallback_available:
                logger.warning(
                    "Primary AI provider [%s] is not configured. Routing directly to fallback [%s].",
                    primary.name,
                    fallback.name,
                )
                return fallback.recognize_food(image_bytes, mime_type=mime_type)
            raise ConfigurationError(
                f"AI provider [{primary.name}] is not configured. "
                "Please configure GEMINI_API_KEY or OPENROUTER_API_KEY in backend/.env."
            )

        # Case 2: Attempt primary provider
        try:
            return primary.recognize_food(image_bytes, mime_type=mime_type)

        except AIRateLimitError as rate_err:
            # Quota exhausted or rate limited: Immediately switch to fallback without retrying primary
            logger.warning(
                "Primary provider [%s] rate limited / quota exhausted: %s.",
                primary.name,
                str(rate_err),
            )
            if fallback_available:
                logger.info(
                    "Immediately switching to fallback provider [%s] for food recognition.",
                    fallback.name,
                )
                try:
                    return fallback.recognize_food(image_bytes, mime_type=mime_type)
                except Exception as fb_err:
                    logger.error(
                        "Fallback provider [%s] also failed after primary quota exhaustion: %s",
                        fallback.name,
                        str(fb_err),
                    )
                    raise AIAllProvidersFailedError(
                        message=f"Both AI providers failed. Primary [{primary.name}] rate limited; fallback [{fallback.name}] failed.",
                        primary_provider=primary.name,
                        primary_error=rate_err,
                        fallback_provider=fallback.name,
                        fallback_error=fb_err,
                    ) from fb_err
            raise rate_err

        except (AITimeoutError, AIUnavailableError) as trans_err:
            # Transient server failure after bounded retries: Failover to fallback
            logger.warning(
                "Primary provider [%s] failed with transient error after retries: %s.",
                primary.name,
                str(trans_err),
            )
            if fallback_available:
                logger.info(
                    "Attempting fallback provider [%s] after primary transient error.",
                    fallback.name,
                )
                try:
                    return fallback.recognize_food(image_bytes, mime_type=mime_type)
                except Exception as fb_err:
                    logger.error(
                        "Fallback provider [%s] also failed after primary transient failure: %s",
                        fallback.name,
                        str(fb_err),
                    )
                    raise AIAllProvidersFailedError(
                        message=f"Both AI providers failed. Primary [{primary.name}] transient failure; fallback [{fallback.name}] failed.",
                        primary_provider=primary.name,
                        primary_error=trans_err,
                        fallback_provider=fallback.name,
                        fallback_error=fb_err,
                    ) from fb_err
            raise trans_err

        except AIAuthenticationError as auth_err:
            # Primary authentication failed: Switch to fallback if available
            logger.error(
                "Primary provider [%s] authentication failed: %s.",
                primary.name,
                str(auth_err),
            )
            if fallback_available:
                logger.info(
                    "Attempting fallback provider [%s] after primary authentication failure.",
                    fallback.name,
                )
                try:
                    return fallback.recognize_food(image_bytes, mime_type=mime_type)
                except Exception as fb_err:
                    raise AIAllProvidersFailedError(
                        message=f"Both AI providers failed. Primary [{primary.name}] authentication failed; fallback [{fallback.name}] failed.",
                        primary_provider=primary.name,
                        primary_error=auth_err,
                        fallback_provider=fallback.name,
                        fallback_error=fb_err,
                    ) from fb_err
            raise auth_err

        except ModelOutputValidationError as val_err:
            # Primary returned malformed model output
            logger.warning(
                "Primary provider [%s] returned malformed output: %s.",
                primary.name,
                str(val_err),
            )
            if fallback_available:
                logger.info(
                    "Attempting fallback provider [%s] after primary validation failure.",
                    fallback.name,
                )
                try:
                    return fallback.recognize_food(image_bytes, mime_type=mime_type)
                except Exception as fb_err:
                    raise AIAllProvidersFailedError(
                        message=f"Both AI providers failed. Primary [{primary.name}] output malformed; fallback [{fallback.name}] failed.",
                        primary_provider=primary.name,
                        primary_error=val_err,
                        fallback_provider=fallback.name,
                        fallback_error=fb_err,
                    ) from fb_err
            raise val_err

        except Exception as exc:
            # Any other unexpected exception
            if fallback_available:
                logger.warning(
                    "Primary provider [%s] encountered unexpected error: %s. Attempting fallback.",
                    primary.name,
                    str(exc),
                )
                try:
                    return fallback.recognize_food(image_bytes, mime_type=mime_type)
                except Exception as fb_err:
                    raise AIAllProvidersFailedError(
                        message=f"Both AI providers failed. Primary [{primary.name}] error: {str(exc)}; fallback [{fallback.name}] failed.",
                        primary_provider=primary.name,
                        primary_error=exc,
                        fallback_provider=fallback.name,
                        fallback_error=fb_err,
                    ) from fb_err
            raise exc

    def parse_voice_meal(
        self,
        transcript: str,
        meal_context: Optional[str] = None,
    ) -> VoiceMealParseResponse:
        """Execute spoken food parsing with primary provider and intelligent failover to secondary."""
        primary = self.primary_provider
        fallback = self.fallback_provider
        fallback_available = self.is_fallback_enabled and fallback.is_configured

        if not primary.is_configured:
            if fallback_available:
                logger.warning(
                    "Primary AI provider [%s] is not configured. Routing directly to fallback [%s].",
                    primary.name,
                    fallback.name,
                )
                return fallback.parse_voice_meal(transcript=transcript, meal_context=meal_context)
            raise ConfigurationError(
                f"AI provider [{primary.name}] is not configured. "
                "Please configure GEMINI_API_KEY or OPENROUTER_API_KEY in backend/.env."
            )

        try:
            return primary.parse_voice_meal(transcript=transcript, meal_context=meal_context)

        except AIRateLimitError as rate_err:
            logger.warning(
                "Primary provider [%s] rate limited / quota exhausted: %s.",
                primary.name,
                str(rate_err),
            )
            if fallback_available:
                logger.info(
                    "Immediately switching to fallback provider [%s] for voice meal parsing.",
                    fallback.name,
                )
                try:
                    return fallback.parse_voice_meal(transcript=transcript, meal_context=meal_context)
                except Exception as fb_err:
                    logger.error(
                        "Fallback provider [%s] also failed after primary quota exhaustion: %s",
                        fallback.name,
                        str(fb_err),
                    )
                    raise AIAllProvidersFailedError(
                        message=f"Both AI providers failed. Primary [{primary.name}] rate limited; fallback [{fallback.name}] failed.",
                        primary_provider=primary.name,
                        primary_error=rate_err,
                        fallback_provider=fallback.name,
                        fallback_error=fb_err,
                    ) from fb_err
            raise rate_err

        except (AITimeoutError, AIUnavailableError) as trans_err:
            logger.warning(
                "Primary provider [%s] failed with transient error after retries: %s.",
                primary.name,
                str(trans_err),
            )
            if fallback_available:
                logger.info(
                    "Attempting fallback provider [%s] after primary transient error.",
                    fallback.name,
                )
                try:
                    return fallback.parse_voice_meal(transcript=transcript, meal_context=meal_context)
                except Exception as fb_err:
                    logger.error(
                        "Fallback provider [%s] also failed after primary transient failure: %s",
                        fallback.name,
                        str(fb_err),
                    )
                    raise AIAllProvidersFailedError(
                        message=f"Both AI providers failed. Primary [{primary.name}] transient failure; fallback [{fallback.name}] failed.",
                        primary_provider=primary.name,
                        primary_error=trans_err,
                        fallback_provider=fallback.name,
                        fallback_error=fb_err,
                    ) from fb_err
            raise trans_err

        except AIAuthenticationError as auth_err:
            logger.error(
                "Primary provider [%s] authentication failed: %s.",
                primary.name,
                str(auth_err),
            )
            if fallback_available:
                logger.info(
                    "Attempting fallback provider [%s] after primary authentication failure.",
                    fallback.name,
                )
                try:
                    return fallback.parse_voice_meal(transcript=transcript, meal_context=meal_context)
                except Exception as fb_err:
                    raise AIAllProvidersFailedError(
                        message=f"Both AI providers failed. Primary [{primary.name}] authentication failed; fallback [{fallback.name}] failed.",
                        primary_provider=primary.name,
                        primary_error=auth_err,
                        fallback_provider=fallback.name,
                        fallback_error=fb_err,
                    ) from fb_err
            raise auth_err

        except ModelOutputValidationError as val_err:
            logger.warning(
                "Primary provider [%s] returned malformed voice output: %s.",
                primary.name,
                str(val_err),
            )
            if fallback_available:
                logger.info(
                    "Attempting fallback provider [%s] after primary validation failure.",
                    fallback.name,
                )
                try:
                    return fallback.parse_voice_meal(transcript=transcript, meal_context=meal_context)
                except Exception as fb_err:
                    raise AIAllProvidersFailedError(
                        message=f"Both AI providers failed. Primary [{primary.name}] output malformed; fallback [{fallback.name}] failed.",
                        primary_provider=primary.name,
                        primary_error=val_err,
                        fallback_provider=fallback.name,
                        fallback_error=fb_err,
                    ) from fb_err
            raise val_err

        except Exception as exc:
            if fallback_available:
                logger.warning(
                    "Primary provider [%s] encountered unexpected error: %s. Attempting fallback.",
                    primary.name,
                    str(exc),
                )
                try:
                    return fallback.parse_voice_meal(transcript=transcript, meal_context=meal_context)
                except Exception as fb_err:
                    raise AIAllProvidersFailedError(
                        message=f"Both AI providers failed. Primary [{primary.name}] error: {str(exc)}; fallback [{fallback.name}] failed.",
                        primary_provider=primary.name,
                        primary_error=exc,
                        fallback_provider=fallback.name,
                        fallback_error=fb_err,
                    ) from fb_err
            raise exc


_ai_service: Optional[DualProviderService] = None


def get_ai_service() -> DualProviderService:
    """Singleton getter for DualProviderService."""
    global _ai_service
    if _ai_service is None:
        _ai_service = DualProviderService()
    return _ai_service


# Backward compatibility aliases
AIService = DualProviderService

"""Google Gemini AI recognition provider using the official Google GenAI SDK."""

import json
import logging
import time
from typing import Callable, Optional, TypeVar
import httpx
from google import genai
from google.genai import errors, types
from pydantic import ValidationError
import tenacity

from app.config import Settings, get_settings
from app.models.food import FoodRecognitionResponse, VoiceMealParseResponse
from app.services.providers.base import (
    AIAuthenticationError,
    AIRateLimitError,
    AIServiceError,
    AITimeoutError,
    AIUnavailableError,
    BaseAIProvider,
    ModelOutputValidationError,
    SYSTEM_INSTRUCTION,
    VOICE_PARSER_SYSTEM_INSTRUCTION,
)

logger = logging.getLogger("bites2go.gemini")

T = TypeVar("T")


def _get_safe_error_summary(exc: BaseException) -> str:
    """Extract a safe summary of an error without exposing secrets, prompts, or API keys."""
    if isinstance(exc, errors.APIError):
        status_part = f" {exc.status}" if exc.status else ""
        return f"HTTP {exc.code}{status_part}".strip()
    if isinstance(exc, (TimeoutError, httpx.TimeoutException)):
        return "Request timed out"
    if isinstance(exc, (httpx.ConnectError, httpx.RemoteProtocolError)):
        return "Connection error / network drop"
    return type(exc).__name__


class GeminiProvider(BaseAIProvider):
    """Gemini AI provider wrapping Google GenAI SDK with bounded retries."""

    def __init__(
        self,
        client: Optional[genai.Client] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        max_retries: Optional[int] = None,
        retry_initial_delay: Optional[float] = None,
        retry_max_delay: Optional[float] = None,
        retry_on_rate_limit: bool = True,
        settings: Optional[Settings] = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._model = model or self._settings.gemini_model
        self._client = client
        self._per_attempt_timeout_seconds = (
            timeout_seconds if timeout_seconds is not None else self._settings.gemini_timeout_seconds
        )
        self._voice_timeout_seconds = min(self._per_attempt_timeout_seconds, 15.0)
        self._max_retries = (
            max_retries if max_retries is not None else self._settings.gemini_max_retries
        )
        self._retry_initial_delay = (
            retry_initial_delay if retry_initial_delay is not None else self._settings.gemini_retry_initial_delay
        )
        self._retry_max_delay = (
            retry_max_delay if retry_max_delay is not None else self._settings.gemini_retry_max_delay
        )
        self._retry_on_rate_limit = retry_on_rate_limit

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def is_configured(self) -> bool:
        return self._settings.is_gemini_configured

    @property
    def client(self) -> genai.Client:
        """Lazily initialize the GenAI client with secure key loading."""
        if self._client is None:
            api_key = self._settings.require_gemini_api_key()
            self._client = genai.Client(api_key=api_key)
        return self._client

    def is_retryable_error(self, exc: BaseException) -> bool:
        """Determine whether an error is transient and retryable within GeminiProvider."""
        if isinstance(exc, errors.APIError):
            code = getattr(exc, "code", None)
            if code in {408, 500, 502, 503, 504}:
                return True
            if isinstance(exc, errors.ServerError):
                return True
            if code == 429:
                if not self._retry_on_rate_limit:
                    return False
                # If confirmed daily quota exhaustion, do not retry
                err_msg = str(exc).lower()
                if "per day" in err_msg or "daily" in err_msg or "retry in" in err_msg:
                    return False
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

    def _execute_with_retry(
        self,
        operation_name: str,
        fn: Callable[[], T],
        max_retries: Optional[int] = None,
        initial_delay: Optional[float] = None,
        max_delay: Optional[float] = None,
        exp_base: float = 2.0,
        jitter: float = 1.0,
    ) -> T:
        """Execute a Gemini API call with bounded automatic retries for transient errors."""
        retries = max_retries if max_retries is not None else self._max_retries
        init_delay = initial_delay if initial_delay is not None else self._retry_initial_delay
        maximum_delay = max_delay if max_delay is not None else self._retry_max_delay
        total_attempts = retries + 1

        attempt_start_times: dict[int, float] = {}
        overall_start_time = time.perf_counter()

        def _before_attempt(retry_state: tenacity.RetryCallState) -> None:
            attempt_num = retry_state.attempt_number
            attempt_start_times[attempt_num] = time.perf_counter()
            logger.info(
                "Gemini API [%s] call starting (attempt %d of %d, model=%s)",
                operation_name,
                attempt_num,
                total_attempts,
                self._model,
            )

        def _after_attempt(retry_state: tenacity.RetryCallState) -> None:
            attempt_num = retry_state.attempt_number
            t_start = attempt_start_times.get(attempt_num, overall_start_time)
            attempt_elapsed = time.perf_counter() - t_start
            if not retry_state.outcome.failed:
                total_elapsed = time.perf_counter() - overall_start_time
                logger.info(
                    "Gemini API [%s] call succeeded on attempt %d of %d (attempt elapsed: %.2fs, total elapsed: %.2fs)",
                    operation_name,
                    attempt_num,
                    total_attempts,
                    attempt_elapsed,
                    total_elapsed,
                )

        def _before_sleep(retry_state: tenacity.RetryCallState) -> None:
            attempt_num = retry_state.attempt_number
            t_start = attempt_start_times.get(attempt_num, overall_start_time)
            attempt_elapsed = time.perf_counter() - t_start
            exc = retry_state.outcome.exception()
            safe_err = _get_safe_error_summary(exc)
            sleep_duration = retry_state.upcoming_sleep
            logger.warning(
                "Gemini API [%s] attempt %d of %d failed with transient error [%s] in %.2fs. "
                "Retrying in %.2fs (next attempt: %d of %d)...",
                operation_name,
                attempt_num,
                total_attempts,
                safe_err,
                attempt_elapsed,
                sleep_duration,
                attempt_num + 1,
                total_attempts,
            )

        retrying = tenacity.Retrying(
            stop=tenacity.stop_after_attempt(total_attempts),
            wait=tenacity.wait_exponential_jitter(
                initial=init_delay,
                max=maximum_delay,
                exp_base=exp_base,
                jitter=jitter,
            ),
            retry=tenacity.retry_if_exception(self.is_retryable_error),
            reraise=True,
            before=_before_attempt,
            after=_after_attempt,
            before_sleep=_before_sleep,
        )

        try:
            return retrying(fn)
        except Exception as final_exc:
            total_elapsed = time.perf_counter() - overall_start_time
            safe_err = _get_safe_error_summary(final_exc)
            logger.error(
                "Gemini API [%s] call terminated after %.2fs and %d attempt(s): %s",
                operation_name,
                total_elapsed,
                len(attempt_start_times) or 1,
                safe_err,
            )

            # Map the final exception to appropriate domain error
            if isinstance(final_exc, errors.APIError):
                code = getattr(final_exc, "code", None)
                if code == 429:
                    raise AIRateLimitError(
                        "Gemini API rate limit or quota exceeded. Please wait a moment and try again.",
                        provider=self.name,
                        code=429,
                        is_quota_exhausted=True,
                    ) from final_exc
                if code in {408, 504}:
                    raise AITimeoutError(
                        "AI recognition service timed out after multiple attempts. Please try again.",
                        provider=self.name,
                        code=code,
                    ) from final_exc
                if code in {500, 502, 503}:
                    raise AIUnavailableError(
                        f"The AI recognition service is temporarily overloaded or unavailable (HTTP {code}). Please try again in a few moments.",
                        provider=self.name,
                        code=code,
                    ) from final_exc
                if code == 401:
                    raise AIAuthenticationError(
                        "AI service authentication failed. Please verify your GEMINI_API_KEY configuration.",
                        provider=self.name,
                        code=401,
                    ) from final_exc
                if code == 403:
                    raise AIAuthenticationError(
                        "AI service access is forbidden. Please verify your API key permissions and project status.",
                        provider=self.name,
                        code=403,
                    ) from final_exc
                if code == 400:
                    raise AIServiceError(
                        "AI service rejected the request payload as invalid.",
                        provider=self.name,
                        code=400,
                    ) from final_exc
                raise AIServiceError(
                    f"Gemini service was unable to process the request (HTTP {code}). Please try again later.",
                    provider=self.name,
                    code=code,
                ) from final_exc

            if isinstance(final_exc, (TimeoutError, httpx.TimeoutException)):
                raise AITimeoutError(
                    "AI recognition request timed out after multiple attempts. Please try again.",
                    provider=self.name,
                ) from final_exc

            if isinstance(final_exc, (httpx.ConnectError, httpx.RemoteProtocolError)):
                raise AIUnavailableError(
                    "Cannot establish connection to AI recognition service. Please check your network and try again.",
                    provider=self.name,
                ) from final_exc

            if isinstance(final_exc, AIServiceError):
                raise final_exc

            raise AIServiceError(
                f"Unexpected error communicating with AI recognition service: {str(final_exc)}",
                provider=self.name,
            ) from final_exc

    def recognize_food(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
    ) -> FoodRecognitionResponse:
        """Analyze food image and return validated structured food candidates."""
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        prompt_text = (
            "Identify each visually distinguishable food item in this meal. "
            "For Indian meals or mixed plates/thalis, detect components separately (breads, rice, dal, sabzi, curries, sides). "
            "Estimate realistic portion weights in grams, calories, and macronutrients, noting any visual ambiguities or alternatives."
        )

        contents = [image_part, prompt_text]

        timeout_ms = int(self._per_attempt_timeout_seconds * 1000)
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=FoodRecognitionResponse,
            temperature=0.2,
            http_options=types.HttpOptions(
                timeout=timeout_ms,
                retry_options=None,  # Keep SDK internal retries at 1 to prevent unexpected request multiplication
            ),
        )

        def _call_gemini() -> types.GenerateContentResponse:
            return self.client.models.generate_content(
                model=self._model,
                contents=contents,
                config=config,
            )

        response = self._execute_with_retry("recognize_food", _call_gemini)

        if not response or not response.text:
            raise ModelOutputValidationError("The AI service returned an empty response.", provider=self.name)

        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        try:
            parsed_data = FoodRecognitionResponse.model_validate_json(raw_text)
            return parsed_data
        except ValidationError as val_err:
            try:
                data = json.loads(raw_text)
                if isinstance(data, dict):
                    if "items" not in data and "candidates" in data:
                        data["items"] = data.pop("candidates")
                    return FoodRecognitionResponse.model_validate(data)
            except Exception:
                pass
            raise ModelOutputValidationError(
                f"Model response failed validation schema: {str(val_err)}",
                provider=self.name,
            ) from val_err
        except Exception as exc:
            raise ModelOutputValidationError(
                f"Failed to decode model JSON output: {str(exc)}",
                provider=self.name,
            ) from exc

    def parse_voice_meal(
        self,
        transcript: str,
        meal_context: Optional[str] = None,
    ) -> VoiceMealParseResponse:
        """Parse spoken food description and return structured items and nutrition."""
        prompt_text = f"Spoken food transcript: {transcript.strip()}"
        if meal_context:
            prompt_text += f"\nMeal context: {meal_context.strip()}"

        contents = [prompt_text]
        timeout_ms = int(self._voice_timeout_seconds * 1000)
        config = types.GenerateContentConfig(
            system_instruction=VOICE_PARSER_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=VoiceMealParseResponse,
            temperature=0.2,
            http_options=types.HttpOptions(
                timeout=timeout_ms,
                retry_options=None,  # Keep SDK internal retries at 1 to prevent unexpected request multiplication
            ),
        )

        def _call_gemini() -> types.GenerateContentResponse:
            return self.client.models.generate_content(
                model=self._model,
                contents=contents,
                config=config,
            )

        response = self._execute_with_retry("parse_voice_meal", _call_gemini)

        if not response or not response.text:
            raise ModelOutputValidationError("The AI service returned an empty response.", provider=self.name)

        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        try:
            parsed_data = VoiceMealParseResponse.model_validate_json(raw_text)
            parsed_data.transcript = transcript.strip()
            return parsed_data
        except ValidationError as val_err:
            try:
                data = json.loads(raw_text)
                if isinstance(data, dict):
                    if "transcript" not in data:
                        data["transcript"] = transcript.strip()
                    return VoiceMealParseResponse.model_validate(data)
            except Exception:
                pass
            raise ModelOutputValidationError(
                f"Model response failed validation schema: {str(val_err)}",
                provider=self.name,
            ) from val_err
        except Exception as exc:
            raise ModelOutputValidationError(
                f"Failed to decode model JSON output: {str(exc)}",
                provider=self.name,
            ) from exc

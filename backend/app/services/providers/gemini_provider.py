"""Google Gemini AI recognition provider using the official Google GenAI SDK."""

import json
import logging
import re
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
    AIRequestCancelledError,
    AIServiceError,
    AITimeoutError,
    AIUnavailableError,
    BaseAIProvider,
    ModelOutputValidationError,
    SYSTEM_INSTRUCTION,
    VOICE_PARSER_SYSTEM_INSTRUCTION,
    get_current_request_id,
    is_request_cancelled,
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


def _safe_gemini_int(val: object) -> Optional[int]:
    """Return integer metric only for real numeric values (safe with MagicMock test objects)."""
    if isinstance(val, bool) or val is None:
        return None
    if isinstance(val, (int, float)):
        return int(val)
    return None


def _clean_markdown_json_text(raw_text: str) -> str:
    """Strip markdown fences around JSON text cleanly."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


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
        thinking_budget: Optional[int] = None,
        max_output_tokens: Optional[int] = None,
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
        self._thinking_budget = (
            thinking_budget
            if thinking_budget is not None
            else getattr(self._settings, "gemini_thinking_budget", 0)
        )
        self._max_output_tokens = (
            max_output_tokens
            if max_output_tokens is not None
            else getattr(self._settings, "gemini_max_output_tokens", 1500)
        )

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
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> T:
        """Execute a Gemini API call with bounded automatic retries for transient errors."""
        if is_request_cancelled(is_cancelled):
            raise AIRequestCancelledError("Client disconnected / request cancelled.", provider=self.name)

        retries = max_retries if max_retries is not None else self._max_retries
        init_delay = initial_delay if initial_delay is not None else self._retry_initial_delay
        maximum_delay = max_delay if max_delay is not None else self._retry_max_delay
        total_attempts = retries + 1

        attempt_start_times: dict[int, float] = {}
        overall_start_time = time.perf_counter()

        def _before_attempt(retry_state: tenacity.RetryCallState) -> None:
            if is_request_cancelled(is_cancelled):
                raise AIRequestCancelledError("Client disconnected / request cancelled.", provider=self.name)
            attempt_num = retry_state.attempt_number
            attempt_start_times[attempt_num] = time.perf_counter()
            logger.info(
                "[Timing][%s] Gemini API [%s] call starting (attempt %d of %d, model=%s)",
                get_current_request_id(),
                operation_name,
                attempt_num,
                total_attempts,
                self._model,
            )

        def _before_sleep(retry_state: tenacity.RetryCallState) -> None:
            if is_request_cancelled(is_cancelled):
                raise AIRequestCancelledError("Client disconnected / request cancelled.", provider=self.name)
            attempt_num = retry_state.attempt_number
            t_start = attempt_start_times.get(attempt_num, overall_start_time)
            attempt_elapsed = time.perf_counter() - t_start
            exc = retry_state.outcome.exception()
            safe_err = _get_safe_error_summary(exc)
            sleep_duration = retry_state.upcoming_sleep
            logger.warning(
                "[Timing][%s] Gemini API [%s] attempt %d of %d failed with transient error [%s] in %.2fs. "
                "Retrying in %.2fs (next attempt: %d of %d)...",
                get_current_request_id(),
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
            before_sleep=_before_sleep,
        )

        try:
            result = retrying(fn)
            attempt_num = retrying.statistics.get("attempt_number", 1)
            total_elapsed = time.perf_counter() - overall_start_time
            t_start = attempt_start_times.get(attempt_num, overall_start_time)
            attempt_elapsed = time.perf_counter() - t_start
            logger.info(
                "[Timing][%s] Gemini API [%s] request succeeded on attempt %d of %d (attempt elapsed: %.3fs, total elapsed: %.3fs)",
                get_current_request_id(),
                operation_name,
                attempt_num,
                total_attempts,
                attempt_elapsed,
                total_elapsed,
            )
            return result
        except Exception as final_exc:
            total_elapsed = time.perf_counter() - overall_start_time
            safe_err = _get_safe_error_summary(final_exc)
            logger.error(
                "[Timing][%s] Gemini API [%s] call terminated after %.2fs and %d attempt(s): %s",
                get_current_request_id(),
                operation_name,
                total_elapsed,
                len(attempt_start_times) or 1,
                safe_err,
            )

            # Map the final exception to appropriate domain error
            if isinstance(final_exc, errors.APIError):
                code = getattr(final_exc, "code", None)
                if code == 429:
                    err_msg = str(final_exc).lower()
                    quota_hit = "per day" in err_msg or "daily" in err_msg or "requestsperday" in err_msg
                    retry_after_s: Optional[float] = None
                    resp_obj = getattr(final_exc, "response", None)
                    resp_headers = getattr(resp_obj, "headers", None)
                    if resp_headers is not None and hasattr(resp_headers, "get"):
                        raw_ra = resp_headers.get("retry-after") or resp_headers.get("Retry-After")
                        if raw_ra is not None:
                            try:
                                retry_after_s = max(0.0, float(str(raw_ra).strip()))
                            except ValueError:
                                retry_after_s = None
                    if retry_after_s is None:
                        m = re.search(r"retry in\s+(\d+(?:\.\d+)?)\s*s", err_msg)
                        if m:
                            try:
                                retry_after_s = max(0.0, float(m.group(1)))
                            except ValueError:
                                retry_after_s = None
                    raise AIRateLimitError(
                        "Gemini API quota exhausted for today. Using fallback provider."
                        if quota_hit
                        else "Gemini API rate limit reached. Please wait a moment and try again.",
                        provider=self.name,
                        code=429,
                        is_quota_exhausted=quota_hit,
                        error_category="daily_quota_exhausted" if quota_hit else "burst_rate_limit",
                        retry_after_seconds=retry_after_s,
                        limit_scope="account" if quota_hit else "model",
                    ) from final_exc
                if code in {408, 504}:
                    raise AITimeoutError(
                        "AI recognition service timed out after multiple attempts. Please try again.",
                        provider=self.name,
                        code=code,
                        error_category="upstream_timeout",
                    ) from final_exc
                if code in {500, 502, 503}:
                    raise AIUnavailableError(
                        f"The AI recognition service is temporarily overloaded or unavailable (HTTP {code}). Please try again in a few moments.",
                        provider=self.name,
                        code=code,
                        error_category="upstream_unavailable",
                    ) from final_exc
                if code == 401:
                    raise AIAuthenticationError(
                        "AI service authentication failed. Please verify your GEMINI_API_KEY configuration.",
                        provider=self.name,
                        code=401,
                        error_category="auth_failed",
                    ) from final_exc
                if code == 403:
                    raise AIAuthenticationError(
                        "AI service access is forbidden. Please verify your API key permissions and project status.",
                        provider=self.name,
                        code=403,
                        error_category="auth_failed",
                    ) from final_exc
                if code == 400:
                    raise AIServiceError(
                        "AI service rejected the request payload as invalid.",
                        provider=self.name,
                        code=400,
                        error_category="bad_request",
                    ) from final_exc
                raise AIServiceError(
                    f"Gemini service was unable to process the request (HTTP {code}). Please try again later.",
                    provider=self.name,
                    code=code,
                    error_category="upstream_error",
                ) from final_exc

            if isinstance(final_exc, (TimeoutError, httpx.TimeoutException)):
                raise AITimeoutError(
                    "AI recognition request timed out after multiple attempts. Please try again.",
                    provider=self.name,
                    error_category="upstream_timeout",
                ) from final_exc

            if isinstance(final_exc, (httpx.ConnectError, httpx.RemoteProtocolError)):
                raise AIUnavailableError(
                    "Cannot establish connection to AI recognition service. Please check your network and try again.",
                    provider=self.name,
                    error_category="network_error",
                ) from final_exc

            if isinstance(final_exc, AIServiceError):
                raise final_exc

            raise AIServiceError(
                f"Unexpected error communicating with AI recognition service: {str(final_exc)}",
                provider=self.name,
                error_category="unexpected_error",
            ) from final_exc

    def _build_generation_config(
        self,
        system_instruction: str,
        response_schema: object,
        timeout_seconds: float,
    ) -> types.GenerateContentConfig:
        """Build tuned GenAI generation config (disabled AFC + configurable thinking budget)."""
        timeout_ms = max(100, int(timeout_seconds * 1000))
        cfg_kwargs: dict[str, object] = {
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": response_schema,
            "temperature": 0.2,
            "max_output_tokens": self._max_output_tokens,
            "automatic_function_calling": types.AutomaticFunctionCallingConfig(disable=True),
            "http_options": types.HttpOptions(
                timeout=timeout_ms,
                retry_options=None,
            ),
        }
        if self._thinking_budget >= 0 and "lite" not in self._model.lower():
            cfg_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=self._thinking_budget)
        return types.GenerateContentConfig(**cfg_kwargs)

    def _extract_and_clean_response_text(
        self,
        operation_name: str,
        response: types.GenerateContentResponse,
    ) -> str:
        """Log safe Gemini response metadata and extract stripped JSON string."""
        req_id = get_current_request_id()
        usage = getattr(response, "usage_metadata", None)
        prompt_tok = _safe_gemini_int(getattr(usage, "prompt_token_count", None)) if usage else None
        cand_tok = _safe_gemini_int(getattr(usage, "candidates_token_count", None)) if usage else None
        think_tok = _safe_gemini_int(getattr(usage, "thoughts_token_count", None)) if usage else None

        finish_reason_str = "unknown"
        candidates = getattr(response, "candidates", None)
        if isinstance(candidates, list) and candidates:
            fr = getattr(candidates[0], "finish_reason", None)
            if fr is not None and isinstance(getattr(fr, "value", fr), str):
                finish_reason_str = str(getattr(fr, "value", fr))

        raw_text_attr = getattr(response, "text", None) if response else None
        has_text = isinstance(raw_text_attr, str) and bool(raw_text_attr.strip())

        logger.info(
            "[Timing][%s] Gemini [%s] response meta: model=%s, finish_reason=%s, "
            "prompt_tokens=%s, candidate_tokens=%s, thoughts_tokens=%s, content_empty=%s",
            req_id,
            operation_name,
            self._model,
            finish_reason_str,
            prompt_tok,
            cand_tok,
            think_tok,
            not has_text,
        )

        if not response or not has_text:
            upper_fr = finish_reason_str.upper()
            if "MAX_TOKENS" in upper_fr:
                raise ModelOutputValidationError(
                    "Gemini exceeded output token budget before returning complete JSON.",
                    provider=self.name,
                    error_category="token_budget_exhausted",
                )
            if any(flag in upper_fr for flag in ("SAFETY", "RECITATION", "BLOCKLIST")):
                raise ModelOutputValidationError(
                    "Gemini blocked the response due to content policy.",
                    provider=self.name,
                    error_category="content_filtered",
                )
            raise ModelOutputValidationError(
                "The AI service returned an empty response.",
                provider=self.name,
                error_category="empty_model_content",
            )

        assert isinstance(raw_text_attr, str)
        t_parse_start = time.perf_counter()
        cleaned = _clean_markdown_json_text(raw_text_attr)
        t_parse_elapsed = time.perf_counter() - t_parse_start
        logger.info(
            "[Timing][%s] Gemini [%s] response JSON text cleaning took %.4fs",
            req_id,
            operation_name,
            t_parse_elapsed,
        )
        return cleaned

    def recognize_food(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        timeout_seconds: Optional[float] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> FoodRecognitionResponse:
        """Analyze food image and return validated structured food candidates."""
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        prompt_text = (
            "Identify each distinct food item on this meal. Separate breads, rice, dal, sabzi, curries, and sides. "
            "Estimate grams, calories, protein, carbohydrates, fat, and note ambiguities."
        )

        contents = [image_part, prompt_text]
        effective_timeout = timeout_seconds if timeout_seconds is not None else self._per_attempt_timeout_seconds
        config = self._build_generation_config(SYSTEM_INSTRUCTION, FoodRecognitionResponse, effective_timeout)

        def _call_gemini() -> types.GenerateContentResponse:
            return self.client.models.generate_content(
                model=self._model,
                contents=contents,
                config=config,
            )

        response = self._execute_with_retry("recognize_food", _call_gemini, is_cancelled=is_cancelled)
        raw_text = self._extract_and_clean_response_text("recognize_food", response)

        t_val_start = time.perf_counter()
        try:
            parsed_data = FoodRecognitionResponse.model_validate_json(raw_text)
            t_val_elapsed = time.perf_counter() - t_val_start
            logger.info("[Timing][%s] Gemini [%s] Pydantic validation took %.4fs", get_current_request_id(), "recognize_food", t_val_elapsed)
            return parsed_data
        except ValidationError as val_err:
            try:
                data = json.loads(raw_text)
                if isinstance(data, dict):
                    if "items" not in data and "candidates" in data:
                        data["items"] = data.pop("candidates")
                    parsed_data = FoodRecognitionResponse.model_validate(data)
                    t_val_elapsed = time.perf_counter() - t_val_start
                    logger.info("[Timing][%s] Gemini [%s] Pydantic validation took %.4fs", get_current_request_id(), "recognize_food", t_val_elapsed)
                    return parsed_data
            except Exception:
                pass
            raise ModelOutputValidationError(
                f"Model response failed validation schema: {str(val_err)}",
                provider=self.name,
                error_category="pydantic_validation_failed",
            ) from val_err
        except Exception as exc:
            raise ModelOutputValidationError(
                f"Failed to decode model JSON output: {str(exc)}",
                provider=self.name,
                error_category="malformed_json",
            ) from exc

    def parse_voice_meal(
        self,
        transcript: str,
        meal_context: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> VoiceMealParseResponse:
        """Parse spoken food description and return structured items and nutrition."""
        prompt_text = f"Spoken food transcript: {transcript.strip()}"
        if meal_context:
            prompt_text += f"\nMeal context: {meal_context.strip()}"

        contents = [prompt_text]
        effective_timeout = timeout_seconds if timeout_seconds is not None else self._voice_timeout_seconds
        config = self._build_generation_config(VOICE_PARSER_SYSTEM_INSTRUCTION, VoiceMealParseResponse, effective_timeout)

        def _call_gemini() -> types.GenerateContentResponse:
            return self.client.models.generate_content(
                model=self._model,
                contents=contents,
                config=config,
            )

        response = self._execute_with_retry("parse_voice_meal", _call_gemini, is_cancelled=is_cancelled)
        raw_text = self._extract_and_clean_response_text("parse_voice_meal", response)

        t_val_start = time.perf_counter()
        try:
            parsed_data = VoiceMealParseResponse.model_validate_json(raw_text)
            parsed_data.transcript = transcript.strip()
            t_val_elapsed = time.perf_counter() - t_val_start
            logger.info("[Timing][%s] Gemini [%s] Pydantic validation took %.4fs", get_current_request_id(), "parse_voice_meal", t_val_elapsed)
            return parsed_data
        except ValidationError as val_err:
            try:
                data = json.loads(raw_text)
                if isinstance(data, dict):
                    if "transcript" not in data:
                        data["transcript"] = transcript.strip()
                    parsed_data = VoiceMealParseResponse.model_validate(data)
                    t_val_elapsed = time.perf_counter() - t_val_start
                    logger.info("[Timing][%s] Gemini [%s] Pydantic validation took %.4fs", get_current_request_id(), "parse_voice_meal", t_val_elapsed)
                    return parsed_data
            except Exception:
                pass
            raise ModelOutputValidationError(
                f"Model response failed validation schema: {str(val_err)}",
                provider=self.name,
                error_category="pydantic_validation_failed",
            ) from val_err
        except Exception as exc:
            raise ModelOutputValidationError(
                f"Failed to decode model JSON output: {str(exc)}",
                provider=self.name,
                error_category="malformed_json",
            ) from exc

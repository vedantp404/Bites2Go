"""OpenRouter AI recognition provider implementing OpenAI-compatible Chat Completions API."""

import base64
import json
import logging
import re
import time
from typing import Any, Callable, Optional, TypeVar
import httpx
from pydantic import ValidationError
import tenacity

from app.config import Settings, get_settings
from app.models.food import (
    FoodItemCandidate,
    FoodRecognitionResponse,
    ParsedVoiceFoodItem,
    UncertaintyInfo,
    VoiceMealParseResponse,
)
from app.services.providers.base import (
    AIAuthenticationError,
    AIRateLimitError,
    AIRequestCancelledError,
    AIServiceError,
    AITimeoutError,
    AITransientError,
    AIUnavailableError,
    BaseAIProvider,
    ModelOutputValidationError,
    SYSTEM_INSTRUCTION,
    VOICE_PARSER_SYSTEM_INSTRUCTION,
    get_current_request_id,
    is_request_cancelled,
)

logger = logging.getLogger("bites2go.openrouter")

T = TypeVar("T")

_UNSET = object()
_MIN_ALTERNATIVE_BUDGET_SECONDS = 7.0

# Models verified not to support OpenAI-style `response_format={"type": "json_object"}`
_MODELS_WITHOUT_RESPONSE_FORMAT = frozenset({
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "thinkingmachines/inkling-2-small:free",
})

# Models verified as text-only (must NEVER receive image payloads)
_TEXT_ONLY_MODEL_IDS = frozenset({
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "liquid/lfm-3-1.7b:free",
    "liquid/lfm-2.5-2.6b:free",
    "recursive/flint-v1.0:free",
    "xingchen-agi/xing4.0-29b-a4b:free",
    "cohere/north-mini-code:free",
})


def is_text_only_openrouter_model(model_id: str) -> bool:
    """Return True when the given OpenRouter model ID is known text-only and cannot accept images."""
    lower_id = model_id.strip().lower()
    if lower_id in _TEXT_ONLY_MODEL_IDS:
        return True
    # Defensive heuristic for Cohere code/text or Flint text variants
    return lower_id.startswith(("cohere/", "recursive/flint", "liquid/lfm-"))

# Routers or endpoints that may reject `reasoning.enabled=False` with HTTP 400
_REASONING_REQUIRED_PREFIXES = (
    "openrouter/free",
    "cohere/",
    "recursive/flint",
)


def is_retryable_openrouter_error(exc: BaseException) -> bool:
    """Determine whether an error from OpenRouter is transient and retryable."""
    if isinstance(exc, (httpx.TimeoutException, TimeoutError, httpx.ConnectError, httpx.RemoteProtocolError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        if code in {408, 500, 502, 503, 504}:
            return True
        # Explicitly do NOT retry 401, 402, 429, 400, 403, 404
        return False
    return False


def _clean_markdown_and_reasoning(raw_text: str) -> str:
    """Strip model reasoning tags (<think>...</think>) and markdown fences."""
    cleaned = raw_text.strip()

    # Remove reasoning/thinking blocks (e.g. from DeepSeek or reasoning models)
    if "<think>" in cleaned and "</think>" in cleaned:
        cleaned = cleaned.split("</think>", 1)[1].strip()

    # Strip markdown code blocks
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    # If surrounded by text, find outer JSON boundaries
    if "{" in cleaned and "}" in cleaned:
        start_idx = cleaned.find("{")
        end_idx = cleaned.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            cleaned = cleaned[start_idx : end_idx + 1].strip()

    return cleaned


def _normalize_food_candidate_dict(item_dict: dict[str, Any]) -> dict[str, Any]:
    """Normalize slight key variances from open models into standard FoodItemCandidate structure."""
    normalized = dict(item_dict)

    # food_name
    if "food_name" not in normalized:
        if "name" in normalized:
            normalized["food_name"] = normalized["name"]
        elif "item" in normalized:
            normalized["food_name"] = normalized["item"]
        elif "food" in normalized:
            normalized["food_name"] = normalized["food"]

    # estimated_quantity
    if "estimated_quantity" not in normalized:
        normalized["estimated_quantity"] = float(normalized.get("quantity", 1.0))

    # unit
    if "unit" not in normalized or not str(normalized.get("unit", "")).strip():
        normalized["unit"] = "serving"

    # estimated_grams
    if "estimated_grams" not in normalized:
        if "weight_grams" in normalized:
            normalized["estimated_grams"] = float(normalized["weight_grams"])
        elif "grams" in normalized:
            normalized["estimated_grams"] = float(normalized["grams"])
        else:
            normalized["estimated_grams"] = 100.0

    # Ensure nutrients are numeric
    for nutrient_key in ("calories", "protein", "carbohydrates", "fat"):
        val = normalized.get(nutrient_key, 0.0)
        try:
            normalized[nutrient_key] = float(val)
        except (ValueError, TypeError):
            normalized[nutrient_key] = 0.0

    # uncertainty
    unc = normalized.get("uncertainty")
    if not isinstance(unc, dict):
        normalized["uncertainty"] = {
            "confidence_score": 0.85,
            "confidence_level": "high",
            "notes": None,
            "alternatives": [],
        }
    else:
        if "confidence_score" not in unc:
            unc["confidence_score"] = 0.85
        if "confidence_level" not in unc or unc["confidence_level"] not in ("high", "medium", "low"):
            score = float(unc.get("confidence_score", 0.85))
            if score >= 0.8:
                unc["confidence_level"] = "high"
            elif score >= 0.5:
                unc["confidence_level"] = "medium"
            else:
                unc["confidence_level"] = "low"
        if "alternatives" not in unc or not isinstance(unc["alternatives"], list):
            unc["alternatives"] = []

    return normalized


def _normalize_voice_candidate_dict(item_dict: dict[str, Any]) -> dict[str, Any]:
    """Normalize slight key variances from open models into standard ParsedVoiceFoodItem structure."""
    normalized = dict(item_dict)

    if "food_description" not in normalized:
        if "description" in normalized:
            normalized["food_description"] = normalized["description"]
        elif "food_name" in normalized:
            normalized["food_description"] = normalized["food_name"]
        elif "name" in normalized:
            normalized["food_description"] = normalized["name"]

    if "quantity" not in normalized:
        normalized["quantity"] = float(normalized.get("estimated_quantity", 1.0))

    if "unit" not in normalized or not str(normalized.get("unit", "")).strip():
        normalized["unit"] = "serving"

    if "estimated_grams" not in normalized:
        if "grams" in normalized:
            normalized["estimated_grams"] = float(normalized["grams"])
        elif "weight_grams" in normalized:
            normalized["estimated_grams"] = float(normalized["weight_grams"])
        else:
            normalized["estimated_grams"] = 100.0

    if "state" not in normalized or normalized["state"] not in ("raw", "cooked", "unspecified"):
        normalized["state"] = "unspecified"

    for nutrient_key in ("calories", "protein", "carbohydrates", "fat"):
        val = normalized.get(nutrient_key, 0.0)
        try:
            normalized[nutrient_key] = float(val)
        except (ValueError, TypeError):
            normalized[nutrient_key] = 0.0

    return normalized


def _safe_int(value: Any) -> Optional[int]:
    """Safely convert numeric token counts without crashing or logging malformed objects."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            return int(stripped)
    return None


def _safe_label(value: Any, default: str = "unknown", max_len: int = 120) -> str:
    """Safely format short string identifiers (model ID, finish_reason) for logs."""
    if not isinstance(value, str):
        return default
    cleaned = " ".join(value.strip().split())
    if not cleaned:
        return default
    return cleaned[:max_len]


def _extract_text_from_message(message: dict[str, Any]) -> tuple[str, bool, bool]:
    """Extract final user-facing text content from an OpenRouter message.

    Never substitutes hidden reasoning/thinking text for final JSON output.
    Returns (extracted_text, has_reasoning_output, has_refusal).
    """
    has_reasoning_output = bool(message.get("reasoning")) or bool(message.get("reasoning_details"))
    has_refusal = bool(message.get("refusal"))
    raw_content = message.get("content")

    if isinstance(raw_content, str):
        return raw_content.strip(), has_reasoning_output, has_refusal

    if isinstance(raw_content, list):
        parts: list[str] = []
        for item in raw_content:
            if isinstance(item, str):
                stripped = item.strip()
                if stripped:
                    parts.append(stripped)
            elif isinstance(item, dict):
                part_type = item.get("type")
                if part_type in ("reasoning", "thinking"):
                    has_reasoning_output = True
                    continue
                if part_type in (None, "text", "output_text") and isinstance(item.get("text"), str):
                    stripped = item["text"].strip()
                    if stripped:
                        parts.append(stripped)
        return "\n".join(parts).strip(), has_reasoning_output, has_refusal

    if isinstance(raw_content, dict):
        if raw_content.get("type") in ("reasoning", "thinking"):
            return "", True, has_refusal
        if isinstance(raw_content.get("text"), str):
            return raw_content["text"].strip(), has_reasoning_output, has_refusal

    # If final content is absent, safely inspect structured function tool_calls (if provided)
    tool_calls = message.get("tool_calls")
    if isinstance(tool_calls, list) and tool_calls:
        first_tc = tool_calls[0]
        if isinstance(first_tc, dict):
            fn_obj = first_tc.get("function")
            if isinstance(fn_obj, dict) and isinstance(fn_obj.get("arguments"), str):
                stripped_args = fn_obj["arguments"].strip()
                if stripped_args:
                    return stripped_args, has_reasoning_output, has_refusal

    return "", has_reasoning_output, has_refusal


def _build_model_payload(
    model_id: str,
    messages: list[dict[str, Any]],
    max_tokens: int,
) -> dict[str, Any]:
    """Build a model-compatible OpenRouter payload without reasoning starvation."""
    lower_id = model_id.lower()
    if any(lower_id == pat or lower_id.startswith(pat) for pat in _REASONING_REQUIRED_PREFIXES):
        reasoning_cfg: dict[str, Any] = {"effort": "low"}
        effective_max_tokens = max(max_tokens, 2500)
    else:
        reasoning_cfg = {"enabled": False}
        effective_max_tokens = max_tokens

    payload: dict[str, Any] = {
        "model": model_id,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": effective_max_tokens,
        "reasoning": reasoning_cfg,
    }
    if model_id not in _MODELS_WITHOUT_RESPONSE_FORMAT:
        payload["response_format"] = {"type": "json_object"}
    return payload


class OpenRouterProvider(BaseAIProvider):
    """OpenRouter fallback AI provider using the Chat Completions endpoint."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        max_retries: Optional[int] = None,
        settings: Optional[Settings] = None,
        http_client: Optional[httpx.Client] = None,
        alternative_model: Any = _UNSET,
        max_tokens: Optional[int] = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._api_key = api_key or self._settings.openrouter_api_key
        self._model = model or self._settings.openrouter_model
        if alternative_model is _UNSET:
            self._alternative_model: Optional[str] = getattr(
                self._settings, "openrouter_alternative_model", None
            )
        else:
            self._alternative_model = alternative_model or None
        if self._alternative_model == self._model:
            self._alternative_model = None
        self._base_url = (base_url or self._settings.openrouter_base_url).rstrip("/")
        self._timeout_seconds = (
            timeout_seconds if timeout_seconds is not None else self._settings.openrouter_timeout_seconds
        )
        self._max_retries = (
            max_retries if max_retries is not None else self._settings.openrouter_max_retries
        )
        self._max_tokens = (
            max_tokens if max_tokens is not None else getattr(self._settings, "openrouter_max_tokens", 2000)
        )
        self._client = http_client

    @property
    def name(self) -> str:
        return "openrouter"

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key or self._settings.is_openrouter_configured)

    def _get_api_key(self) -> str:
        if self._api_key:
            return self._api_key
        return self._settings.require_openrouter_api_key()

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=httpx.Timeout(self._timeout_seconds, connect=10.0),
                headers={
                    "HTTP-Referer": "https://bites2go.app",
                    "X-Title": "Bites2Go Food Recognition",
                },
            )
        return self._client

    def _map_status_code_error(
        self,
        status_code: Optional[int],
        cause: Optional[BaseException] = None,
    ) -> AIServiceError:
        """Map an HTTP or embedded OpenRouter error status code to a normalized domain exception."""
        if status_code in (401, 403):
            return AIAuthenticationError(
                "OpenRouter authentication failed. Please verify OPENROUTER_API_KEY.",
                provider=self.name,
                code=status_code,
                error_category="auth_failed",
            )
        if status_code == 400:
            return AIServiceError(
                "OpenRouter request failed with HTTP 400.",
                provider=self.name,
                code=400,
                error_category="bad_request",
            )
        if status_code == 402:
            return AIRateLimitError(
                "OpenRouter credit balance exhausted. Please add credits or select a free model.",
                provider=self.name,
                code=402,
                is_quota_exhausted=True,
                error_category="quota_exhausted",
            )
        if status_code == 429:
            return AIRateLimitError(
                "OpenRouter rate limit or quota exceeded.",
                provider=self.name,
                code=429,
                is_quota_exhausted=True,
                error_category="rate_limit",
            )
        if status_code in {408, 504}:
            return AITimeoutError(
                "OpenRouter request timed out after multiple attempts.",
                provider=self.name,
                code=status_code,
                error_category="upstream_timeout",
            )
        if status_code in {500, 502, 503}:
            return AIUnavailableError(
                f"OpenRouter service is temporarily unavailable (HTTP {status_code}).",
                provider=self.name,
                code=status_code,
                error_category="upstream_unavailable",
            )
        return AIServiceError(
            f"OpenRouter request failed with HTTP {status_code}.",
            provider=self.name,
            code=status_code,
            error_category="upstream_error",
        )

    def _execute_with_retry(
        self,
        operation_name: str,
        fn: Callable[[], httpx.Response],
        is_cancelled: Optional[Callable[[], bool]] = None,
        model_name: Optional[str] = None,
        max_retries_override: Optional[int] = None,
    ) -> tuple[dict[str, Any], float]:
        """Execute OpenRouter HTTP call with bounded retries and return (json_data, duration_s)."""
        if is_request_cancelled(is_cancelled):
            raise AIRequestCancelledError("Client disconnected / request cancelled.", provider=self.name)

        active_model = model_name or self._model
        retries = max_retries_override if max_retries_override is not None else self._max_retries
        total_attempts = retries + 1

        attempt_start_times: dict[int, float] = {}
        overall_start_time = time.perf_counter()

        def _before_attempt(retry_state: tenacity.RetryCallState) -> None:
            if is_request_cancelled(is_cancelled):
                raise AIRequestCancelledError("Client disconnected / request cancelled.", provider=self.name)
            attempt_num = retry_state.attempt_number
            attempt_start_times[attempt_num] = time.perf_counter()
            logger.info(
                "[Timing][%s] OpenRouter API [%s] call starting (attempt %d of %d, model=%s)",
                get_current_request_id(),
                operation_name,
                attempt_num,
                total_attempts,
                active_model,
            )

        def _before_sleep(retry_state: tenacity.RetryCallState) -> None:
            if is_request_cancelled(is_cancelled):
                raise AIRequestCancelledError("Client disconnected / request cancelled.", provider=self.name)
            exc = retry_state.outcome.exception()
            attempt_num = retry_state.attempt_number
            t_start = attempt_start_times.get(attempt_num, overall_start_time)
            attempt_elapsed = time.perf_counter() - t_start
            sleep_sec = retry_state.upcoming_sleep
            logger.warning(
                "[Timing][%s] OpenRouter API [%s] attempt %d of %d failed with transient error [%s] in %.3fs. Retrying in %.2fs...",
                get_current_request_id(),
                operation_name,
                attempt_num,
                total_attempts,
                type(exc).__name__,
                attempt_elapsed,
                sleep_sec,
            )

        retrying = tenacity.Retrying(
            stop=tenacity.stop_after_attempt(total_attempts),
            wait=tenacity.wait_exponential_jitter(initial=1.0, max=4.0),
            retry=tenacity.retry_if_exception(is_retryable_openrouter_error),
            reraise=True,
            before=_before_attempt,
            before_sleep=_before_sleep,
        )

        try:
            response = retrying(fn)
            attempt_num = retrying.statistics.get("attempt_number", 1)
            total_elapsed = time.perf_counter() - overall_start_time
            t_attempt_start = attempt_start_times.get(attempt_num, overall_start_time)
            attempt_elapsed = time.perf_counter() - t_attempt_start
            logger.info(
                "[Timing][%s] OpenRouter API [%s] request succeeded on attempt %d of %d (attempt elapsed: %.3fs, total elapsed: %.3fs)",
                get_current_request_id(),
                operation_name,
                attempt_num,
                total_attempts,
                attempt_elapsed,
                total_elapsed,
            )
            response.raise_for_status()
            t_body_start = time.perf_counter()
            try:
                data = response.json()
            except ValueError as json_err:
                raise ModelOutputValidationError(
                    f"OpenRouter HTTP response body could not be decoded as JSON: {str(json_err)}",
                    provider=self.name,
                    error_category="malformed_json",
                ) from json_err
            t_body_elapsed = time.perf_counter() - t_body_start
            logger.info(
                "[Timing][%s] OpenRouter [%s] response body read and JSON decoding took %.4fs",
                get_current_request_id(),
                operation_name,
                t_body_elapsed,
            )
            return data, time.perf_counter() - overall_start_time
        except httpx.HTTPStatusError as http_err:
            status_code = http_err.response.status_code
            safe_err = f"HTTP {status_code}"
            logger.error("OpenRouter API [%s] HTTP error (model=%s): %s", operation_name, active_model, safe_err)
            raise self._map_status_code_error(status_code) from http_err

        except (httpx.TimeoutException, TimeoutError) as timeout_err:
            raise AITimeoutError(
                "OpenRouter request timed out after multiple attempts.",
                provider=self.name,
                error_category="upstream_timeout",
            ) from timeout_err

        except (httpx.ConnectError, httpx.RemoteProtocolError) as net_err:
            raise AIUnavailableError(
                "Cannot establish connection to OpenRouter API.",
                provider=self.name,
                error_category="upstream_unavailable",
            ) from net_err

        except Exception as exc:
            if isinstance(exc, AIServiceError):
                raise exc
            raise AIServiceError(
                f"Unexpected error communicating with OpenRouter: {str(exc)}",
                provider=self.name,
                error_category="unexpected_error",
            ) from exc

    def _extract_and_log_response_text(
        self,
        operation_name: str,
        requested_model: str,
        data: dict[str, Any],
        duration: float,
    ) -> tuple[str, Optional[str]]:
        """Validate OpenRouter envelope, emit safe diagnostics, and extract final text content."""
        req_id = get_current_request_id()
        configured_model = _safe_label(self._model, default="unknown")
        req_model_label = _safe_label(requested_model, default="unknown")

        if not isinstance(data, dict):
            logger.warning(
                "[Timing][%s] OpenRouter [%s] response meta: configured_model=%s, requested_model=%s, "
                "actual_model=unknown, finish_reason=unknown, prompt_tokens=None, completion_tokens=None, "
                "reasoning_tokens=None, content_empty=True, duration=%.3fs, failure_category=malformed_schema_shape",
                req_id,
                operation_name,
                configured_model,
                req_model_label,
                duration,
            )
            raise ModelOutputValidationError(
                "OpenRouter response JSON is not an object.",
                provider=self.name,
                error_category="malformed_schema_shape",
            )

        if "error" in data and isinstance(data["error"], dict) and not data.get("choices"):
            embedded_err = data["error"]
            raw_code = embedded_err.get("code")
            try:
                status_code = int(raw_code) if raw_code is not None else 502
            except (TypeError, ValueError):
                status_code = 502
            logger.warning(
                "[Timing][%s] OpenRouter [%s] embedded error payload (configured_model=%s, requested_model=%s, code=%s, duration=%.3fs)",
                req_id,
                operation_name,
                configured_model,
                req_model_label,
                status_code,
                duration,
            )
            raise self._map_status_code_error(status_code)

        actual_model = _safe_label(data.get("model"), default="unknown")
        usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
        prompt_tokens = _safe_int(usage.get("prompt_tokens"))
        completion_tokens = _safe_int(usage.get("completion_tokens"))
        comp_details = usage.get("completion_tokens_details")
        if not isinstance(comp_details, dict):
            comp_details = {}
        out_details = usage.get("output_tokens_details")
        if not isinstance(out_details, dict):
            out_details = {}
        reasoning_tokens = _safe_int(
            comp_details.get("reasoning_tokens")
            if comp_details.get("reasoning_tokens") is not None
            else (
                usage.get("reasoning_tokens")
                if usage.get("reasoning_tokens") is not None
                else out_details.get("reasoning_tokens")
            )
        )

        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            logger.warning(
                "[Timing][%s] OpenRouter [%s] response meta: configured_model=%s, requested_model=%s, "
                "actual_model=%s, finish_reason=none, prompt_tokens=%s, completion_tokens=%s, "
                "reasoning_tokens=%s, content_empty=True, duration=%.3fs, failure_category=empty_choices",
                req_id,
                operation_name,
                configured_model,
                req_model_label,
                actual_model,
                prompt_tokens,
                completion_tokens,
                reasoning_tokens,
                duration,
            )
            raise ModelOutputValidationError(
                "OpenRouter returned empty choices in response.",
                provider=self.name,
                error_category="empty_choices",
            )

        first_choice = choices[0] if isinstance(choices[0], dict) else {}
        finish_reason = _safe_label(first_choice.get("finish_reason"), default="unknown")
        message = first_choice.get("message") if isinstance(first_choice.get("message"), dict) else {}

        extracted_text, has_reasoning, has_refusal = _extract_text_from_message(message)
        content_empty = not bool(extracted_text)

        logger.info(
            "[Timing][%s] OpenRouter [%s] response meta: configured_model=%s, requested_model=%s, "
            "actual_model=%s, finish_reason=%s, prompt_tokens=%s, completion_tokens=%s, "
            "reasoning_tokens=%s, has_reasoning=%s, content_empty=%s, duration=%.3fs",
            req_id,
            operation_name,
            configured_model,
            req_model_label,
            actual_model,
            finish_reason,
            prompt_tokens,
            completion_tokens,
            reasoning_tokens,
            has_reasoning,
            content_empty,
            duration,
        )

        if content_empty:
            if finish_reason == "length":
                failure_category = "token_budget_exhausted"
                err_msg = (
                    "OpenRouter exhausted completion token budget before producing final message content."
                )
            elif finish_reason == "content_filter" or has_refusal:
                failure_category = "content_filtered"
                err_msg = "OpenRouter response was withheld by content filter or refusal."
            else:
                failure_category = "empty_model_content"
                err_msg = "OpenRouter message content was empty."

            logger.warning(
                "[Timing][%s] OpenRouter [%s] empty output classified (failure_category=%s, "
                "configured_model=%s, actual_model=%s, finish_reason=%s, completion_tokens=%s, "
                "reasoning_tokens=%s, has_reasoning=%s, duration=%.3fs)",
                req_id,
                operation_name,
                failure_category,
                configured_model,
                actual_model,
                finish_reason,
                completion_tokens,
                reasoning_tokens,
                has_reasoning,
                duration,
            )
            raise ModelOutputValidationError(
                err_msg,
                provider=self.name,
                error_category=failure_category,
            )

        return extracted_text, finish_reason

    def _decode_json_object(
        self,
        operation_name: str,
        raw_text: str,
        finish_reason: Optional[str],
    ) -> dict[str, Any]:
        """Strip markdown/think blocks and parse final JSON object with explicit failure classification."""
        cleaned_json_str = _clean_markdown_and_reasoning(raw_text)
        try:
            parsed_raw = json.loads(cleaned_json_str)
        except json.JSONDecodeError as json_err:
            failure_category = "token_budget_exhausted" if finish_reason == "length" else "malformed_json"
            logger.warning(
                "[Timing][%s] OpenRouter [%s] JSON decode failed (failure_category=%s, finish_reason=%s)",
                get_current_request_id(),
                operation_name,
                failure_category,
                finish_reason,
            )
            raise ModelOutputValidationError(
                f"OpenRouter response could not be parsed as JSON: {str(json_err)}",
                provider=self.name,
                error_category=failure_category,
            ) from json_err

        if not isinstance(parsed_raw, dict):
            logger.warning(
                "[Timing][%s] OpenRouter [%s] decoded JSON is not an object (failure_category=malformed_schema_shape)",
                get_current_request_id(),
                operation_name,
            )
            raise ModelOutputValidationError(
                "OpenRouter JSON response is not a valid object.",
                provider=self.name,
                error_category="malformed_schema_shape",
            )
        return parsed_raw

    def _run_with_optional_alternative_model(
        self,
        operation_name: str,
        messages: list[dict[str, Any]],
        parse_and_validate_fn: Callable[[dict[str, Any], float, str], T],
        timeout_seconds: Optional[float] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> T:
        """Execute primary OpenRouter model and allow at most one bounded alternative-model attempt."""
        api_key = self._get_api_key()
        url = f"{self._base_url}/chat/completions"
        client = self._get_client()
        overall_budget = timeout_seconds if timeout_seconds is not None else self._timeout_seconds
        t_overall_start = time.perf_counter()

        has_alternative = bool(self._alternative_model and self._alternative_model != self._model)
        if has_alternative and overall_budget >= 16.0:
            primary_timeout = min(
                overall_budget,
                max(overall_budget - _MIN_ALTERNATIVE_BUDGET_SECONDS, 11.5),
            )
        else:
            primary_timeout = overall_budget

        def _invoke_model(
            model_id: str,
            attempt_budget: float,
            max_retries_override: Optional[int],
        ) -> T:
            payload = _build_model_payload(model_id, messages, self._max_tokens)
            connect_timeout = min(5.0, max(attempt_budget, 0.5))
            req_timeout = (
                attempt_budget
                if attempt_budget <= 5.0
                else httpx.Timeout(attempt_budget, connect=connect_timeout)
            )

            def _call_openrouter() -> httpx.Response:
                t_req_start = time.perf_counter()
                resp = client.post(
                    url,
                    headers={"Authorization": f"Bearer {api_key}"},
                    json=payload,
                    timeout=req_timeout,
                )
                t_req_elapsed = time.perf_counter() - t_req_start
                logger.info(
                    "[Timing][%s] OpenRouter [%s] HTTP request completed in %.3fs (status: %d, model=%s)",
                    get_current_request_id(),
                    operation_name,
                    t_req_elapsed,
                    resp.status_code,
                    model_id,
                )
                return resp

            data, call_duration = self._execute_with_retry(
                operation_name,
                _call_openrouter,
                is_cancelled=is_cancelled,
                model_name=model_id,
                max_retries_override=max_retries_override,
            )
            return parse_and_validate_fn(data, call_duration, model_id)

        try:
            return _invoke_model(self._model, primary_timeout, None)
        except (AIRequestCancelledError, AIAuthenticationError):
            raise
        except (ModelOutputValidationError, AITransientError) as exc:
            # Never fall back inside OpenRouter on bad payload (HTTP 400)
            if exc.code == 400 or getattr(exc, "error_category", None) == "bad_request":
                raise
            rem = overall_budget - (time.perf_counter() - t_overall_start)
            if (
                not has_alternative
                or is_request_cancelled(is_cancelled)
                or rem < _MIN_ALTERNATIVE_BUDGET_SECONDS
            ):
                raise

            reason_cat = getattr(exc, "error_category", None) or type(exc).__name__
            logger.warning(
                "[Timing][%s] OpenRouter [%s] switching to alternative model [%s] from [%s] "
                "(failure_category=%s, remaining_budget=%.2fs)",
                get_current_request_id(),
                operation_name,
                self._alternative_model,
                self._model,
                reason_cat,
                rem,
            )
            assert self._alternative_model is not None
            if operation_name == "recognize_food" and is_text_only_openrouter_model(self._alternative_model):
                logger.error(
                    "[Timing][%s] OpenRouter [%s] blocked image routing to text-only alternative model [%s]",
                    get_current_request_id(),
                    operation_name,
                    self._alternative_model,
                )
                raise exc
            return _invoke_model(self._alternative_model, rem, 0)

    def recognize_food(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        timeout_seconds: Optional[float] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> FoodRecognitionResponse:
        """Recognize food items from an image using OpenRouter vision chat completion."""
        if is_text_only_openrouter_model(self._model):
            logger.error(
                "[Timing][%s] OpenRouter [recognize_food] blocked attempt to route image data to text-only model [%s]",
                get_current_request_id(),
                self._model,
            )
            raise AIServiceError(
                f"Configured OpenRouter model [{self._model}] does not support image input.",
                provider=self.name,
                code=400,
                error_category="model_vision_unsupported",
            )

        b64_image = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{b64_image}"

        prompt_text = (
            "Identify distinct meal components cleanly (breads, rice, dal, sabzi, curries, sides) with realistic grams and macros. "
            'Respond ONLY with raw JSON matching: {"success":true,"summary":"...",'
            '"items":[{"food_name":"...","estimated_quantity":1.0,"unit":"bowl","estimated_grams":150.0,'
            '"calories":180.0,"protein":7.0,"carbohydrates":28.0,"fat":4.0,'
            '"uncertainty":{"confidence_score":0.88,"confidence_level":"high","notes":null,"alternatives":[]}}],"warnings":[]}'
        )

        messages = [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url},
                    },
                ],
            },
        ]

        def _parse_and_validate_photo(
            data: dict[str, Any],
            call_duration: float,
            requested_model: str,
        ) -> FoodRecognitionResponse:
            content_text, finish_reason = self._extract_and_log_response_text(
                "recognize_food", requested_model, data, call_duration
            )
            t_parse_start = time.perf_counter()
            parsed_raw = self._decode_json_object("recognize_food", content_text, finish_reason)

            raw_items = parsed_raw.get("items")
            if raw_items is None:
                if "candidates" in parsed_raw:
                    raw_items = parsed_raw.pop("candidates")
                elif "foods" in parsed_raw:
                    raw_items = parsed_raw.pop("foods")
                elif "food_items" in parsed_raw:
                    raw_items = parsed_raw.pop("food_items")
                else:
                    raw_items = []

            if not isinstance(raw_items, list):
                raise ModelOutputValidationError(
                    "OpenRouter response 'items' field is not a list.",
                    provider=self.name,
                    error_category="malformed_schema_shape",
                )

            parsed_raw["items"] = [
                _normalize_food_candidate_dict(it) for it in raw_items if isinstance(it, dict)
            ]
            if "success" not in parsed_raw:
                parsed_raw["success"] = True
            if "summary" not in parsed_raw:
                parsed_raw["summary"] = ""
            if "warnings" not in parsed_raw or not isinstance(parsed_raw["warnings"], list):
                parsed_raw["warnings"] = []
            t_parse_elapsed = time.perf_counter() - t_parse_start
            logger.info(
                "[Timing][%s] OpenRouter [%s] response JSON parsing took %.4fs",
                get_current_request_id(),
                "recognize_food",
                t_parse_elapsed,
            )

            t_val_start = time.perf_counter()
            try:
                validated = FoodRecognitionResponse.model_validate(parsed_raw)
                t_val_elapsed = time.perf_counter() - t_val_start
                logger.info(
                    "[Timing][%s] OpenRouter [%s] Pydantic validation took %.4fs",
                    get_current_request_id(),
                    "recognize_food",
                    t_val_elapsed,
                )
                return validated
            except ValidationError as val_err:
                logger.warning(
                    "[Timing][%s] OpenRouter [%s] Pydantic validation failed (failure_category=pydantic_validation_failed)",
                    get_current_request_id(),
                    "recognize_food",
                )
                raise ModelOutputValidationError(
                    f"OpenRouter response failed validation schema: {str(val_err)}",
                    provider=self.name,
                    error_category="pydantic_validation_failed",
                ) from val_err

        return self._run_with_optional_alternative_model(
            operation_name="recognize_food",
            messages=messages,
            parse_and_validate_fn=_parse_and_validate_photo,
            timeout_seconds=timeout_seconds,
            is_cancelled=is_cancelled,
        )

    def parse_voice_meal(
        self,
        transcript: str,
        meal_context: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> VoiceMealParseResponse:
        """Parse spoken food description using OpenRouter chat completion."""
        cleaned_transcript = transcript.strip()
        user_content = f"Spoken food transcript: {cleaned_transcript}"
        if meal_context:
            user_content += f"\nMeal context: {meal_context.strip()}"

        user_content += (
            '\nReturn ONLY raw JSON matching: {"success":true,"transcript":"...","summary":"...",'
            '"items":[{"food_description":"...","quantity":1.0,"unit":"bowl","preparation":null,'
            '"state":"raw|cooked|unspecified","estimated_grams":150.0,"calories":180.0,'
            '"protein":7.0,"carbohydrates":28.0,"fat":4.0,"confidence":0.9,"confidence_level":"high",'
            '"alternatives":[],"notes":null}],"warnings":[],"clarifying_questions":[]}'
        )

        messages = [
            {"role": "system", "content": VOICE_PARSER_SYSTEM_INSTRUCTION},
            {"role": "user", "content": user_content},
        ]

        def _parse_and_validate_voice(
            data: dict[str, Any],
            call_duration: float,
            requested_model: str,
        ) -> VoiceMealParseResponse:
            content_text, finish_reason = self._extract_and_log_response_text(
                "parse_voice_meal", requested_model, data, call_duration
            )
            t_parse_start = time.perf_counter()
            parsed_raw = self._decode_json_object("parse_voice_meal", content_text, finish_reason)

            raw_items = parsed_raw.get("items")
            if raw_items is None:
                if "candidates" in parsed_raw:
                    raw_items = parsed_raw.pop("candidates")
                elif "foods" in parsed_raw:
                    raw_items = parsed_raw.pop("foods")
                else:
                    raw_items = []

            if not isinstance(raw_items, list):
                raise ModelOutputValidationError(
                    "OpenRouter response 'items' field is not a list.",
                    provider=self.name,
                    error_category="malformed_schema_shape",
                )

            parsed_raw["items"] = [
                _normalize_voice_candidate_dict(it) for it in raw_items if isinstance(it, dict)
            ]
            parsed_raw["transcript"] = cleaned_transcript
            if "success" not in parsed_raw:
                parsed_raw["success"] = True
            if "summary" not in parsed_raw:
                parsed_raw["summary"] = ""
            if "warnings" not in parsed_raw or not isinstance(parsed_raw["warnings"], list):
                parsed_raw["warnings"] = []
            t_parse_elapsed = time.perf_counter() - t_parse_start
            logger.info(
                "[Timing][%s] OpenRouter [%s] response JSON parsing took %.4fs",
                get_current_request_id(),
                "parse_voice_meal",
                t_parse_elapsed,
            )

            t_val_start = time.perf_counter()
            try:
                validated = VoiceMealParseResponse.model_validate(parsed_raw)
                t_val_elapsed = time.perf_counter() - t_val_start
                logger.info(
                    "[Timing][%s] OpenRouter [%s] Pydantic validation took %.4fs",
                    get_current_request_id(),
                    "parse_voice_meal",
                    t_val_elapsed,
                )
                return validated
            except ValidationError as val_err:
                logger.warning(
                    "[Timing][%s] OpenRouter [%s] Pydantic validation failed (failure_category=pydantic_validation_failed)",
                    get_current_request_id(),
                    "parse_voice_meal",
                )
                raise ModelOutputValidationError(
                    f"OpenRouter voice parsing failed validation schema: {str(val_err)}",
                    provider=self.name,
                    error_category="pydantic_validation_failed",
                ) from val_err

        return self._run_with_optional_alternative_model(
            operation_name="parse_voice_meal",
            messages=messages,
            parse_and_validate_fn=_parse_and_validate_voice,
            timeout_seconds=timeout_seconds,
            is_cancelled=is_cancelled,
        )


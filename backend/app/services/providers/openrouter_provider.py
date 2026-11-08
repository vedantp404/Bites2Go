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
    AIServiceError,
    AITimeoutError,
    AIUnavailableError,
    BaseAIProvider,
    ModelOutputValidationError,
    SYSTEM_INSTRUCTION,
    VOICE_PARSER_SYSTEM_INSTRUCTION,
)

logger = logging.getLogger("bites2go.openrouter")

T = TypeVar("T")


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
    ) -> None:
        self._settings = settings or get_settings()
        self._api_key = api_key or self._settings.openrouter_api_key
        self._model = model or self._settings.openrouter_model
        self._base_url = (base_url or self._settings.openrouter_base_url).rstrip("/")
        self._timeout_seconds = (
            timeout_seconds if timeout_seconds is not None else self._settings.openrouter_timeout_seconds
        )
        self._max_retries = (
            max_retries if max_retries is not None else self._settings.openrouter_max_retries
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

    def _execute_with_retry(
        self,
        operation_name: str,
        fn: Callable[[], httpx.Response],
    ) -> dict[str, Any]:
        """Execute OpenRouter HTTP call with bounded retries for transient errors."""
        retries = self._max_retries
        total_attempts = retries + 1

        overall_start_time = time.perf_counter()

        def _before_attempt(retry_state: tenacity.RetryCallState) -> None:
            logger.info(
                "OpenRouter API [%s] call starting (attempt %d of %d, model=%s)",
                operation_name,
                retry_state.attempt_number,
                total_attempts,
                self._model,
            )

        def _after_attempt(retry_state: tenacity.RetryCallState) -> None:
            if not retry_state.outcome.failed:
                total_elapsed = time.perf_counter() - overall_start_time
                logger.info(
                    "OpenRouter API [%s] succeeded on attempt %d of %d (total elapsed: %.2fs)",
                    operation_name,
                    retry_state.attempt_number,
                    total_attempts,
                    total_elapsed,
                )

        def _before_sleep(retry_state: tenacity.RetryCallState) -> None:
            exc = retry_state.outcome.exception()
            logger.warning(
                "OpenRouter API [%s] attempt %d of %d failed with transient error [%s]. Retrying...",
                operation_name,
                retry_state.attempt_number,
                total_attempts,
                type(exc).__name__,
            )

        retrying = tenacity.Retrying(
            stop=tenacity.stop_after_attempt(total_attempts),
            wait=tenacity.wait_exponential_jitter(initial=1.0, max=4.0),
            retry=tenacity.retry_if_exception(is_retryable_openrouter_error),
            reraise=True,
            before=_before_attempt,
            after=_after_attempt,
            before_sleep=_before_sleep,
        )

        try:
            response = retrying(fn)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as http_err:
            status_code = http_err.response.status_code
            safe_err = f"HTTP {status_code}"
            logger.error("OpenRouter API [%s] HTTP error: %s", operation_name, safe_err)

            if status_code in (401, 403):
                raise AIAuthenticationError(
                    "OpenRouter authentication failed. Please verify OPENROUTER_API_KEY.",
                    provider=self.name,
                    code=status_code,
                ) from http_err
            if status_code == 402:
                raise AIRateLimitError(
                    "OpenRouter credit balance exhausted. Please add credits or select a free model.",
                    provider=self.name,
                    code=402,
                    is_quota_exhausted=True,
                ) from http_err
            if status_code == 429:
                raise AIRateLimitError(
                    "OpenRouter rate limit or quota exceeded.",
                    provider=self.name,
                    code=429,
                    is_quota_exhausted=True,
                ) from http_err
            if status_code in {408, 504}:
                raise AITimeoutError(
                    "OpenRouter request timed out after multiple attempts.",
                    provider=self.name,
                    code=status_code,
                ) from http_err
            if status_code in {500, 502, 503}:
                raise AIUnavailableError(
                    f"OpenRouter service is temporarily unavailable (HTTP {status_code}).",
                    provider=self.name,
                    code=status_code,
                ) from http_err

            raise AIServiceError(
                f"OpenRouter request failed with HTTP {status_code}.",
                provider=self.name,
                code=status_code,
            ) from http_err

        except (httpx.TimeoutException, TimeoutError) as timeout_err:
            raise AITimeoutError(
                "OpenRouter request timed out after multiple attempts.",
                provider=self.name,
            ) from timeout_err

        except (httpx.ConnectError, httpx.RemoteProtocolError) as net_err:
            raise AIUnavailableError(
                "Cannot establish connection to OpenRouter API.",
                provider=self.name,
            ) from net_err

        except Exception as exc:
            if isinstance(exc, AIServiceError):
                raise exc
            raise AIServiceError(
                f"Unexpected error communicating with OpenRouter: {str(exc)}",
                provider=self.name,
            ) from exc

    def recognize_food(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
    ) -> FoodRecognitionResponse:
        """Recognize food items from an image using OpenRouter vision chat completion."""
        api_key = self._get_api_key()
        b64_image = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{b64_image}"

        prompt_text = (
            "Identify each visually distinguishable food item in this meal photo. "
            "For Indian meals or mixed plates/thalis, detect components separately (breads, rice, dal, sabzi, curries, sides). "
            "Estimate realistic portion weights in grams, calories, and macronutrients, noting visual ambiguities or alternatives.\n\n"
            "You MUST respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            '  "success": true,\n'
            '  "summary": "Brief meal description",\n'
            '  "items": [\n'
            "    {\n"
            '      "food_name": "Item name",\n'
            '      "estimated_quantity": 1.0,\n'
            '      "unit": "bowl",\n'
            '      "estimated_grams": 150.0,\n'
            '      "calories": 180.0,\n'
            '      "protein": 7.0,\n'
            '      "carbohydrates": 28.0,\n'
            '      "fat": 4.0,\n'
            '      "uncertainty": {\n'
            '        "confidence_score": 0.88,\n'
            '        "confidence_level": "high",\n'
            '        "notes": null,\n'
            '        "alternatives": []\n'
            "      }\n"
            "    }\n"
            "  ],\n"
            '  "warnings": []\n'
            "}"
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

        payload = {
            "model": self._model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        url = f"{self._base_url}/chat/completions"
        client = self._get_client()

        def _call_openrouter() -> httpx.Response:
            return client.post(
                url,
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
            )

        data = self._execute_with_retry("recognize_food", _call_openrouter)

        choices = data.get("choices", [])
        if not choices:
            raise ModelOutputValidationError(
                "OpenRouter returned empty choices in response.",
                provider=self.name,
            )

        content = choices[0].get("message", {}).get("content", "")
        if not content:
            raise ModelOutputValidationError(
                "OpenRouter message content was empty.",
                provider=self.name,
            )

        cleaned_json_str = _clean_markdown_and_reasoning(content)

        try:
            parsed_raw = json.loads(cleaned_json_str)
        except json.JSONDecodeError as json_err:
            raise ModelOutputValidationError(
                f"OpenRouter response could not be parsed as JSON: {str(json_err)}",
                provider=self.name,
            ) from json_err

        if not isinstance(parsed_raw, dict):
            raise ModelOutputValidationError(
                "OpenRouter JSON response is not a valid object.",
                provider=self.name,
            )

        # Normalize items list
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
            )

        parsed_raw["items"] = [_normalize_food_candidate_dict(it) for it in raw_items if isinstance(it, dict)]
        if "success" not in parsed_raw:
            parsed_raw["success"] = True
        if "summary" not in parsed_raw:
            parsed_raw["summary"] = ""
        if "warnings" not in parsed_raw or not isinstance(parsed_raw["warnings"], list):
            parsed_raw["warnings"] = []

        try:
            return FoodRecognitionResponse.model_validate(parsed_raw)
        except ValidationError as val_err:
            raise ModelOutputValidationError(
                f"OpenRouter response failed validation schema: {str(val_err)}",
                provider=self.name,
            ) from val_err

    def parse_voice_meal(
        self,
        transcript: str,
        meal_context: Optional[str] = None,
    ) -> VoiceMealParseResponse:
        """Parse spoken food description using OpenRouter chat completion."""
        api_key = self._get_api_key()

        user_content = f"Spoken food transcript: {transcript.strip()}"
        if meal_context:
            user_content += f"\nMeal context: {meal_context.strip()}"

        user_content += (
            "\n\nYou MUST respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            '  "success": true,\n'
            f'  "transcript": "{transcript.strip()}",\n'
            '  "summary": "Brief summary",\n'
            '  "items": [\n'
            "    {\n"
            '      "food_description": "Item description",\n'
            '      "quantity": 1.0,\n'
            '      "unit": "bowl",\n'
            '      "preparation": null,\n'
            '      "state": "unspecified",\n'
            '      "estimated_grams": 150.0,\n'
            '      "calories": 180.0,\n'
            '      "protein": 7.0,\n'
            '      "carbohydrates": 28.0,\n'
            '      "fat": 4.0\n'
            "    }\n"
            "  ],\n"
            '  "warnings": []\n'
            "}"
        )

        messages = [
            {"role": "system", "content": VOICE_PARSER_SYSTEM_INSTRUCTION},
            {"role": "user", "content": user_content},
        ]

        payload = {
            "model": self._model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        url = f"{self._base_url}/chat/completions"
        client = self._get_client()

        def _call_openrouter() -> httpx.Response:
            return client.post(
                url,
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
            )

        data = self._execute_with_retry("parse_voice_meal", _call_openrouter)

        choices = data.get("choices", [])
        if not choices:
            raise ModelOutputValidationError(
                "OpenRouter returned empty choices in response.",
                provider=self.name,
            )

        content = choices[0].get("message", {}).get("content", "")
        if not content:
            raise ModelOutputValidationError(
                "OpenRouter message content was empty.",
                provider=self.name,
            )

        cleaned_json_str = _clean_markdown_and_reasoning(content)

        try:
            parsed_raw = json.loads(cleaned_json_str)
        except json.JSONDecodeError as json_err:
            raise ModelOutputValidationError(
                f"OpenRouter response could not be parsed as JSON: {str(json_err)}",
                provider=self.name,
            ) from json_err

        if not isinstance(parsed_raw, dict):
            raise ModelOutputValidationError(
                "OpenRouter JSON response is not a valid object.",
                provider=self.name,
            )

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
            )

        parsed_raw["items"] = [_normalize_voice_candidate_dict(it) for it in raw_items if isinstance(it, dict)]
        parsed_raw["transcript"] = transcript.strip()
        if "success" not in parsed_raw:
            parsed_raw["success"] = True
        if "summary" not in parsed_raw:
            parsed_raw["summary"] = ""
        if "warnings" not in parsed_raw or not isinstance(parsed_raw["warnings"], list):
            parsed_raw["warnings"] = []

        try:
            return VoiceMealParseResponse.model_validate(parsed_raw)
        except ValidationError as val_err:
            raise ModelOutputValidationError(
                f"OpenRouter voice parsing failed validation schema: {str(val_err)}",
                provider=self.name,
            ) from val_err


"""Gemini API food recognition service using the official Google GenAI SDK."""

import json
import logging
import time
from typing import Callable, Optional, TypeVar
import httpx
from google import genai
from google.genai import errors, types
from pydantic import ValidationError
import tenacity

from app.config import get_settings
from app.models.food import FoodRecognitionResponse, VoiceMealParseResponse

logger = logging.getLogger("bites2go.gemini")

T = TypeVar("T")


class GeminiServiceError(RuntimeError):
    """Base exception for Gemini service failures."""
    pass


class GeminiTransientError(GeminiServiceError):
    """Base exception for transient/retryable Gemini service failures."""
    def __init__(self, message: str, code: Optional[int] = None) -> None:
        super().__init__(message)
        self.code = code


class GeminiTimeoutError(GeminiTransientError):
    """Raised when AI service requests time out after retries."""
    pass


class GeminiUnavailableError(GeminiTransientError):
    """Raised when upstream AI service is temporarily unavailable or overloaded."""
    pass


class RateLimitError(GeminiTransientError):
    """Raised when Gemini API quota or rate limits are reached."""
    pass


class ModelOutputValidationError(GeminiServiceError):
    """Raised when model returns malformed, unparseable, or invalid structured data."""
    pass


def is_transient_gemini_error(exc: BaseException) -> bool:
    """Determine whether an error from the Gemini API is transient and retryable."""
    if isinstance(exc, errors.APIError):
        code = getattr(exc, "code", None)
        # Transient HTTP status codes:
        # 429: Rate limit / Resource exhausted
        # 408: Request timeout
        # 500: Internal server error
        # 502: Bad gateway
        # 503: Service unavailable
        # 504: Gateway timeout
        if code in {408, 429, 500, 502, 503, 504}:
            return True
        if isinstance(exc, errors.ServerError):
            return True
        # Explicitly do NOT retry 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404, etc.
        return False

    # Transient transport and network errors
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


SYSTEM_INSTRUCTION = (
    "You are an expert nutrition and dietary analysis AI specializing in global cuisines, with specific expertise in Indian, Asian, Mediterranean, and Western meals. "
    "Analyze the provided food image and identify each visually distinguishable food item separately on mixed plates, thalis, or bowls.\n\n"
    "Key Cuisine Recognition Guidelines (especially for Indian & mixed meals):\n"
    "- Flatbreads: Accurately distinguish Roti/Chapati (whole wheat, ~30-45g per piece, ~80-120 kcal), Naan (tandoor leavened bread, ~100-130g, ~260-350 kcal), Paratha (layered/stuffed flatbread, ~70-120g, ~200-320 kcal), and Puri/Bhatura (deep-fried bread).\n"
    "- Grains & Rice: Distinguish Plain Steamed Basmati Rice (~150-200g per cup/katori, ~190-250 kcal), Jeera Rice, Pulao, Biryani, and Fried Rice.\n"
    "- Dals & Lentils: Identify specific dal preparations where visually discernible (e.g. Yellow Dal Tadka, Dal Makhani with cream/butter, Chana Dal, Sambar, Rasam, Rajma, Chole) with typical katori/bowl portions (~150-200g).\n"
    "- Sabzis & Vegetables: Distinguish dry vegetable preparations (Sukhi Sabzi like Aloo Gobi, Bhindi Masala, Jeera Aloo, Baingan Bharta) from gravies. Estimate realistic oil/tadka content (~120-200 kcal per 150g).\n"
    "- Paneer Dishes: Identify paneer dishes (Paneer Butter Masala, Palak Paneer, Kadai Paneer, Matar Paneer, Paneer Bhurji) estimating visible paneer chunks (~100-200g total with gravy, ~250-400 kcal).\n"
    "- Curries & Gravies: Identify the protein and base style (onion-tomato, coconut, or dairy/cream-based) for Chicken Curry, Egg Curry, Kofta, or fish.\n"
    "- Accompaniments & Sides: Separately detect side items: Kachumber Salad (cucumber, tomato, onion), Raita (~100g, ~60-90 kcal), Papad (~15-20g, ~45-70 kcal), Mint/Coriander Chutney (1-2 tbsp, ~15-30g), Sweet Chutney, and Pickles/Achar (~10-15g).\n\n"
    "Separation & Deduplication Rules:\n"
    "- Multi-Item Separation: On mixed plates or thalis, identify each separate bowl, heap, or item as a distinct food candidate. Do not lump rice and dal together unless thoroughly mixed in the same container.\n"
    "- Deduplication: If multiple pieces of the same bread or item appear (e.g. 2 rotis or 3 idlis), group them into a single item with estimated_quantity reflecting the total count (e.g. estimated_quantity: 2.0, unit: 'rotis', estimated_grams: 70.0) rather than listing duplicate entries.\n"
    "- Grounded Accuracy & Non-Invention: Only report items clearly supported by visual evidence in the image. Never invent or hallucinate unseen sides or hidden ingredients. If the image shows non-food objects or an empty plate, return an empty items list.\n"
    "- Uncertainty & Alternatives: When a dish is visually ambiguous (e.g. Yellow Dal could be Toor Dal Tadka or Moong Dal, or a red curry could be Paneer Makhani or Chicken Tikka Masala), set confidence_level to 'medium' or 'low', explain the ambiguity in uncertainty.notes, and provide 2-3 plausible alternatives in uncertainty.alternatives.\n\n"
    "Portion & Nutrition Consistency Rules:\n"
    "- Estimate each item's portion independently based on visual scale against plate/bowl size.\n"
    "- Keep calories and macronutrients mutually consistent: Calories ~ (Protein * 4) + (Carbohydrates * 4) + (Fat * 9).\n"
    "- All nutrient numbers must be finite, non-negative numbers representing the portion size."
)

VOICE_PARSER_SYSTEM_INSTRUCTION = (
    "You are an expert dietary and nutritional AI parser specializing in converting spoken meal descriptions into structured, itemized foods.\n\n"
    "Core Capabilities & Rules:\n"
    "1. Multi-Item Separation:\n"
    "   - Split complex utterances into discrete, individually countable food items (e.g. 'two scrambled eggs, a slice of sourdough toast with butter, and a black coffee' -> 3 items: Scrambled eggs, Sourdough toast with butter, Black coffee).\n"
    "   - For Indian meals (e.g. 'two rotis, a bowl of dal tadka, and some kachumber salad' or '100g paneer bhurji and a paratha'), break down into distinct items: Roti, Dal Tadka, Kachumber Salad, etc.\n\n"
    "2. In-Flight Corrections & Modifications:\n"
    "   - Accurately parse speech corrections and revisions (e.g. 'one roti, actually make that two rotis' -> 2 rotis; 'an apple, wait no, two oranges' -> 2 oranges; 'chai with sugar, actually without sugar' -> chai without sugar).\n"
    "   - Add an entry to 'warnings' when a self-correction was detected and applied.\n\n"
    "3. Colloquial Quantities & Realistic Weights:\n"
    "   - Translate informal speech measures to realistic weights in grams:\n"
    "     * 'a bowl of oatmeal / dal' -> ~150-200g (1 bowl)\n"
    "     * 'a handful of almonds' -> ~28-30g (1 handful)\n"
    "     * 'a cup of chai' -> ~150ml/g (1 cup)\n"
    "     * 'a slice of toast' -> ~30-40g (1 slice)\n"
    "     * 'a tablespoon of peanut butter / ghee' -> ~15g (1 tbsp)\n"
    "     * 'two medium apples' -> ~360g (~180g each, 2 pieces)\n"
    "     * 'half a chicken breast' -> ~85-100g (0.5 piece)\n"
    "     * 'two rotis/chapatis' -> ~60-70g (2 pieces, ~30-35g each)\n\n"
    "4. State & Preparation Method:\n"
    "   - Mark state as 'raw' or 'cooked' when relevant (e.g. '100g raw chicken breast' -> state: 'raw', ~120 kcal vs '100g cooked chicken breast' -> state: 'cooked', ~165 kcal; '50g raw oats' -> state: 'raw' vs 'a bowl of cooked oatmeal' -> state: 'cooked').\n"
    "   - Note preparation details (fried, grilled, boiled, with ghee, skim milk, unsweetened).\n\n"
    "5. Nutritional Consistency & Plausibility:\n"
    "   - Ensure Calories ~ (Protein * 4) + (Carbohydrates * 4) + (Fat * 9) within standard margin.\n"
    "   - All macro and calorie values must be non-negative numbers representing the portion size.\n\n"
    "6. Ambiguity & Clarification:\n"
    "   - If an item is vague (e.g. 'some pasta' or 'curry'), assign a reasonable default, note the assumption in notes, set confidence_level to 'medium' or 'low', provide plausible alternatives in 'alternatives', and optionally add a clarifying question in 'clarifying_questions'."
)


class GeminiService:
    """Service wrapping Google GenAI SDK for structured food recognition with bounded retries."""

    def __init__(
        self,
        client: Optional[genai.Client] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        max_retries: Optional[int] = None,
        retry_initial_delay: Optional[float] = None,
        retry_max_delay: Optional[float] = None,
    ) -> None:
        self._settings = get_settings()
        self._model = model or self._settings.gemini_model
        self._client = client
        self._per_attempt_timeout_seconds = (
            timeout_seconds if timeout_seconds is not None else self._settings.gemini_timeout_seconds
        )
        self._voice_timeout_seconds = min(self._per_attempt_timeout_seconds, 12.0)
        self._max_retries = (
            max_retries if max_retries is not None else self._settings.gemini_max_retries
        )
        self._retry_initial_delay = (
            retry_initial_delay
            if retry_initial_delay is not None
            else self._settings.gemini_retry_initial_delay
        )
        self._retry_max_delay = (
            retry_max_delay
            if retry_max_delay is not None
            else self._settings.gemini_retry_max_delay
        )

    @property
    def client(self) -> genai.Client:
        """Lazily initialize the GenAI client with secure key loading."""
        if self._client is None:
            api_key = self._settings.require_gemini_api_key()
            self._client = genai.Client(api_key=api_key)
        return self._client

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
        """Execute a Gemini API call with bounded automatic retries for transient failures.

        - Retries HTTP 429, 500, 502, 503, 504, and network/timeout exceptions.
        - Permanent failures (400, 401, 403, 404, schema mismatches) fail immediately without retrying.
        - Logs each attempt, elapsed time, retry decision, and final failure with useful error details.
        - Never logs API keys, prompt contents, or image bytes.
        """
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
            retry=tenacity.retry_if_exception(is_transient_gemini_error),
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
                "Gemini API [%s] call failed after %.2fs and %d attempt(s): %s",
                operation_name,
                total_elapsed,
                len(attempt_start_times) or 1,
                safe_err,
            )

            # Map the final exception to appropriate domain error
            if isinstance(final_exc, errors.APIError):
                code = getattr(final_exc, "code", None)
                if code == 429:
                    raise RateLimitError(
                        "Gemini API rate limit or quota exceeded. Please wait a moment and try again.",
                        code=429,
                    ) from final_exc
                if code in {408, 504}:
                    raise GeminiTimeoutError(
                        "AI recognition service timed out after multiple attempts. Please try again.",
                        code=code,
                    ) from final_exc
                if code in {500, 502, 503}:
                    raise GeminiUnavailableError(
                        f"The AI recognition service is temporarily overloaded or unavailable (HTTP {code}). Please try again in a few moments.",
                        code=code,
                    ) from final_exc
                if code == 401:
                    raise GeminiServiceError(
                        "AI service authentication failed. Please verify your GEMINI_API_KEY configuration."
                    ) from final_exc
                if code == 403:
                    raise GeminiServiceError(
                        "AI service access is forbidden. Please verify your API key permissions and project status."
                    ) from final_exc
                if code == 400:
                    raise GeminiServiceError(
                        "AI service rejected the request payload as invalid."
                    ) from final_exc
                raise GeminiServiceError(
                    f"Gemini service was unable to process the request (HTTP {code}). Please try again later."
                ) from final_exc

            if isinstance(final_exc, (TimeoutError, httpx.TimeoutException)):
                raise GeminiTimeoutError(
                    "AI recognition request timed out after multiple attempts. Please try again."
                ) from final_exc

            if isinstance(final_exc, (httpx.ConnectError, httpx.RemoteProtocolError)):
                raise GeminiUnavailableError(
                    "Cannot establish connection to AI recognition service. Please check your network and try again."
                ) from final_exc

            if isinstance(final_exc, GeminiServiceError):
                raise final_exc

            raise GeminiServiceError(
                "Unexpected error communicating with AI recognition service."
            ) from final_exc

    def recognize_food(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
    ) -> FoodRecognitionResponse:
        """Analyze food image and return validated structured food candidates.

        Args:
            image_bytes: Sanitized JPEG/PNG image bytes.
            mime_type: MIME type of the image.

        Returns:
            FoodRecognitionResponse containing validated food items.
        """
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
            raise ModelOutputValidationError("The AI service returned an empty response.")

        raw_text = response.text.strip()

        # Handle possible markdown backticks if model wraps json
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
            # Try to recover if wrapped or slightly malformed
            try:
                data = json.loads(raw_text)
                if isinstance(data, dict):
                    # Check if items are nested under candidates or food_items
                    if "items" not in data and "candidates" in data:
                        data["items"] = data.pop("candidates")
                    return FoodRecognitionResponse.model_validate(data)
            except Exception:
                pass
            raise ModelOutputValidationError(
                f"Model response failed validation schema: {str(val_err)}"
            ) from val_err
        except Exception as exc:
            raise ModelOutputValidationError(
                f"Failed to decode model JSON output: {str(exc)}"
            ) from exc

    def parse_voice_meal(
        self,
        transcript: str,
        meal_context: Optional[str] = None,
    ) -> VoiceMealParseResponse:
        """Parse spoken food description and return structured items and nutrition.

        Args:
            transcript: Cleaned voice transcript text.
            meal_context: Optional meal context (Breakfast, Lunch, Dinner, Snacks).

        Returns:
            VoiceMealParseResponse containing itemized foods and nutritional estimates.
        """
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
            raise ModelOutputValidationError("The AI service returned an empty response.")

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
                f"Model response failed validation schema: {str(val_err)}"
            ) from val_err
        except Exception as exc:
            raise ModelOutputValidationError(
                f"Failed to decode model JSON output: {str(exc)}"
            ) from exc


_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Singleton getter for GeminiService."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service


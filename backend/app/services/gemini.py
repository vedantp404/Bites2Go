"""Gemini API food recognition service using the official Google GenAI SDK."""

import json
from typing import Optional
import httpx
from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.config import get_settings
from app.models.food import FoodRecognitionResponse, VoiceMealParseResponse


class GeminiServiceError(RuntimeError):
    """Base exception for Gemini service failures."""
    pass


class RateLimitError(GeminiServiceError):
    """Raised when Gemini API quota or rate limits are reached."""
    pass


class ModelOutputValidationError(GeminiServiceError):
    """Raised when model returns malformed, unparseable, or invalid structured data."""
    pass


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
    """Service wrapping Google GenAI SDK for structured food recognition."""

    def __init__(
        self,
        client: Optional[genai.Client] = None,
        model: Optional[str] = None,
    ) -> None:
        self._settings = get_settings()
        self._model = model or self._settings.gemini_model
        self._client = client

    @property
    def client(self) -> genai.Client:
        """Lazily initialize the GenAI client with secure key loading."""
        if self._client is None:
            api_key = self._settings.require_gemini_api_key()
            self._client = genai.Client(api_key=api_key)
        return self._client

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

        timeout_ms = int(self._settings.gemini_timeout_seconds * 1000)
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=FoodRecognitionResponse,
            temperature=0.2,
            http_options=types.HttpOptions(timeout=timeout_ms),
        )

        try:
            response = self.client.models.generate_content(
                model=self._model,
                contents=contents,
                config=config,
            )
        except (TimeoutError, httpx.TimeoutException) as exc:
            raise GeminiServiceError(
                "AI recognition request timed out. Please try again."
            ) from exc
        except errors.APIError as exc:
            code = getattr(exc, "code", None)
            if code == 429:
                raise RateLimitError(
                    "Gemini API rate limit or quota exceeded. Please wait a moment and try again."
                ) from exc
            raise GeminiServiceError(
                "Gemini service was unable to process the image. Please try again later."
            ) from exc
        except Exception as exc:
            if isinstance(exc, GeminiServiceError):
                raise
            raise GeminiServiceError("Unexpected error communicating with AI recognition service.") from exc

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
        timeout_ms = int(self._settings.gemini_timeout_seconds * 1000)
        config = types.GenerateContentConfig(
            system_instruction=VOICE_PARSER_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=VoiceMealParseResponse,
            temperature=0.2,
            http_options=types.HttpOptions(timeout=timeout_ms),
        )

        try:
            response = self.client.models.generate_content(
                model=self._model,
                contents=contents,
                config=config,
            )
        except (TimeoutError, httpx.TimeoutException) as exc:
            raise GeminiServiceError(
                "AI voice parsing request timed out. Please try again."
            ) from exc
        except errors.APIError as exc:
            code = getattr(exc, "code", None)
            if code == 429:
                raise RateLimitError(
                    "Gemini API rate limit or quota exceeded. Please wait a moment and try again."
                ) from exc
            raise GeminiServiceError(
                "Gemini service was unable to process the spoken description. Please try again later."
            ) from exc
        except Exception as exc:
            if isinstance(exc, GeminiServiceError):
                raise
            raise GeminiServiceError(
                "Unexpected error communicating with AI voice recognition service."
            ) from exc

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


"""Gemini API food recognition service using the official Google GenAI SDK."""

import json
from typing import Optional
import httpx
from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.config import get_settings
from app.models.food import FoodRecognitionResponse


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
    "You are an expert nutrition and dietary analysis AI. "
    "Analyze the provided food image with high accuracy and identify all distinct food components. "
    "For each food item:\n"
    "1. food_name: Clean, recognizable food title.\n"
    "2. estimated_quantity: Numeric quantity count (e.g. 1.0, 0.5, 2.0).\n"
    "3. unit: Descriptive serving unit (e.g. slice, cup, bowl, fillet, piece, serving).\n"
    "4. estimated_grams: Realistic weight in grams based on visual scale.\n"
    "5. calories: Total calories (kcal) for this portion.\n"
    "6. protein: Protein in grams (g).\n"
    "7. carbohydrates: Carbohydrates in grams (g).\n"
    "8. fat: Dietary fat in grams (g).\n"
    "9. uncertainty: confidence_score (0.0 to 1.0), confidence_level ('high', 'medium', or 'low'), "
    "notes on preparation or sauces, and alternatives if ambiguous.\n"
    "Be grounded, conservative, and realistic. Never output negative numbers or hallucinated foods."
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
        prompt_text = "Identify all food items in this meal and estimate their portion size, weight, and macronutrients."

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


_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Singleton getter for GeminiService."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service


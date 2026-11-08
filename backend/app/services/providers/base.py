"""Base abstraction and exception definitions for AI recognition providers."""

import contextvars
from abc import ABC, abstractmethod
from typing import Callable, Optional

from app.models.food import FoodRecognitionResponse, VoiceMealParseResponse


class AIServiceError(RuntimeError):
    """Base exception for all AI provider errors."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        code: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.code = code


class AITransientError(AIServiceError):
    """Base exception for transient/retryable AI failures (e.g. rate limits, 503, 504)."""
    pass


class AITimeoutError(AITransientError):
    """Raised when an AI request times out after retries."""
    pass


class AIUnavailableError(AITransientError):
    """Raised when an AI service is temporarily overloaded or unavailable (HTTP 500, 502, 503)."""
    pass


class AIRateLimitError(AITransientError):
    """Raised when API rate limits or daily quotas are reached."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        code: int = 429,
        is_quota_exhausted: bool = False,
    ) -> None:
        super().__init__(message, provider=provider, code=code)
        self.is_quota_exhausted = is_quota_exhausted


class AIAuthenticationError(AIServiceError):
    """Raised when API authentication fails (HTTP 401/403)."""
    pass


class ModelOutputValidationError(AIServiceError):
    """Raised when model returns malformed, unparseable, or invalid structured data."""
    pass


class AIRequestCancelledError(AIServiceError):
    """Raised when the client disconnects or aborts the in-flight AI request."""
    pass


class AIAllProvidersFailedError(AIServiceError):
    """Raised when all configured providers (primary and fallback) have failed."""

    def __init__(
        self,
        message: str,
        primary_provider: str,
        primary_error: Optional[Exception] = None,
        fallback_provider: Optional[str] = None,
        fallback_error: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, provider=primary_provider)
        self.primary_provider = primary_provider
        self.primary_error = primary_error
        self.fallback_provider = fallback_provider
        self.fallback_error = fallback_error


# Backward compatibility aliases
GeminiServiceError = AIServiceError
GeminiTransientError = AITransientError
GeminiTimeoutError = AITimeoutError
GeminiUnavailableError = AIUnavailableError
RateLimitError = AIRateLimitError


current_cancellation_check: contextvars.ContextVar[Optional[Callable[[], bool]]] = (
    contextvars.ContextVar("current_cancellation_check", default=None)
)


def is_request_cancelled(explicit_check: Optional[Callable[[], bool]] = None) -> bool:
    """Check whether the active request has been cancelled by client disconnect."""
    if explicit_check is not None and explicit_check():
        return True
    ctx_check = current_cancellation_check.get()
    if ctx_check is not None and ctx_check():
        return True
    return False


class BaseAIProvider(ABC):
    """Abstract interface defining required capabilities for food AI providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier: 'gemini' | 'openrouter'."""
        pass

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Whether this provider has necessary credentials/keys configured."""
        pass

    @abstractmethod
    def recognize_food(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        timeout_seconds: Optional[float] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> FoodRecognitionResponse:
        """Recognize food from image bytes and return normalized FoodRecognitionResponse."""
        pass

    @abstractmethod
    def parse_voice_meal(
        self,
        transcript: str,
        meal_context: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> VoiceMealParseResponse:
        """Parse voice transcript and return normalized VoiceMealParseResponse."""
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


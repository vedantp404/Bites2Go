"""Tests for /api/v1/recognize-food with mocked Gemini service."""

import base64
import json
from unittest.mock import MagicMock
import httpx
import pytest
from fastapi.testclient import TestClient
from google.genai import errors

from app.config import ConfigurationError
from app.models.food import (
    FoodItemCandidate,
    FoodRecognitionResponse,
    ParsedVoiceFoodItem,
    UncertaintyInfo,
    VoiceMealParseResponse,
)
from app.routers.food import get_gemini_service
from app.services.gemini import (
    GeminiService,
    GeminiServiceError,
    GeminiTimeoutError,
    GeminiUnavailableError,
    ModelOutputValidationError,
    RateLimitError,
    is_transient_gemini_error,
)


def test_recognize_food_success(
    client: TestClient,
    sample_jpeg_bytes: bytes,
    mock_food_response: FoodRecognitionResponse,
) -> None:
    """Verify standard multipart upload succeeds with mocked Gemini response."""
    mock_service = MagicMock(spec=GeminiService)
    mock_service.recognize_food.return_value = mock_food_response

    client.app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/recognize-food",
            files={"file": ("meal.jpg", sample_jpeg_bytes, "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["items"]) == 2
        assert data["items"][0]["food_name"] == "Scrambled Eggs"
        assert data["items"][0]["calories"] == 140.0
        assert data["items"][0]["protein"] == 12.0
        assert data["items"][0]["uncertainty"]["confidence_score"] == 0.92
    finally:
        client.app.dependency_overrides.clear()


def test_recognize_food_base64_success(
    client: TestClient,
    sample_jpeg_bytes: bytes,
    mock_food_response: FoodRecognitionResponse,
) -> None:
    """Verify base64 JSON payload succeeds with mocked Gemini response."""
    mock_service = MagicMock(spec=GeminiService)
    mock_service.recognize_food.return_value = mock_food_response

    b64_string = base64.b64encode(sample_jpeg_bytes).decode("utf-8")

    client.app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/recognize-food/base64",
            json={"image_base64": b64_string},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["items"]) == 2
    finally:
        client.app.dependency_overrides.clear()


def test_recognize_food_missing_file(client: TestClient) -> None:
    """Verify 400 Bad Request if file parameter is omitted."""
    response = client.post("/api/v1/recognize-food")
    assert response.status_code == 400
    assert "Missing image file" in response.json()["detail"]


def test_recognize_food_corrupted_image(client: TestClient) -> None:
    """Verify 400 Bad Request if file contents are corrupted bytes."""
    corrupted_data = b"NOT_A_VALID_IMAGE_HEADER_OR_DATA"
    response = client.post(
        "/api/v1/recognize-food",
        files={"file": ("corrupted.jpg", corrupted_data, "image/jpeg")},
    )
    assert response.status_code == 400
    assert "valid image" in response.json()["detail"].lower()


def test_recognize_food_handles_rate_limit(
    client: TestClient,
    sample_jpeg_bytes: bytes,
) -> None:
    """Verify 429 Too Many Requests when Gemini rate limit is encountered."""
    mock_service = MagicMock(spec=GeminiService)
    mock_service.recognize_food.side_effect = RateLimitError("Rate limit exceeded")

    client.app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/recognize-food",
            files={"file": ("meal.jpg", sample_jpeg_bytes, "image/jpeg")},
        )
        assert response.status_code == 429
        assert "rate limit" in response.json()["detail"].lower()
    finally:
        client.app.dependency_overrides.clear()


def test_recognize_food_handles_model_validation_failure(
    client: TestClient,
    sample_jpeg_bytes: bytes,
) -> None:
    """Verify 502 Bad Gateway when Gemini returns unparseable nutritional data."""
    mock_service = MagicMock(spec=GeminiService)
    mock_service.recognize_food.side_effect = ModelOutputValidationError("Invalid model schema output")

    client.app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/recognize-food",
            files={"file": ("meal.jpg", sample_jpeg_bytes, "image/jpeg")},
        )
        assert response.status_code == 502
        assert "unparseable or malformed" in response.json()["detail"].lower()
    finally:
        client.app.dependency_overrides.clear()


def test_recognize_food_handles_missing_configuration(
    client: TestClient,
    sample_jpeg_bytes: bytes,
) -> None:
    """Verify 503 Service Unavailable when GEMINI_API_KEY is unconfigured."""
    mock_service = MagicMock(spec=GeminiService)
    mock_service.recognize_food.side_effect = ConfigurationError("GEMINI_API_KEY is not configured")

    client.app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/recognize-food",
            files={"file": ("meal.jpg", sample_jpeg_bytes, "image/jpeg")},
        )
        assert response.status_code == 503
        assert "GEMINI_API_KEY is not configured" in response.json()["detail"]
    finally:
        client.app.dependency_overrides.clear()


def test_recognize_mixed_indian_meal(
    client: TestClient,
    sample_jpeg_bytes: bytes,
) -> None:
    """Verify recognition of a multi-item mixed Indian meal with accurate portion estimates."""
    from app.models.food import FoodItemCandidate, UncertaintyInfo

    indian_thali = FoodRecognitionResponse(
        success=True,
        summary="Indian thali meal with 2 rotis, yellow dal tadka, steamed basmati rice, and bhindi masala.",
        items=[
            FoodItemCandidate(
                food_name="Whole Wheat Roti",
                estimated_quantity=2.0,
                unit="pieces",
                estimated_grams=70.0,
                calories=190.0,
                protein=6.0,
                carbohydrates=38.0,
                fat=1.5,
                uncertainty=UncertaintyInfo(
                    confidence_score=0.92,
                    confidence_level="high",
                    notes="Two medium roasted chapatis/rotis without excess ghee",
                    alternatives=[],
                ),
            ),
            FoodItemCandidate(
                food_name="Yellow Dal Tadka",
                estimated_quantity=1.0,
                unit="katori/bowl",
                estimated_grams=180.0,
                calories=150.0,
                protein=9.0,
                carbohydrates=20.0,
                fat=4.0,
                uncertainty=UncertaintyInfo(
                    confidence_score=0.85,
                    confidence_level="high",
                    notes="Yellow lentil dal with cumin and mustard seed tadka",
                    alternatives=["Toor Dal", "Moong Dal"],
                ),
            ),
            FoodItemCandidate(
                food_name="Steamed Basmati Rice",
                estimated_quantity=1.0,
                unit="cup",
                estimated_grams=150.0,
                calories=195.0,
                protein=4.0,
                carbohydrates=43.0,
                fat=0.5,
                uncertainty=UncertaintyInfo(
                    confidence_score=0.95,
                    confidence_level="high",
                    notes="Plain boiled long-grain basmati rice",
                    alternatives=[],
                ),
            ),
            FoodItemCandidate(
                food_name="Bhindi Masala (Okra Sabzi)",
                estimated_quantity=1.0,
                unit="serving",
                estimated_grams=120.0,
                calories=110.0,
                protein=2.5,
                carbohydrates=12.0,
                fat=6.0,
                uncertainty=UncertaintyInfo(
                    confidence_score=0.88,
                    confidence_level="high",
                    notes="Pan-fried spiced okra with onions and tomatoes",
                    alternatives=["Aloo Bhindi"],
                ),
            ),
        ],
        warnings=[],
    )

    mock_service = MagicMock(spec=GeminiService)
    mock_service.recognize_food.return_value = indian_thali

    client.app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/recognize-food",
            files={"file": ("thali.jpg", sample_jpeg_bytes, "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 4
        # Verify total calories calculation across items
        total_cal = sum(item["calories"] for item in data["items"])
        assert total_cal == 645.0
        assert data["items"][0]["food_name"] == "Whole Wheat Roti"
        assert data["items"][0]["estimated_quantity"] == 2.0
    finally:
        client.app.dependency_overrides.clear()


def test_recognize_ambiguous_food_with_alternatives(
    client: TestClient,
    sample_jpeg_bytes: bytes,
) -> None:
    """Verify handling of visually ambiguous curry with confidence and alternatives."""
    from app.models.food import FoodItemCandidate, UncertaintyInfo

    ambiguous_meal = FoodRecognitionResponse(
        success=True,
        summary="Red curry dish with cubed protein, visual distinction between paneer and tofu is ambiguous.",
        items=[
            FoodItemCandidate(
                food_name="Paneer Butter Masala",
                estimated_quantity=1.0,
                unit="bowl",
                estimated_grams=200.0,
                calories=320.0,
                protein=12.0,
                carbohydrates=16.0,
                fat=24.0,
                uncertainty=UncertaintyInfo(
                    confidence_score=0.65,
                    confidence_level="medium",
                    notes="Rich tomato cream gravy with white cubes; could be tofu or paneer",
                    alternatives=["Tofu Tikka Masala", "Chicken Tikka Masala"],
                ),
            ),
        ],
        warnings=["Visual inspection cannot distinguish paneer from firm tofu with high confidence."],
    )

    mock_service = MagicMock(spec=GeminiService)
    mock_service.recognize_food.return_value = ambiguous_meal

    client.app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/recognize-food",
            files={"file": ("curry.jpg", sample_jpeg_bytes, "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        item = data["items"][0]
        assert item["uncertainty"]["confidence_level"] == "medium"
        assert "Tofu Tikka Masala" in item["uncertainty"]["alternatives"]
        assert len(data["warnings"]) == 1
    finally:
        client.app.dependency_overrides.clear()


def test_recognize_no_food_detected(
    client: TestClient,
    sample_jpeg_bytes: bytes,
) -> None:
    """Verify empty candidates response when no food is identifiable in photo."""
    empty_result = FoodRecognitionResponse(
        success=True,
        summary="No food items detected in this image.",
        items=[],
        warnings=["The image appears to show non-food objects or an empty surface."],
    )

    mock_service = MagicMock(spec=GeminiService)
    mock_service.recognize_food.return_value = empty_result

    client.app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/recognize-food",
            files={"file": ("desk.jpg", sample_jpeg_bytes, "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["items"]) == 0
        assert "No food items" in data["summary"]
    finally:
        client.app.dependency_overrides.clear()


def test_deduplicate_identical_food_candidates() -> None:
    """Verify that multiple duplicate items with same name are merged into a single consolidated item."""
    from app.models.food import FoodItemCandidate, UncertaintyInfo

    raw_response = FoodRecognitionResponse(
        success=True,
        summary="Meal with 2 separate rotis listed individually.",
        items=[
            FoodItemCandidate(
                food_name="Roti",
                estimated_quantity=1.0,
                unit="piece",
                estimated_grams=35.0,
                calories=95.0,
                protein=3.0,
                carbohydrates=19.0,
                fat=1.0,
                uncertainty=UncertaintyInfo(
                    confidence_score=0.9,
                    confidence_level="high",
                    notes="Roti piece 1",
                    alternatives=["Chapati"],
                ),
            ),
            FoodItemCandidate(
                food_name="Roti",
                estimated_quantity=1.0,
                unit="piece",
                estimated_grams=35.0,
                calories=95.0,
                protein=3.0,
                carbohydrates=19.0,
                fat=1.0,
                uncertainty=UncertaintyInfo(
                    confidence_score=0.9,
                    confidence_level="high",
                    notes="Roti piece 2",
                    alternatives=["Phulka"],
                ),
            ),
        ],
    )

    assert len(raw_response.items) == 1
    merged = raw_response.items[0]
    assert merged.food_name == "Roti"
    assert merged.estimated_quantity == 2.0
    assert merged.estimated_grams == 70.0
    assert merged.calories == 190.0
    assert merged.protein == 6.0
    assert merged.carbohydrates == 38.0
    assert merged.fat == 2.0
    assert "Chapati" in merged.uncertainty.alternatives
    assert "Phulka" in merged.uncertainty.alternatives


def test_parse_voice_meal_success(
    client: TestClient,
    mock_voice_meal_response: VoiceMealParseResponse,
) -> None:
    """Verify standard voice transcript parsing succeeds with mocked Gemini service."""
    mock_service = MagicMock(spec=GeminiService)
    mock_service.parse_voice_meal.return_value = mock_voice_meal_response

    client.app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/parse-voice-meal",
            json={
                "transcript": "two scrambled eggs, a slice of whole wheat toast with butter, and a cup of black coffee",
                "meal_context": "Breakfast",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["items"]) == 3
        assert data["items"][0]["food_description"] == "Scrambled Eggs"
        assert data["items"][0]["quantity"] == 2.0
        assert data["items"][0]["calories"] == 140.0
        assert data["items"][1]["food_description"] == "Whole Wheat Toast with Butter"
        assert data["items"][2]["food_description"] == "Black Coffee"
        mock_service.parse_voice_meal.assert_called_once_with(
            transcript="two scrambled eggs, a slice of whole wheat toast with butter, and a cup of black coffee",
            meal_context="Breakfast",
        )
    finally:
        client.app.dependency_overrides.clear()


def test_parse_voice_meal_indian_meal_and_corrections(
    client: TestClient,
) -> None:
    """Verify voice parsing with self-corrections and Indian foods."""
    indian_voice_response = VoiceMealParseResponse(
        success=True,
        transcript="one roti, actually make that two rotis with ghee, and a bowl of yellow dal tadka",
        summary="Indian lunch with 2 rotis with ghee and dal tadka.",
        items=[
            ParsedVoiceFoodItem(
                food_description="Roti with Ghee",
                quantity=2.0,
                unit="pieces",
                preparation="whole wheat flatbread brushed with ghee",
                state="cooked",
                estimated_grams=70.0,
                calories=210.0,
                protein=6.0,
                carbohydrates=36.0,
                fat=5.0,
                confidence=0.92,
                confidence_level="high",
                alternatives=["Chapati", "Phulka"],
                notes="2 rotis (~30g each) + 1 tsp ghee",
            ),
            ParsedVoiceFoodItem(
                food_description="Yellow Dal Tadka",
                quantity=1.0,
                unit="bowl",
                preparation="cooked yellow toor dal with cumin tadka",
                state="cooked",
                estimated_grams=180.0,
                calories=160.0,
                protein=8.5,
                carbohydrates=22.0,
                fat=4.5,
                confidence=0.88,
                confidence_level="high",
                alternatives=["Moong Dal", "Chana Dal"],
                notes="Standard katori portion (~180g)",
            ),
        ],
        warnings=["Applied self-correction: updated quantity of rotis from 1 to 2."],
        clarifying_questions=[],
    )

    mock_service = MagicMock(spec=GeminiService)
    mock_service.parse_voice_meal.return_value = indian_voice_response

    client.app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/parse-voice-meal",
            json={
                "transcript": "one roti, actually make that two rotis with ghee, and a bowl of yellow dal tadka",
                "meal_context": "Lunch",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["items"]) == 2
        assert data["items"][0]["quantity"] == 2.0
        assert "warnings" in data
        assert len(data["warnings"]) == 1
        assert "correction" in data["warnings"][0].lower()
    finally:
        client.app.dependency_overrides.clear()


def test_parse_voice_meal_raw_vs_cooked_weights() -> None:
    """Verify raw vs cooked distinction in ParsedVoiceFoodItem."""
    raw_item = ParsedVoiceFoodItem(
        food_description="Raw Chicken Breast",
        quantity=100.0,
        unit="gram",
        preparation="uncooked, boneless skinless",
        state="raw",
        estimated_grams=100.0,
        calories=120.0,
        protein=26.0,
        carbohydrates=0.0,
        fat=1.5,
        confidence=0.95,
        confidence_level="high",
    )
    cooked_item = ParsedVoiceFoodItem(
        food_description="Cooked Chicken Breast",
        quantity=100.0,
        unit="gram",
        preparation="grilled, cooked",
        state="cooked",
        estimated_grams=100.0,
        calories=165.0,
        protein=31.0,
        carbohydrates=0.0,
        fat=3.6,
        confidence=0.95,
        confidence_level="high",
    )
    assert raw_item.state == "raw"
    assert cooked_item.state == "cooked"
    assert raw_item.calories < cooked_item.calories


def test_parse_voice_meal_empty_transcript_bad_request(client: TestClient) -> None:
    """Verify 400 or 422 Bad Request on empty or whitespace-only transcript."""
    response = client.post(
        "/api/v1/parse-voice-meal",
        json={"transcript": "   "},
    )
    assert response.status_code in (400, 422)


def test_parse_voice_meal_missing_transcript_bad_request(client: TestClient) -> None:
    """Verify 422 Unprocessable Entity when transcript field is omitted."""
    response = client.post(
        "/api/v1/parse-voice-meal",
        json={"meal_context": "Dinner"},
    )
    assert response.status_code == 422


def test_parse_voice_meal_rate_limit(client: TestClient) -> None:
    """Verify 429 Too Many Requests when Gemini rate limit is hit."""
    mock_service = MagicMock(spec=GeminiService)
    mock_service.parse_voice_meal.side_effect = RateLimitError("Rate limit exceeded")

    client.app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/parse-voice-meal",
            json={"transcript": "a bowl of cereal"},
        )
        assert response.status_code == 429
        assert "rate limit" in response.json()["detail"].lower()
    finally:
        client.app.dependency_overrides.clear()


def test_parse_voice_meal_malformed_output_bad_gateway(client: TestClient) -> None:
    """Verify 502 Bad Gateway when Gemini returns unparseable or malformed output."""
    mock_service = MagicMock(spec=GeminiService)
    mock_service.parse_voice_meal.side_effect = ModelOutputValidationError("Invalid json")

    client.app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/parse-voice-meal",
            json={"transcript": "a cup of green tea"},
        )
        assert response.status_code == 502
    finally:
        client.app.dependency_overrides.clear()


def test_parse_voice_meal_service_unconfigured(client: TestClient) -> None:
    """Verify 503 Service Unavailable when Gemini API key is missing."""
    mock_service = MagicMock(spec=GeminiService)
    mock_service.parse_voice_meal.side_effect = ConfigurationError("Missing GEMINI_API_KEY")

    client.app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/parse-voice-meal",
            json={"transcript": "an orange"},
        )
        assert response.status_code == 503
        assert "gemini_api_key" in response.json()["detail"].lower()
    finally:
        client.app.dependency_overrides.clear()


def test_parsed_voice_food_item_macro_clamping() -> None:
    """Verify that macros exceeding reported calories adjust calories consistently."""
    # 30g protein (120 kcal) + 40g carbs (160 kcal) + 20g fat (180 kcal) = 460 kcal
    # If model reports 50 kcal, validator adjusts calories to ~460 kcal
    item = ParsedVoiceFoodItem(
        food_description="High Protein Shake",
        quantity=1.0,
        unit="bottle",
        estimated_grams=300.0,
        calories=50.0,
        protein=30.0,
        carbohydrates=40.0,
        fat=20.0,
        confidence=0.9,
        confidence_level="high",
    )
    assert item.calories >= 460.0


# ============================================================================
# Automatic Retry & Transient Failure Tests
# ============================================================================


def test_is_transient_gemini_error_classification() -> None:
    """Verify that is_transient_gemini_error accurately identifies transient vs permanent failures."""
    # Transient API errors
    e504 = errors.ServerError(504, {"error": {"code": 504, "message": "Gateway Timeout"}})
    e503 = errors.ServerError(503, {"error": {"code": 503, "message": "Service Unavailable"}})
    e502 = errors.ServerError(502, {"error": {"code": 502, "message": "Bad Gateway"}})
    e500 = errors.ServerError(500, {"error": {"code": 500, "message": "Internal Server Error"}})
    e429 = errors.ClientError(429, {"error": {"code": 429, "message": "Resource Exhausted"}})
    e408 = errors.ClientError(408, {"error": {"code": 408, "message": "Request Timeout"}})
    assert is_transient_gemini_error(e504) is True
    assert is_transient_gemini_error(e503) is True
    assert is_transient_gemini_error(e502) is True
    assert is_transient_gemini_error(e500) is True
    assert is_transient_gemini_error(e429) is True
    assert is_transient_gemini_error(e408) is True

    # Transient transport errors
    assert is_transient_gemini_error(httpx.ReadTimeout("Timeout")) is True
    assert is_transient_gemini_error(httpx.ConnectError("Connection drop")) is True
    assert is_transient_gemini_error(TimeoutError("System timeout")) is True

    # Permanent failures - NEVER retry
    e401 = errors.ClientError(401, {"error": {"code": 401, "message": "API Key Invalid"}})
    e400 = errors.ClientError(400, {"error": {"code": 400, "message": "Bad Request"}})
    e403 = errors.ClientError(403, {"error": {"code": 403, "message": "Forbidden"}})
    e404 = errors.ClientError(404, {"error": {"code": 404, "message": "Model Not Found"}})
    assert is_transient_gemini_error(e401) is False
    assert is_transient_gemini_error(e400) is False
    assert is_transient_gemini_error(e403) is False
    assert is_transient_gemini_error(e404) is False
    assert is_transient_gemini_error(ModelOutputValidationError("bad json")) is False
    assert is_transient_gemini_error(ConfigurationError("key missing")) is False


def test_gemini_service_retry_504_transient_success(sample_jpeg_bytes: bytes) -> None:
    """Verify GeminiService automatically retries on HTTP 504 Gateway Timeout and succeeds on attempt 2."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "success": True,
        "summary": "Scrambled Eggs",
        "items": [{
            "food_name": "Scrambled Eggs",
            "estimated_quantity": 2.0,
            "unit": "eggs",
            "estimated_grams": 100.0,
            "calories": 140.0,
            "protein": 12.0,
            "carbohydrates": 1.5,
            "fat": 9.5,
            "uncertainty": {
                "confidence_score": 0.95,
                "confidence_level": "high",
                "notes": None,
                "alternatives": []
            }
        }],
        "warnings": []
    })

    # Fail attempt 1 with HTTP 504, succeed on attempt 2
    mock_client.models.generate_content.side_effect = [
        errors.ServerError(504, {"error": {"code": 504, "message": "Gateway Timeout"}}),
        mock_response,
    ]

    service = GeminiService(
        client=mock_client,
        retry_initial_delay=0.001,
        retry_max_delay=0.005,
    )
    result = service.recognize_food(sample_jpeg_bytes)

    assert result.success is True
    assert len(result.items) == 1
    assert result.items[0].food_name == "Scrambled Eggs"
    assert mock_client.models.generate_content.call_count == 2


def test_gemini_service_retry_503_two_retries_success(sample_jpeg_bytes: bytes) -> None:
    """Verify GeminiService handles two consecutive HTTP 503 errors and succeeds on attempt 3."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "success": True,
        "summary": "Yellow Dal",
        "items": [{
            "food_name": "Yellow Dal Tadka",
            "estimated_quantity": 1.0,
            "unit": "bowl",
            "estimated_grams": 180.0,
            "calories": 150.0,
            "protein": 9.0,
            "carbohydrates": 20.0,
            "fat": 4.0,
            "uncertainty": {
                "confidence_score": 0.9,
                "confidence_level": "high",
                "notes": None,
                "alternatives": []
            }
        }],
        "warnings": []
    })

    # Fail attempts 1 and 2 with HTTP 503, succeed on attempt 3
    mock_client.models.generate_content.side_effect = [
        errors.ServerError(503, {"error": {"code": 503, "message": "Service Unavailable"}}),
        errors.ServerError(503, {"error": {"code": 503, "message": "Service Unavailable"}}),
        mock_response,
    ]

    service = GeminiService(
        client=mock_client,
        retry_initial_delay=0.001,
        retry_max_delay=0.005,
    )
    result = service.recognize_food(sample_jpeg_bytes)

    assert result.success is True
    assert len(result.items) == 1
    assert result.items[0].food_name == "Yellow Dal Tadka"
    assert mock_client.models.generate_content.call_count == 3


def test_gemini_service_retry_429_rate_limit_success(sample_jpeg_bytes: bytes) -> None:
    """Verify GeminiService automatically retries on HTTP 429 Rate Limit and succeeds."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "success": True,
        "summary": "Apple",
        "items": [{
            "food_name": "Apple",
            "estimated_quantity": 1.0,
            "unit": "piece",
            "estimated_grams": 182.0,
            "calories": 95.0,
            "protein": 0.5,
            "carbohydrates": 25.0,
            "fat": 0.3,
            "uncertainty": {
                "confidence_score": 0.95,
                "confidence_level": "high",
                "notes": None,
                "alternatives": []
            }
        }],
        "warnings": []
    })

    mock_client.models.generate_content.side_effect = [
        errors.ClientError(429, {"error": {"code": 429, "message": "Resource Exhausted"}}),
        mock_response,
    ]

    service = GeminiService(
        client=mock_client,
        retry_initial_delay=0.001,
        retry_max_delay=0.005,
    )
    result = service.recognize_food(sample_jpeg_bytes)

    assert result.success is True
    assert mock_client.models.generate_content.call_count == 2


def test_gemini_service_retry_timeout_success(sample_jpeg_bytes: bytes) -> None:
    """Verify GeminiService retries on httpx.TimeoutException and succeeds."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "success": True,
        "summary": "Banana",
        "items": [{
            "food_name": "Banana",
            "estimated_quantity": 1.0,
            "unit": "piece",
            "estimated_grams": 118.0,
            "calories": 105.0,
            "protein": 1.3,
            "carbohydrates": 27.0,
            "fat": 0.3,
            "uncertainty": {
                "confidence_score": 0.95,
                "confidence_level": "high",
                "notes": None,
                "alternatives": []
            }
        }],
        "warnings": []
    })

    mock_client.models.generate_content.side_effect = [
        httpx.ReadTimeout("Read timed out"),
        mock_response,
    ]

    service = GeminiService(
        client=mock_client,
        retry_initial_delay=0.001,
        retry_max_delay=0.005,
    )
    result = service.recognize_food(sample_jpeg_bytes)

    assert result.success is True
    assert mock_client.models.generate_content.call_count == 2


def test_gemini_service_exhausted_retries_raises_unavailable(sample_jpeg_bytes: bytes) -> None:
    """Verify persistent HTTP 503 raises GeminiUnavailableError after exactly 3 attempts."""
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        errors.ServerError(503, {"error": {"code": 503, "message": "Service Unavailable"}}),
        errors.ServerError(503, {"error": {"code": 503, "message": "Service Unavailable"}}),
        errors.ServerError(503, {"error": {"code": 503, "message": "Service Unavailable"}}),
    ]

    service = GeminiService(
        client=mock_client,
        max_retries=2,
        retry_initial_delay=0.001,
        retry_max_delay=0.005,
    )

    with pytest.raises(GeminiUnavailableError) as exc_info:
        service.recognize_food(sample_jpeg_bytes)

    assert exc_info.value.code == 503
    assert mock_client.models.generate_content.call_count == 3


def test_gemini_service_exhausted_retries_raises_timeout(sample_jpeg_bytes: bytes) -> None:
    """Verify persistent HTTP 504 raises GeminiTimeoutError after exactly 3 attempts."""
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        errors.ServerError(504, {"error": {"code": 504, "message": "Gateway Timeout"}}),
        errors.ServerError(504, {"error": {"code": 504, "message": "Gateway Timeout"}}),
        errors.ServerError(504, {"error": {"code": 504, "message": "Gateway Timeout"}}),
    ]

    service = GeminiService(
        client=mock_client,
        max_retries=2,
        retry_initial_delay=0.001,
        retry_max_delay=0.005,
    )

    with pytest.raises(GeminiTimeoutError) as exc_info:
        service.recognize_food(sample_jpeg_bytes)

    assert exc_info.value.code == 504
    assert mock_client.models.generate_content.call_count == 3


def test_gemini_service_permanent_auth_failure_no_retries(sample_jpeg_bytes: bytes) -> None:
    """Verify permanent HTTP 401 Unauthorized fails immediately on attempt 1 without retrying."""
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = errors.ClientError(
        401, {"error": {"code": 401, "message": "API Key Invalid"}}
    )

    service = GeminiService(
        client=mock_client,
        max_retries=2,
        retry_initial_delay=0.001,
        retry_max_delay=0.005,
    )

    with pytest.raises(GeminiServiceError) as exc_info:
        service.recognize_food(sample_jpeg_bytes)

    assert "authentication failed" in str(exc_info.value).lower()
    assert mock_client.models.generate_content.call_count == 1


def test_gemini_service_permanent_bad_request_no_retries(sample_jpeg_bytes: bytes) -> None:
    """Verify permanent HTTP 400 Bad Request fails immediately on attempt 1 without retrying."""
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = errors.ClientError(
        400, {"error": {"code": 400, "message": "Invalid argument: Image payload corrupted"}}
    )

    service = GeminiService(
        client=mock_client,
        max_retries=2,
        retry_initial_delay=0.001,
        retry_max_delay=0.005,
    )

    with pytest.raises(GeminiServiceError) as exc_info:
        service.recognize_food(sample_jpeg_bytes)

    assert "invalid" in str(exc_info.value).lower()
    assert mock_client.models.generate_content.call_count == 1


def test_gemini_service_malformed_response_no_retries(sample_jpeg_bytes: bytes) -> None:
    """Verify unparseable response raises ModelOutputValidationError on attempt 1 without retrying."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "This is not valid JSON at all and cannot be parsed."
    mock_client.models.generate_content.return_value = mock_response

    service = GeminiService(
        client=mock_client,
        max_retries=2,
        retry_initial_delay=0.001,
        retry_max_delay=0.005,
    )

    with pytest.raises(ModelOutputValidationError):
        service.recognize_food(sample_jpeg_bytes)

    assert mock_client.models.generate_content.call_count == 1


def test_gemini_service_parse_voice_meal_retry_transient_success() -> None:
    """Verify parse_voice_meal retries on transient 503 and succeeds on attempt 2."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "success": True,
        "transcript": "two boiled eggs",
        "summary": "Two boiled eggs",
        "items": [{
            "food_description": "Boiled Eggs",
            "quantity": 2.0,
            "unit": "eggs",
            "preparation": "hard boiled",
            "state": "cooked",
            "estimated_grams": 100.0,
            "calories": 155.0,
            "protein": 13.0,
            "carbohydrates": 1.1,
            "fat": 11.0,
            "confidence": 0.95,
            "confidence_level": "high",
            "alternatives": [],
            "notes": None,
        }],
        "warnings": [],
        "clarifying_questions": [],
    })

    mock_client.models.generate_content.side_effect = [
        errors.ServerError(503, {"error": {"code": 503, "message": "Service Unavailable"}}),
        mock_response,
    ]

    service = GeminiService(
        client=mock_client,
        retry_initial_delay=0.001,
        retry_max_delay=0.005,
    )
    result = service.parse_voice_meal("two boiled eggs")

    assert result.success is True
    assert len(result.items) == 1
    assert result.items[0].food_description == "Boiled Eggs"
    assert mock_client.models.generate_content.call_count == 2


def test_recognize_food_endpoint_returns_504_on_timeout(
    client: TestClient,
    sample_jpeg_bytes: bytes,
) -> None:
    """Verify /api/v1/recognize-food returns HTTP 504 on GeminiTimeoutError with structured headers."""
    mock_service = MagicMock(spec=GeminiService)
    mock_service.recognize_food.side_effect = GeminiTimeoutError("Timed out after retries", code=504)

    client.app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/recognize-food",
            files={"file": ("meal.jpg", sample_jpeg_bytes, "image/jpeg")},
        )
        assert response.status_code == 504
        assert "timed out after multiple attempts" in response.json()["detail"].lower()
        assert response.headers.get("X-Error-Category") == "upstream_timeout"
        assert response.headers.get("Retry-After") == "2"
    finally:
        client.app.dependency_overrides.clear()


def test_recognize_food_endpoint_returns_503_on_unavailable(
    client: TestClient,
    sample_jpeg_bytes: bytes,
) -> None:
    """Verify /api/v1/recognize-food returns HTTP 503 on GeminiUnavailableError with structured headers."""
    mock_service = MagicMock(spec=GeminiService)
    mock_service.recognize_food.side_effect = GeminiUnavailableError("Service overloaded", code=503)

    client.app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/recognize-food",
            files={"file": ("meal.jpg", sample_jpeg_bytes, "image/jpeg")},
        )
        assert response.status_code == 503
        assert "temporarily overloaded or unavailable" in response.json()["detail"].lower()
        assert response.headers.get("X-Error-Category") == "upstream_unavailable"
        assert response.headers.get("Retry-After") == "3"
    finally:
        client.app.dependency_overrides.clear()


def test_parse_voice_meal_endpoint_returns_504_on_timeout(client: TestClient) -> None:
    """Verify /api/v1/parse-voice-meal returns HTTP 504 on GeminiTimeoutError."""
    mock_service = MagicMock(spec=GeminiService)
    mock_service.parse_voice_meal.side_effect = GeminiTimeoutError("Voice timed out", code=504)

    client.app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/parse-voice-meal",
            json={"transcript": "two chapatis and dal"},
        )
        assert response.status_code == 504
        assert "timed out after multiple attempts" in response.json()["detail"].lower()
        assert response.headers.get("X-Error-Category") == "upstream_timeout"
    finally:
        client.app.dependency_overrides.clear()


def test_parse_voice_meal_endpoint_returns_503_on_unavailable(client: TestClient) -> None:
    """Verify /api/v1/parse-voice-meal returns HTTP 503 on GeminiUnavailableError."""
    mock_service = MagicMock(spec=GeminiService)
    mock_service.parse_voice_meal.side_effect = GeminiUnavailableError("Voice service down", code=503)

    client.app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/parse-voice-meal",
            json={"transcript": "a bowl of curd rice"},
        )
        assert response.status_code == 503
        assert "temporarily overloaded or unavailable" in response.json()["detail"].lower()
        assert response.headers.get("X-Error-Category") == "upstream_unavailable"
    finally:
        client.app.dependency_overrides.clear()




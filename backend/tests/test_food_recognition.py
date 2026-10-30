"""Tests for /api/v1/recognize-food with mocked Gemini service."""

import base64
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from app.config import ConfigurationError
from app.models.food import FoodRecognitionResponse
from app.routers.food import get_gemini_service
from app.services.gemini import (
    GeminiService,
    ModelOutputValidationError,
    RateLimitError,
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



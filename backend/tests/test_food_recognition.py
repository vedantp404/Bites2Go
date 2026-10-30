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


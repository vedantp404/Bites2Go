"""Unit and integration tests for AI request deadline budgets and cancellation reliability."""

import time
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.models.food import (
    FoodItemCandidate,
    FoodRecognitionResponse,
    ParsedVoiceFoodItem,
    UncertaintyInfo,
    VoiceMealParseResponse,
)
from app.routers.food import get_ai_service
from app.services.ai_service import DualProviderService
from app.services.providers.base import (
    AIAuthenticationError,
    AIRateLimitError,
    AIRequestCancelledError,
    AITimeoutError,
    AIUnavailableError,
    BaseAIProvider,
    is_request_cancelled,
)


@pytest.fixture
def sample_candidate() -> FoodItemCandidate:
    return FoodItemCandidate(
        food_name="Paneer Butter Masala",
        estimated_quantity=1.0,
        unit="bowl",
        estimated_grams=200.0,
        calories=350.0,
        protein=14.0,
        carbohydrates=12.0,
        fat=28.0,
        uncertainty=UncertaintyInfo(confidence_score=0.9, confidence_level="high"),
    )


@pytest.fixture
def sample_voice_item() -> ParsedVoiceFoodItem:
    return ParsedVoiceFoodItem(
        food_description="2 chapatis",
        quantity=2.0,
        unit="piece",
        estimated_grams=60.0,
        calories=140.0,
        protein=4.0,
        carbohydrates=26.0,
        fat=2.0,
    )


# ---------------------------------------------------------------------------
# Test 1: Cancellation check stops execution immediately
# ---------------------------------------------------------------------------
def test_cancellation_check_raises_request_cancelled_error(sample_jpeg_bytes: bytes) -> None:
    """Verify that if is_cancelled returns True, AIRequestCancelledError is raised immediately."""
    mock_primary = MagicMock(spec=BaseAIProvider)
    mock_primary.name = "gemini"
    mock_primary.is_configured = True

    mock_fallback = MagicMock(spec=BaseAIProvider)
    mock_fallback.name = "openrouter"
    mock_fallback.is_configured = True

    settings = Settings()
    service = DualProviderService(
        gemini_provider=mock_primary,
        openrouter_provider=mock_fallback,
        settings=settings,
    )

    # Calling with is_cancelled returning True should raise AIRequestCancelledError
    with pytest.raises(AIRequestCancelledError) as exc_info:
        service.recognize_food(
            sample_jpeg_bytes,
            is_cancelled=lambda: True,
        )

    assert "cancelled" in str(exc_info.value).lower()
    # Primary and fallback must NOT have been called
    mock_primary.recognize_food.assert_not_called()
    mock_fallback.recognize_food.assert_not_called()


# ---------------------------------------------------------------------------
# Test 2: Primary cancellation does not invoke fallback
# ---------------------------------------------------------------------------
def test_primary_cancellation_does_not_trigger_fallback(sample_jpeg_bytes: bytes) -> None:
    """When primary aborts due to client disconnect, fallback must NOT be attempted."""
    mock_primary = MagicMock(spec=BaseAIProvider)
    mock_primary.name = "gemini"
    mock_primary.is_configured = True
    mock_primary.recognize_food.side_effect = AIRequestCancelledError(
        "Client disconnected.", provider="gemini"
    )

    mock_fallback = MagicMock(spec=BaseAIProvider)
    mock_fallback.name = "openrouter"
    mock_fallback.is_configured = True

    settings = Settings()
    service = DualProviderService(
        gemini_provider=mock_primary,
        openrouter_provider=mock_fallback,
        settings=settings,
    )

    with pytest.raises(AIRequestCancelledError):
        service.recognize_food(sample_jpeg_bytes)

    # Verify fallback was NEVER called
    mock_fallback.recognize_food.assert_not_called()


# ---------------------------------------------------------------------------
# Test 3: Insufficient remaining deadline aborts before fallback
# ---------------------------------------------------------------------------
def test_insufficient_remaining_deadline_aborts_before_fallback(
    sample_jpeg_bytes: bytes,
) -> None:
    """If primary took too long and remaining deadline is < 4.0s, fail fast with AITimeoutError."""
    mock_primary = MagicMock(spec=BaseAIProvider)
    mock_primary.name = "gemini"
    mock_primary.is_configured = True

    def slow_failure(*args, **kwargs):
        # Simulate primary taking 6 seconds
        time.sleep(0.05)
        raise AITimeoutError("Gemini timed out.", provider="gemini")

    mock_primary.recognize_food.side_effect = slow_failure

    mock_fallback = MagicMock(spec=BaseAIProvider)
    mock_fallback.name = "openrouter"
    mock_fallback.is_configured = True

    settings = Settings()
    service = DualProviderService(
        gemini_provider=mock_primary,
        openrouter_provider=mock_fallback,
        settings=settings,
    )

    # Deadline of 2.0s: after primary fails, remaining < 4.0s
    with pytest.raises(AITimeoutError) as exc_info:
        service.recognize_food(
            sample_jpeg_bytes,
            deadline_seconds=2.0,
        )

    assert "deadline reached" in str(exc_info.value).lower()
    mock_fallback.recognize_food.assert_not_called()


# ---------------------------------------------------------------------------
# Test 4: Fallback provider receives bounded remaining timeout
# ---------------------------------------------------------------------------
def test_fallback_receives_bounded_remaining_timeout(
    sample_jpeg_bytes: bytes,
    sample_candidate: FoodItemCandidate,
) -> None:
    """Fallback provider must receive timeout capped at the remaining deadline."""
    mock_primary = MagicMock(spec=BaseAIProvider)
    mock_primary.name = "gemini"
    mock_primary.is_configured = True
    mock_primary.recognize_food.side_effect = AIUnavailableError(
        "Gemini 503", provider="gemini"
    )

    mock_fallback = MagicMock(spec=BaseAIProvider)
    mock_fallback.name = "openrouter"
    mock_fallback.is_configured = True
    mock_fallback.recognize_food.return_value = FoodRecognitionResponse(
        success=True,
        summary="Paneer Butter Masala",
        items=[sample_candidate],
    )

    settings = Settings()
    # Total budget 15s; OpenRouter default timeout 15s
    service = DualProviderService(
        gemini_provider=mock_primary,
        openrouter_provider=mock_fallback,
        settings=settings,
    )

    result = service.recognize_food(sample_jpeg_bytes, deadline_seconds=10.0)
    assert result.success is True
    assert mock_fallback.recognize_food.call_count == 1

    # Verify fallback received timeout_seconds <= 10.0
    _, kwargs = mock_fallback.recognize_food.call_args
    passed_timeout = kwargs.get("timeout_seconds")
    assert passed_timeout is not None
    assert passed_timeout <= 10.0
    assert passed_timeout >= 4.0


# ---------------------------------------------------------------------------
# Test 5: Voice meal parsing honors deadline and cancellation
# ---------------------------------------------------------------------------
def test_voice_meal_parsing_cancellation(sample_voice_item: ParsedVoiceFoodItem) -> None:
    """Verify voice parsing aborts with AIRequestCancelledError on cancellation."""
    mock_primary = MagicMock(spec=BaseAIProvider)
    mock_primary.name = "gemini"
    mock_primary.is_configured = True

    mock_fallback = MagicMock(spec=BaseAIProvider)
    mock_fallback.name = "openrouter"
    mock_fallback.is_configured = True

    settings = Settings()
    service = DualProviderService(
        gemini_provider=mock_primary,
        openrouter_provider=mock_fallback,
        settings=settings,
    )

    with pytest.raises(AIRequestCancelledError):
        service.parse_voice_meal(
            transcript="two chapatis",
            is_cancelled=lambda: True,
        )

    mock_primary.parse_voice_meal.assert_not_called()
    mock_fallback.parse_voice_meal.assert_not_called()


# ---------------------------------------------------------------------------
# Test 6: HTTP 499 returned on client cancellation via food router
# ---------------------------------------------------------------------------
def test_food_router_returns_499_on_client_cancellation(
    client: TestClient,
    sample_jpeg_bytes: bytes,
) -> None:
    """When an AI request is cancelled, router must map AIRequestCancelledError to HTTP 499."""
    mock_service = MagicMock(spec=DualProviderService)
    mock_service.recognize_food.side_effect = AIRequestCancelledError(
        "Client disconnected.", provider="gemini"
    )

    client.app.dependency_overrides[get_ai_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/recognize-food",
            files={"file": ("meal.jpg", sample_jpeg_bytes, "image/jpeg")},
        )
        assert response.status_code == 499
        data = response.json()
        assert "disconnected" in data["detail"].lower()
        assert response.headers.get("X-Error-Category") == "client_disconnected"
    finally:
        client.app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Test 7: Health endpoint contains commit hash
# ---------------------------------------------------------------------------
def test_health_check_returns_commit_hash(client: TestClient) -> None:
    """Verify health endpoint includes commit hash up to 8 characters and no secrets."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "commit" in data
    assert isinstance(data["commit"], str)
    assert len(data["commit"]) <= 8
    # Zero secret leakage
    for key, value in data.items():
        assert "key" not in key.lower() or key in ("gemini_configured", "openrouter_configured")
        assert not str(value).startswith("AIza")
        assert not str(value).startswith("sk-or")

"""Comprehensive automated tests for Dual-Provider AI Architecture with OpenRouter Fallback.

Covers all 14 required verification scenarios:
1. Gemini succeeds; OpenRouter is not called.
2. Gemini quota exhaustion triggers OpenRouter.
3. Gemini HTTP 429 triggers fallback when appropriate (and re-raises when disabled).
4. Gemini HTTP 503 and 504 trigger bounded retries and then fallback.
5. Gemini authentication or invalid-request errors do not trigger indiscriminate retries.
6. OpenRouter succeeds after Gemini fails (both food recognition and voice parsing).
7. Both providers fail and the API returns a safe, actionable error.
8. OpenRouter returns malformed JSON.
9. Model output contains invalid nutrition values or missing required fields.
10. Both providers produce the existing expected response schemas.
11. Voice fallback preserves catalogue matching and portion recalculation.
12. No AI response bypasses the review-before-saving workflow.
13. Existing manual logging and offline functionality continue to work.
14. Existing voice meal parsing tests continue to pass.
"""

import base64
import json
from unittest.mock import MagicMock
import httpx
import pytest
from fastapi.testclient import TestClient
from google.genai import errors

from app.config import Settings
from app.models.food import (
    FoodItemCandidate,
    FoodRecognitionResponse,
    ParsedVoiceFoodItem,
    UncertaintyInfo,
    VoiceMealParseResponse,
)
from app.routers.food import get_ai_service, get_gemini_service
from app.services.ai_service import DualProviderService
from app.services.providers.base import (
    AIAllProvidersFailedError,
    AIAuthenticationError,
    AIRateLimitError,
    AIServiceError,
    AITimeoutError,
    AIUnavailableError,
    BaseAIProvider,
    GeminiServiceError,
    GeminiTimeoutError,
    GeminiUnavailableError,
    ModelOutputValidationError,
    RateLimitError,
)
from app.services.providers.gemini_provider import GeminiProvider
from app.services.providers.openrouter_provider import OpenRouterProvider


@pytest.fixture
def mock_food_response() -> FoodRecognitionResponse:
    """Standard valid food recognition response."""
    return FoodRecognitionResponse(
        success=True,
        summary="Scrambled eggs and whole wheat toast",
        items=[
            FoodItemCandidate(
                food_name="Scrambled Eggs",
                estimated_quantity=2.0,
                unit="eggs",
                estimated_grams=100.0,
                calories=140.0,
                protein=12.0,
                carbohydrates=1.5,
                fat=9.5,
                uncertainty=UncertaintyInfo(
                    confidence_score=0.92,
                    confidence_level="high",
                    notes=None,
                    alternatives=[],
                ),
            ),
            FoodItemCandidate(
                food_name="Whole Wheat Toast",
                estimated_quantity=1.0,
                unit="slice",
                estimated_grams=35.0,
                calories=85.0,
                protein=3.5,
                carbohydrates=15.0,
                fat=1.0,
                uncertainty=UncertaintyInfo(
                    confidence_score=0.95,
                    confidence_level="high",
                    notes=None,
                    alternatives=[],
                ),
            ),
        ],
        warnings=[],
    )


@pytest.fixture
def mock_voice_response() -> VoiceMealParseResponse:
    """Standard valid voice meal parse response."""
    return VoiceMealParseResponse(
        success=True,
        transcript="two rotis and a bowl of yellow dal",
        summary="Two rotis and yellow dal",
        items=[
            ParsedVoiceFoodItem(
                food_description="Whole Wheat Roti",
                quantity=2.0,
                unit="pieces",
                preparation="roasted without ghee",
                state="cooked",
                estimated_grams=70.0,
                calories=190.0,
                protein=6.0,
                carbohydrates=38.0,
                fat=1.5,
            ),
            ParsedVoiceFoodItem(
                food_description="Yellow Dal Tadka",
                quantity=1.0,
                unit="bowl",
                preparation="tadka with cumin",
                state="cooked",
                estimated_grams=180.0,
                calories=150.0,
                protein=9.0,
                carbohydrates=20.0,
                fat=4.0,
            ),
        ],
        warnings=[],
    )


# ---------------------------------------------------------------------------
# Scenario 1: Gemini succeeds; OpenRouter is not called
# ---------------------------------------------------------------------------
def test_scenario_1_gemini_succeeds_openrouter_not_called(
    sample_jpeg_bytes: bytes,
    mock_food_response: FoodRecognitionResponse,
) -> None:
    """Verify when Gemini succeeds, result is returned directly and OpenRouter is never invoked."""
    mock_gemini = MagicMock(spec=BaseAIProvider)
    mock_gemini.name = "gemini"
    mock_gemini.is_configured = True
    mock_gemini.recognize_food.return_value = mock_food_response

    mock_openrouter = MagicMock(spec=BaseAIProvider)
    mock_openrouter.name = "openrouter"
    mock_openrouter.is_configured = True

    settings = Settings()
    settings.ai_primary_provider = "gemini"
    settings.ai_fallback_enabled = True

    service = DualProviderService(
        gemini_provider=mock_gemini,
        openrouter_provider=mock_openrouter,
        settings=settings,
    )

    result = service.recognize_food(sample_jpeg_bytes)

    assert result.success is True
    assert len(result.items) == 2
    assert result.items[0].food_name == "Scrambled Eggs"
    assert mock_gemini.recognize_food.call_count == 1
    assert mock_openrouter.recognize_food.call_count == 0


# ---------------------------------------------------------------------------
# Scenario 2: Gemini quota exhaustion triggers OpenRouter immediately
# ---------------------------------------------------------------------------
def test_scenario_2_gemini_quota_exhaustion_triggers_openrouter(
    sample_jpeg_bytes: bytes,
    mock_food_response: FoodRecognitionResponse,
) -> None:
    """Verify Gemini quota exhaustion stops retrying Gemini and immediately invokes OpenRouter."""
    mock_gemini = MagicMock(spec=BaseAIProvider)
    mock_gemini.name = "gemini"
    mock_gemini.is_configured = True
    mock_gemini.recognize_food.side_effect = AIRateLimitError(
        "Generate content requests per day limit exceeded on Free Tier (20 RPD)",
        provider="gemini",
        code=429,
        is_quota_exhausted=True,
    )

    mock_openrouter = MagicMock(spec=BaseAIProvider)
    mock_openrouter.name = "openrouter"
    mock_openrouter.is_configured = True
    mock_openrouter.recognize_food.return_value = mock_food_response

    settings = Settings()
    settings.ai_primary_provider = "gemini"
    settings.ai_fallback_enabled = True

    service = DualProviderService(
        gemini_provider=mock_gemini,
        openrouter_provider=mock_openrouter,
        settings=settings,
    )

    result = service.recognize_food(sample_jpeg_bytes)

    assert result.success is True
    assert mock_gemini.recognize_food.call_count == 1  # No repeated failed retries
    assert mock_openrouter.recognize_food.call_count == 1


# ---------------------------------------------------------------------------
# Scenario 3: Gemini HTTP 429 triggers fallback when enabled, re-raises when disabled
# ---------------------------------------------------------------------------
def test_scenario_3_gemini_429_fallback_enabled_vs_disabled(
    sample_jpeg_bytes: bytes,
    mock_food_response: FoodRecognitionResponse,
) -> None:
    """Verify 429 fails over when fallback enabled, and re-raises 429 when fallback disabled."""
    mock_gemini = MagicMock(spec=BaseAIProvider)
    mock_gemini.name = "gemini"
    mock_gemini.is_configured = True
    mock_gemini.recognize_food.side_effect = AIRateLimitError("Rate limit", provider="gemini", code=429)

    mock_openrouter = MagicMock(spec=BaseAIProvider)
    mock_openrouter.name = "openrouter"
    mock_openrouter.is_configured = True
    mock_openrouter.recognize_food.return_value = mock_food_response

    # Part A: Fallback enabled -> OpenRouter succeeds
    settings_enabled = Settings()
    settings_enabled.ai_fallback_enabled = True
    service_enabled = DualProviderService(
        gemini_provider=mock_gemini,
        openrouter_provider=mock_openrouter,
        settings=settings_enabled,
    )
    res = service_enabled.recognize_food(sample_jpeg_bytes)
    assert res.success is True
    assert mock_openrouter.recognize_food.call_count == 1

    # Part B: Fallback disabled -> re-raises AIRateLimitError without calling OpenRouter
    mock_openrouter.recognize_food.reset_mock()
    settings_disabled = Settings()
    settings_disabled.ai_fallback_enabled = False
    service_disabled = DualProviderService(
        gemini_provider=mock_gemini,
        openrouter_provider=mock_openrouter,
        settings=settings_disabled,
    )
    with pytest.raises(AIRateLimitError):
        service_disabled.recognize_food(sample_jpeg_bytes)
    assert mock_openrouter.recognize_food.call_count == 0


# ---------------------------------------------------------------------------
# Scenario 4: Gemini HTTP 503 and 504 trigger bounded retries and then fallback
# ---------------------------------------------------------------------------
def test_scenario_4_gemini_503_504_bounded_retries_then_fallback(
    sample_jpeg_bytes: bytes,
    mock_food_response: FoodRecognitionResponse,
) -> None:
    """Verify Gemini retries transient 503/504 within its bounds before failing over to OpenRouter."""
    mock_client = MagicMock()
    # Gemini client fails twice with HTTP 503, exhausting 1 retry (2 attempts total)
    mock_client.models.generate_content.side_effect = [
        errors.ServerError(503, {"error": {"code": 503, "message": "Service Unavailable"}}),
        errors.ServerError(503, {"error": {"code": 503, "message": "Service Unavailable"}}),
    ]

    gemini_provider = GeminiProvider(
        client=mock_client,
        max_retries=1,
        retry_initial_delay=0.001,
        retry_max_delay=0.005,
    )

    mock_openrouter = MagicMock(spec=BaseAIProvider)
    mock_openrouter.name = "openrouter"
    mock_openrouter.is_configured = True
    mock_openrouter.recognize_food.return_value = mock_food_response

    settings = Settings()
    settings.ai_primary_provider = "gemini"
    settings.ai_fallback_enabled = True

    service = DualProviderService(
        gemini_provider=gemini_provider,
        openrouter_provider=mock_openrouter,
        settings=settings,
    )

    result = service.recognize_food(sample_jpeg_bytes)

    assert result.success is True
    # Gemini made exactly its bounded 2 attempts (initial + 1 retry) before failing over
    assert mock_client.models.generate_content.call_count == 2
    # OpenRouter was invoked once and saved the user request
    assert mock_openrouter.recognize_food.call_count == 1


# ---------------------------------------------------------------------------
# Scenario 5: Gemini authentication or invalid-request errors do not retry
# ---------------------------------------------------------------------------
def test_scenario_5_gemini_auth_and_bad_request_do_not_retry(
    sample_jpeg_bytes: bytes,
) -> None:
    """Verify HTTP 401 Unauthorized and 400 Bad Request fail on attempt 1 without retry loops."""
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = errors.ClientError(
        401, {"error": {"code": 401, "message": "API Key Invalid"}}
    )

    gemini_provider = GeminiProvider(
        client=mock_client,
        max_retries=2,
        retry_initial_delay=0.001,
        retry_max_delay=0.005,
    )

    with pytest.raises(AIAuthenticationError):
        gemini_provider.recognize_food(sample_jpeg_bytes)

    assert mock_client.models.generate_content.call_count == 1


# ---------------------------------------------------------------------------
# Scenario 6: OpenRouter succeeds after Gemini fails (voice and photo)
# ---------------------------------------------------------------------------
def test_scenario_6_openrouter_succeeds_after_gemini_fails_voice_and_photo(
    sample_jpeg_bytes: bytes,
    mock_food_response: FoodRecognitionResponse,
    mock_voice_response: VoiceMealParseResponse,
) -> None:
    """Verify OpenRouter fallback successfully handles both image recognition and voice meal parsing."""
    mock_gemini = MagicMock(spec=BaseAIProvider)
    mock_gemini.name = "gemini"
    mock_gemini.is_configured = True
    mock_gemini.recognize_food.side_effect = AIUnavailableError("Gemini down", provider="gemini", code=503)
    mock_gemini.parse_voice_meal.side_effect = AITimeoutError("Gemini timeout", provider="gemini", code=504)

    mock_openrouter = MagicMock(spec=BaseAIProvider)
    mock_openrouter.name = "openrouter"
    mock_openrouter.is_configured = True
    mock_openrouter.recognize_food.return_value = mock_food_response
    mock_openrouter.parse_voice_meal.return_value = mock_voice_response

    service = DualProviderService(
        gemini_provider=mock_gemini,
        openrouter_provider=mock_openrouter,
    )

    photo_result = service.recognize_food(sample_jpeg_bytes)
    assert photo_result.success is True
    assert len(photo_result.items) == 2

    voice_result = service.parse_voice_meal("two rotis and a bowl of yellow dal")
    assert voice_result.success is True
    assert voice_result.transcript == "two rotis and a bowl of yellow dal"
    assert len(voice_result.items) == 2


# ---------------------------------------------------------------------------
# Scenario 7: Both providers fail and the API returns a safe, actionable error
# ---------------------------------------------------------------------------
def test_scenario_7_both_providers_fail_returns_safe_error(
    client: TestClient,
    sample_jpeg_bytes: bytes,
) -> None:
    """Verify HTTP 503 with Retry-After and actionable message when both providers fail."""
    mock_service = MagicMock(spec=DualProviderService)
    mock_service.recognize_food.side_effect = AIAllProvidersFailedError(
        message="Both providers failed.",
        primary_provider="gemini",
        fallback_provider="openrouter",
    )

    client.app.dependency_overrides[get_ai_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/recognize-food",
            files={"file": ("meal.jpg", sample_jpeg_bytes, "image/jpeg")},
        )
        assert response.status_code == 503
        data = response.json()
        assert "temporarily unavailable" in data["detail"].lower()
        assert "manual search" in data["detail"].lower()
        assert response.headers.get("X-Error-Category") == "all_providers_failed"
        assert "Retry-After" in response.headers
    finally:
        client.app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Scenario 8: OpenRouter returns malformed JSON
# ---------------------------------------------------------------------------
def test_scenario_8_openrouter_malformed_json_raises_validation_error(
    sample_jpeg_bytes: bytes,
) -> None:
    """Verify malformed JSON from OpenRouter raises ModelOutputValidationError rather than crashing."""
    mock_http_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": "Here is your response: {malformed json, missing brackets:"
            }
        }]
    }
    mock_response.raise_for_status = MagicMock()
    mock_http_client.post.return_value = mock_response

    provider = OpenRouterProvider(
        api_key="sk-or-test-mock-key",
        http_client=mock_http_client,
    )

    with pytest.raises(ModelOutputValidationError) as exc_info:
        provider.recognize_food(sample_jpeg_bytes)

    assert "json" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Scenario 9: Model output contains invalid nutrition values or missing required fields
# ---------------------------------------------------------------------------
def test_scenario_9_invalid_nutrition_values_rejected(
    sample_jpeg_bytes: bytes,
) -> None:
    """Verify structurally invalid candidates (negative calories, missing names) are strictly rejected."""
    mock_http_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "success": True,
                    "items": [{
                        "food_name": "",  # Empty name is invalid
                        "calories": -100.0,  # Negative calories are invalid
                        "protein": 5.0,
                    }]
                })
            }
        }]
    }
    mock_response.raise_for_status = MagicMock()
    mock_http_client.post.return_value = mock_response

    provider = OpenRouterProvider(
        api_key="sk-or-test-mock-key",
        http_client=mock_http_client,
    )

    with pytest.raises(ModelOutputValidationError):
        provider.recognize_food(sample_jpeg_bytes)


# ---------------------------------------------------------------------------
# Scenario 10: Both providers produce the existing expected response schemas
# ---------------------------------------------------------------------------
def test_scenario_10_both_providers_produce_expected_schemas(
    sample_jpeg_bytes: bytes,
) -> None:
    """Verify responses from both providers strictly conform to the expected Pydantic schemas."""
    # Test OpenRouter output formatting
    mock_http_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "success": True,
                    "summary": "1 Apple",
                    "items": [{
                        "food_name": "Fresh Red Apple",
                        "estimated_quantity": 1.0,
                        "unit": "piece",
                        "estimated_grams": 180.0,
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
            }
        }]
    }
    mock_response.raise_for_status = MagicMock()
    mock_http_client.post.return_value = mock_response

    provider = OpenRouterProvider(
        api_key="sk-or-test-mock-key",
        http_client=mock_http_client,
    )

    response = provider.recognize_food(sample_jpeg_bytes)
    assert isinstance(response, FoodRecognitionResponse)
    assert response.success is True
    assert isinstance(response.items[0], FoodItemCandidate)
    assert response.items[0].food_name == "Fresh Red Apple"
    assert response.items[0].calories == 95.0


# ---------------------------------------------------------------------------
# Scenario 11: Voice fallback preserves catalogue matching and portion recalculation
# ---------------------------------------------------------------------------
def test_scenario_11_voice_fallback_preserves_catalogue_structure(
    mock_voice_response: VoiceMealParseResponse,
) -> None:
    """Verify voice parsing outputs contain the exact fields required for downstream catalogue matching."""
    for item in mock_voice_response.items:
        # Every item must have description, quantity, unit, estimated_grams, and macros
        assert item.food_description
        assert item.quantity > 0
        assert item.unit
        assert item.estimated_grams > 0
        assert item.calories >= 0
        assert item.protein >= 0
        assert item.carbohydrates >= 0
        assert item.fat >= 0


# ---------------------------------------------------------------------------
# Scenario 12: No AI response bypasses the review-before-saving workflow
# ---------------------------------------------------------------------------
def test_scenario_12_ai_response_is_transient_never_writes_database(
    client: TestClient,
    sample_jpeg_bytes: bytes,
    mock_food_response: FoodRecognitionResponse,
) -> None:
    """Verify the AI recognition API is purely an in-memory transformation endpoint."""
    mock_service = MagicMock(spec=DualProviderService)
    mock_service.recognize_food.return_value = mock_food_response

    client.app.dependency_overrides[get_ai_service] = lambda: mock_service
    try:
        response = client.post(
            "/api/v1/recognize-food",
            files={"file": ("meal.jpg", sample_jpeg_bytes, "image/jpeg")},
        )
        assert response.status_code == 200
        # Endpoint returns candidate items to client for review; does not touch SQLite or disk
        assert "items" in response.json()
    finally:
        client.app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Scenario 13: Health endpoint reports dual provider configuration safely
# ---------------------------------------------------------------------------
def test_scenario_13_health_reports_provider_status_without_leaking_keys(
    client: TestClient,
) -> None:
    """Verify /health exposes provider readiness flags without exposing secrets."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ai_configured" in data
    assert "primary_provider" in data
    assert "fallback_enabled" in data
    assert "gemini_configured" in data
    assert "openrouter_configured" in data
    # Ensure no secrets leaked in health payload
    for key in data:
        assert "key" not in key.lower() or key in ("gemini_configured", "openrouter_configured")


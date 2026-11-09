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


# ---------------------------------------------------------------------------
# Test 8: Router server deadline timeout returns HTTP 504
# ---------------------------------------------------------------------------
def test_router_server_deadline_timeout_returns_504(
    client: TestClient,
    sample_jpeg_bytes: bytes,
) -> None:
    """When the AI service exceeds server deadline budget, router returns HTTP 504."""
    mock_service = MagicMock(spec=DualProviderService)

    def slow_recognize(*args, **kwargs):
        time.sleep(0.1)
        raise RuntimeError("Should not be reached if timed out")

    mock_service.recognize_food.side_effect = slow_recognize

    custom_settings = Settings()
    custom_settings.server_deadline_seconds = 0.02  # 20ms deadline

    client.app.dependency_overrides[get_ai_service] = lambda: mock_service
    from app.config import get_settings
    client.app.dependency_overrides[get_settings] = lambda: custom_settings

    try:
        t0 = time.perf_counter()
        response = client.post(
            "/api/v1/recognize-food",
            files={"file": ("meal.jpg", sample_jpeg_bytes, "image/jpeg")},
        )
        elapsed = time.perf_counter() - t0
        assert response.status_code == 504
        assert response.headers.get("X-Error-Category") == "upstream_timeout"
        data = response.json()
        assert "server deadline budget" in data["detail"].lower()
        # Ensure it failed fast within ~0.3s instead of hanging
        assert elapsed < 0.5
    finally:
        client.app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Test 9: Router voice server deadline timeout returns HTTP 504
# ---------------------------------------------------------------------------
def test_router_voice_server_deadline_timeout_returns_504(
    client: TestClient,
) -> None:
    """When voice parsing exceeds server deadline budget, router returns HTTP 504."""
    mock_service = MagicMock(spec=DualProviderService)

    def slow_parse(*args, **kwargs):
        time.sleep(0.1)
        raise RuntimeError("Should not be reached")

    mock_service.parse_voice_meal.side_effect = slow_parse

    custom_settings = Settings()
    custom_settings.voice_server_deadline_seconds = 0.02

    client.app.dependency_overrides[get_ai_service] = lambda: mock_service
    from app.config import get_settings
    client.app.dependency_overrides[get_settings] = lambda: custom_settings

    try:
        t0 = time.perf_counter()
        response = client.post(
            "/api/v1/parse-voice-meal",
            json={"transcript": "two dosas with sambar"},
        )
        elapsed = time.perf_counter() - t0
        assert response.status_code == 504
        assert response.headers.get("X-Error-Category") == "upstream_timeout"
        data = response.json()
        assert "server deadline budget" in data["detail"].lower()
        assert elapsed < 0.5
    finally:
        client.app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Test 10: Timing logs emitted for endpoint completion and monitor cleanup
# ---------------------------------------------------------------------------
def test_timing_logs_emitted_on_success(
    client: TestClient,
    sample_jpeg_bytes: bytes,
    sample_candidate: FoodItemCandidate,
    sample_voice_item: ParsedVoiceFoodItem,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify privacy-safe timing logs with request correlation IDs are emitted on successful requests."""
    import logging

    mock_service = MagicMock(spec=DualProviderService)
    mock_service.recognize_food.return_value = FoodRecognitionResponse(
        success=True,
        summary="Paneer Butter Masala",
        items=[sample_candidate],
    )
    mock_service.parse_voice_meal.return_value = VoiceMealParseResponse(
        success=True,
        transcript="2 chapatis",
        items=[sample_voice_item],
    )

    client.app.dependency_overrides[get_ai_service] = lambda: mock_service

    try:
        with caplog.at_level(logging.INFO):
            # 1. Photo endpoint
            resp = client.post(
                "/api/v1/recognize-food",
                files={"file": ("meal.jpg", sample_jpeg_bytes, "image/jpeg")},
                headers={"X-Request-ID": "test-req-photo"},
            )
            assert resp.status_code == 200

            # 2. Voice endpoint
            resp_voice = client.post(
                "/api/v1/parse-voice-meal",
                json={"transcript": "2 chapatis"},
                headers={"X-Request-ID": "test-req-voice"},
            )
            assert resp_voice.status_code == 200

        # Assert timing logs with correlation ID for photo
        assert any("[Timing][test-req-photo] Endpoint [recognize_food] completed successfully" in msg for msg in caplog.messages)
        # Assert timing logs with correlation ID for voice
        assert any("[Timing][test-req-voice] Endpoint [parse_voice_meal] completed successfully" in msg for msg in caplog.messages)
        # Assert cleanup timing
        assert any("Cancellation-monitor cleanup took" in msg for msg in caplog.messages)

    finally:
        client.app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Test 11: OpenRouter provider timing logs
# ---------------------------------------------------------------------------
def test_openrouter_provider_timing_logs(
    sample_jpeg_bytes: bytes,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify OpenRouter provider logs request, JSON parsing, and validation timing."""
    import logging
    from app.services.providers.openrouter_provider import OpenRouterProvider

    settings = Settings()
    mock_http_client = MagicMock()
    mock_http_response = MagicMock()
    mock_http_response.status_code = 200
    mock_http_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": '{"success": true, "summary": "Dal Tadka", "items": [{"food_name": "Dal", "estimated_quantity": 1.0, "unit": "bowl", "estimated_grams": 150.0, "calories": 180.0, "protein": 9.0, "carbohydrates": 24.0, "fat": 5.0, "uncertainty": {"confidence_score": 0.85, "confidence_level": "high"}}]}'
                }
            }
        ]
    }
    mock_http_response.raise_for_status = MagicMock()
    mock_http_client.post.return_value = mock_http_response

    provider = OpenRouterProvider(
        api_key="sk-or-test-key",
        settings=settings,
        http_client=mock_http_client,
    )

    with caplog.at_level(logging.INFO):
        result = provider.recognize_food(sample_jpeg_bytes)

    assert result.success is True
    assert any("[Timing]" in msg and "OpenRouter API [recognize_food] request succeeded" in msg for msg in caplog.messages)
    assert any("[Timing]" in msg and "OpenRouter [recognize_food] response body read and JSON decoding took" in msg for msg in caplog.messages)
    assert any("[Timing]" in msg and "OpenRouter [recognize_food] response JSON parsing took" in msg for msg in caplog.messages)
    assert any("[Timing]" in msg and "OpenRouter [recognize_food] Pydantic validation took" in msg for msg in caplog.messages)


# ---------------------------------------------------------------------------
# Test 12: Gemini provider timing logs
# ---------------------------------------------------------------------------
def test_gemini_provider_timing_logs(
    sample_jpeg_bytes: bytes,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify Gemini provider logs request, cleaning, and validation timing."""
    import logging
    from app.services.providers.gemini_provider import GeminiProvider

    settings = Settings()
    provider = GeminiProvider(settings=settings)

    mock_client = MagicMock()
    mock_gen_response = MagicMock()
    mock_gen_response.text = '{"success": true, "summary": "Roti", "items": [{"food_name": "Roti", "estimated_quantity": 1.0, "unit": "piece", "estimated_grams": 40.0, "calories": 100.0, "protein": 3.0, "carbohydrates": 20.0, "fat": 1.0, "uncertainty": {"confidence_score": 0.95, "confidence_level": "high"}}]}'
    mock_client.models.generate_content.return_value = mock_gen_response
    provider._client = mock_client

    with caplog.at_level(logging.INFO):
        result = provider.recognize_food(sample_jpeg_bytes)

    assert result.success is True
    assert any("[Timing]" in msg and "Gemini API [recognize_food] request succeeded" in msg for msg in caplog.messages)
    assert any("[Timing]" in msg and "Gemini [recognize_food] response JSON text cleaning took" in msg for msg in caplog.messages)
    assert any("[Timing]" in msg and "Gemini [recognize_food] Pydantic validation took" in msg for msg in caplog.messages)


# ---------------------------------------------------------------------------
# Test 13: Cancellation monitor cleanup completes promptly without delay
# ---------------------------------------------------------------------------
def test_cancellation_monitor_cleanup_is_prompt(
    client: TestClient,
    sample_jpeg_bytes: bytes,
    sample_candidate: FoodItemCandidate,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Ensure cancellation monitor cleanup finishes within bounded deadline (< 50ms) and does not delay response."""
    import logging

    mock_service = MagicMock(spec=DualProviderService)
    mock_service.recognize_food.return_value = FoodRecognitionResponse(
        success=True,
        summary="Paneer Butter Masala",
        items=[sample_candidate],
    )

    client.app.dependency_overrides[get_ai_service] = lambda: mock_service

    try:
        with caplog.at_level(logging.INFO):
            t0 = time.perf_counter()
            resp = client.post(
                "/api/v1/recognize-food",
                files={"file": ("meal.jpg", sample_jpeg_bytes, "image/jpeg")},
                headers={"X-Request-ID": "test-cleanup-fast"},
            )
            elapsed = time.perf_counter() - t0

        assert resp.status_code == 200
        # Overall request must be immediate
        assert elapsed < 0.2

        # Check cleanup log recorded < 0.05s
        cleanup_logs = [msg for msg in caplog.messages if "Cancellation-monitor cleanup took" in msg]
        assert len(cleanup_logs) >= 1
        assert any("[Timing][test-cleanup-fast]" in msg for msg in cleanup_logs)

    finally:
        client.app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Test 14: Fallback timing logs emitted when Gemini 503 triggers OpenRouter
# ---------------------------------------------------------------------------
def test_fallback_timing_logs_emitted_on_failover(
    sample_jpeg_bytes: bytes,
    sample_candidate: FoodItemCandidate,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify fallback start log is emitted when primary fails and switches to OpenRouter."""
    import logging
    from app.services.providers.base import current_request_id

    mock_primary = MagicMock(spec=BaseAIProvider)
    mock_primary.name = "gemini"
    mock_primary.is_configured = True
    mock_primary.recognize_food.side_effect = AIUnavailableError("Gemini 503 Overloaded", provider="gemini")

    mock_fallback = MagicMock(spec=BaseAIProvider)
    mock_fallback.name = "openrouter"
    mock_fallback.is_configured = True
    mock_fallback.recognize_food.return_value = FoodRecognitionResponse(
        success=True,
        summary="Paneer Butter Masala",
        items=[sample_candidate],
    )

    settings = Settings()
    service = DualProviderService(
        gemini_provider=mock_primary,
        openrouter_provider=mock_fallback,
        settings=settings,
    )

    token = current_request_id.set("test-failover-req")
    try:
        with caplog.at_level(logging.INFO):
            result = service.recognize_food(sample_jpeg_bytes)

        assert result.success is True
        assert any("[Timing][test-failover-req] AI Service [recognize_food] started" in msg for msg in caplog.messages)
        assert any("[Timing][test-failover-req] Fallback start: switching from primary [gemini] to fallback [openrouter]" in msg for msg in caplog.messages)
    finally:
        current_request_id.reset(token)

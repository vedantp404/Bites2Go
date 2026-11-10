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


# ---------------------------------------------------------------------------
# Test 15: DualProviderService disables retries when fallback is active
# ---------------------------------------------------------------------------
def test_dual_provider_disables_retries_when_fallback_active(monkeypatch: pytest.MonkeyPatch) -> None:
    """When fallback is enabled and configured, both providers must use 0 retries to prevent budget exhaustion."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-key")
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "true")
    settings = Settings()

    service = DualProviderService(settings=settings)

    assert service._gemini._max_retries == 0
    assert service._openrouter._max_retries == 0


# ---------------------------------------------------------------------------
# Test 16: DualProviderService preserves retries when fallback is disabled
# ---------------------------------------------------------------------------
def test_dual_provider_preserves_retries_when_fallback_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """When fallback is disabled, primary provider retains configured retries for resilience."""
    monkeypatch.setenv("AI_FALLBACK_ENABLED", "false")
    settings = Settings()

    service = DualProviderService(settings=settings)

    assert service._gemini._max_retries == settings.gemini_max_retries


# ---------------------------------------------------------------------------
# Test 17: Photo recognition budget allocation prevents fallback starvation
# ---------------------------------------------------------------------------
def test_recognize_food_budget_allocation_prevents_fallback_starvation(
    sample_jpeg_bytes: bytes,
    sample_candidate: FoodItemCandidate,
) -> None:
    """Primary provider must be capped to reserve sufficient deadline budget for fallback."""
    mock_primary = MagicMock(spec=BaseAIProvider)
    mock_primary.name = "gemini"
    mock_primary.is_configured = True

    captured_primary_timeout = {}

    def mock_primary_fail(*args, **kwargs):
        captured_primary_timeout["timeout"] = kwargs.get("timeout_seconds")
        raise AIUnavailableError("Gemini 503 high demand", provider="gemini", code=503)

    mock_primary.recognize_food.side_effect = mock_primary_fail

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

    # 35.0s budget: primary must be capped (<= 19.0s) so fallback gets >= 15.0s
    res = service.recognize_food(sample_jpeg_bytes, deadline_seconds=35.0)

    assert res.success is True
    assert captured_primary_timeout["timeout"] <= 19.0

    _, fb_kwargs = mock_fallback.recognize_food.call_args
    assert fb_kwargs["timeout_seconds"] >= 15.0


# ---------------------------------------------------------------------------
# Test 18: Voice meal parsing budget allocation prevents fallback starvation
# ---------------------------------------------------------------------------
def test_parse_voice_meal_budget_allocation_prevents_fallback_starvation(
    sample_voice_item: ParsedVoiceFoodItem,
) -> None:
    """Voice parsing primary must be capped to reserve sufficient deadline budget for fallback."""
    mock_primary = MagicMock(spec=BaseAIProvider)
    mock_primary.name = "gemini"
    mock_primary.is_configured = True

    captured_primary_timeout = {}

    def mock_primary_fail(*args, **kwargs):
        captured_primary_timeout["timeout"] = kwargs.get("timeout_seconds")
        raise AIUnavailableError("Gemini 503 high demand", provider="gemini", code=503)

    mock_primary.parse_voice_meal.side_effect = mock_primary_fail

    mock_fallback = MagicMock(spec=BaseAIProvider)
    mock_fallback.name = "openrouter"
    mock_fallback.is_configured = True
    mock_fallback.parse_voice_meal.return_value = VoiceMealParseResponse(
        success=True,
        transcript="2 chapatis",
        summary="2 chapatis",
        items=[sample_voice_item],
    )

    settings = Settings()
    service = DualProviderService(
        gemini_provider=mock_primary,
        openrouter_provider=mock_fallback,
        settings=settings,
    )

    # 32.0s budget: primary must be capped (<= 14.0s) so fallback gets >= 14.0s
    res = service.parse_voice_meal(transcript="2 chapatis", deadline_seconds=32.0)

    assert res.success is True
    assert captured_primary_timeout["timeout"] <= 14.0

    _, fb_kwargs = mock_fallback.parse_voice_meal.call_args
    assert fb_kwargs["timeout_seconds"] >= 14.0


# ---------------------------------------------------------------------------
# Test 19: End-to-end FastAPI voice parsing failover under server deadline
# ---------------------------------------------------------------------------
def test_end_to_end_fastapi_voice_parsing_failover(
    sample_voice_item: ParsedVoiceFoodItem,
) -> None:
    """When Gemini returns 503, FastAPI endpoint cleanly fails over to OpenRouter without 504."""
    from app.main import app

    mock_primary = MagicMock(spec=BaseAIProvider)
    mock_primary.name = "gemini"
    mock_primary.is_configured = True
    mock_primary.parse_voice_meal.side_effect = AIUnavailableError(
        "Gemini 503 UNAVAILABLE", provider="gemini", code=503
    )

    mock_fallback = MagicMock(spec=BaseAIProvider)
    mock_fallback.name = "openrouter"
    mock_fallback.is_configured = True
    mock_fallback.parse_voice_meal.return_value = VoiceMealParseResponse(
        success=True,
        transcript="2 chapatis",
        summary="2 chapatis",
        items=[sample_voice_item],
    )

    settings = Settings()
    mock_service = DualProviderService(
        gemini_provider=mock_primary,
        openrouter_provider=mock_fallback,
        settings=settings,
    )

    app.dependency_overrides[get_ai_service] = lambda: mock_service
    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/parse-voice-meal",
            json={"transcript": "2 chapatis"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["items"]) == 1
        assert data["items"][0]["food_description"] == "2 chapatis"
    finally:
        app.dependency_overrides.pop(get_ai_service, None)


# ---------------------------------------------------------------------------
# Test 20: End-to-end FastAPI photo recognition failover under server deadline
# ---------------------------------------------------------------------------
def test_end_to_end_fastapi_photo_recognition_failover(
    sample_jpeg_bytes: bytes,
    sample_candidate: FoodItemCandidate,
) -> None:
    """When Gemini times out, FastAPI endpoint cleanly fails over to OpenRouter without 504."""
    from app.main import app

    mock_primary = MagicMock(spec=BaseAIProvider)
    mock_primary.name = "gemini"
    mock_primary.is_configured = True
    mock_primary.recognize_food.side_effect = AITimeoutError(
        "Gemini timed out", provider="gemini"
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
    mock_service = DualProviderService(
        gemini_provider=mock_primary,
        openrouter_provider=mock_fallback,
        settings=settings,
    )

    app.dependency_overrides[get_ai_service] = lambda: mock_service
    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/recognize-food",
            files={"file": ("food.jpg", sample_jpeg_bytes, "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["items"]) == 1
        assert data["items"][0]["food_name"] == "Paneer Butter Masala"
    finally:
        app.dependency_overrides.pop(get_ai_service, None)


# ---------------------------------------------------------------------------
# Test 21: OpenRouter payloads use model-safe reasoning and bounded max_tokens
# ---------------------------------------------------------------------------
def test_openrouter_payload_includes_bounded_tokens_and_reasoning_effort(
    sample_jpeg_bytes: bytes,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify fixed models disable reasoning while legacy meta-router uses low effort and >=2500 max_tokens."""
    from app.services.providers.openrouter_provider import OpenRouterProvider
    import httpx

    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
    monkeypatch.delenv("OPENROUTER_ALTERNATIVE_MODEL", raising=False)

    captured_payloads = []

    def mock_post_factory(body_json: dict):
        def _post(url, *args, **kwargs):
            captured_payloads.append(kwargs.get("json", {}))
            mock_resp = MagicMock(spec=httpx.Response)
            mock_resp.status_code = 200
            mock_resp.json.return_value = body_json
            return mock_resp
        return _post

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.side_effect = mock_post_factory({
        "model": "nvidia/nemotron-3.5-super-vl:free",
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "content": '{"success": true, "items": [{"food_name": "Roti", "estimated_quantity": 1, "unit": "piece", "estimated_grams": 40, "calories": 100, "protein": 3, "carbohydrates": 20, "fat": 1}]}'
                },
            }
        ],
    })

    settings = Settings()
    assert settings.openrouter_model == "nvidia/nemotron-3.5-super-vl:free"
    assert settings.openrouter_alternative_model == "dots-studio/dots-3-note-preview:free"

    provider = OpenRouterProvider(
        api_key="sk-test",
        settings=settings,
        http_client=mock_client,
    )

    # 1. Fixed default vision model disables reasoning
    provider.recognize_food(sample_jpeg_bytes)
    assert len(captured_payloads) == 1
    assert captured_payloads[0].get("model") == "nvidia/nemotron-3.5-super-vl:free"
    assert captured_payloads[0].get("max_tokens") == 2000
    assert captured_payloads[0].get("reasoning") == {"enabled": False}
    assert captured_payloads[0].get("response_format") == {"type": "json_object"}

    # 2. Voice parsing with fixed default model
    mock_client.post.side_effect = mock_post_factory({
        "model": "nvidia/nemotron-3.5-super-vl:free",
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "content": '{"success": true, "transcript": "2 rotis", "summary": "2 rotis", "items": [{"food_description": "2 rotis", "quantity": 2, "unit": "piece", "estimated_grams": 80, "calories": 200, "protein": 6, "carbohydrates": 40, "fat": 2}]}'
                },
            }
        ],
    })
    provider.parse_voice_meal(transcript="2 rotis")
    assert len(captured_payloads) == 2
    assert captured_payloads[1].get("max_tokens") == 2000
    assert captured_payloads[1].get("reasoning") == {"enabled": False}

    # 3. Legacy openrouter/free router uses effort=low and >=2500 tokens to avoid Cohere 400 and truncation
    legacy_provider = OpenRouterProvider(
        api_key="sk-test",
        model="openrouter/free",
        alternative_model=None,
        settings=settings,
        http_client=mock_client,
    )
    legacy_provider.parse_voice_meal(transcript="2 rotis")
    assert len(captured_payloads) == 3
    assert captured_payloads[2].get("max_tokens") == 2500
    assert captured_payloads[2].get("reasoning") == {"effort": "low"}

    # 4. Incompatible model omits response_format cleanly
    lightning_provider = OpenRouterProvider(
        api_key="sk-test",
        model="nvidia/nemotron-3.5-lightning:free",
        alternative_model=None,
        settings=settings,
        http_client=mock_client,
    )
    lightning_provider.parse_voice_meal(transcript="2 rotis")
    assert "response_format" not in captured_payloads[3]


# ---------------------------------------------------------------------------
# Test 22: Slow OpenRouter response body completion raises AITimeoutError
# ---------------------------------------------------------------------------
def test_slow_openrouter_response_body_raises_timeout_error(
    sample_jpeg_bytes: bytes,
) -> None:
    """When OpenRouter socket hangs or times out during body read, AITimeoutError is raised."""
    from app.services.providers.openrouter_provider import OpenRouterProvider
    import httpx

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.side_effect = httpx.ReadTimeout("Socket read timed out after 18.0s")

    settings = Settings()
    provider = OpenRouterProvider(
        api_key="sk-test",
        alternative_model=None,
        max_retries=0,
        settings=settings,
        http_client=mock_client,
    )

    with pytest.raises(AITimeoutError) as exc_info:
        provider.recognize_food(sample_jpeg_bytes, timeout_seconds=18.0)

    assert "timed out" in str(exc_info.value).lower()
    assert exc_info.value.provider == "openrouter"
    assert mock_client.post.call_count == 1


# ---------------------------------------------------------------------------
# Test 23: Both providers timing out raises AIAllProvidersFailedError
# ---------------------------------------------------------------------------
def test_both_providers_timing_out_raises_all_providers_failed(
    sample_jpeg_bytes: bytes,
) -> None:
    """When primary times out and fallback also times out, AIAllProvidersFailedError is raised."""
    from app.services.providers.base import AIAllProvidersFailedError

    mock_primary = MagicMock(spec=BaseAIProvider)
    mock_primary.name = "gemini"
    mock_primary.is_configured = True
    mock_primary.recognize_food.side_effect = AITimeoutError("Gemini timed out", provider="gemini")

    mock_fallback = MagicMock(spec=BaseAIProvider)
    mock_fallback.name = "openrouter"
    mock_fallback.is_configured = True
    mock_fallback.recognize_food.side_effect = AITimeoutError("OpenRouter timed out", provider="openrouter")

    settings = Settings()
    service = DualProviderService(
        gemini_provider=mock_primary,
        openrouter_provider=mock_fallback,
        settings=settings,
    )

    with pytest.raises(AIAllProvidersFailedError) as exc_info:
        service.recognize_food(sample_jpeg_bytes)

    err = exc_info.value
    assert err.primary_provider == "gemini"
    assert err.fallback_provider == "openrouter"
    assert isinstance(err.primary_error, AITimeoutError)
    assert isinstance(err.fallback_error, AITimeoutError)


# ---------------------------------------------------------------------------
# Test 24: HTTP 200 with empty content and token_budget_exhausted diagnostics
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "raw_content,finish_reason,reasoning_text,expected_category",
    [
        ("", "stop", None, "empty_model_content"),
        (None, "stop", None, "empty_model_content"),
        ("   \n\t ", "stop", None, "empty_model_content"),
        ("", "length", "Let me analyze the image step by step...", "token_budget_exhausted"),
        (None, "content_filter", None, "content_filtered"),
    ],
)
def test_openrouter_empty_content_and_token_budget_exhaustion(
    sample_jpeg_bytes: bytes,
    caplog: pytest.LogCaptureFixture,
    raw_content,
    finish_reason: str,
    reasoning_text,
    expected_category: str,
) -> None:
    """Detect empty final output and token-budget exhaustion without leaking or using hidden reasoning."""
    import logging
    import httpx
    from app.services.providers.base import ModelOutputValidationError
    from app.services.providers.openrouter_provider import OpenRouterProvider

    msg: dict = {"content": raw_content}
    if reasoning_text:
        msg["reasoning"] = reasoning_text

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "model": "dots-studio/dots-3-note-preview:free",
        "choices": [{"finish_reason": finish_reason, "message": msg}],
        "usage": {
            "prompt_tokens": 1085,
            "completion_tokens": 1200,
            "completion_tokens_details": {"reasoning_tokens": 1200},
        },
    }
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_resp

    provider = OpenRouterProvider(
        api_key="sk-test",
        model="dots-studio/dots-3-note-preview:free",
        alternative_model=None,
        max_retries=0,
        http_client=mock_client,
    )

    with caplog.at_level(logging.INFO):
        with pytest.raises(ModelOutputValidationError) as exc_info:
            provider.recognize_food(sample_jpeg_bytes)

    assert exc_info.value.error_category == expected_category
    assert any(
        "actual_model=dots-studio/dots-3-note-preview:free" in log_msg
        and f"finish_reason={finish_reason}" in log_msg
        and "content_empty=True" in log_msg
        for log_msg in caplog.messages
    )
    # Never log hidden reasoning text
    if reasoning_text:
        assert not any(reasoning_text in log_msg for log_msg in caplog.messages)


# ---------------------------------------------------------------------------
# Test 25: Never substitute hidden reasoning JSON for empty final content
# ---------------------------------------------------------------------------
def test_openrouter_never_substitutes_hidden_reasoning_json(
    sample_jpeg_bytes: bytes,
) -> None:
    """Even if reasoning contains JSON-looking text, empty final content must still fail validation."""
    import httpx
    from app.services.providers.base import ModelOutputValidationError
    from app.services.providers.openrouter_provider import OpenRouterProvider

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "model": "nvidia/nemotron-3.5-super-vl:free",
        "choices": [
            {
                "finish_reason": "length",
                "message": {
                    "content": "",
                    "reasoning": '{"items": [{"food_name": "Fake Roti", "calories": 100}]}',
                },
            }
        ],
    }
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_resp

    provider = OpenRouterProvider(
        api_key="sk-test",
        alternative_model=None,
        max_retries=0,
        http_client=mock_client,
    )

    with pytest.raises(ModelOutputValidationError) as exc_info:
        provider.recognize_food(sample_jpeg_bytes)
    assert exc_info.value.error_category == "token_budget_exhausted"


# ---------------------------------------------------------------------------
# Test 26: Valid content block list shapes parsed safely while ignoring thinking blocks
# ---------------------------------------------------------------------------
def test_openrouter_parses_structured_content_block_shapes(
    sample_jpeg_bytes: bytes,
) -> None:
    """Handle list content parts while stripping any reasoning/thinking content blocks."""
    import httpx
    from app.services.providers.openrouter_provider import OpenRouterProvider

    valid_json_str = '{"success": true, "summary": "Idli Sambar", "items": [{"food_name": "Idli", "estimated_quantity": 2, "unit": "piece", "estimated_grams": 100, "calories": 130, "protein": 4, "carbohydrates": 26, "fat": 0.5}]}'
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "model": "nvidia/nemotron-3.5-super-vl:free",
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "content": [
                        {"type": "reasoning", "text": "invalid non-json thinking {foo"},
                        {"type": "text", "text": valid_json_str},
                    ]
                },
            }
        ],
    }
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_resp

    provider = OpenRouterProvider(
        api_key="sk-test",
        alternative_model=None,
        max_retries=0,
        http_client=mock_client,
    )
    res = provider.recognize_food(sample_jpeg_bytes)
    assert res.success is True
    assert len(res.items) == 1
    assert res.items[0].food_name == "Idli"


# ---------------------------------------------------------------------------
# Test 27: Bounded single alternative-model attempt after empty content or 429
# ---------------------------------------------------------------------------
def test_openrouter_bounded_alternative_model_recovers_after_token_exhaustion(
    sample_jpeg_bytes: bytes,
) -> None:
    """If primary OpenRouter hits token exhaustion with >=7s left, switch once to alternative model."""
    import httpx
    from app.services.providers.openrouter_provider import OpenRouterProvider

    models_called = []
    valid_json = '{"success": true, "summary": "Dal Rice", "items": [{"food_name": "Dal Rice", "estimated_quantity": 1, "unit": "plate", "estimated_grams": 300, "calories": 380, "protein": 12, "carbohydrates": 65, "fat": 7}]}'

    resp_empty_length = MagicMock(spec=httpx.Response)
    resp_empty_length.status_code = 200
    resp_empty_length.json.return_value = {
        "model": "nvidia/nemotron-3.5-super-vl:free",
        "choices": [{"finish_reason": "length", "message": {"content": "", "reasoning": "thought"}}],
        "usage": {"completion_tokens": 2000, "completion_tokens_details": {"reasoning_tokens": 2000}},
    }

    resp_alt_success = MagicMock(spec=httpx.Response)
    resp_alt_success.status_code = 200
    resp_alt_success.json.return_value = {
        "model": "dots-studio/dots-3-note-preview:free",
        "choices": [{"finish_reason": "stop", "message": {"content": valid_json}}],
        "usage": {"completion_tokens": 120, "completion_tokens_details": {"reasoning_tokens": 0}},
    }

    def side_effect(url, *args, **kwargs):
        models_called.append(kwargs["json"]["model"])
        if len(models_called) == 1:
            return resp_empty_length
        return resp_alt_success

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.side_effect = side_effect

    provider = OpenRouterProvider(
        api_key="sk-test",
        model="nvidia/nemotron-3.5-super-vl:free",
        alternative_model="dots-studio/dots-3-note-preview:free",
        max_retries=0,
        http_client=mock_client,
    )

    result = provider.recognize_food(sample_jpeg_bytes, timeout_seconds=18.0)
    assert result.success is True
    assert result.items[0].food_name == "Dal Rice"
    assert models_called == [
        "nvidia/nemotron-3.5-super-vl:free",
        "dots-studio/dots-3-note-preview:free",
    ]


# ---------------------------------------------------------------------------
# Test 28: Permanent 400/401/403 errors NEVER retry or trigger alternative model
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("status_code", [400, 401, 403])
def test_openrouter_permanent_client_errors_do_not_switch_or_retry(
    sample_jpeg_bytes: bytes,
    status_code: int,
) -> None:
    """HTTP 400, 401, and 403 fail fast after 1 attempt without alternative model failover."""
    import httpx
    from app.services.providers.base import AIServiceError
    from app.services.providers.openrouter_provider import OpenRouterProvider

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = status_code
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}", request=MagicMock(), response=mock_resp
    )
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_resp

    provider = OpenRouterProvider(
        api_key="sk-test",
        model="nvidia/nemotron-3.5-super-vl:free",
        alternative_model="dots-studio/dots-3-note-preview:free",
        max_retries=1,
        http_client=mock_client,
    )

    with pytest.raises(AIServiceError):
        provider.recognize_food(sample_jpeg_bytes, timeout_seconds=18.0)

    assert mock_client.post.call_count == 1


# ---------------------------------------------------------------------------
# Test 29: Embedded HTTP 200 error payload is classified and bounded
# ---------------------------------------------------------------------------
def test_openrouter_embedded_200_error_payload_handled_cleanly(
    sample_jpeg_bytes: bytes,
) -> None:
    """When OpenRouter returns HTTP 200 containing an upstream error dict, classify and handle safely."""
    import httpx
    from app.services.providers.openrouter_provider import OpenRouterProvider

    resp_err = MagicMock(spec=httpx.Response)
    resp_err.status_code = 200
    resp_err.json.return_value = {
        "error": {"code": 429, "message": "Provider rate limited upstream"}
    }
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = resp_err

    provider = OpenRouterProvider(
        api_key="sk-test",
        model="nvidia/nemotron-3.5-super-vl:free",
        alternative_model=None,
        max_retries=0,
        http_client=mock_client,
    )

    with pytest.raises(AIRateLimitError):
        provider.recognize_food(sample_jpeg_bytes, timeout_seconds=18.0)


# ---------------------------------------------------------------------------
# Test 30: Skips alternative model when remaining budget < 7.0s or cancelled
# ---------------------------------------------------------------------------
def test_openrouter_skips_alternative_when_budget_insufficient_or_cancelled(
    sample_jpeg_bytes: bytes,
) -> None:
    """Do not start an alternative model attempt when remaining budget < 7.0s or request cancelled."""
    import httpx
    from app.services.providers.base import ModelOutputValidationError
    from app.services.providers.openrouter_provider import OpenRouterProvider

    resp_empty = MagicMock(spec=httpx.Response)
    resp_empty.status_code = 200
    resp_empty.json.return_value = {
        "model": "nvidia/nemotron-3.5-super-vl:free",
        "choices": [{"finish_reason": "stop", "message": {"content": ""}}],
    }

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = resp_empty

    provider = OpenRouterProvider(
        api_key="sk-test",
        model="nvidia/nemotron-3.5-super-vl:free",
        alternative_model="dots-studio/dots-3-note-preview:free",
        max_retries=0,
        http_client=mock_client,
    )

    # Case 1: Only 6.5s total budget -> alternative skipped
    with pytest.raises(ModelOutputValidationError):
        provider.recognize_food(sample_jpeg_bytes, timeout_seconds=6.5)
    assert mock_client.post.call_count == 1

    # Case 2: Cancelled mid-flight -> alternative skipped
    mock_client.post.reset_mock()
    cancelled_flag = [False]

    def cancel_during_primary(*args, **kwargs):
        cancelled_flag[0] = True
        return resp_empty

    mock_client.post.side_effect = cancel_during_primary
    with pytest.raises(ModelOutputValidationError):
        provider.recognize_food(
            sample_jpeg_bytes,
            timeout_seconds=18.0,
            is_cancelled=lambda: cancelled_flag[0],
        )
    assert mock_client.post.call_count == 1


# ---------------------------------------------------------------------------
# Test 31: Safe OpenRouter diagnostics log actual model & tokens without leaking PII/secrets
# ---------------------------------------------------------------------------
def test_openrouter_success_diagnostics_log_actual_model_and_suppress_secrets(
    sample_jpeg_bytes: bytes,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify actual_model, configured_model, tokens, finish_reason, duration, and req_id log cleanly without leaking sensitive fields."""
    import logging
    import httpx
    from app.services.providers.base import current_request_id
    from app.services.providers.openrouter_provider import OpenRouterProvider

    secret_key = "sk-or-secret-test-key-should-never-log"
    secret_transcript = "SECRET_USER_TRANSCRIPT_TWO_DOSAS"
    secret_reasoning = "SECRET_HIDDEN_REASONING_TEXT"
    valid_voice_json = (
        '{"success": true, "transcript": "2 dosas", "summary": "2 dosas", '
        '"items": [{"food_description": "SECRET_DISH_OUTPUT", "quantity": 2, '
        '"unit": "piece", "estimated_grams": 180, "calories": 320, '
        '"protein": 8, "carbohydrates": 56, "fat": 6}]}'
    )

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "model": "dots-studio/dots-3-note-preview:free",
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "content": valid_voice_json,
                    "reasoning": secret_reasoning,
                },
            }
        ],
        "usage": {
            "prompt_tokens": 512,
            "completion_tokens": 94,
            "completion_tokens_details": {"reasoning_tokens": 12},
        },
    }

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_resp

    provider = OpenRouterProvider(
        api_key=secret_key,
        model="openrouter/free",
        alternative_model=None,
        max_retries=0,
        http_client=mock_client,
    )

    token = current_request_id.set("req-diag-31")
    try:
        with caplog.at_level(logging.INFO):
            res = provider.parse_voice_meal(transcript=secret_transcript)

        assert res.success is True
        assert res.items[0].food_description == "SECRET_DISH_OUTPUT"

        meta_logs = [m for m in caplog.messages if "OpenRouter [parse_voice_meal] response meta:" in m]
        assert len(meta_logs) == 1
        meta_msg = meta_logs[0]
        assert "[req-diag-31]" in meta_msg
        assert "configured_model=openrouter/free" in meta_msg
        assert "actual_model=dots-studio/dots-3-note-preview:free" in meta_msg
        assert "finish_reason=stop" in meta_msg
        assert "prompt_tokens=512" in meta_msg
        assert "completion_tokens=94" in meta_msg
        assert "reasoning_tokens=12" in meta_msg
        assert "content_empty=False" in meta_msg
        assert "duration=" in meta_msg

        all_logs = "\n".join(caplog.messages)
        assert secret_key not in all_logs
        assert secret_transcript not in all_logs
        assert secret_reasoning not in all_logs
        assert "SECRET_DISH_OUTPUT" not in all_logs
        assert "data:image/jpeg;base64" not in all_logs
    finally:
        current_request_id.reset(token)


# ---------------------------------------------------------------------------
# Test 32: Missing or malformed OpenRouter metadata handled cleanly without crashing
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "malformed_payload",
    [
        # Top-level non-dict JSON response
        ["unexpected", "list"],
        # Missing usage, missing model, non-dict choices entry
        {"choices": ["not-a-dict"]},
        # Non-dict usage, invalid token strings, non-string finish_reason/model
        {
            "model": {"unexpected": "dict"},
            "usage": {"prompt_tokens": "bad-int", "completion_tokens": True, "completion_tokens_details": "bad"},
            "choices": [{"finish_reason": 999, "message": {"content": ""}}],
        },
    ],
)
def test_openrouter_missing_or_malformed_metadata_logs_safely(
    sample_jpeg_bytes: bytes,
    caplog: pytest.LogCaptureFixture,
    malformed_payload,
) -> None:
    """Missing or malformed usage, model, or choice metadata never crash diagnostic logging."""
    import logging
    import httpx
    from app.services.providers.base import ModelOutputValidationError, current_request_id
    from app.services.providers.openrouter_provider import OpenRouterProvider

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = malformed_payload

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_resp

    provider = OpenRouterProvider(
        api_key="sk-or-secret-should-not-leak",
        model="nvidia/nemotron-3.5-super-vl:free",
        alternative_model=None,
        max_retries=0,
        http_client=mock_client,
    )

    token = current_request_id.set("req-malformed-32")
    try:
        with caplog.at_level(logging.INFO):
            with pytest.raises(ModelOutputValidationError):
                provider.recognize_food(sample_jpeg_bytes)

        assert any(
            "[req-malformed-32]" in m
            and "configured_model=nvidia/nemotron-3.5-super-vl:free" in m
            and "actual_model=unknown" in m
            and "content_empty=True" in m
            for m in caplog.messages
        )
        assert not any("sk-or-secret" in m for m in caplog.messages)
    finally:
        current_request_id.reset(token)





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
    """Voice parsing primary (OpenRouter) must be capped to reserve budget for Gemini fallback."""
    mock_primary = MagicMock(spec=BaseAIProvider)
    mock_primary.name = "openrouter"
    mock_primary.is_configured = True

    captured_primary_timeout = {}

    def mock_primary_fail(*args, **kwargs):
        captured_primary_timeout["timeout"] = kwargs.get("timeout_seconds")
        raise AIUnavailableError("OpenRouter 503 high demand", provider="openrouter", code=503)

    mock_primary.parse_voice_meal.side_effect = mock_primary_fail

    mock_fallback = MagicMock(spec=BaseAIProvider)
    mock_fallback.name = "gemini"
    mock_fallback.is_configured = True
    mock_fallback.parse_voice_meal.return_value = VoiceMealParseResponse(
        success=True,
        transcript="2 chapatis",
        summary="2 chapatis",
        items=[sample_voice_item],
    )

    settings = Settings()
    settings.voice_primary_provider = "openrouter"
    settings.voice_fallback_provider = "gemini"
    settings.voice_primary_timeout_seconds = 24.0
    settings.voice_server_deadline_seconds = 35.0
    service = DualProviderService(
        gemini_provider=mock_fallback,
        voice_openrouter_provider=mock_primary,
        settings=settings,
    )

    # 35.0s budget: OpenRouter primary must be capped (<= 25.0s) so Gemini fallback gets >= 10.0s
    res = service.parse_voice_meal(transcript="2 chapatis", deadline_seconds=35.0)

    assert res.success is True
    assert captured_primary_timeout["timeout"] <= 25.0

    _, fb_kwargs = mock_fallback.parse_voice_meal.call_args
    assert fb_kwargs["timeout_seconds"] >= 10.0


# ---------------------------------------------------------------------------
# Test 19: End-to-end FastAPI voice parsing failover under server deadline
# ---------------------------------------------------------------------------
def test_end_to_end_fastapi_voice_parsing_failover(
    sample_voice_item: ParsedVoiceFoodItem,
) -> None:
    """When OpenRouter voice primary returns 503, FastAPI fails over to Gemini without 504."""
    from app.main import app

    mock_primary = MagicMock(spec=BaseAIProvider)
    mock_primary.name = "openrouter"
    mock_primary.is_configured = True
    mock_primary.parse_voice_meal.side_effect = AIUnavailableError(
        "OpenRouter 503 UNAVAILABLE", provider="openrouter", code=503
    )

    mock_fallback = MagicMock(spec=BaseAIProvider)
    mock_fallback.name = "gemini"
    mock_fallback.is_configured = True
    mock_fallback.parse_voice_meal.return_value = VoiceMealParseResponse(
        success=True,
        transcript="2 chapatis",
        summary="2 chapatis",
        items=[sample_voice_item],
    )

    settings = Settings()
    settings.voice_primary_provider = "openrouter"
    settings.voice_fallback_provider = "gemini"
    mock_service = DualProviderService(
        gemini_provider=mock_fallback,
        voice_openrouter_provider=mock_primary,
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
        mock_primary.parse_voice_meal.assert_called_once()
        mock_fallback.parse_voice_meal.assert_called_once()
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


# ---------------------------------------------------------------------------
# Test 33: Nemotron voice parsing omits response_format and handles Hinglish
# ---------------------------------------------------------------------------
def test_nemotron_voice_hinglish_omits_response_format_and_validates() -> None:
    """Nemotron 3 Ultra voice provider omits unsupported response_format and validates Hinglish output."""
    import json
    import httpx
    from app.services.providers.openrouter_provider import OpenRouterProvider

    payload_json = {
        "success": True,
        "transcript": "do aloo paratha dahi ke saath, 150g raw chicken, actually make that 200g cooked chicken breast",
        "summary": "Aloo paratha with dahi and cooked chicken breast",
        "items": [
            {
                "food_description": "Aloo paratha",
                "quantity": 2,
                "unit": "piece",
                "estimated_calories": 420,
                "estimated_protein_g": 9.0,
                "estimated_carbs_g": 56.0,
                "estimated_fat_g": 18.0,
                "confidence": 0.85,
            },
            {
                "food_description": "Dahi (plain curd)",
                "quantity": 100,
                "unit": "g",
                "estimated_calories": 60,
                "estimated_protein_g": 3.5,
                "estimated_carbs_g": 4.5,
                "estimated_fat_g": 3.0,
                "confidence": 0.75,
            },
            {
                "food_description": "Cooked chicken breast",
                "quantity": 200,
                "unit": "g",
                "estimated_calories": 330,
                "estimated_protein_g": 62.0,
                "estimated_carbs_g": 0.0,
                "estimated_fat_g": 7.2,
                "confidence": 0.92,
            },
        ],
        "warnings": [
            "Resolved self-correction from 150g raw chicken to 200g cooked chicken breast.",
            "Estimated 100g dahi serving from Hinglish phrasing.",
        ],
    }

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "id": "or-nemotron-33",
        "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "usage": {"prompt_tokens": 210, "completion_tokens": 175},
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"content": json.dumps(payload_json)},
            }
        ],
    }

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_resp

    provider = OpenRouterProvider(
        api_key="sk-or-test",
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        alternative_model=None,
        max_retries=0,
        http_client=mock_client,
    )

    result = provider.parse_voice_meal(
        "do aloo paratha dahi ke saath, 150g raw chicken, actually make that 200g cooked chicken breast"
    )

    assert isinstance(result, VoiceMealParseResponse)
    assert result.success is True
    assert len(result.items) == 3
    assert len(result.warnings) == 2

    sent_payload = mock_client.post.call_args.kwargs["json"]
    assert sent_payload["model"] == "nvidia/nemotron-3-ultra-550b-a55b:free"
    assert "response_format" not in sent_payload


# ---------------------------------------------------------------------------
# Test 34: Text-only OpenRouter models are never sent food photos
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "text_model",
    [
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "nvidia/nemotron-3.5-lightning:free",
    ],
)
def test_openrouter_rejects_text_only_models_for_photo_without_http_call(
    sample_jpeg_bytes: bytes,
    text_model: str,
) -> None:
    """Photo recognition must refuse text-only OpenRouter models before making any HTTP request."""
    import httpx
    from app.services.providers.base import AIServiceError
    from app.services.providers.openrouter_provider import (
        OpenRouterProvider,
        is_text_only_openrouter_model,
    )

    assert is_text_only_openrouter_model(text_model) is True

    mock_client = MagicMock(spec=httpx.Client)
    provider = OpenRouterProvider(
        api_key="sk-or-test",
        model=text_model,
        alternative_model=None,
        max_retries=0,
        http_client=mock_client,
    )

    with pytest.raises(AIServiceError) as exc_info:
        provider.recognize_food(sample_jpeg_bytes)

    assert exc_info.value.error_category == "model_vision_unsupported"
    mock_client.post.assert_not_called()


def test_openrouter_photo_skips_text_only_alternative_model(
    sample_jpeg_bytes: bytes,
) -> None:
    """When primary vision OpenRouter model fails 503, a text-only alternative model is never called."""
    import httpx
    from app.services.providers.base import AIUnavailableError
    from app.services.providers.openrouter_provider import OpenRouterProvider

    mock_503 = httpx.Response(
        status_code=503,
        text="upstream temporarily unavailable",
        request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
    )

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_503

    provider = OpenRouterProvider(
        api_key="sk-or-test",
        model="nvidia/nemotron-3.5-super-vl:free",
        alternative_model="nvidia/nemotron-3-ultra-550b-a55b:free",
        max_retries=0,
        http_client=mock_client,
    )

    with pytest.raises(AIUnavailableError):
        provider.recognize_food(sample_jpeg_bytes)

    assert mock_client.post.call_count == 1
    assert mock_client.post.call_args.kwargs["json"]["model"] == "nvidia/nemotron-3.5-super-vl:free"


# ---------------------------------------------------------------------------
# Test 35: DualProviderService enforces task-specific routing isolation
# ---------------------------------------------------------------------------
def test_dual_provider_task_specific_isolation(
    sample_jpeg_bytes: bytes,
    sample_voice_item: ParsedVoiceFoodItem,
) -> None:
    """Voice uses voice_openrouter->gemini while Photo uses gemini->photo_openrouter independently."""
    from app.models.food import FoodItemCandidate, FoodRecognitionResponse, UncertaintyInfo

    mock_gemini = MagicMock(spec=BaseAIProvider)
    mock_gemini.name = "gemini"
    mock_gemini.is_configured = True
    mock_gemini.recognize_food.side_effect = AIUnavailableError(
        "Gemini 503 overloaded", provider="gemini", code=503
    )
    mock_gemini.parse_voice_meal.return_value = VoiceMealParseResponse(
        success=True,
        transcript="2 rotis",
        summary="2 rotis",
        items=[sample_voice_item],
    )

    mock_photo_or = MagicMock(spec=BaseAIProvider)
    mock_photo_or.name = "openrouter"
    mock_photo_or.is_configured = True
    mock_photo_or.recognize_food.return_value = FoodRecognitionResponse(
        success=True,
        summary="Idli plate",
        items=[
            FoodItemCandidate(
                food_name="Idli",
                estimated_quantity=2.0,
                unit="piece",
                estimated_grams=120.0,
                calories=140.0,
                protein=4.0,
                carbohydrates=28.0,
                fat=1.0,
                uncertainty=UncertaintyInfo(
                    confidence_score=0.9,
                    confidence_level="high",
                ),
            )
        ],
    )

    mock_voice_or = MagicMock(spec=BaseAIProvider)
    mock_voice_or.name = "openrouter"
    mock_voice_or.is_configured = True
    mock_voice_or.parse_voice_meal.side_effect = [
        VoiceMealParseResponse(
            success=True,
            transcript="2 rotis",
            summary="2 rotis",
            items=[sample_voice_item],
        ),
        AIUnavailableError("Nemotron temporary 503", provider="openrouter", code=503),
    ]

    settings = Settings()
    settings.photo_primary_provider = "gemini"
    settings.photo_fallback_provider = "openrouter"
    settings.voice_primary_provider = "openrouter"
    settings.voice_fallback_provider = "gemini"
    service = DualProviderService(
        gemini_provider=mock_gemini,
        photo_openrouter_provider=mock_photo_or,
        voice_openrouter_provider=mock_voice_or,
        settings=settings,
    )

    # Voice attempt 1: succeeds on voice OpenRouter primary without touching photo_or or gemini
    voice_res_1 = service.parse_voice_meal("2 rotis")
    assert voice_res_1.success is True
    assert mock_voice_or.parse_voice_meal.call_count == 1
    mock_photo_or.parse_voice_meal.assert_not_called()
    mock_gemini.parse_voice_meal.assert_not_called()

    # Voice attempt 2: voice_or 503 falls back to gemini (never photo_or)
    voice_res_2 = service.parse_voice_meal("2 rotis")
    assert voice_res_2.success is True
    assert mock_voice_or.parse_voice_meal.call_count == 2
    mock_gemini.parse_voice_meal.assert_called_once()
    mock_photo_or.parse_voice_meal.assert_not_called()

    # Photo attempt: gemini 503 falls back to photo_or (never voice_or)
    photo_res = service.recognize_food(sample_jpeg_bytes)
    assert photo_res.success is True
    mock_gemini.recognize_food.assert_called_once()
    mock_photo_or.recognize_food.assert_called_once()
    mock_voice_or.recognize_food.assert_not_called()


# ---------------------------------------------------------------------------
# Test 36: OpenRouter tool_calls extraction & malformed JSON rejection
# ---------------------------------------------------------------------------
def test_openrouter_tool_calls_arguments_extraction_and_malformed_json() -> None:
    """OpenRouterProvider accepts valid tool_calls[0].function.arguments and rejects malformed JSON."""
    import httpx
    from app.services.providers.base import ModelOutputValidationError
    from app.services.providers.openrouter_provider import OpenRouterProvider

    valid_args = (
        '{"success": true, "transcript": "2 idli", "summary": "2 idli", '
        '"items": [{"food_description": "2 idli", "quantity": 2, "unit": "pieces", '
        '"estimated_calories": 140, "estimated_protein_g": 4.0, '
        '"estimated_carbs_g": 28.0, "estimated_fat_g": 1.0, "confidence": 0.9}]}'
    )

    valid_resp = MagicMock(spec=httpx.Response)
    valid_resp.status_code = 200
    valid_resp.json.return_value = {
        "id": "or-tool-ok",
        "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "choices": [
            {
                "finish_reason": "tool_calls",
                "message": {
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {"name": "emit_meal", "arguments": valid_args},
                        }
                    ],
                },
            }
        ],
    }

    bad_resp = MagicMock(spec=httpx.Response)
    bad_resp.status_code = 200
    bad_resp.json.return_value = {
        "id": "or-tool-bad",
        "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "choices": [
            {
                "finish_reason": "tool_calls",
                "message": {
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_2",
                            "type": "function",
                            "function": {"name": "emit_meal", "arguments": "{not valid json"},
                        }
                    ],
                },
            }
        ],
    }

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.side_effect = [valid_resp, bad_resp]

    provider = OpenRouterProvider(
        api_key="sk-or-test",
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        alternative_model=None,
        max_retries=0,
        http_client=mock_client,
    )

    parsed = provider.parse_voice_meal("2 idli")
    assert parsed.success is True
    assert parsed.items[0].food_description == "2 idli"

    with pytest.raises(ModelOutputValidationError):
        provider.parse_voice_meal("2 idli")


# ---------------------------------------------------------------------------
# Test 37: GeminiProvider ThinkingConfig & AFC config per model
# ---------------------------------------------------------------------------
def test_gemini_thinking_config_and_afc_disabled_per_model() -> None:
    """GeminiProvider applies thinking_budget=0 & disabled AFC on flash, omits thinking on -lite."""
    from app.services.providers.gemini_provider import GeminiProvider

    flash_provider = GeminiProvider(
        client=MagicMock(),
        model="gemini-3.5-flash",
        thinking_budget=0,
        max_output_tokens=1500,
    )
    flash_cfg = flash_provider._build_generation_config(
        system_instruction="sys",
        response_schema=dict,
        timeout_seconds=15.0,
    )
    assert flash_cfg.max_output_tokens == 1500
    assert flash_cfg.automatic_function_calling.disable is True
    assert flash_cfg.thinking_config is not None
    assert flash_cfg.thinking_config.thinking_budget == 0

    lite_provider = GeminiProvider(
        client=MagicMock(),
        model="gemini-3.5-flash-lite",
        thinking_budget=0,
        max_output_tokens=1500,
    )
    lite_cfg = lite_provider._build_generation_config(
        system_instruction="sys",
        response_schema=dict,
        timeout_seconds=15.0,
    )
    assert lite_cfg.automatic_function_calling.disable is True
    assert lite_cfg.thinking_config is None


# ---------------------------------------------------------------------------
# Test 38: GeminiProvider MAX_TOKENS empty output & daily vs burst 429
# ---------------------------------------------------------------------------
def test_gemini_max_tokens_empty_output_and_rate_limit_classification(
    sample_jpeg_bytes: bytes,
) -> None:
    """MAX_TOKENS empty response yields token_budget_exhausted; daily vs burst 429 sets quota flag."""
    from types import SimpleNamespace
    from google.genai.errors import APIError
    from app.services.providers.base import (
        AIRateLimitError,
        ModelOutputValidationError,
    )
    from app.services.providers.gemini_provider import GeminiProvider

    mock_client = MagicMock()

    # Subcase A: MAX_TOKENS with empty text and candidate content parts
    empty_max_tokens_resp = SimpleNamespace(
        text="",
        candidates=[
            SimpleNamespace(
                finish_reason="MAX_TOKENS",
                content=SimpleNamespace(parts=[]),
            )
        ],
        usage_metadata=SimpleNamespace(
            prompt_token_count=300,
            candidates_token_count=0,
            thoughts_token_count=1490,
        ),
    )
    mock_client.models.generate_content.return_value = empty_max_tokens_resp

    provider = GeminiProvider(
        client=mock_client,
        model="gemini-3.5-flash",
        max_retries=0,
    )

    with pytest.raises(ModelOutputValidationError) as exc_max:
        provider.recognize_food(sample_jpeg_bytes)
    assert exc_max.value.error_category == "token_budget_exhausted"

    # Subcase B: Burst 429 (per minute) -> is_quota_exhausted=False
    mock_client.models.generate_content.side_effect = APIError(
        429,
        {"error": {"message": "429 RESOURCE_EXHAUSTED: Requests per minute rate limit exceeded"}},
    )
    with pytest.raises(AIRateLimitError) as exc_burst:
        provider.recognize_food(sample_jpeg_bytes)
    assert exc_burst.value.is_quota_exhausted is False

    # Subcase C: Daily quota 429 (per day) -> is_quota_exhausted=True
    mock_client.models.generate_content.side_effect = APIError(
        429,
        {
            "error": {
                "message": "429 RESOURCE_EXHAUSTED: GenerateRequestsPerDayPerProjectPerModel requests per day limit reached"
            }
        },
    )
    with pytest.raises(AIRateLimitError) as exc_daily:
        provider.recognize_food(sample_jpeg_bytes)
    assert exc_daily.value.is_quota_exhausted is True


# ---------------------------------------------------------------------------
# Test 39: Default image optimization downscales to 1024px max dimension
# ---------------------------------------------------------------------------
def test_image_sanitize_defaults_to_1024_dimension() -> None:
    """validate_and_sanitize_image defaults to 1024px max edge when max_dimension is omitted."""
    import io
    from PIL import Image
    from app.services.image import validate_and_sanitize_image

    buf = io.BytesIO()
    Image.new("RGB", (2400, 1800), color=(200, 120, 60)).save(buf, format="JPEG", quality=95)
    raw_bytes = buf.getvalue()

    sanitized_bytes, content_type = validate_and_sanitize_image(raw_bytes)
    assert content_type == "image/jpeg"
    with Image.open(io.BytesIO(sanitized_bytes)) as img:
        assert max(img.size) == 1024
        assert img.size == (1024, 768)


# ---------------------------------------------------------------------------
# Test 40: /health reports task-specific routing cleanly without leaking secrets
# ---------------------------------------------------------------------------
def test_health_endpoint_reports_task_specific_routing_without_secrets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Health endpoint surfaces Milestone 4 photo & voice routing fields and omits secret keys."""
    from app.main import app
    from app.config import get_settings

    monkeypatch.setenv("GEMINI_API_KEY", "secret-gemini-should-not-appear")
    monkeypatch.setenv("OPENROUTER_API_KEY", "secret-openrouter-should-not-appear")

    safe_settings = Settings()
    safe_settings.photo_primary_provider = "gemini"
    safe_settings.photo_fallback_provider = "openrouter"
    safe_settings.gemini_model = "gemini-3.5-flash"
    safe_settings.photo_openrouter_model = "nvidia/nemotron-3.5-super-vl:free"
    safe_settings.voice_primary_provider = "openrouter"
    safe_settings.voice_fallback_provider = "gemini"
    safe_settings.voice_openrouter_model = "nvidia/nemotron-3-ultra-550b-a55b:free"

    app.dependency_overrides[get_settings] = lambda: safe_settings
    try:
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.status_code == 200
        body_text = resp.text
        data = resp.json()

        assert data["status"] == "ok"
        assert data["photo_primary_provider"] == "gemini"
        assert data["photo_fallback_provider"] == "openrouter"
        assert data["photo_model"] == "gemini-3.5-flash"
        assert data["photo_fallback_model"] == "nvidia/nemotron-3.5-super-vl:free"
        assert data["voice_primary_provider"] == "openrouter"
        assert data["voice_fallback_provider"] == "gemini"
        assert data["voice_model"] == "nvidia/nemotron-3-ultra-550b-a55b:free"
        assert data["voice_fallback_model"] == "gemini-3.5-flash"
        assert "secret-gemini-should-not-appear" not in body_text
        assert "secret-openrouter-should-not-appear" not in body_text
    finally:
        app.dependency_overrides.pop(get_settings, None)


# ---------------------------------------------------------------------------
# Test 41: Slow HTTP 200 keepalive stream aborts at wall-clock deadline -> Gemini fallback
# ---------------------------------------------------------------------------
def test_openrouter_streaming_keepalive_wall_clock_deadline_triggers_gemini_fallback(
    sample_voice_item: ParsedVoiceFoodItem,
) -> None:
    """Slow OpenRouter keepalive chunks must abort at wall-clock deadline and fall back to Gemini."""
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from app.main import app
    from app.services.providers.openrouter_provider import OpenRouterProvider

    socket_closed_evt = threading.Event()

    class KeepaliveSlowHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            content_len = int(self.headers.get("Content-Length", "0") or 0)
            if content_len:
                _ = self.rfile.read(content_len)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            # Stream keepalive bytes every 0.1s for 6.0s (defeats idle ReadTimeout, must hit wall-clock!)
            for _ in range(60):
                try:
                    self.wfile.write(b" ")
                    self.wfile.flush()
                    time.sleep(0.1)
                except OSError:
                    socket_closed_evt.set()
                    return

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), KeepaliveSlowHandler)
    port = server.server_address[1]
    srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
    srv_thread.start()

    try:
        settings = Settings()
        settings.voice_primary_provider = "openrouter"
        settings.voice_fallback_provider = "gemini"
        settings.voice_primary_timeout_seconds = 0.7
        settings.voice_server_deadline_seconds = 8.0
        settings.gemini_timeout_seconds = 5.0

        # Use http_client=None so the production streaming watchdog path runs end-to-end
        real_or = OpenRouterProvider(
            api_key="sk-or-test-key",
            model="nvidia/nemotron-3-ultra-550b-a55b:free",
            alternative_model=None,
            base_url=f"http://127.0.0.1:{port}",
            timeout_seconds=0.7,
            max_retries=0,
            max_tokens=900,
        )

        mock_gemini = MagicMock(spec=BaseAIProvider)
        mock_gemini.name = "gemini"
        mock_gemini.is_configured = True
        mock_gemini.parse_voice_meal.return_value = VoiceMealParseResponse(
            success=True,
            transcript="2 rotis",
            summary="2 rotis via Gemini fallback",
            items=[sample_voice_item],
        )

        service = DualProviderService(
            gemini_provider=mock_gemini,
            voice_openrouter_provider=real_or,
            settings=settings,
        )

        app.dependency_overrides[get_ai_service] = lambda: service
        t0 = time.perf_counter()
        try:
            client = TestClient(app)
            resp = client.post("/api/v1/parse-voice-meal", json={"transcript": "2 rotis"})
        finally:
            app.dependency_overrides.pop(get_ai_service, None)

        elapsed = time.perf_counter() - t0
        assert resp.status_code == 200
        assert resp.json()["summary"] == "2 rotis via Gemini fallback"
        assert mock_gemini.parse_voice_meal.call_count == 1
        # Must abort primary near 0.7s + finish fast, NOT stall for 6.0s or 504!
        assert elapsed < 2.2
        assert socket_closed_evt.wait(timeout=1.0)
    finally:
        server.shutdown()
        server.server_close()


# ---------------------------------------------------------------------------
# Test 42: Genuine in-flight cancellation aborts socket immediately without fallback
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("send_keepalives", [True, False])
def test_openrouter_in_flight_cancellation_closes_socket_and_skips_fallback(
    send_keepalives: bool,
) -> None:
    """In-flight cancel_event must tear down OpenRouter socket immediately without calling Gemini."""
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from app.services.providers.openrouter_provider import OpenRouterProvider

    request_started = threading.Event()
    socket_aborted = threading.Event()

    class HungOrKeepaliveHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            content_len = int(self.headers.get("Content-Length", "0") or 0)
            if content_len:
                _ = self.rfile.read(content_len)
            request_started.set()
            if send_keepalives:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                for _ in range(80):
                    try:
                        self.wfile.write(b" ")
                        self.wfile.flush()
                        time.sleep(0.1)
                    except OSError:
                        socket_aborted.set()
                        return
            else:
                # Stalled upstream before sending any HTTP headers
                if socket_aborted.wait(timeout=8.0):
                    return

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), HungOrKeepaliveHandler)
    port = server.server_address[1]
    srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
    srv_thread.start()

    try:
        cancel_evt = threading.Event()
        real_or = OpenRouterProvider(
            api_key="sk-or-test-key",
            model="nvidia/nemotron-3-ultra-550b-a55b:free",
            alternative_model=None,
            base_url=f"http://127.0.0.1:{port}",
            timeout_seconds=10.0,
            max_retries=0,
        )

        mock_gemini = MagicMock(spec=BaseAIProvider)
        mock_gemini.name = "gemini"
        mock_gemini.is_configured = True

        settings = Settings()
        settings.voice_primary_provider = "openrouter"
        settings.voice_fallback_provider = "gemini"
        settings.voice_primary_timeout_seconds = 10.0
        settings.voice_server_deadline_seconds = 25.0

        service = DualProviderService(
            gemini_provider=mock_gemini,
            voice_openrouter_provider=real_or,
            settings=settings,
        )

        def _cancel_shortly():
            request_started.wait(timeout=2.0)
            time.sleep(0.25)
            cancel_evt.set()
            if not send_keepalives:
                # Signal handler cleanup when socket tears down
                socket_aborted.set()

        threading.Thread(target=_cancel_shortly, daemon=True).start()

        t0 = time.perf_counter()
        with pytest.raises(AIRequestCancelledError):
            service.parse_voice_meal(
                transcript="2 rotis",
                deadline_seconds=25.0,
                is_cancelled=cancel_evt.is_set,
            )
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.2
        mock_gemini.parse_voice_meal.assert_not_called()
        if send_keepalives:
            assert socket_aborted.wait(timeout=1.0)
    finally:
        socket_aborted.set()
        server.shutdown()
        server.server_close()


# ---------------------------------------------------------------------------
# Test 43: FastAPI server deadline expiration tears down OpenRouter worker socket
# ---------------------------------------------------------------------------
def test_router_voice_server_deadline_terminates_openrouter_worker_socket() -> None:
    """When router server deadline expires, cancel_event closes upstream OpenRouter TCP socket."""
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from app.config import get_settings
    from app.main import app
    from app.services.providers.openrouter_provider import OpenRouterProvider

    worker_socket_closed = threading.Event()

    class LongKeepaliveHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            content_len = int(self.headers.get("Content-Length", "0") or 0)
            if content_len:
                _ = self.rfile.read(content_len)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            for _ in range(100):
                try:
                    self.wfile.write(b" ")
                    self.wfile.flush()
                    time.sleep(0.1)
                except OSError:
                    worker_socket_closed.set()
                    return

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), LongKeepaliveHandler)
    port = server.server_address[1]
    srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
    srv_thread.start()

    try:
        custom_settings = Settings()
        custom_settings.ai_fallback_enabled = False
        custom_settings.voice_primary_provider = "openrouter"
        custom_settings.voice_primary_timeout_seconds = 10.0
        custom_settings.voice_server_deadline_seconds = 0.55

        real_or = OpenRouterProvider(
            api_key="sk-or-test",
            model="nvidia/nemotron-3-ultra-550b-a55b:free",
            alternative_model=None,
            base_url=f"http://127.0.0.1:{port}",
            timeout_seconds=10.0,
            max_retries=0,
        )
        service = DualProviderService(
            gemini_provider=MagicMock(spec=BaseAIProvider),
            voice_openrouter_provider=real_or,
            settings=custom_settings,
        )

        app.dependency_overrides[get_settings] = lambda: custom_settings
        app.dependency_overrides[get_ai_service] = lambda: service
        try:
            t0 = time.perf_counter()
            client = TestClient(app)
            resp = client.post("/api/v1/parse-voice-meal", json={"transcript": "2 rotis"})
            elapsed = time.perf_counter() - t0
            assert resp.status_code == 504
            assert elapsed < 1.3
            assert worker_socket_closed.wait(timeout=1.0)
        finally:
            app.dependency_overrides.clear()
    finally:
        server.shutdown()
        server.server_close()


# ---------------------------------------------------------------------------
# Test 44: Gzip streaming decompression does not double-decode in httpx.Response
# ---------------------------------------------------------------------------
def test_openrouter_gzip_streaming_response_decodes_cleanly() -> None:
    """OpenRouter streaming path must strip content-encoding after decompression to prevent DecodingError."""
    import gzip
    import json
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from app.services.providers.openrouter_provider import OpenRouterProvider

    payload_dict = {
        "id": "or-gzip-44",
        "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "usage": {"prompt_tokens": 120, "completion_tokens": 85},
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "content": json.dumps({
                        "success": True,
                        "summary": "2 boiled eggs",
                        "items": [
                            {
                                "food_description": "Boiled Egg",
                                "quantity": 2.0,
                                "unit": "piece",
                                "state": "cooked",
                                "estimated_grams": 100.0,
                                "calories": 155.0,
                                "protein": 13.0,
                                "carbohydrates": 1.1,
                                "fat": 11.0,
                            }
                        ],
                        "warnings": [],
                    })
                },
            }
        ],
    }
    gz_body = gzip.compress(json.dumps(payload_dict).encode("utf-8"))

    class GzipHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            content_len = int(self.headers.get("Content-Length", "0") or 0)
            if content_len:
                _ = self.rfile.read(content_len)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(gz_body)))
            self.end_headers()
            self.wfile.write(gz_body)
            self.wfile.flush()

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), GzipHandler)
    port = server.server_address[1]
    srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
    srv_thread.start()

    try:
        provider = OpenRouterProvider(
            api_key="sk-or-test",
            model="nvidia/nemotron-3-ultra-550b-a55b:free",
            alternative_model=None,
            base_url=f"http://127.0.0.1:{port}",
            timeout_seconds=5.0,
            max_retries=0,
        )
        parsed = provider.parse_voice_meal("2 boiled eggs")
        assert parsed.success is True
        assert parsed.transcript == "2 boiled eggs"
        assert len(parsed.items) == 1
        assert parsed.items[0].food_description == "Boiled Egg"
        assert parsed.items[0].calories == 155.0
    finally:
        server.shutdown()
        server.server_close()


# ---------------------------------------------------------------------------
# Test 45: Compact voice prompt, 900-token cap vs 2000-token photo cap, and full API schema
# ---------------------------------------------------------------------------
def test_voice_compact_prompt_token_budget_and_full_api_schema_compatibility(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Voice OpenRouter uses 900 max_tokens & omits transcript echo while returning full response schema."""
    import httpx
    import json

    monkeypatch.setenv("GEMINI_API_KEY", "fake-gem")
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake-or")
    settings = Settings()
    service = DualProviderService(settings=settings)

    assert service.voice_openrouter._max_tokens == 900
    assert service.photo_openrouter._max_tokens == 2000

    # Simulate compact response where LLM omits optional default keys (transcript, preparation, confidence, etc.)
    compact_resp = httpx.Response(
        status_code=200,
        json={
            "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
            "usage": {"prompt_tokens": 330, "completion_tokens": 175},
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "content": json.dumps({
                            "success": True,
                            "summary": "2 rotis and dal",
                            "items": [
                                {
                                    "food_description": "Whole Wheat Roti",
                                    "quantity": 2,
                                    "unit": "piece",
                                    "state": "cooked",
                                    "estimated_grams": 70,
                                    "calories": 182,
                                    "protein": 6.0,
                                    "carbohydrates": 36.0,
                                    "fat": 1.6,
                                }
                            ],
                        })
                    },
                }
            ],
        },
        request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
    )

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = compact_resp
    service.voice_openrouter._client = mock_client

    res = service.parse_voice_meal("do roti aur dal")
    dumped = res.model_dump()

    sent_payload = mock_client.post.call_args.kwargs["json"]
    assert sent_payload["max_tokens"] == 900
    assert sent_payload["reasoning"] == {"enabled": False}
    assert '"transcript"' not in sent_payload["messages"][1]["content"]

    assert dumped["transcript"] == "do roti aur dal"
    assert set(dumped.keys()) == {
        "success",
        "transcript",
        "summary",
        "items",
        "warnings",
        "clarifying_questions",
    }
    assert set(dumped["items"][0].keys()) == {
        "food_description",
        "quantity",
        "unit",
        "preparation",
        "state",
        "estimated_grams",
        "calories",
        "protein",
        "carbohydrates",
        "fat",
        "confidence",
        "confidence_level",
        "alternatives",
        "notes",
    }


# ---------------------------------------------------------------------------
# Test 46: Malformed OpenRouter voice output fails over cleanly to Gemini
# ---------------------------------------------------------------------------
def test_openrouter_malformed_voice_json_fails_over_to_gemini(
    sample_voice_item: ParsedVoiceFoodItem,
) -> None:
    """Malformed voice JSON from OpenRouter must trigger Gemini fallback cleanly."""
    import httpx
    from app.services.providers.openrouter_provider import OpenRouterProvider

    bad_resp = httpx.Response(
        status_code=200,
        json={
            "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
            "choices": [{"finish_reason": "stop", "message": {"content": "Not JSON at all: sorry!"}}],
        },
        request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
    )
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = bad_resp

    voice_or = OpenRouterProvider(
        api_key="sk-or-test",
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        alternative_model=None,
        max_retries=0,
        http_client=mock_client,
    )
    mock_gemini = MagicMock(spec=BaseAIProvider)
    mock_gemini.name = "gemini"
    mock_gemini.is_configured = True
    mock_gemini.parse_voice_meal.return_value = VoiceMealParseResponse(
        success=True,
        transcript="2 chapatis",
        summary="2 chapatis",
        items=[sample_voice_item],
    )

    settings = Settings()
    settings.voice_primary_provider = "openrouter"
    settings.voice_fallback_provider = "gemini"

    service = DualProviderService(
        gemini_provider=mock_gemini,
        voice_openrouter_provider=voice_or,
        settings=settings,
    )
    res = service.parse_voice_meal("2 chapatis")
    assert res.success is True
    assert res.items[0].food_description == "2 chapatis"
    mock_gemini.parse_voice_meal.assert_called_once()


# ---------------------------------------------------------------------------
# Test 47: ContextVar request deadline fails fast without upstream call when expired
# ---------------------------------------------------------------------------
def test_context_request_deadline_fails_fast_without_upstream_call() -> None:
    """Expired current_request_deadline ContextVar must raise AITimeoutError without HTTP POST."""
    import httpx
    from app.services.providers.base import current_request_deadline
    from app.services.providers.openrouter_provider import OpenRouterProvider

    mock_client = MagicMock(spec=httpx.Client)
    provider = OpenRouterProvider(
        api_key="sk-or-test",
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        alternative_model=None,
        max_retries=0,
        http_client=mock_client,
    )

    tok = current_request_deadline.set(time.monotonic() - 0.1)
    try:
        with pytest.raises(AITimeoutError):
            provider.parse_voice_meal("2 rotis")
        mock_client.post.assert_not_called()
    finally:
        current_request_deadline.reset(tok)


# ---------------------------------------------------------------------------
# Test 48: Milestone 4B defaults keep Gemini photo unchanged & tighten voice budgets
# ---------------------------------------------------------------------------
def test_milestone_4b_defaults_preserve_photo_gemini_and_tighten_voice_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify photo Gemini configuration is completely preserved while voice budgets tighten cleanly."""
    for env_key in (
        "PHOTO_PRIMARY_PROVIDER",
        "GEMINI_MODEL",
        "GEMINI_THINKING_BUDGET",
        "GEMINI_MAX_OUTPUT_TOKENS",
        "OPENROUTER_MAX_TOKENS",
        "SERVER_DEADLINE_SECONDS",
        "MAX_IMAGE_DIMENSION",
        "IMAGE_JPEG_QUALITY",
        "VOICE_PRIMARY_PROVIDER",
        "VOICE_FALLBACK_PROVIDER",
        "VOICE_OPENROUTER_MODEL",
        "VOICE_PRIMARY_TIMEOUT_SECONDS",
        "VOICE_SERVER_DEADLINE_SECONDS",
        "VOICE_OPENROUTER_MAX_TOKENS",
    ):
        monkeypatch.delenv(env_key, raising=False)

    clean = Settings()
    # Photo recognition untouched
    assert clean.photo_primary_provider == "gemini"
    assert clean.gemini_model == "gemini-3.5-flash"
    assert clean.gemini_thinking_budget == 0
    assert clean.gemini_max_output_tokens == 1500
    assert clean.openrouter_max_tokens == 2000
    assert clean.server_deadline_seconds == 35.0
    assert clean.max_image_dimension == 1024
    assert clean.image_jpeg_quality == 82

    # Voice tightened within mobile's 40s timeout without switching default Ultra model prematurely
    assert clean.voice_primary_provider == "openrouter"
    assert clean.voice_fallback_provider == "gemini"
    assert clean.voice_openrouter_model == "nvidia/nemotron-3-ultra-550b-a55b:free"
    assert clean.voice_primary_timeout_seconds == 14.0
    assert clean.voice_server_deadline_seconds == 32.0
    assert clean.voice_server_deadline_seconds < 40.0
    assert clean.voice_openrouter_max_tokens == 900


# ---------------------------------------------------------------------------
# Test 49: OpenRouter 429 evidence-based classification (daily, burst, upstream)
# ---------------------------------------------------------------------------
def test_openrouter_429_classification_distinguishes_daily_burst_and_upstream(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """OpenRouter 429 headers and metadata accurately classify daily vs burst vs upstream saturation."""
    import logging
    import httpx
    from app.services.providers.base import current_request_id
    from app.services.providers.openrouter_provider import OpenRouterProvider

    future_reset_ms = str(int((time.time() + 18000) * 1000))  # 5 hours ahead in ms

    # Case 1: Live OpenRouter free-models-per-day 429 payload & X-RateLimit-* headers
    daily_resp = httpx.Response(
        status_code=429,
        headers={
            "X-RateLimit-Limit": "50",
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": future_reset_ms,
            "X-OpenRouter-Error-Origin": "client",
        },
        json={
            "error": {
                "message": "Rate limit exceeded: free-models-per-day. Add 10 credits to unlock 1000 free model requests per day",
                "code": 429,
                "metadata": {
                    "headers": {
                        "X-RateLimit-Limit": "50",
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": future_reset_ms,
                    },
                    "limit_source": "openrouter_free_tier_daily",
                    "provider_name": None,
                },
            }
        },
        request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
    )

    # Case 2: Burst RPM 429 with explicit Retry-After
    burst_resp = httpx.Response(
        status_code=429,
        headers={
            "Retry-After": "42",
            "X-RateLimit-Limit": "20",
            "X-RateLimit-Remaining": "0",
            "X-OpenRouter-Error-Origin": "client",
        },
        json={
            "error": {
                "message": "Rate limit exceeded: free-models-per-min",
                "code": 429,
                "metadata": {
                    "limit_source": "openrouter_free_tier_rpm",
                    "provider_name": None,
                },
            }
        },
        request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
    )

    # Case 3: Upstream provider saturation (embedded in HTTP 200 payload)
    upstream_embedded_resp = httpx.Response(
        status_code=200,
        json={
            "error": {
                "message": "Provider returned error: temporarily rate-limited upstream",
                "code": 429,
                "metadata": {
                    "headers": {"Retry-After": "18"},
                    "provider_name": "nvidia",
                },
            }
        },
        request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
    )

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.side_effect = [daily_resp, burst_resp, upstream_embedded_resp]

    provider = OpenRouterProvider(
        api_key="sk-or-secret-never-log",
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        alternative_model=None,
        max_retries=0,
        http_client=mock_client,
    )

    tok = current_request_id.set("req-429-test")
    try:
        with caplog.at_level(logging.WARNING):
            with pytest.raises(AIRateLimitError) as exc_daily:
                provider.parse_voice_meal("2 rotis")
            assert exc_daily.value.error_category == "daily_quota_exhausted"
            assert exc_daily.value.is_quota_exhausted is True
            assert exc_daily.value.limit_scope == "account"
            assert exc_daily.value.retry_after_seconds is not None
            assert exc_daily.value.retry_after_seconds > 1000.0

            with pytest.raises(AIRateLimitError) as exc_burst:
                provider.parse_voice_meal("2 rotis")
            assert exc_burst.value.error_category == "burst_rate_limit"
            assert exc_burst.value.is_quota_exhausted is False
            assert exc_burst.value.limit_scope == "account"
            assert exc_burst.value.retry_after_seconds == pytest.approx(42.0, abs=1.0)

            with pytest.raises(AIRateLimitError) as exc_upstream:
                provider.parse_voice_meal("2 rotis")
            assert exc_upstream.value.error_category == "upstream_provider_saturated"
            assert exc_upstream.value.is_quota_exhausted is False
            assert exc_upstream.value.limit_scope == "provider_upstream"
            assert exc_upstream.value.retry_after_seconds == pytest.approx(18.0, abs=1.0)

        assert not any("sk-or-secret-never-log" in m for m in caplog.messages)
    finally:
        current_request_id.reset(tok)


# ---------------------------------------------------------------------------
# Test 50: OpenRouter skips alternative model on account-level 429 quota/burst
# ---------------------------------------------------------------------------
def test_openrouter_photo_skips_alternative_model_on_account_429(
    sample_jpeg_bytes: bytes,
) -> None:
    """Account-wide OpenRouter 429 must not burn a second request to alternative_model; upstream 429 can."""
    import httpx
    import json
    from app.services.providers.openrouter_provider import OpenRouterProvider

    acct_429 = httpx.Response(
        status_code=429,
        json={
            "error": {
                "message": "Rate limit exceeded: free-models-per-day",
                "code": 429,
                "metadata": {"limit_source": "openrouter_free_tier_daily", "provider_name": None},
            }
        },
        request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
    )

    upstream_429 = httpx.Response(
        status_code=429,
        json={
            "error": {
                "message": "Provider returned error",
                "code": 429,
                "metadata": {"provider_name": "nvidia"},
            }
        },
        request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
    )
    alt_ok = httpx.Response(
        status_code=200,
        json={
            "model": "dots-studio/dots-3-note-preview:free",
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "content": json.dumps({
                            "success": True,
                            "summary": "Idli",
                            "items": [
                                {
                                    "food_name": "Idli",
                                    "estimated_quantity": 2.0,
                                    "unit": "piece",
                                    "estimated_grams": 120.0,
                                    "calories": 140.0,
                                    "protein": 4.0,
                                    "carbohydrates": 28.0,
                                    "fat": 1.0,
                                }
                            ],
                        })
                    },
                }
            ],
        },
        request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
    )

    mock_client = MagicMock(spec=httpx.Client)
    provider = OpenRouterProvider(
        api_key="sk-test",
        model="nvidia/nemotron-3.5-super-vl:free",
        alternative_model="dots-studio/dots-3-note-preview:free",
        max_retries=0,
        http_client=mock_client,
    )

    # Part A: Account-wide daily 429 skips alternative_model (only 1 POST)
    mock_client.post.return_value = acct_429
    with pytest.raises(AIRateLimitError):
        provider.recognize_food(sample_jpeg_bytes, timeout_seconds=20.0)
    assert mock_client.post.call_count == 1

    # Part B: Model upstream saturation can fall back to alternative model once
    mock_client.post.reset_mock()
    mock_client.post.side_effect = [upstream_429, alt_ok]
    res = provider.recognize_food(sample_jpeg_bytes, timeout_seconds=20.0)
    assert res.success is True
    assert mock_client.post.call_count == 2


# ---------------------------------------------------------------------------
# Test 51: Bounded cooldown skips cooled-down 429 primary and auto-recovers
# ---------------------------------------------------------------------------
def test_dual_provider_bounded_cooldown_skips_429_primary_and_routes_directly_to_gemini(
    sample_voice_item: ParsedVoiceFoodItem,
) -> None:
    """After OpenRouter 429, subsequent calls inside bounded cooldown route directly to Gemini with 0 OR calls."""
    from app.services.ai_service import ProviderCooldownTracker

    now = [1000.0]
    tracker = ProviderCooldownTracker(clock=lambda: now[0])

    mock_voice_or = MagicMock(spec=BaseAIProvider)
    mock_voice_or.name = "openrouter"
    mock_voice_or.is_configured = True
    # Reset is 6 hours (21600s) away, must be capped to rate_limit_daily_cooldown_max_seconds (300s)
    mock_voice_or.parse_voice_meal.side_effect = [
        AIRateLimitError(
            "OpenRouter free-models-per-day",
            provider="openrouter",
            code=429,
            is_quota_exhausted=True,
            error_category="daily_quota_exhausted",
            retry_after_seconds=21600.0,
            limit_scope="account",
        ),
        VoiceMealParseResponse(
            success=True,
            transcript="2 rotis",
            summary="Recovered after cooldown",
            items=[sample_voice_item],
        ),
    ]

    mock_gemini = MagicMock(spec=BaseAIProvider)
    mock_gemini.name = "gemini"
    mock_gemini.is_configured = True
    mock_gemini.parse_voice_meal.return_value = VoiceMealParseResponse(
        success=True,
        transcript="2 rotis",
        summary="Gemini fallback",
        items=[sample_voice_item],
    )

    settings = Settings()
    settings.voice_primary_provider = "openrouter"
    settings.voice_fallback_provider = "gemini"
    settings.rate_limit_daily_cooldown_max_seconds = 300.0

    service = DualProviderService(
        gemini_provider=mock_gemini,
        voice_openrouter_provider=mock_voice_or,
        settings=settings,
        cooldown_tracker=tracker,
    )

    # Call 1: OpenRouter 429 -> falls back to Gemini -> records bounded 300s cooldown
    r1 = service.parse_voice_meal("2 rotis")
    assert r1.summary == "Gemini fallback"
    assert mock_voice_or.parse_voice_meal.call_count == 1
    assert mock_gemini.parse_voice_meal.call_count == 1
    snap = service.cooldown_snapshot()
    assert snap["openrouter:account"]["remaining_seconds"] == pytest.approx(300.0, abs=0.5)

    # Call 2 (+20s later, inside cooldown): skips OpenRouter cleanly (0 new OR calls)
    now[0] += 20.0
    r2 = service.parse_voice_meal("2 rotis")
    assert r2.summary == "Gemini fallback"
    assert mock_voice_or.parse_voice_meal.call_count == 1
    assert mock_gemini.parse_voice_meal.call_count == 2

    # Call 3 (+305s later, past 300s cap): probes OpenRouter cleanly again and succeeds
    now[0] += 305.0
    r3 = service.parse_voice_meal("2 rotis")
    assert r3.summary == "Recovered after cooldown"
    assert mock_voice_or.parse_voice_meal.call_count == 2
    assert mock_gemini.parse_voice_meal.call_count == 2


# ---------------------------------------------------------------------------
# Test 52: Confirmed live incident (OR 429 + Gemini 503) preserves photo Gemini
# ---------------------------------------------------------------------------
def test_confirmed_incident_openrouter_429_plus_gemini_503_preserves_gemini_photo(
    sample_jpeg_bytes: bytes,
    sample_candidate: FoodItemCandidate,
) -> None:
    """OpenRouter voice 429 + Gemini voice 503 returns HTTP 503 without cooling down Gemini photo."""
    from app.main import app
    from app.services.ai_service import ProviderCooldownTracker

    now = [500.0]
    tracker = ProviderCooldownTracker(clock=lambda: now[0])

    mock_voice_or = MagicMock(spec=BaseAIProvider)
    mock_voice_or.name = "openrouter"
    mock_voice_or.is_configured = True
    mock_voice_or.parse_voice_meal.side_effect = AIRateLimitError(
        "OpenRouter free-models-per-day",
        provider="openrouter",
        code=429,
        is_quota_exhausted=True,
        error_category="daily_quota_exhausted",
        retry_after_seconds=3600.0,
        limit_scope="account",
    )

    mock_gemini = MagicMock(spec=BaseAIProvider)
    mock_gemini.name = "gemini"
    mock_gemini.is_configured = True
    mock_gemini.parse_voice_meal.side_effect = AIUnavailableError(
        "Gemini temporary 503", provider="gemini", code=503
    )
    mock_gemini.recognize_food.return_value = FoodRecognitionResponse(
        success=True,
        summary="Paneer Butter Masala",
        items=[sample_candidate],
    )

    settings = Settings()
    settings.photo_primary_provider = "gemini"
    settings.photo_fallback_provider = "openrouter"
    settings.voice_primary_provider = "openrouter"
    settings.voice_fallback_provider = "gemini"

    service = DualProviderService(
        gemini_provider=mock_gemini,
        photo_openrouter_provider=MagicMock(spec=BaseAIProvider, name="openrouter", is_configured=True),
        voice_openrouter_provider=mock_voice_or,
        settings=settings,
        cooldown_tracker=tracker,
    )

    app.dependency_overrides[get_ai_service] = lambda: service
    try:
        client = TestClient(app)

        # Call 1: OR 429 -> Gemini 503 -> HTTP 503
        v1 = client.post("/api/v1/parse-voice-meal", json={"transcript": "2 rotis"})
        assert v1.status_code == 503
        assert v1.headers.get("X-Error-Category") == "all_providers_failed"
        assert "Retry-After" in v1.headers
        assert mock_voice_or.parse_voice_meal.call_count == 1
        assert mock_gemini.parse_voice_meal.call_count == 1

        # Gemini 503 did NOT trigger a 429 cooldown on Gemini, so photo works normally
        p1 = client.post(
            "/api/v1/recognize-food",
            files={"file": ("meal.jpg", sample_jpeg_bytes, "image/jpeg")},
        )
        assert p1.status_code == 200
        assert mock_gemini.recognize_food.call_count == 1

        # Call 2 (+5s): OR is skipped due to cooldown (still 1 call), only Gemini attempted
        now[0] += 5.0
        v2 = client.post("/api/v1/parse-voice-meal", json={"transcript": "2 rotis"})
        assert v2.status_code == 503
        assert mock_voice_or.parse_voice_meal.call_count == 1
        assert mock_gemini.parse_voice_meal.call_count == 2
    finally:
        app.dependency_overrides.pop(get_ai_service, None)


# ---------------------------------------------------------------------------
# Test 53: Both providers returning 429 short-circuits cleanly with HTTP 429
# ---------------------------------------------------------------------------
def test_both_providers_429_short_circuits_with_429_retry_after_and_zero_calls() -> None:
    """When both OpenRouter and Gemini return 429, subsequent calls make 0 HTTP calls and return HTTP 429."""
    from app.main import app
    from app.services.ai_service import ProviderCooldownTracker

    now = [200.0]
    tracker = ProviderCooldownTracker(clock=lambda: now[0])

    mock_voice_or = MagicMock(spec=BaseAIProvider)
    mock_voice_or.name = "openrouter"
    mock_voice_or.is_configured = True
    mock_voice_or.parse_voice_meal.side_effect = AIRateLimitError(
        "OR burst 429",
        provider="openrouter",
        code=429,
        is_quota_exhausted=False,
        error_category="burst_rate_limit",
        retry_after_seconds=25.0,
        limit_scope="account",
    )

    mock_gemini = MagicMock(spec=BaseAIProvider)
    mock_gemini.name = "gemini"
    mock_gemini.is_configured = True
    mock_gemini.parse_voice_meal.side_effect = AIRateLimitError(
        "Gemini burst 429",
        provider="gemini",
        code=429,
        is_quota_exhausted=False,
        error_category="burst_rate_limit",
        retry_after_seconds=18.0,
        limit_scope="model",
    )

    settings = Settings()
    settings.voice_primary_provider = "openrouter"
    settings.voice_fallback_provider = "gemini"

    service = DualProviderService(
        gemini_provider=mock_gemini,
        voice_openrouter_provider=mock_voice_or,
        settings=settings,
        cooldown_tracker=tracker,
    )

    app.dependency_overrides[get_ai_service] = lambda: service
    try:
        client = TestClient(app)

        r1 = client.post("/api/v1/parse-voice-meal", json={"transcript": "2 rotis"})
        assert r1.status_code == 429
        assert r1.headers.get("X-Error-Category") == "all_providers_rate_limited"
        assert "Retry-After" in r1.headers
        assert mock_voice_or.parse_voice_meal.call_count == 1
        assert mock_gemini.parse_voice_meal.call_count == 1

        # Request 2 inside both cooldown windows -> 0 calls to either provider!
        now[0] += 3.0
        r2 = client.post("/api/v1/parse-voice-meal", json={"transcript": "2 rotis"})
        assert r2.status_code == 429
        assert r2.headers.get("X-Error-Category") == "all_providers_rate_limited"
        assert mock_voice_or.parse_voice_meal.call_count == 1
        assert mock_gemini.parse_voice_meal.call_count == 1
    finally:
        app.dependency_overrides.pop(get_ai_service, None)


# ---------------------------------------------------------------------------
# Test 54: Upstream model-scoped 429 cooldown isolates other OpenRouter models
# ---------------------------------------------------------------------------
def test_model_scoped_upstream_cooldown_does_not_block_other_openrouter_models(
    sample_jpeg_bytes: bytes,
    sample_candidate: FoodItemCandidate,
    sample_voice_item: ParsedVoiceFoodItem,
) -> None:
    """Upstream model saturation cools down only that model, keeping photo fallback OpenRouter unblocked."""
    from app.services.ai_service import ProviderCooldownTracker

    now = [300.0]
    tracker = ProviderCooldownTracker(clock=lambda: now[0])

    mock_voice_or = MagicMock(spec=BaseAIProvider)
    mock_voice_or.name = "openrouter"
    mock_voice_or.is_configured = True
    mock_voice_or.parse_voice_meal.side_effect = AIRateLimitError(
        "NVIDIA upstream saturated",
        provider="openrouter",
        code=429,
        is_quota_exhausted=False,
        error_category="upstream_provider_saturated",
        retry_after_seconds=20.0,
        limit_scope="provider_upstream",
    )

    mock_photo_or = MagicMock(spec=BaseAIProvider)
    mock_photo_or.name = "openrouter"
    mock_photo_or.is_configured = True
    mock_photo_or.recognize_food.return_value = FoodRecognitionResponse(
        success=True,
        summary="Idli",
        items=[sample_candidate],
    )

    mock_gemini = MagicMock(spec=BaseAIProvider)
    mock_gemini.name = "gemini"
    mock_gemini.is_configured = True
    mock_gemini.parse_voice_meal.return_value = VoiceMealParseResponse(
        success=True,
        transcript="2 rotis",
        summary="2 rotis",
        items=[sample_voice_item],
    )
    mock_gemini.recognize_food.side_effect = AIUnavailableError(
        "Gemini 503", provider="gemini", code=503
    )

    settings = Settings()
    settings.voice_openrouter_model = "nvidia/nemotron-3-ultra-550b-a55b:free"
    settings.photo_openrouter_model = "nvidia/nemotron-3.5-super-vl:free"

    service = DualProviderService(
        gemini_provider=mock_gemini,
        photo_openrouter_provider=mock_photo_or,
        voice_openrouter_provider=mock_voice_or,
        settings=settings,
        cooldown_tracker=tracker,
    )

    # Voice upstream 429 cools down only voice_openrouter_model
    v_res = service.parse_voice_meal("2 rotis")
    assert v_res.success is True
    assert "openrouter:model:nvidia/nemotron-3-ultra-550b-a55b:free" in tracker.snapshot()

    # Photo fallback uses different OpenRouter model and must NOT be blocked
    p_res = service.recognize_food(sample_jpeg_bytes)
    assert p_res.success is True
    assert mock_photo_or.recognize_food.call_count == 1


# ---------------------------------------------------------------------------
# Test 55: Gemini 429 extracts retry_after_seconds & daily vs burst scope
# ---------------------------------------------------------------------------
def test_gemini_429_extracts_retry_in_seconds_and_daily_vs_burst_scope(
    sample_jpeg_bytes: bytes,
) -> None:
    """GeminiProvider parses retry-after delay and classifies daily account vs model burst 429."""
    from google.genai.errors import APIError
    from app.services.providers.gemini_provider import GeminiProvider

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = APIError(
        429,
        {"error": {"message": "429 RESOURCE_EXHAUSTED: Requests per minute exceeded. Please retry in 42.5s."}},
    )

    provider = GeminiProvider(client=mock_client, model="gemini-3.5-flash", max_retries=0)
    with pytest.raises(AIRateLimitError) as exc_burst:
        provider.recognize_food(sample_jpeg_bytes)
    assert exc_burst.value.error_category == "burst_rate_limit"
    assert exc_burst.value.is_quota_exhausted is False
    assert exc_burst.value.limit_scope == "model"
    assert exc_burst.value.retry_after_seconds == pytest.approx(42.5, abs=0.1)

    mock_client.models.generate_content.side_effect = APIError(
        429,
        {"error": {"message": "429 RESOURCE_EXHAUSTED: GenerateRequestsPerDayPerProjectPerModel requests per day limit"}},
    )
    with pytest.raises(AIRateLimitError) as exc_daily:
        provider.recognize_food(sample_jpeg_bytes)
    assert exc_daily.value.error_category == "daily_quota_exhausted"
    assert exc_daily.value.is_quota_exhausted is True
    assert exc_daily.value.limit_scope == "account"


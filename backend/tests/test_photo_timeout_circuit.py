from unittest.mock import MagicMock
from app.config import Settings
from app.services.ai_service import DualProviderService
from app.services.providers.base import BaseAIProvider, AITimeoutError


def test_repeated_photo_timeouts_skip_primary_then_probe_after_expiry(mock_food_response, monkeypatch):
    now = [100.0]
    monkeypatch.setattr("app.services.ai_service.time.monotonic", lambda: now[0])
    primary = MagicMock(spec=BaseAIProvider)
    primary.name = "gemini"
    primary.is_configured = True
    primary.recognize_food.side_effect = AITimeoutError("timeout", provider="gemini")
    fallback = MagicMock(spec=BaseAIProvider)
    fallback.name = "openrouter"
    fallback.is_configured = True
    fallback.recognize_food.return_value = mock_food_response
    settings = Settings()
    settings.photo_primary_provider = settings.ai_primary_provider = "gemini"
    settings.ai_fallback_enabled = True
    service = DualProviderService(gemini_provider=primary, openrouter_provider=fallback, settings=settings)
    # Mirrors the supplied roughly 77s then 98s gaps between scans.
    for gap in [0, 77, 98]:
        now[0] += gap
        assert service.recognize_food(b"synthetic").success
    assert primary.recognize_food.call_count == 2
    assert fallback.recognize_food.call_count == 3
    assert fallback.recognize_food.call_args.kwargs["timeout_seconds"] <= settings.server_deadline_seconds
    now[0] += 121
    primary.recognize_food.side_effect = None
    primary.recognize_food.return_value = mock_food_response
    assert service.recognize_food(b"synthetic").success
    assert primary.recognize_food.call_count == 3
    assert fallback.recognize_food.call_count == 3

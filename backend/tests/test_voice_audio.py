"""Deterministic mocked tests for audio-native voice meal logging (Milestone 4F)."""

import json
import logging
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from google.genai import errors, types

from app.config import Settings, get_settings
from app.main import app
from app.models.food import ParsedVoiceFoodItem, VoiceMealParseResponse
from app.routers.food import get_gemini_service
from app.services.ai_service import DualProviderService
from app.services.audio import (
    AudioSizeExceededError,
    InvalidAudioError,
    validate_and_sanitize_audio,
)
from app.services.providers.base import (
    AIRequestCancelledError,
    ModelOutputValidationError,
)
from app.services.providers.gemini_provider import GeminiProvider


def _fake_m4a_bytes(size: int = 128) -> bytes:
    header = b"\x00\x00\x00\x18ftypM4A \x00\x00\x00\x00M4A mp42isom"
    return header + (b"\x01" * max(0, size - len(header)))


def _fake_wav_bytes(size: int = 128) -> bytes:
    header = b"RIFF\x24\x00\x00\x00WAVEfmt "
    return header + (b"\x00" * max(0, size - len(header)))


def _gemini_json_response(payload: dict, finish_reason: str = "STOP") -> SimpleNamespace:
    return SimpleNamespace(
        text=json.dumps(payload),
        candidates=[SimpleNamespace(finish_reason=finish_reason)],
        usage_metadata=SimpleNamespace(
            prompt_token_count=260,
            candidates_token_count=190,
            thoughts_token_count=0,
        ),
    )


def test_validate_and_sanitize_audio_accepts_supported_containers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_AUDIO_SIZE_BYTES", str(1024 * 1024))
    raw_m4a, mime_m4a = validate_and_sanitize_audio(_fake_m4a_bytes(), content_type="audio/x-m4a", filename="meal.m4a")
    assert mime_m4a == "audio/m4a"
    assert len(raw_m4a) == 128

    raw_wav, mime_wav = validate_and_sanitize_audio(_fake_wav_bytes(), filename="sample.wav")
    assert mime_wav == "audio/wav"
    assert len(raw_wav) == 128

    # Filename extension fallback when header lacks standard prefix
    _, mime_aac = validate_and_sanitize_audio(b"\xff\xf1\x50\x80" + b"\x00" * 64, filename="clip.aac")
    assert mime_aac == "audio/aac"


def test_validate_and_sanitize_audio_rejects_empty_non_audio_and_oversize(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(InvalidAudioError):
        validate_and_sanitize_audio(b"tiny")

    with pytest.raises(InvalidAudioError):
        validate_and_sanitize_audio(b"\xff\xd8\xff\xe0" + b"\x00" * 64, content_type="audio/m4a", filename="photo.m4a")

    with pytest.raises(InvalidAudioError):
        validate_and_sanitize_audio(b"<!DOCTYPE html><html></html>" + b" " * 32, filename="bad.m4a")

    with pytest.raises(AudioSizeExceededError):
        validate_and_sanitize_audio(_fake_m4a_bytes(size=128), filename="large.m4a", max_size_bytes=64)


def test_gemini_parse_voice_audio_handles_user_reference_meal_and_modifiers(caplog: pytest.LogCaptureFixture) -> None:
    """Tests scrambled eggs, sourdough toast with butter modifier, black coffee, 1->2 banana correction, whey uncertainty."""
    expected_payload = {
        "success": True,
        "transcript": (
            "Two scrambled eggs, a slice of sourdough toast with butter, and black coffee. "
            "One banana, actually make that two bananas, and a scoop of whey protein."
        ),
        "summary": "2 scrambled eggs, sourdough toast with butter, black coffee, 2 bananas, 1 scoop whey protein",
        "items": [
            {
                "food_description": "Scrambled eggs",
                "quantity": 2.0,
                "unit": "egg",
                "preparation": "scrambled",
                "modifiers": [],
                "state": "cooked",
                "portion_specified": True,
                "estimated_grams": 110.0,
                "calories": 165.0,
                "protein": 13.0,
                "carbohydrates": 1.6,
                "fat": 11.5,
                "confidence": 0.94,
                "confidence_level": "high",
                "alternatives": [],
                "notes": "2 medium eggs scrambled",
            },
            {
                "food_description": "Sourdough toast",
                "quantity": 1.0,
                "unit": "slice",
                "preparation": "toasted",
                "modifiers": ["with butter"],
                "state": "cooked",
                "portion_specified": True,
                "estimated_grams": 45.0,
                "calories": 120.0,
                "protein": 4.0,
                "carbohydrates": 22.0,
                "fat": 1.0,
                "confidence": 0.78,
                "confidence_level": "medium",
                "alternatives": [],
                "notes": "Toast only; butter amount not specified",
            },
            {
                "food_description": "Black coffee",
                "quantity": 1.0,
                "unit": "cup",
                "preparation": "brewed black",
                "modifiers": [],
                "state": "cooked",
                "portion_specified": True,
                "estimated_grams": 240.0,
                "calories": 2.0,
                "protein": 0.3,
                "carbohydrates": 0.0,
                "fat": 0.0,
                "confidence": 0.96,
                "confidence_level": "high",
                "alternatives": [],
                "notes": "Unsweetened black coffee",
            },
            {
                "food_description": "Banana",
                "quantity": 2.0,
                "unit": "banana",
                "preparation": "fresh",
                "modifiers": [],
                "state": "unspecified",
                "portion_specified": True,
                "estimated_grams": 236.0,
                "calories": 210.0,
                "protein": 2.6,
                "carbohydrates": 54.0,
                "fat": 0.8,
                "confidence": 0.95,
                "confidence_level": "high",
                "alternatives": [],
                "notes": "Self-corrected from 1 to 2 bananas",
            },
            {
                "food_description": "Whey protein powder",
                "quantity": 1.0,
                "unit": "scoop",
                "preparation": "mixed",
                "modifiers": [],
                "state": "unspecified",
                "portion_specified": True,
                "estimated_grams": 30.0,
                "calories": 120.0,
                "protein": 24.0,
                "carbohydrates": 3.0,
                "fat": 1.5,
                "confidence": 0.65,
                "confidence_level": "medium",
                "alternatives": ["Whey isolate powder (~30g scoop)", "Whey concentrate powder (~32g scoop)"],
                "notes": "Scoop weight and brand macros vary; verify label",
            },
        ],
        "warnings": ["Adjusted Banana quantity from 1 to 2 per spoken self-correction."],
        "clarifying_questions": [
            "How much butter did you spread on the sourdough toast?",
            "Which whey protein brand/scoop size did you use?",
        ],
    }

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _gemini_json_response(expected_payload)

    settings = Settings()
    settings.gemini_model = "gemini-3.5-flash"
    provider = GeminiProvider(client=mock_client, settings=settings, max_retries=0)

    with caplog.at_level(logging.INFO):
        res = provider.parse_voice_audio(_fake_m4a_bytes(), mime_type="audio/m4a", meal_context="Breakfast")

    assert res.success is True
    assert "sourdough toast" in res.transcript.lower()
    assert len(res.items) == 5
    eggs = res.items[0]
    assert eggs.food_description == "Scrambled eggs"
    assert eggs.quantity == 2.0
    assert eggs.unit == "egg"
    toast = res.items[1]
    assert toast.food_description == "Sourdough toast"
    assert toast.modifiers == ["with butter"]
    banana = res.items[3]
    assert banana.quantity == 2.0
    assert banana.unit == "banana"
    whey = res.items[4]
    assert "whey" in whey.food_description.lower()
    assert whey.confidence_level == "medium"
    assert len(whey.alternatives) >= 1
    assert len(res.clarifying_questions) == 2

    # Ensure raw transcript text never leaks to logs
    assert "sourdough" not in caplog.text.lower()
    assert "whey" not in caplog.text.lower()

    # Verify audio bytes part passed with schema & thinking_budget=0
    call_kwargs = mock_client.models.generate_content.call_args.kwargs
    parts = call_kwargs["contents"]
    assert isinstance(parts[0], types.Part)
    assert parts[0].inline_data.mime_type == "audio/m4a"
    assert call_kwargs["config"].response_mime_type == "application/json"
    assert call_kwargs["config"].thinking_config.thinking_budget == 0


def test_gemini_parse_voice_audio_unspecified_portion_preserves_null_macros() -> None:
    payload = {
        "success": True,
        "transcript": "Some chicken curry and boiled rice cooked not raw",
        "summary": "Chicken curry (portion unstated) and cooked boiled rice",
        "items": [
            {
                "food_description": "Chicken curry",
                "quantity": 1.0,
                "unit": "serving",
                "preparation": "curry",
                "modifiers": [],
                "state": "cooked",
                "portion_specified": False,
                "estimated_grams": None,
                "calories": None,
                "protein": None,
                "carbohydrates": None,
                "fat": None,
                "confidence": 0.4,
                "confidence_level": "low",
                "alternatives": ["Homestyle chicken curry", "Butter chicken"],
                "notes": "Portion size was not stated in speech",
            },
            {
                "food_description": "Boiled white rice",
                "quantity": 100.0,
                "unit": "g",
                "preparation": "boiled",
                "modifiers": [],
                "state": "cooked",
                "portion_specified": True,
                "estimated_grams": 100.0,
                "calories": 130.0,
                "protein": 2.7,
                "carbohydrates": 28.0,
                "fat": 0.3,
                "confidence": 0.92,
                "confidence_level": "high",
                "alternatives": [],
                "notes": None,
            },
        ],
        "warnings": [],
        "clarifying_questions": ["How many bowls or grams of chicken curry did you have?"],
    }
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _gemini_json_response(payload)
    provider = GeminiProvider(client=mock_client, settings=Settings(), max_retries=0)

    res = provider.parse_voice_audio(_fake_m4a_bytes(), mime_type="audio/m4a")
    assert res.items[0].portion_specified is False
    assert res.items[0].estimated_grams is None
    assert res.items[0].calories is None
    assert res.items[1].state == "cooked"
    assert res.items[1].estimated_grams == 100.0


def test_gemini_parse_voice_audio_single_bounded_repair_and_no_loop() -> None:
    """Malformed JSON triggers at most ONE bounded repair attempt, never a retry loop."""
    malformed_resp = SimpleNamespace(
        text="{invalid json",
        candidates=[SimpleNamespace(finish_reason="STOP")],
        usage_metadata=SimpleNamespace(prompt_token_count=100, candidates_token_count=6, thoughts_token_count=0),
    )
    repaired_payload = {
        "success": True,
        "transcript": "Two rotis, no wait, three rotis",
        "summary": "3 whole wheat rotis",
        "items": [
            {
                "food_description": "Whole wheat roti",
                "quantity": 3.0,
                "unit": "roti",
                "preparation": "griddle cooked",
                "modifiers": [],
                "state": "cooked",
                "portion_specified": True,
                "estimated_grams": 105.0,
                "calories": 270.0,
                "protein": 9.0,
                "carbohydrates": 54.0,
                "fat": 2.1,
                "confidence": 0.9,
                "confidence_level": "high",
                "alternatives": [],
                "notes": "Self-corrected from 2 to 3 rotis",
            }
        ],
        "warnings": ["Adjusted Roti quantity from 2 to 3."],
        "clarifying_questions": [],
    }
    repaired_resp = _gemini_json_response(repaired_payload)

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [malformed_resp, repaired_resp]
    provider = GeminiProvider(client=mock_client, settings=Settings(), max_retries=0)

    res = provider.parse_voice_audio(_fake_m4a_bytes(), mime_type="audio/m4a")
    assert mock_client.models.generate_content.call_count == 2
    assert res.items[0].quantity == 3.0

    # If both initial and single repair remain malformed, raise cleanly without extra attempts
    still_bad = MagicMock()
    still_bad.models.generate_content.side_effect = [malformed_resp, malformed_resp]
    provider_bad = GeminiProvider(client=still_bad, settings=Settings(), max_retries=0)
    with pytest.raises(ModelOutputValidationError):
        provider_bad.parse_voice_audio(_fake_m4a_bytes(), mime_type="audio/m4a")
    assert still_bad.models.generate_content.call_count == 2


def test_parse_voice_audio_endpoint_multipart_errors_and_health() -> None:
    client = TestClient(app)

    # Missing file -> 400
    resp_missing = client.post("/api/v1/parse-voice-audio")
    assert resp_missing.status_code == 400

    # Non-audio payload -> 400
    resp_img = client.post(
        "/api/v1/parse-voice-audio",
        files={"file": ("not_audio.m4a", b"\xff\xd8\xff\xe0" + b"\x00" * 64, "audio/m4a")},
    )
    assert resp_img.status_code == 400

    # Success path via mocked service
    mock_service = MagicMock(spec=DualProviderService)
    mock_service.parse_voice_audio.return_value = VoiceMealParseResponse(
        success=True,
        transcript="do aloo paratha dahi ke saath",
        summary="2 Aloo Paratha with curd",
        items=[
            ParsedVoiceFoodItem(
                food_description="Aloo paratha",
                quantity=2.0,
                unit="paratha",
                preparation="pan fried",
                modifiers=["with dahi"],
                state="cooked",
                portion_specified=True,
                estimated_grams=200.0,
                calories=520.0,
                protein=10.0,
                carbohydrates=70.0,
                fat=22.0,
            )
        ],
    )
    app.dependency_overrides[get_gemini_service] = lambda: mock_service
    try:
        resp_ok = client.post(
            "/api/v1/parse-voice-audio",
            files={"file": ("meal.m4a", _fake_m4a_bytes(256), "audio/m4a")},
            data={"meal_context": "Breakfast"},
        )
        assert resp_ok.status_code == 200
        body = resp_ok.json()
        assert body["transcript"] == "do aloo paratha dahi ke saath"
        assert body["items"][0]["modifiers"] == ["with dahi"]
        assert body["items"][0]["quantity"] == 2.0

        # Client cancel -> 499
        mock_service.parse_voice_audio.side_effect = AIRequestCancelledError("aborted", provider="gemini")
        resp_cancel = client.post(
            "/api/v1/parse-voice-audio",
            files={"file": ("meal.m4a", _fake_m4a_bytes(256), "audio/m4a")},
        )
        assert resp_cancel.status_code == 499

        # Rate limit -> 429 with bounded Retry-After
        from app.services.providers.base import AIRateLimitError, AITimeoutError
        mock_service.parse_voice_audio.side_effect = AIRateLimitError(
            "Quota reached",
            provider="gemini",
            retry_after_seconds=22.0,
            is_quota_exhausted=True,
            error_category="daily_quota_exhausted",
        )
        resp_429 = client.post(
            "/api/v1/parse-voice-audio",
            files={"file": ("meal.m4a", _fake_m4a_bytes(256), "audio/m4a")},
        )
        assert resp_429.status_code == 429
        assert resp_429.headers.get("Retry-After") == "22"

        # Upstream timeout -> 504
        mock_service.parse_voice_audio.side_effect = AITimeoutError("Timed out", provider="gemini")
        resp_504 = client.post(
            "/api/v1/parse-voice-audio",
            files={"file": ("meal.m4a", _fake_m4a_bytes(256), "audio/m4a")},
        )
        assert resp_504.status_code == 504

        # Malformed model output -> 502
        mock_service.parse_voice_audio.side_effect = ModelOutputValidationError("Bad output", provider="gemini")
        resp_502 = client.post(
            "/api/v1/parse-voice-audio",
            files={"file": ("meal.m4a", _fake_m4a_bytes(256), "audio/m4a")},
        )
        assert resp_502.status_code == 502
    finally:
        app.dependency_overrides.clear()

    # Oversize upload -> 413 via settings override
    small_settings = Settings()
    small_settings.max_audio_size_bytes = 64
    app.dependency_overrides[get_settings] = lambda: small_settings
    try:
        resp_413 = client.post(
            "/api/v1/parse-voice-audio",
            files={"file": ("meal.m4a", _fake_m4a_bytes(256), "audio/m4a")},
        )
        assert resp_413.status_code == 413
    finally:
        app.dependency_overrides.clear()

    # Verify /health exposes voice_audio routing cleanly without secrets
    health = client.get("/health")
    assert health.status_code == 200
    hdata = health.json()
    assert hdata["voice_audio_primary_provider"] == "gemini"
    assert "audio/m4a" in hdata["voice_audio_supported_formats"]


def test_eval_voice_audio_cli_requires_consent_and_scores_mocked_responses(tmp_path: Path, monkeypatch):
    from scripts import eval_voice_audio

    audio_file = tmp_path / "meal.m4a"
    audio_file.write_bytes(_fake_m4a_bytes(128))
    manifest_file = tmp_path / "manifest.json"
    manifest_file.write_text(
        json.dumps([
            {
                "id": "english-correction",
                "file": str(audio_file),
                "meal_context": "Breakfast",
                "expected_foods": ["Scrambled eggs", "Sourdough toast", "Banana"],
                "expected_quantities": {"Scrambled eggs": 2, "Banana": 2},
                "correction_expected": True,
            }
        ]),
        encoding="utf-8",
    )

    monkeypatch.setattr(sys, "argv", ["eval_voice_audio.py", "--manifest", str(manifest_file)])
    assert eval_voice_audio.main() == 2

    class _MockResponse:
        status_code = 200

        def json(self):
            return {
                "items": [
                    {"food_description": "Scrambled eggs", "quantity": 2.0},
                    {"food_description": "Sourdough toast", "quantity": 1.0},
                    {"food_description": "Banana", "quantity": 2.0},
                ]
            }

    class _MockClient:
        def __init__(self, timeout=45.0):
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def post(self, url, files=None, data=None):
            assert url.endswith("/api/v1/parse-voice-audio")
            return _MockResponse()

    monkeypatch.setattr(eval_voice_audio.httpx, "Client", _MockClient)
    summary = eval_voice_audio.evaluate_manifest(manifest_file, "http://127.0.0.1:8000")
    assert summary["total_cases"] == 1
    assert summary["unsuccessful_requests"] == 0
    assert summary["food_name_accuracy"] == 1.0
    assert summary["quantity_accuracy"] == 1.0
    assert summary["correction_accuracy"] == 1.0

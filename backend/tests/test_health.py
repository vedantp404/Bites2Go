"""Tests for /health endpoint."""

from fastapi.testclient import TestClient


def test_health_check_returns_ok(client: TestClient) -> None:
    """Verify health endpoint responds with 200 OK and expected keys."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data
    assert "version" in data
    assert "ai_configured" in data
    assert "model" in data
    # Ensure no secrets or API keys are leaked in health output
    assert "key" not in data
    assert "api_key" not in data


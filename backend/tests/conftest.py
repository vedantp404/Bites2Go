"""Test fixtures and mock helpers for the backend test suite."""

import io
import sys
from pathlib import Path
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from PIL import Image

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.main import app
from app.models.food import (
    FoodItemCandidate,
    FoodRecognitionResponse,
    UncertaintyInfo,
)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Test client for FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_jpeg_bytes() -> bytes:
    """Generate a valid, minimal in-memory JPEG image."""
    buffer = io.BytesIO()
    image = Image.new("RGB", (100, 100), color=(200, 50, 50))
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


@pytest.fixture
def sample_png_bytes() -> bytes:
    """Generate a valid, minimal in-memory PNG image."""
    buffer = io.BytesIO()
    image = Image.new("RGBA", (120, 120), color=(50, 200, 50, 255))
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def mock_food_response() -> FoodRecognitionResponse:
    """Sample valid structured food recognition response."""
    return FoodRecognitionResponse(
        success=True,
        summary="A healthy breakfast of scrambled eggs and avocado toast.",
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
                    notes="Assumed prepared with minimal butter.",
                    alternatives=["Omelette", "Egg Whites"],
                ),
            ),
            FoodItemCandidate(
                food_name="Avocado Toast",
                estimated_quantity=1.0,
                unit="slice",
                estimated_grams=85.0,
                calories=190.0,
                protein=4.0,
                carbohydrates=18.0,
                fat=11.0,
                uncertainty=UncertaintyInfo(
                    confidence_score=0.88,
                    confidence_level="high",
                    notes="Assumed whole grain bread and 1/4 avocado.",
                    alternatives=["Toast with guacamole"],
                ),
            ),
        ],
        warnings=[],
    )


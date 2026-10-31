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
    ParsedVoiceFoodItem,
    UncertaintyInfo,
    VoiceMealParseResponse,
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


@pytest.fixture
def mock_voice_meal_response() -> VoiceMealParseResponse:
    """Sample valid structured voice meal parsing response."""
    return VoiceMealParseResponse(
        success=True,
        transcript="two scrambled eggs, a slice of whole wheat toast with butter, and a cup of black coffee",
        summary="Breakfast comprising scrambled eggs, buttered toast, and black coffee.",
        items=[
            ParsedVoiceFoodItem(
                food_description="Scrambled Eggs",
                quantity=2.0,
                unit="eggs",
                preparation="scrambled",
                state="cooked",
                estimated_grams=100.0,
                calories=140.0,
                protein=12.0,
                carbohydrates=1.5,
                fat=9.5,
                confidence=0.95,
                confidence_level="high",
                alternatives=["Omelette", "Fried Eggs"],
                notes="Standard whole egg preparation",
            ),
            ParsedVoiceFoodItem(
                food_description="Whole Wheat Toast with Butter",
                quantity=1.0,
                unit="slice",
                preparation="toasted with butter",
                state="cooked",
                estimated_grams=40.0,
                calories=110.0,
                protein=3.5,
                carbohydrates=14.0,
                fat=4.5,
                confidence=0.90,
                confidence_level="high",
                alternatives=["White toast with butter"],
                notes="Assumed 1 slice bread (~30g) + 1 tsp butter (~5g)",
            ),
            ParsedVoiceFoodItem(
                food_description="Black Coffee",
                quantity=1.0,
                unit="cup",
                preparation="brewed, no sugar",
                state="cooked",
                estimated_grams=240.0,
                calories=2.0,
                protein=0.3,
                carbohydrates=0.2,
                fat=0.0,
                confidence=0.98,
                confidence_level="high",
                alternatives=["Americano"],
                notes="Unsweetened black coffee",
            ),
        ],
        warnings=[],
        clarifying_questions=[],
    )


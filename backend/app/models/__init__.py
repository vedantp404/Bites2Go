"""Domain models and Pydantic schemas for the AI backend."""

from .food import (
    FoodItemCandidate,
    FoodRecognitionResponse,
    UncertaintyInfo,
)

__all__ = [
    "UncertaintyInfo",
    "FoodItemCandidate",
    "FoodRecognitionResponse",
]


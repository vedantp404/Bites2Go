"""Food recognition models and validation schemas."""

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class UncertaintyInfo(BaseModel):
    """Uncertainty and estimation confidence for recognized food."""

    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score from 0.0 (uncertain) to 1.0 (very certain)",
    )
    confidence_level: Literal["high", "medium", "low"] = Field(
        ...,
        description="High (>0.8), Medium (0.5-0.8), or Low (<0.5)",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Assumptions or visible uncertainty notes (e.g. sauce content, cut, preparation style)",
    )
    alternatives: list[str] = Field(
        default_factory=list,
        description="Alternative food interpretations if ambiguous",
    )


class FoodItemCandidate(BaseModel):
    """A single food item identified in a meal photo."""

    food_name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Name of the recognized food item",
    )
    estimated_quantity: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Estimated quantity count (e.g. 1.0, 0.5, 2.0)",
    )
    unit: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Serving unit description (e.g. cup, piece, slice, fillet, bowl, serving)",
    )
    estimated_grams: float = Field(
        ...,
        ge=0.0,
        le=5000.0,
        description="Estimated weight in grams",
    )
    calories: float = Field(
        ...,
        ge=0.0,
        le=10000.0,
        description="Estimated energy in kilocalories",
    )
    protein: float = Field(
        ...,
        ge=0.0,
        le=1000.0,
        description="Estimated protein in grams",
    )
    carbohydrates: float = Field(
        ...,
        ge=0.0,
        le=1000.0,
        description="Estimated carbohydrates in grams",
    )
    fat: float = Field(
        ...,
        ge=0.0,
        le=1000.0,
        description="Estimated dietary fat in grams",
    )
    uncertainty: UncertaintyInfo = Field(
        ...,
        description="Confidence level and estimation notes",
    )

    @field_validator("food_name")
    @classmethod
    def clean_food_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("food_name cannot be empty or whitespace only")
        return cleaned

    @field_validator("unit")
    @classmethod
    def clean_unit(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            return "serving"
        return cleaned

    @model_validator(mode="after")
    def validate_macronutrient_consistency(self) -> "FoodItemCandidate":
        """Verify that macros are not glaringly contradictory with calories."""
        # 1g protein ~ 4 kcal, 1g carb ~ 4 kcal, 1g fat ~ 9 kcal
        macro_calories = (self.protein * 4.0) + (self.carbohydrates * 4.0) + (self.fat * 9.0)
        
        # If macros alone exceed reported calories by more than 300 kcal or 2.5x, flag/clamp
        # We allow standard variance for fiber, alcohol, and estimation margin
        if self.calories > 0 and macro_calories > max(self.calories * 2.5, self.calories + 300):
            # Rather than failing the whole response, adjust calories to fit calculated macros
            self.calories = round(macro_calories, 1)

        # Round all nutrition numbers to 1 decimal place for clean UI display
        self.estimated_quantity = round(self.estimated_quantity, 2)
        self.estimated_grams = round(self.estimated_grams, 1)
        self.calories = round(self.calories, 1)
        self.protein = round(self.protein, 1)
        self.carbohydrates = round(self.carbohydrates, 1)
        self.fat = round(self.fat, 1)
        self.uncertainty.confidence_score = round(self.uncertainty.confidence_score, 2)
        return self


class FoodRecognitionResponse(BaseModel):
    """Top-level structured response returned by the food recognition endpoint."""

    success: bool = Field(
        default=True,
        description="Whether food recognition was processed successfully",
    )
    summary: str = Field(
        default="",
        description="High-level description of the analyzed meal",
    )
    items: list[FoodItemCandidate] = Field(
        default_factory=list,
        description="List of recognized food components in the meal",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Sanity or ambiguity warnings for the user",
    )

    @model_validator(mode="after")
    def deduplicate_items(self) -> "FoodRecognitionResponse":
        """Merge or deduplicate identical food candidate names if model duplicates them."""
        if not self.items or len(self.items) <= 1:
            return self

        seen: dict[str, FoodItemCandidate] = {}
        for item in self.items:
            key = item.food_name.strip().lower()
            if key in seen:
                existing = seen[key]
                existing.estimated_quantity = round(
                    existing.estimated_quantity + item.estimated_quantity, 2
                )
                existing.estimated_grams = round(
                    existing.estimated_grams + item.estimated_grams, 1
                )
                existing.calories = round(existing.calories + item.calories, 1)
                existing.protein = round(existing.protein + item.protein, 1)
                existing.carbohydrates = round(
                    existing.carbohydrates + item.carbohydrates, 1
                )
                existing.fat = round(existing.fat + item.fat, 1)

                # Merge alternatives without duplicates
                merged_alts = list(
                    dict.fromkeys(
                        existing.uncertainty.alternatives
                        + item.uncertainty.alternatives
                    )
                )
                existing.uncertainty.alternatives = merged_alts
            else:
                seen[key] = item

        self.items = list(seen.values())
        return self

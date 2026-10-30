"""Food recognition API endpoint."""

import base64
from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from app.config import ConfigurationError
from app.models.food import FoodRecognitionResponse
from app.services.gemini import (
    GeminiService,
    GeminiServiceError,
    ModelOutputValidationError,
    RateLimitError,
    get_gemini_service,
)
from app.services.image import (
    ImageSizeExceededError,
    InvalidImageError,
    validate_and_sanitize_image,
)

router = APIRouter(prefix="/api/v1", tags=["Food Recognition"])


class Base64ImagePayload(BaseModel):
    """Optional JSON payload for base64 image submissions."""

    image_base64: str = Field(..., description="Base64-encoded image string")


@router.post(
    "/recognize-food",
    response_model=FoodRecognitionResponse,
    status_code=status.HTTP_200_OK,
    summary="Recognize foods and estimate macronutrients from a photo",
)
async def recognize_food(
    file: Optional[UploadFile] = File(None),
    gemini_service: GeminiService = Depends(get_gemini_service),
) -> FoodRecognitionResponse:
    """Analyze an uploaded food image in-memory and return validated food components.

    - Strips all EXIF metadata and device tags before analysis.
    - Never persists photos to disk or external storage.
    - Calls Gemini with structured output validation.
    """
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing image file in multipart upload. Use field name 'file'.",
        )

    try:
        raw_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded file payload.",
        ) from exc

    if not raw_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    try:
        sanitized_bytes, mime_type = validate_and_sanitize_image(raw_bytes)
        response = gemini_service.recognize_food(sanitized_bytes, mime_type=mime_type)
        return response

    except InvalidImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ImageSizeExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        ) from exc
    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except RateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        ) from exc
    except ModelOutputValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI model returned an unparseable or malformed nutritional response.",
        ) from exc
    except GeminiServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI food recognition service encountered an error. Please try again.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during food recognition.",
        ) from exc


@router.post(
    "/recognize-food/base64",
    response_model=FoodRecognitionResponse,
    status_code=status.HTTP_200_OK,
    summary="Recognize foods from a base64 encoded image string",
)
async def recognize_food_base64(
    payload: Base64ImagePayload,
    gemini_service: GeminiService = Depends(get_gemini_service),
) -> FoodRecognitionResponse:
    """Analyze a base64-encoded food image string in-memory."""
    raw_b64 = payload.image_base64.strip()
    if "," in raw_b64:
        # Strip data URL prefix if present (e.g. data:image/jpeg;base64,...)
        raw_b64 = raw_b64.split(",", 1)[1]

    try:
        raw_bytes = base64.b64decode(raw_b64)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid base64 image data.",
        ) from exc

    try:
        sanitized_bytes, mime_type = validate_and_sanitize_image(raw_bytes)
        response = gemini_service.recognize_food(sanitized_bytes, mime_type=mime_type)
        return response

    except InvalidImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ImageSizeExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        ) from exc
    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except RateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
        ) from exc
    except ModelOutputValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI model returned an unparseable or malformed nutritional response.",
        ) from exc
    except GeminiServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI food recognition service encountered an error. Please try again.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during food recognition.",
        ) from exc


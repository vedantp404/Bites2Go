"""In-memory image validation and metadata stripping service."""

import io
from typing import Tuple
from PIL import Image, ImageOps, UnidentifiedImageError

from app.config import get_settings


class InvalidImageError(ValueError):
    """Raised when an uploaded file is not a valid, decodable image."""
    pass


class ImageSizeExceededError(ValueError):
    """Raised when an uploaded image exceeds the allowed file size limit."""
    pass


def validate_and_sanitize_image(
    image_bytes: bytes,
    max_dimension: int = 1600,
) -> Tuple[bytes, str]:
    """Validate, sanitize, strip metadata, and downscale an image entirely in memory.

    - Checks file size against configured limit.
    - Decodes image and ensures valid format (JPEG, PNG, WEBP, etc.).
    - Applies EXIF orientation to keep correct physical orientation.
    - Strips all EXIF metadata, GPS tags, device details, and timestamps.
    - Resizes to a maximum dimension if larger, conserving bandwidth and API latency.
    - Re-encodes as clean, sanitized JPEG bytes in memory.

    Args:
        image_bytes: Raw bytes from uploaded multipart file.
        max_dimension: Maximum allowed width or height in pixels.

    Returns:
        Tuple of (sanitized_bytes, mime_type).
    """
    settings = get_settings()

    if not image_bytes or len(image_bytes) < 16:
        raise InvalidImageError("Image data is empty or too small to be a valid image file.")

    if len(image_bytes) > settings.max_image_size_bytes:
        raise ImageSizeExceededError(
            f"Image size exceeds the maximum allowed limit of {settings.max_image_size_bytes // (1024 * 1024)}MB."
        )

    try:
        # Load image in memory
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Handle EXIF rotation so rotated phone photos appear right-side up
            try:
                transposed = ImageOps.exif_transpose(img)
                if transposed is not None:
                    img = transposed
            except Exception:
                # If EXIF transpose fails, continue with original orientation
                pass

            # Convert to RGB to discard alpha channels and ensure JPEG compatibility
            if img.mode != "RGB":
                rgb_img = img.convert("RGB")
            else:
                rgb_img = img.copy()

            # Downscale if dimensions exceed max_dimension
            width, height = rgb_img.size
            if width > max_dimension or height > max_dimension:
                rgb_img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

            # Re-encode to clean JPEG buffer without EXIF metadata
            output_buffer = io.BytesIO()
            rgb_img.save(
                output_buffer,
                format="JPEG",
                quality=88,
                optimize=True,
            )
            sanitized_bytes = output_buffer.getvalue()

            return sanitized_bytes, "image/jpeg"

    except UnidentifiedImageError as exc:
        raise InvalidImageError("Uploaded file could not be recognized as a valid image format.") from exc
    except Exception as exc:
        if isinstance(exc, (InvalidImageError, ImageSizeExceededError)):
            raise
        raise InvalidImageError(f"Failed to process image: {str(exc)}") from exc


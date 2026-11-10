"""In-memory image validation and metadata stripping service."""

import io
from typing import Optional, Tuple
from PIL import Image, ImageOps, UnidentifiedImageError

from app.config import get_settings

# Enforce a strict 20 megapixel decoding limit to prevent decompression bomb denial-of-service
Image.MAX_IMAGE_PIXELS = 20_000_000


class InvalidImageError(ValueError):
    """Raised when an uploaded file is not a valid, decodable image."""
    pass


class ImageSizeExceededError(ValueError):
    """Raised when an uploaded image exceeds the allowed file size limit."""
    pass


def validate_and_sanitize_image(
    image_bytes: bytes,
    max_dimension: Optional[int] = None,
) -> Tuple[bytes, str]:
    """Validate, sanitize, strip metadata, and downscale an image entirely in memory.

    - Checks file size against configured limit.
    - Decodes image and ensures valid format (JPEG, PNG, WEBP, etc.).
    - Applies EXIF orientation to keep correct physical orientation.
    - Strips all EXIF metadata, GPS tags, device details, and timestamps.
    - Resizes to a maximum dimension if larger (default 1024px @ quality=82), conserving bandwidth and latency.
    - Re-encodes as clean, sanitized JPEG bytes in memory.
    """
    settings = get_settings()
    effective_max_dim = max_dimension if max_dimension is not None else settings.max_image_dimension
    jpeg_quality = getattr(settings, "image_jpeg_quality", 82)

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

            # Downscale if dimensions exceed effective_max_dim
            width, height = rgb_img.size
            if width > effective_max_dim or height > effective_max_dim:
                rgb_img.thumbnail((effective_max_dim, effective_max_dim), Image.Resampling.LANCZOS)

            # Re-encode to clean JPEG buffer without EXIF metadata
            output_buffer = io.BytesIO()
            rgb_img.save(
                output_buffer,
                format="JPEG",
                quality=jpeg_quality,
                optimize=True,
            )
            sanitized_bytes = output_buffer.getvalue()

            return sanitized_bytes, "image/jpeg"

    except Image.DecompressionBombError as exc:
        raise InvalidImageError("Image exceeds maximum allowed resolution (20 megapixels).") from exc
    except UnidentifiedImageError as exc:
        raise InvalidImageError("Uploaded file could not be recognized as a valid image format.") from exc
    except Exception as exc:
        if isinstance(exc, (InvalidImageError, ImageSizeExceededError)):
            raise
        raise InvalidImageError(f"Failed to process image: {str(exc)}") from exc


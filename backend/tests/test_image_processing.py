"""Tests for in-memory image validation and metadata stripping."""

import io
import pytest
from PIL import Image

from app.services.image import (
    ImageSizeExceededError,
    InvalidImageError,
    validate_and_sanitize_image,
)


def test_validate_and_sanitize_valid_jpeg(sample_jpeg_bytes: bytes) -> None:
    """Verify that a valid JPEG is processed in memory and returned as image/jpeg."""
    sanitized_bytes, mime = validate_and_sanitize_image(sample_jpeg_bytes)
    assert mime == "image/jpeg"
    assert isinstance(sanitized_bytes, bytes)
    assert len(sanitized_bytes) > 0

    with Image.open(io.BytesIO(sanitized_bytes)) as img:
        assert img.format == "JPEG"
        assert img.mode == "RGB"
        assert img.size == (100, 100)


def test_validate_and_sanitize_converts_png_to_jpeg(sample_png_bytes: bytes) -> None:
    """Verify that PNG images with alpha are converted cleanly to RGB JPEG."""
    sanitized_bytes, mime = validate_and_sanitize_image(sample_png_bytes)
    assert mime == "image/jpeg"

    with Image.open(io.BytesIO(sanitized_bytes)) as img:
        assert img.format == "JPEG"
        assert img.mode == "RGB"


def test_validate_and_sanitize_resizes_large_images() -> None:
    """Verify that images larger than max_dimension are downscaled maintaining aspect ratio."""
    buffer = io.BytesIO()
    # 2400 x 1200 image
    image = Image.new("RGB", (2400, 1200), color=(100, 100, 100))
    image.save(buffer, format="JPEG")

    sanitized_bytes, _ = validate_and_sanitize_image(buffer.getvalue(), max_dimension=1600)

    with Image.open(io.BytesIO(sanitized_bytes)) as img:
        assert max(img.size) <= 1600
        # Aspect ratio should remain 2:1
        assert img.size == (1600, 800)


def test_validate_and_sanitize_strips_exif_metadata() -> None:
    """Verify that EXIF metadata is stripped completely during sanitization."""
    from PIL import ExifTags

    buffer = io.BytesIO()
    image = Image.new("RGB", (150, 150), color=(255, 255, 255))
    exif_data = image.getexif()
    # Tag 0x010E is ImageDescription, 0x010F is Make
    exif_data[0x010E] = "Sensitive User Location/Description"
    exif_data[0x010F] = "TestCameraManufacturer"
    image.save(buffer, format="JPEG", exif=exif_data)

    # Sanitize image
    sanitized_bytes, _ = validate_and_sanitize_image(buffer.getvalue())

    # Verify no EXIF metadata survived
    with Image.open(io.BytesIO(sanitized_bytes)) as sanitized_img:
        exif = sanitized_img.getexif()
        assert 0x010E not in exif
        assert 0x010F not in exif


def test_validate_and_sanitize_rejects_corrupted_bytes() -> None:
    """Verify that invalid/corrupt data raises InvalidImageError."""
    corrupted_data = b"This is not a real image file, just random text bytes."
    with pytest.raises(InvalidImageError):
        validate_and_sanitize_image(corrupted_data)


def test_validate_and_sanitize_rejects_empty_bytes() -> None:
    """Verify that empty bytes raise InvalidImageError."""
    with pytest.raises(InvalidImageError):
        validate_and_sanitize_image(b"")


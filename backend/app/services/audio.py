"""In-memory audio upload validation and MIME normalization service."""

from typing import Optional, Tuple

from app.config import get_settings

MIN_AUDIO_BYTES = 32

SUPPORTED_AUDIO_MIME_TYPES: frozenset[str] = frozenset(
    {
        "audio/mp4",
        "audio/m4a",
        "audio/aac",
        "audio/mpeg",
        "audio/wav",
        "audio/ogg",
        "audio/webm",
        "audio/flac",
    }
)

_MIME_ALIASES: dict[str, str] = {
    "audio/x-m4a": "audio/m4a",
    "audio/m4a": "audio/m4a",
    "audio/mp4": "audio/mp4",
    "video/mp4": "audio/mp4",
    "audio/mp4a-latm": "audio/mp4",
    "audio/aac": "audio/aac",
    "audio/x-aac": "audio/aac",
    "audio/mp3": "audio/mpeg",
    "audio/mpeg": "audio/mpeg",
    "audio/wav": "audio/wav",
    "audio/x-wav": "audio/wav",
    "audio/wave": "audio/wav",
    "audio/ogg": "audio/ogg",
    "audio/opus": "audio/ogg",
    "audio/webm": "audio/webm",
    "video/webm": "audio/webm",
    "audio/flac": "audio/flac",
    "audio/x-flac": "audio/flac",
}

_EXT_TO_MIME: dict[str, str] = {
    ".m4a": "audio/m4a",
    ".mp4": "audio/mp4",
    ".aac": "audio/aac",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".opus": "audio/ogg",
    ".webm": "audio/webm",
    ".flac": "audio/flac",
}

_DISALLOWED_MAGIC_PREFIXES: tuple[bytes, ...] = (
    b"\xff\xd8\xff",  # JPEG
    b"\x89PNG\r\n\x1a\n",  # PNG
    b"GIF87a",
    b"GIF89a",
    b"%PDF",
    b"MZ",  # PE executable
    b"\x7fELF",  # ELF binary
    b"<!DOCTYPE",
    b"<html",
    b"<HTML",
)


class InvalidAudioError(ValueError):
    """Raised when an uploaded audio file is empty, corrupted, or unsupported."""


class AudioSizeExceededError(ValueError):
    """Raised when an uploaded audio file exceeds the allowed size limit."""


def _detect_magic_mime(raw: bytes) -> Optional[str]:
    """Detect canonical audio container MIME from leading magic bytes when recognizable."""
    if len(raw) >= 12 and raw[:4] == b"RIFF" and raw[8:12] == b"WAVE":
        return "audio/wav"
    if len(raw) >= 12 and raw[4:8] == b"ftyp":
        brand = raw[8:12]
        if brand.startswith(b"M4A"):
            return "audio/m4a"
        return "audio/mp4"
    if raw.startswith(b"fLaC"):
        return "audio/flac"
    if raw.startswith(b"OggS"):
        return "audio/ogg"
    if raw.startswith(b"\x1a\x45\xdf\xa3"):
        return "audio/webm"
    if raw.startswith(b"ID3") or (len(raw) >= 2 and raw[0] == 0xFF and (raw[1] & 0xE6) in (0xE2, 0xE4, 0xE6)):
        return "audio/mpeg"
    if len(raw) >= 2 and raw[0] == 0xFF and (raw[1] & 0xF6) == 0xF0:
        return "audio/aac"
    return None


def _normalize_declared_mime(content_type: Optional[str]) -> Optional[str]:
    if not content_type:
        return None
    base_ct = content_type.split(";", 1)[0].strip().lower()
    return _MIME_ALIASES.get(base_ct)


def _mime_from_filename(filename: Optional[str]) -> Optional[str]:
    if not filename:
        return None
    lower = filename.strip().lower()
    for ext, mime in _EXT_TO_MIME.items():
        if lower.endswith(ext):
            return mime
    return None


def validate_and_sanitize_audio(
    audio_bytes: bytes,
    content_type: Optional[str] = None,
    filename: Optional[str] = None,
    max_size_bytes: Optional[int] = None,
) -> Tuple[bytes, str]:
    """Validate an uploaded meal audio clip strictly in memory.

    - Rejects empty, truncated, oversized, or non-audio payloads (images, HTML, binaries).
    - Infers and normalizes canonical MIME type from container headers, Content-Type, or extension.
    - Never writes raw audio bytes to disk.
    """
    settings = get_settings()
    max_bytes = (
        max_size_bytes
        if max_size_bytes is not None
        else getattr(settings, "max_audio_size_bytes", 10 * 1024 * 1024)
    )

    if not audio_bytes or len(audio_bytes) < MIN_AUDIO_BYTES:
        raise InvalidAudioError("Audio recording is empty or too short to transcribe.")

    if len(audio_bytes) > max_bytes:
        max_mb = max(1, max_bytes // (1024 * 1024))
        raise AudioSizeExceededError(
            f"Audio recording exceeds the maximum allowed size limit of {max_mb}MB."
        )

    head = audio_bytes[:32].lstrip()
    for disallowed in _DISALLOWED_MAGIC_PREFIXES:
        if audio_bytes.startswith(disallowed) or head.startswith(disallowed):
            raise InvalidAudioError("Uploaded file is not a supported audio recording.")

    magic_mime = _detect_magic_mime(audio_bytes)
    declared_mime = _normalize_declared_mime(content_type)
    ext_mime = _mime_from_filename(filename)

    resolved_mime = magic_mime or declared_mime or ext_mime
    if not resolved_mime or resolved_mime not in SUPPORTED_AUDIO_MIME_TYPES:
        raise InvalidAudioError(
            "Unsupported audio format. Please record M4A, MP4, AAC, MP3, WAV, OGG, or WEBM audio."
        )

    return audio_bytes, resolved_mime

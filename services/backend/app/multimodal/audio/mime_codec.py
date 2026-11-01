"""T22: Cross-browser audio MIME and codec inspection.

Validates audio headers for:
- Chrome/Android: audio/webm (EBML Opus/Vorbis)
- Safari/iOS: audio/mp4, audio/x-m4a, audio/aac (ISO BMFF ftyp box)
- Firefox/Desktop: audio/ogg (OggS)
- Uncompressed: audio/wav (RIFF WAVE)
- Standard: audio/mpeg (ID3 or MPEG frame sync)
"""

ALLOWED_AUDIO_MIMES = {
    "audio/webm": [b"\x1a\x45\xdf\xa3"],
    "audio/mp4": [b"ftyp"],
    "audio/x-m4a": [b"ftyp"],
    "audio/aac": [b"\xff\xf1", b"\xff\xf9", b"ID3"],
    "audio/ogg": [b"OggS"],
    "audio/wav": [b"RIFF"],
    "audio/x-wav": [b"RIFF"],
    "audio/mpeg": [b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"],
    "audio/mp3": [b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"],
}

MAX_AUDIO_BYTES = 15 * 1024 * 1024  # 15 MB max audio file


def detect_audio_mime_from_bytes(data: bytes) -> str | None:
    """Inspects header bytes to detect genuine audio container format."""
    if len(data) < 4:
        return None

    # 1. WebM (EBML header \x1a\x45\xdf\xa3)
    if data.startswith(b"\x1a\x45\xdf\xa3"):
        return "audio/webm"

    # 2. Ogg container (OggS)
    if data.startswith(b"OggS"):
        return "audio/ogg"

    # 3. WAV (RIFF....WAVE)
    if data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WAVE":
        return "audio/wav"

    # 4. MP4 / M4A (ISO base media file format)
    # Typically offset 4-8 has "ftyp"
    if len(data) >= 8 and data[4:8] == b"ftyp":
        brand = data[8:12] if len(data) >= 12 else b""
        if brand in (b"M4A ", b"M4B ", b"M4P "):
            return "audio/x-m4a"
        return "audio/mp4"

    # 5. MP3 (ID3 tag or MPEG sync word 0xFFE / 0xFFF)
    if data.startswith(b"ID3"):
        return "audio/mpeg"
    if data.startswith((b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")):
        return "audio/mpeg"

    # 6. AAC ADTS headers (0xFFF1, 0xFFF9)
    if data.startswith((b"\xff\xf1", b"\xff\xf9")):
        return "audio/aac"

    return None


def validate_audio_file(data: bytes, declared_mime: str) -> tuple[bool, str | None, str | None]:
    """T22: Validates actual audio payload against declared MIME and security limits.

    Returns: (is_valid, detected_mime, error_detail)
    """
    if not data or len(data) == 0:
        return False, None, "Audio payload is empty."

    if len(data) > MAX_AUDIO_BYTES:
        return (
            False,
            None,
            f"Audio file exceeds maximum size of {MAX_AUDIO_BYTES // (1024 * 1024)} MB.",
        )

    # Reject active content / executables immediately
    if data.startswith((b"MZ", b"\x7fELF")):
        return False, None, "Executable binaries are strictly forbidden."

    lower_prefix = data[:512].lower()
    if b"<html" in lower_prefix or b"<?php" in lower_prefix or b"<script" in lower_prefix:
        return False, None, "Script or HTML active content is strictly forbidden."

    detected = detect_audio_mime_from_bytes(data)

    # Normalize declared
    declared = declared_mime.split(";")[0].strip().lower()

    if not detected:
        # Check if declared is in allowed list and header is a recognized loose match
        if declared in ALLOWED_AUDIO_MIMES:
            # Tolerant container check for certain browser recorder implementations
            for sig in ALLOWED_AUDIO_MIMES[declared]:
                if sig in data[:64]:
                    return True, declared, None
        return (
            False,
            None,
            f"Unsupported or unrecognized audio signature for declared MIME '{declared_mime}'.",
        )

    # Compatibility mapping: mp4/x-m4a and mpeg/mp3 and wav/x-wav are inter-compatible
    compat_pairs = {
        ("audio/mp4", "audio/x-m4a"),
        ("audio/x-m4a", "audio/mp4"),
        ("audio/mpeg", "audio/mp3"),
        ("audio/mp3", "audio/mpeg"),
        ("audio/wav", "audio/x-wav"),
        ("audio/x-wav", "audio/wav"),
    }

    if declared != detected and (declared, detected) not in compat_pairs:
        # Check if browser declared audio/webm with codecs=opus
        if declared == "audio/webm" and detected == "audio/webm":
            return True, "audio/webm", None
        return (
            False,
            detected,
            f"Declared audio MIME '{declared_mime}' does not match detected container '{detected}'.",
        )

    return True, detected, None

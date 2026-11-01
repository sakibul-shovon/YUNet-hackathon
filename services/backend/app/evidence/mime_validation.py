# Allowlisted MIME types for evidence ingestion
ALLOWED_MIME_TYPES = {
    # Documents
    "application/pdf",
    # Images
    "image/png",
    "image/jpeg",
    "image/webp",
    # Audio
    "audio/webm",
    "audio/ogg",
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/x-m4a",
}


def detect_mime_from_bytes(data: bytes) -> str | None:
    """T10: Inspects actual magic bytes to determine true MIME type and reject spoofed headers."""
    if not data or len(data) < 4:
        return None

    # PDF: %PDF-
    if data.startswith(b"%PDF-"):
        return "application/pdf"

    # PNG: \x89PNG\r\n\x1a\n
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"

    # JPEG: \xff\xd8\xff
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"

    # WEBP: RIFF....WEBP
    if data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WEBP":
        return "image/webp"

    # WAV: RIFF....WAVE
    if data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WAVE":
        return "audio/wav"

    # OGG: OggS
    if data.startswith(b"OggS"):
        return "audio/ogg"

    # MP3: ID3 or MPEG sync frames \xff\xfb, \xff\xf3, \xff\xf2
    if data.startswith(b"ID3") or (len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0):
        return "audio/mpeg"

    # MP4 / M4A: ....ftyp in first 16 bytes
    if len(data) >= 12 and data[4:8] == b"ftyp":
        return "audio/mp4"

    # WebM / MKV: \x1a\x45\xdf\xa3 (EBML Header)
    if data.startswith(b"\x1a\x45\xdf\xa3"):
        return "audio/webm"

    return None


def validate_file_signature(declared_mime: str, data: bytes) -> tuple[bool, str | None, str | None]:
    """T10: Validates that declared MIME matches the inspected file bytes.

    Returns: (is_valid, detected_mime, error_message)
    """
    # 1. Reject active content/executables immediately
    if data.startswith((b"MZ", b"\x7fELF")):
        return False, None, "Executable binaries are strictly forbidden."

    # Reject HTML/PHP/Script active content
    lower_prefix = data[:512].lower()
    if b"<html" in lower_prefix or b"<?php" in lower_prefix or b"<script" in lower_prefix:
        return False, None, "HTML or script active content is strictly forbidden."

    detected = detect_mime_from_bytes(data)
    if not detected:
        return (
            False,
            None,
            f"Unknown or unsupported binary signature for declared type '{declared_mime}'",
        )

    # Canonicalize declared
    declared = declared_mime.strip().lower()

    # Mappings for compatible variations
    compatible_groups = [
        {"audio/wav", "audio/x-wav"},
        {"audio/mpeg", "audio/mp3"},
        {"audio/mp4", "audio/x-m4a"},
        {"application/pdf"},
        {"image/png"},
        {"image/jpeg"},
        {"image/webp"},
        {"audio/webm"},
        {"audio/ogg"},
    ]

    for grp in compatible_groups:
        if detected in grp and declared in grp:
            return True, detected, None

    return (
        False,
        detected,
        f"MIME spoof detected: declared '{declared_mime}' but actual bytes are '{detected}'",
    )

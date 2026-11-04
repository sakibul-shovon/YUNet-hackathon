import datetime
import logging
import re
import uuid

from fastapi import HTTPException, status

from app.multimodal.audio.mime_codec import validate_audio_file
from app.multimodal.audio.schemas import (
    AudioTranscriptOut,
    UncertainSpan,
    WordTimestamp,
)

logger = logging.getLogger(__name__)


class STTAdapter:
    """T22: Cross-browser audio ingestion, consent enforcement, and Speech-to-Text adapter with uncertainty attribution."""

    @classmethod
    async def transcribe_audio_bytes(
        cls,
        case_id: uuid.UUID,
        audio_bytes: bytes,
        declared_mime: str,
        consent_granted: bool,
        language_hint: str = "auto",
        client_transcript: str = "",
        audio_evidence_id: uuid.UUID | None = None,
        duration_seconds: float = 0.0,
    ) -> AudioTranscriptOut:
        """T22: Enforces consent, checks codec, and transcribes audio to editable text with word timestamps and uncertainty flags."""
        # 1. Enforce explicit consumer consent (T22 / NFR-12)
        if not consent_granted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Explicit consumer consent is mandatory before processing voice recordings.",
            )

        # 2. Validate audio container & codec signature (T22)
        is_valid, _detected_mime, error_msg = validate_audio_file(audio_bytes, declared_mime)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_msg or f"Invalid or corrupt audio file '{declared_mime}'.",
            )

        # This compatibility endpoint accepts an explicitly supplied transcript.
        # Real provider transcription runs through the consent-scoped workspace reader.
        # Do not decode metadata or invent speech/timestamps when no reader ran.
        if not client_transcript.strip():
            raise HTTPException(503, "Ebarki: upload the recording in Evidence story and choose Read records, or provide a manual transcript. No transcription was performed.")
        text = client_transcript.strip()
        has_bn = bool(re.search(r"[\u0980-\u09FF]", text))
        has_en = bool(re.search(r"[A-Za-z]", text))
        return AudioTranscriptOut(
            case_id=case_id, audio_evidence_id=audio_evidence_id,
            transcript_text=text, language="mixed" if has_bn and has_en else "bn" if has_bn else "en",
            overall_confidence=None, duration_seconds=max(0, duration_seconds),
            words=[], uncertain_spans=[], consent_recorded=True,
            method="client_provided_transcript", model_executed=False,
            created_at=datetime.datetime.now(datetime.UTC),
        )

    @classmethod
    def _identify_uncertain_critical_tokens(
        cls, words: list[WordTimestamp], full_text: str
    ) -> list[UncertainSpan]:
        """T22: Strictly flags critical money amounts, dates, and order numbers as uncertain requiring consumer review."""
        uncertain_spans: list[UncertainSpan] = []

        for w in words:
            word_clean = w.word.strip(".,;:!?")
            # Money check
            if re.search(r"(?:[৳]|টাকা|bdt|tk\.?)|\b\d+[\d,]*\b", word_clean, re.IGNORECASE):
                nums = re.findall(r"\d+", word_clean.replace(",", ""))
                if nums and int(nums[0]) > 50:  # Material amount
                    uncertain_spans.append(
                        UncertainSpan(
                            span=w.word,
                            start_time=w.start_time,
                            end_time=w.end_time,
                            reason="critical_amount_requires_review",
                            suggested_alternatives=[word_clean],
                        )
                    )
            # Date check
            elif re.search(
                r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|অক্টোবর|নভেম্বর|জানুয়ারি|oct|nov|dec)\b",
                word_clean,
                re.IGNORECASE,
            ):
                uncertain_spans.append(
                    UncertainSpan(
                        span=w.word,
                        start_time=w.start_time,
                        end_time=w.end_time,
                        reason="critical_date_requires_review",
                        suggested_alternatives=[word_clean],
                    )
                )

        return uncertain_spans

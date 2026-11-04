import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field


class WordTimestamp(BaseModel):
    word: str
    start_time: float
    end_time: float
    confidence: float = 1.0


class UncertainSpan(BaseModel):
    span: str
    start_time: float
    end_time: float
    reason: str  # e.g. 'unclear_pronunciation', 'critical_amount_requires_review', 'low_confidence'
    suggested_alternatives: list[str] = Field(default_factory=list)


class AudioTranscriptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_id: uuid.UUID
    audio_evidence_id: uuid.UUID | None = None
    transcript_text: str
    language: str  # 'bn', 'en', 'mixed'
    overall_confidence: float | None
    method: str = 'client_provided_transcript'
    model_executed: bool = False
    duration_seconds: float
    words: list[WordTimestamp] = Field(default_factory=list)
    uncertain_spans: list[UncertainSpan] = Field(default_factory=list)
    consent_recorded: bool = True
    created_at: datetime.datetime

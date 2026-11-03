import datetime
import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FactAssertionCreate(BaseModel):
    field_name: str = Field(..., max_length=128)
    field_type: str = Field(..., pattern="^(money|date|boolean|string|select)$")
    raw_value: Any
    original_text: str | None = None
    origin: str = Field("user_statement", max_length=64)
    issue_id: uuid.UUID | None = None
    span_start: int | None = None
    span_end: int | None = None


class FactAssertionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    issue_id: uuid.UUID | None = None
    field_name: str
    field_type: str
    typed_value: Any
    original_text: str
    origin: str
    created_case_version: int
    is_active: bool
    created_at: datetime.datetime
    review_outcome: str | None = None


class FactReviewSubmission(BaseModel):
    review_outcome: str = Field(..., pattern="^(accepted|corrected|rejected|unsure)$")
    corrected_value: Any | None = None
    corrected_original_text: str | None = None
    rationale: str | None = None


class FactReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    assertion_id: uuid.UUID
    reviewer_principal_id: uuid.UUID
    review_outcome: str
    correction_assertion_id: uuid.UUID | None = None
    reviewed_case_version: int
    rationale: str | None = None
    reviewed_at: datetime.datetime


class FactResolutionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    field_name: str
    selected_assertion_id: uuid.UUID | None = None
    resolution_status: str
    rationale: str | None = None
    case_version: int
    resolved_at: datetime.datetime


class MultimodalFactProposal(BaseModel):
    field_name: str = Field(..., max_length=128)
    field_type: str = Field(..., pattern="^(money|date|boolean|string|select)$")
    raw_value: Any
    original_text: str
    origin: str = Field(
        "user_statement", max_length=64
    )  # 'voice_transcript', 'document_extraction', 'chat_screenshot'
    source_type: str = Field("evidence_span", max_length=64)
    locator_meta: dict[str, Any] | None = None


class MultimodalProposalResult(BaseModel):
    assertion: FactAssertionOut
    source_link_id: uuid.UUID
    has_conflict: bool = False
    conflicting_assertion_id: uuid.UUID | None = None
    conflict_message_en: str | None = None
    conflict_message_bn: str | None = None

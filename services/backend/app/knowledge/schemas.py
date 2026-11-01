import datetime
import uuid

from pydantic import BaseModel, Field


class SourceProvisionOut(BaseModel):
    id: uuid.UUID
    provision_path: str
    title: str
    text_content: str
    normalized_text: str
    page_number: int | None = None
    created_at: datetime.datetime


class SourceCandidateOut(BaseModel):
    id: uuid.UUID
    family_id: uuid.UUID
    version_tag: str
    issuer: str
    document_type: str
    applicability_status: str
    clean_text_hash: str
    created_at: datetime.datetime


class ReviewSubmission(BaseModel):
    scope: str = Field(..., pattern="^(origin_and_procedure|statutory_interpretation)$")
    decision: str = Field("approved", pattern="^(approved|rejected|conditional)$")
    rationale: str = Field(..., min_length=10)
    limitations: str | None = None


class ReviewResultOut(BaseModel):
    id: uuid.UUID
    source_version_id: uuid.UUID
    reviewer_name: str
    scope: str
    decision: str
    approved_at: datetime.datetime


class ReleaseBuildRequest(BaseModel):
    release_id: str = Field(..., pattern="^[A-Za-z0-9_.-]+$")
    release_mode: str = Field("procedure_guidance", pattern="^(procedure_guidance|reviewed_statutory_guidance)$")
    source_version_ids: list[uuid.UUID]
    rules: list[dict] = Field(default_factory=list)


class KnowledgeReleaseOut(BaseModel):
    id: uuid.UUID
    release_id: str
    release_mode: str
    manifest_hash: str
    is_active: bool
    created_at: datetime.datetime
    promoted_at: datetime.datetime | None = None

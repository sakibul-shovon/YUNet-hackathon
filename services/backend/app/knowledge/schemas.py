import datetime
import uuid
from typing import Any

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
    url: str
    status: str
    raw_hash: str
    origin_chain: dict[str, Any] = Field(default_factory=dict)
    fetched_at: datetime.datetime


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
    portal_maps: list[dict] = Field(default_factory=list)
    lexical_index_hash: str | None = None
    dense_index_model: str | None = None


class KnowledgeReleaseOut(BaseModel):
    id: uuid.UUID
    release_id: str
    release_mode: str
    manifest_hash: str
    is_active: bool
    manifest_data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime.datetime
    promoted_at: datetime.datetime | None = None


# --- P11 Extensions ---


class WatcherCheckRequest(BaseModel):
    source_id: str
    simulate_fixture: str | None = None


class WatcherCheckResponse(BaseModel):
    source_id: str
    target_url: str
    status: str
    change_type: str | None = None
    raw_hash: str | None = None
    clean_text_hash: str | None = None
    quarantine_reason: str | None = None
    error_message: str | None = None
    candidate_id: uuid.UUID | None = None
    fetched_at: datetime.datetime


class ManualImportRequest(BaseModel):
    family_slug: str
    title: str
    text_content: str
    issuer: str
    document_type: str = "statute"
    official_url: str | None = None
    publication_date: str | None = None
    commencement_date: str | None = None


class CandidateDiffOut(BaseModel):
    candidate_id: uuid.UUID
    family_slug: str
    is_current_law: bool = False
    publication_date: str | None = None
    commencement_date: str | None = None
    commencement_status: str
    has_transitional_clauses: bool = False
    transitional_notes: list[str] = Field(default_factory=list)
    impacted_rules: list[str] = Field(default_factory=list)
    impacted_domains: list[str] = Field(default_factory=list)
    provision_diffs: list[dict[str, Any]] = Field(default_factory=list)
    added_count: int = 0
    modified_count: int = 0
    repealed_count: int = 0
    unchanged_count: int = 0


class ReleaseRollbackRequest(BaseModel):
    target_release_id: str
    rationale: str = Field(..., min_length=5)


class SourceHealthItem(BaseModel):
    source_id: str
    title_en: str
    title_bn: str
    official_url: str
    document_type: str
    status: str
    health_status: str
    procedural_scope: str
    is_authoritative_for_penalties: bool = False
    notice: str | None = None


class SourceHealthResponse(BaseModel):
    active_release_id: str | None = None
    active_release_mode: str | None = None
    active_manifest_hash: str | None = None
    sources: list[SourceHealthItem] = Field(default_factory=list)


class ReassessmentQueueResult(BaseModel):
    release_id: str
    impacted_cases_count: int
    flagged_case_ids: list[uuid.UUID]
    affected_rules: list[str]


class CaseReassessmentResult(BaseModel):
    case_id: uuid.UUID
    reassessed_at: datetime.datetime
    release_id: str
    has_changed: bool
    prior_primary_action: str | None = None
    new_primary_action: str | None = None
    decision_diff: dict[str, Any] = Field(default_factory=dict)

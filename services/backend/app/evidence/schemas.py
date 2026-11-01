import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field


class UploadIntentCreate(BaseModel):
    case_id: uuid.UUID
    declared_filename: str = Field(..., min_length=1, max_length=255)
    declared_mime_type: str = Field(..., min_length=3, max_length=128)
    declared_byte_size: int = Field(..., ge=1, le=20 * 1024 * 1024)  # Max 20 MB per item


class UploadIntentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    intent_id: uuid.UUID
    case_id: uuid.UUID
    upload_url: str
    upload_token: str
    token_expires_at: datetime.datetime
    max_byte_size: int
    storage_kind: str


class UploadCompleteRequest(BaseModel):
    idempotency_key: str | None = None


class EvidenceItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_id: uuid.UUID
    original_filename: str
    declared_mime_type: str
    detected_mime_type: str | None = None
    byte_size: int
    sha256_hash: str | None = None
    status: str
    is_quarantined: bool
    rejection_reason: str | None = None
    rejection_code: str | None = None
    is_retryable: bool = False
    guidance_en: str | None = None
    guidance_bn: str | None = None
    created_at: datetime.datetime


class EvidenceSpanLinkCreate(BaseModel):
    assertion_id: uuid.UUID
    page_number: int | None = 1
    normalized_box: list[float] | None = None
    selected_text: str | None = None


class EvidenceSpanLinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    assertion_id: uuid.UUID
    evidence_id: uuid.UUID
    source_type: str
    page_number: int | None = None
    normalized_box: list[float] | None = None
    selected_text: str | None = None
    created_at: datetime.datetime


class ReconciliationItem(BaseModel):
    evidence_id: uuid.UUID
    filename: str
    amount_minor_units: int
    is_duplicate: bool = False
    is_linked: bool = True


class PaymentReconciliationResult(BaseModel):
    case_id: uuid.UUID
    narrated_amount_minor_units: int
    linked_evidence_total_minor_units: int
    discrepancy_minor_units: int
    is_reconciled: bool
    status: str  # 'reconciled', 'discrepancy', 'unlinked_evidence_available', 'no_receipts'
    reconciled_items: list[ReconciliationItem] = Field(default_factory=list)
    unlinked_items: list[ReconciliationItem] = Field(default_factory=list)
    prompt_en: str
    prompt_bn: str

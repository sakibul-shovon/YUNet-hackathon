import datetime
import uuid

from pydantic import BaseModel, Field


class PrincipalOut(BaseModel):
    id: uuid.UUID
    kind: str
    locale: str
    consent_revision: int
    created_at: datetime.datetime
    roles: list[str] = Field(default_factory=lambda: ["consumer"])


class GuestSessionResponse(BaseModel):
    principal_id: uuid.UUID
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes
    csrf_token: str


class UpgradeRequest(BaseModel):
    verified_user_id: str
    verified_email: str
    provider_access_token: str | None = None


class UpgradeResponse(BaseModel):
    principal_id: uuid.UUID
    kind: str
    access_token: str
    message: str


class ConsentCreate(BaseModel):
    purpose: str
    policy_version: str
    processor_version: str | None = None
    affirmative_action: str
    case_id: uuid.UUID | None = None


class ConsentOut(BaseModel):
    id: uuid.UUID
    principal_id: uuid.UUID
    case_id: uuid.UUID | None = None
    purpose: str
    policy_version: str
    processor_version: str | None = None
    affirmative_action: str
    granted_at: datetime.datetime
    withdrawn_at: datetime.datetime | None = None


class DeletionRequestCreate(BaseModel):
    case_id: uuid.UUID | None = None
    scope: str = "case"  # 'case' or 'principal_all'
    retention_acknowledged: bool = True


class DeletionRequestOut(BaseModel):
    id: uuid.UUID
    principal_id: uuid.UUID
    case_id: uuid.UUID | None = None
    scope: str
    status: str
    requested_at: datetime.datetime
    access_revoked_at: datetime.datetime | None = None
    completed_at: datetime.datetime | None = None

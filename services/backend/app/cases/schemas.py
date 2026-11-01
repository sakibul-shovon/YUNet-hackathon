import datetime
import uuid
from typing import Any

from pydantic import BaseModel, Field


class CaseCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    jurisdiction: str = Field("BD", max_length=8)
    locale: str = Field("en-BD", max_length=16)
    desired_outcomes: list[str] = Field(default_factory=list)
    incident_date: str | None = None
    merchant_name: str | None = None
    story_narrative: str | None = None
    is_demo: bool = False


class CaseUpdate(BaseModel):
    expected_version: int = Field(..., description="Mandatory expected row_version for optimistic concurrency")
    title: str | None = Field(None, min_length=3, max_length=255)
    desired_outcomes: list[str] | None = None
    merchant_name: str | None = None
    incident_date: str | None = None
    story_narrative: str | None = None
    lifecycle_status: str | None = None


class CaseOut(BaseModel):
    id: uuid.UUID
    principal_id: uuid.UUID
    display_reference: str
    title: str
    jurisdiction: str
    locale: str
    desired_outcomes: list[str]
    lifecycle_status: str
    consent_status: str = "active"
    row_version: int
    is_demo: bool
    incident_date: str | None = None
    merchant_name: str | None = None
    story_narrative: str | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime


class CaseListOut(BaseModel):
    items: list[CaseOut]
    total: int


class CaseEventOut(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    event_sequence: int
    event_type: str
    actor_type: str
    created_at: datetime.datetime
    payload: dict[str, Any]

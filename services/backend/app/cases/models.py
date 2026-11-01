import datetime
import uuid
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.identity.models import Principal


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    principal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("principals.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    display_reference: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(8), default="BD", nullable=False)
    locale: Mapped[str] = mapped_column(String(16), default="en-BD", nullable=False)
    desired_outcomes: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    lifecycle_status: Mapped[str] = mapped_column(
        String(32),
        default="draft",
        index=True,
        nullable=False,
    )  # 'draft', 'active', 'archived', 'deleting', 'deleted'
    row_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    incident_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    merchant_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    story_narrative: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        index=True,
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    principal: Mapped["Principal"] = relationship("Principal", back_populates="cases")
    snapshots: Mapped[list["CaseSnapshot"]] = relationship(
        "CaseSnapshot",
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="CaseSnapshot.version.desc()",
    )
    issue_tracks: Mapped[list["IssueTrack"]] = relationship(
        "IssueTrack",
        back_populates="case",
        cascade="all, delete-orphan",
    )
    events: Mapped[list["CaseEvent"]] = relationship(
        "CaseEvent",
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="CaseEvent.event_sequence.asc()",
    )
    external_references: Mapped[list["ExternalReference"]] = relationship(
        "ExternalReference",
        back_populates="case",
        cascade="all, delete-orphan",
    )
    reminders: Mapped[list["CaseReminder"]] = relationship(
        "CaseReminder",
        back_populates="case",
        cascade="all, delete-orphan",
    )


class CaseSnapshot(Base):
    __tablename__ = "case_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("cases.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    principal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("principals.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    canonical_input_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    fact_assertion_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    issue_state: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )

    case: Mapped["Case"] = relationship("Case", back_populates="snapshots")

    __table_args__ = (
        UniqueConstraint("case_id", "version", name="uq_case_snapshots_case_version"),
    )


class IssueTrack(Base):
    __tablename__ = "issue_tracks"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("cases.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    principal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("principals.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    canonical_taxonomy: Mapped[str] = mapped_column(String(128), nullable=False)
    hypothesis_state: Mapped[str] = mapped_column(
        String(32),
        default="hypothesis",
        nullable=False,
    )  # 'hypothesis', 'confirmed', 'rejected'
    user_review: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )  # 'accepted', 'corrected', 'rejected', 'unsure'
    desired_remedy: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )  # 'full_refund', 'partial_refund', 'replacement', 'repair', 'apology'
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )

    case: Mapped["Case"] = relationship("Case", back_populates="issue_tracks")


class CaseEvent(Base):
    __tablename__ = "case_events"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("cases.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    principal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("principals.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    event_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )  # 'consumer', 'system', 'reviewer'
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        nullable=True,
    )
    schema_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        index=True,
        nullable=False,
    )

    case: Mapped["Case"] = relationship("Case", back_populates="events")

    __table_args__ = (
        UniqueConstraint("case_id", "event_sequence", name="uq_case_events_case_seq"),
    )


class ExternalReference(Base):
    __tablename__ = "external_references"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("cases.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    principal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("principals.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    authority_or_channel: Mapped[str] = mapped_column(String(64), nullable=False)
    encrypted_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    origin: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )  # 'user_reported', 'official_receipt'
    reported_event_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )

    case: Mapped["Case"] = relationship("Case", back_populates="external_references")


class OutboxMessage(Base):
    __tablename__ = "outbox"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(64), nullable=False)
    aggregate_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        index=True,
        nullable=False,
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        index=True,
        nullable=False,
    )
    dispatched_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)


class CaseReminder(Base):
    __tablename__ = "case_reminders"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("cases.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    principal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("principals.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    reminder_title: Mapped[str] = mapped_column(String(255), nullable=False)
    remind_at: Mapped[str] = mapped_column(String(64), nullable=False)  # ISO 8601 UTC string
    category: Mapped[str] = mapped_column(
        String(64),
        default="personal_follow_up",
        nullable=False,
    )  # 'personal_follow_up', 'seller_response_sla', 'portal_check'
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )

    case: Mapped["Case"] = relationship("Case", back_populates="reminders")


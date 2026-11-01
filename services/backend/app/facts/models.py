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
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FactAssertion(Base):
    __tablename__ = "fact_assertions"

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
    issue_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("issue_tracks.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    field_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    field_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )  # 'money', 'date', 'boolean', 'string', 'select'
    typed_value: Mapped[dict[str, Any] | Any] = mapped_column(JSON, nullable=False)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    origin: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )  # 'user_statement', 'document_extraction', 'inferred_reconciliation', 'system_default'
    asserting_actor_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("principals.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_case_version: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        index=True,
        nullable=False,
    )

    # Relationships
    source_links: Mapped[list["FactSourceLink"]] = relationship(
        "FactSourceLink",
        back_populates="assertion",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list["FactReview"]] = relationship(
        "FactReview",
        foreign_keys="FactReview.assertion_id",
        back_populates="assertion",
        cascade="all, delete-orphan",
    )


class FactSourceLink(Base):
    __tablename__ = "fact_source_links"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    assertion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("fact_assertions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )  # 'user_narrative_span', 'document_span', 'external_verification'
    span_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    span_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    locator_meta: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )

    assertion: Mapped["FactAssertion"] = relationship("FactAssertion", back_populates="source_links")


class FactReview(Base):
    __tablename__ = "fact_reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    assertion_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("fact_assertions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    reviewer_principal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("principals.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    review_outcome: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )  # 'accepted', 'corrected', 'rejected', 'unsure'
    correction_assertion_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("fact_assertions.id", ondelete="SET NULL"),
        nullable=True,
    )
    reviewed_case_version: Mapped[int] = mapped_column(Integer, nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )

    assertion: Mapped["FactAssertion"] = relationship("FactAssertion", foreign_keys=[assertion_id], back_populates="reviews")


class FactResolution(Base):
    __tablename__ = "fact_resolutions"

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
    field_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    selected_assertion_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("fact_assertions.id", ondelete="SET NULL"),
        nullable=True,
    )
    resolution_status: Mapped[str] = mapped_column(
        String(32),
        default="resolved",
        nullable=False,
    )  # 'resolved', 'unresolved', 'contested', 'unknown'
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    case_version: Mapped[int] = mapped_column(Integer, nullable=False)
    resolved_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )

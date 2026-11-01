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


class SourceFamily(Base):
    __tablename__ = "source_families"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    issuer: Mapped[str] = mapped_column(String(255), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(8), default="BD", nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )

    versions: Mapped[list["SourceVersion"]] = relationship(
        "SourceVersion",
        back_populates="family",
        cascade="all, delete-orphan",
    )
    candidates: Mapped[list["SourceCandidate"]] = relationship(
        "SourceCandidate",
        back_populates="family",
        cascade="all, delete-orphan",
    )


class SourceCandidate(Base):
    __tablename__ = "source_candidates"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    family_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("source_families.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    origin_chain: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    raw_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        default="candidate",
        nullable=False,
    )  # 'discovered', 'fetched', 'quarantined', 'rejected', 'candidate'
    fetched_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )

    family: Mapped["SourceFamily"] = relationship("SourceFamily", back_populates="candidates")


class SourceVersion(Base):
    __tablename__ = "source_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    family_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("source_families.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    version_tag: Mapped[str] = mapped_column(String(64), nullable=False)  # e.g. "2009-enacted", "2026-v1"
    raw_bytes_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    text_content: Mapped[str] = mapped_column(Text, nullable=False)
    clean_text_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    issuer: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )  # 'statute', 'circular', 'procedure_guide', 'portal_map'
    publication_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    commencement_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    effective_from: Mapped[str | None] = mapped_column(String(32), nullable=True)
    effective_to: Mapped[str | None] = mapped_column(String(32), nullable=True)
    applicability_status: Mapped[str] = mapped_column(
        String(32),
        default="candidate",
        index=True,
        nullable=False,
    )  # 'candidate', 'approved', 'archived', 'superseded'
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )

    family: Mapped["SourceFamily"] = relationship("SourceFamily", back_populates="versions")
    provisions: Mapped[list["SourceProvision"]] = relationship(
        "SourceProvision",
        back_populates="source_version",
        cascade="all, delete-orphan",
    )
    approvals: Mapped[list["SourceApproval"]] = relationship(
        "SourceApproval",
        back_populates="source_version",
        cascade="all, delete-orphan",
    )


class SourceProvision(Base):
    __tablename__ = "source_provisions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    source_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("source_versions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    provision_path: Mapped[str] = mapped_column(String(64), index=True, nullable=False)  # e.g. "sec:45", "sec:45(2)"
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    text_content: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_text: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parent_provision_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("source_provisions.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )

    source_version: Mapped["SourceVersion"] = relationship("SourceVersion", back_populates="provisions")
    chunks: Mapped[list["RetrievalChunk"]] = relationship(
        "RetrievalChunk",
        back_populates="provision",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("source_version_id", "provision_path", name="uq_source_provision_path"),
    )


class SourceApproval(Base):
    __tablename__ = "source_approvals"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    source_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("source_versions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    provision_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("source_provisions.id", ondelete="CASCADE"),
        nullable=True,
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    reviewer_name: Mapped[str] = mapped_column(String(128), nullable=False)
    scope: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )  # 'origin_and_procedure', 'statutory_interpretation'
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    limitations: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision: Mapped[str] = mapped_column(String(32), default="approved", nullable=False)
    approved_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )

    source_version: Mapped["SourceVersion"] = relationship("SourceVersion", back_populates="approvals")


class KnowledgeRelease(Base):
    __tablename__ = "knowledge_releases"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    release_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    release_mode: Mapped[str] = mapped_column(
        String(32),
        default="procedure_guidance",
        nullable=False,
    )  # 'procedure_guidance', 'reviewed_statutory_guidance'
    manifest_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    manifest_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )
    promoted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class RetrievalChunk(Base):
    __tablename__ = "retrieval_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    release_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    provision_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("source_provisions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    normalized_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )

    provision: Mapped["SourceProvision"] = relationship("SourceProvision", back_populates="chunks")

import datetime
import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

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
    storage_kind: Mapped[str] = mapped_column(
        String(32),
        default="local_disk",
        nullable=False,
    )  # 'local_disk', 's3', 'supabase'
    quarantine_path: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )
    accepted_path: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )  # Sanitized display metadata, never a filesystem path!
    declared_mime_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    detected_mime_type: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    byte_size: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    sha256_hash: Mapped[str | None] = mapped_column(
        String(64),
        index=True,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="intent_created",
        index=True,
        nullable=False,
    )  # 'intent_created', 'quarantined', 'validating', 'accepted', 'rejected', 'quarantine_expired', 'deleted'
    rejection_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    rejection_code: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    is_retryable: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    guidance_en: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    guidance_bn: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    is_quarantined: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    upload_token: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )
    token_expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    intent_consumed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    quota_reserved_bytes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
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

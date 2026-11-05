"""Durable platform configuration and administrative action receipts."""
import datetime
import uuid

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AdminRecord(Base):
    __tablename__ = 'admin_records'
    key: Mapped[str] = mapped_column(String(240), primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC), nullable=False)


class AdminAuditEntry(Base):
    __tablename__ = 'admin_audit_entries'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC), nullable=False, index=True)

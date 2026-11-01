"""Evidence items and upload vault

Revision ID: 0004_evidence_vault
Revises: 0003_facts
Create Date: 2026-11-01 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0004_evidence_vault"
down_revision: Union[str, None] = "0003_facts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "evidence_items",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("case_id", sa.Uuid(), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("principal_id", sa.Uuid(), sa.ForeignKey("principals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("storage_kind", sa.String(length=32), nullable=False, server_default="local_disk"),
        sa.Column("quarantine_path", sa.String(length=512), nullable=False),
        sa.Column("accepted_path", sa.String(length=512), nullable=True),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("declared_mime_type", sa.String(length=128), nullable=False),
        sa.Column("detected_mime_type", sa.String(length=128), nullable=True),
        sa.Column("byte_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sha256_hash", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="intent_created"),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("rejection_code", sa.String(length=64), nullable=True),
        sa.Column("is_retryable", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("guidance_en", sa.Text(), nullable=True),
        sa.Column("guidance_bn", sa.Text(), nullable=True),
        sa.Column("is_quarantined", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("upload_token", sa.String(length=128), nullable=False),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("intent_consumed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("quota_reserved_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_evidence_items_case_id", "evidence_items", ["case_id"])
    op.create_index("ix_evidence_items_principal_id", "evidence_items", ["principal_id"])
    op.create_index("ix_evidence_items_upload_token", "evidence_items", ["upload_token"], unique=True)
    op.create_index("ix_evidence_items_status", "evidence_items", ["status"])
    op.create_index("ix_evidence_items_sha256_hash", "evidence_items", ["sha256_hash"])


def downgrade() -> None:
    op.drop_index("ix_evidence_items_sha256_hash", table_name="evidence_items")
    op.drop_index("ix_evidence_items_status", table_name="evidence_items")
    op.drop_index("ix_evidence_items_upload_token", table_name="evidence_items")
    op.drop_index("ix_evidence_items_principal_id", table_name="evidence_items")
    op.drop_index("ix_evidence_items_case_id", table_name="evidence_items")
    op.drop_table("evidence_items")

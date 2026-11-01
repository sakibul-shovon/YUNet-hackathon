"""Living case reminders and tracking

Revision ID: 0005_living_case_reminders
Revises: 0004_evidence_vault
Create Date: 2026-11-01 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0005_living_case_reminders"
down_revision: Union[str, None] = "0004_evidence_vault"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "case_reminders",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("case_id", sa.Uuid(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("principal_id", sa.Uuid(as_uuid=True), sa.ForeignKey("principals.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("reminder_title", sa.String(length=255), nullable=False),
        sa.Column("remind_at", sa.String(length=64), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False, server_default="personal_follow_up"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("case_reminders")


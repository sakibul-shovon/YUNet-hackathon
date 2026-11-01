"""Fact assertions, source links, reviews and resolutions

Revision ID: 0003_facts
Revises: 0002_knowledge
Create Date: 2026-11-01 11:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0003_facts"
down_revision: Union[str, None] = "0002_knowledge"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Fact Assertions
    op.create_table(
        "fact_assertions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("case_id", sa.Uuid(), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("issue_id", sa.Uuid(), sa.ForeignKey("issue_tracks.id", ondelete="SET NULL"), nullable=True),
        sa.Column("field_name", sa.String(length=128), nullable=False),
        sa.Column("field_type", sa.String(length=32), nullable=False),
        sa.Column("typed_value", sa.JSON(), nullable=False),
        sa.Column("original_text", sa.Text(), nullable=False),
        sa.Column("origin", sa.String(length=64), nullable=False),
        sa.Column("asserting_actor_id", sa.Uuid(), sa.ForeignKey("principals.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_case_version", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_fact_assertions_case_id", "fact_assertions", ["case_id"])
    op.create_index("ix_fact_assertions_issue_id", "fact_assertions", ["issue_id"])
    op.create_index("ix_fact_assertions_field_name", "fact_assertions", ["field_name"])
    op.create_index("ix_fact_assertions_is_active", "fact_assertions", ["is_active"])
    op.create_index("ix_fact_assertions_created_at", "fact_assertions", ["created_at"])

    # 2. Fact Source Links
    op.create_table(
        "fact_source_links",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("assertion_id", sa.Uuid(), sa.ForeignKey("fact_assertions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("span_start", sa.Integer(), nullable=True),
        sa.Column("span_end", sa.Integer(), nullable=True),
        sa.Column("locator_meta", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_fact_source_links_assertion_id", "fact_source_links", ["assertion_id"])

    # 3. Fact Reviews
    op.create_table(
        "fact_reviews",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("assertion_id", sa.Uuid(), sa.ForeignKey("fact_assertions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewer_principal_id", sa.Uuid(), sa.ForeignKey("principals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("review_outcome", sa.String(length=32), nullable=False),
        sa.Column("correction_assertion_id", sa.Uuid(), sa.ForeignKey("fact_assertions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reviewed_case_version", sa.Integer(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_fact_reviews_assertion_id", "fact_reviews", ["assertion_id"])
    op.create_index("ix_fact_reviews_reviewer_principal_id", "fact_reviews", ["reviewer_principal_id"])

    # 4. Fact Resolutions
    op.create_table(
        "fact_resolutions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("case_id", sa.Uuid(), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("field_name", sa.String(length=128), nullable=False),
        sa.Column("selected_assertion_id", sa.Uuid(), sa.ForeignKey("fact_assertions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("resolution_status", sa.String(length=32), nullable=False, server_default="resolved"),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("case_version", sa.Integer(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_fact_resolutions_case_id", "fact_resolutions", ["case_id"])
    op.create_index("ix_fact_resolutions_field_name", "fact_resolutions", ["field_name"])


def downgrade() -> None:
    op.drop_table("fact_resolutions")
    op.drop_table("fact_reviews")
    op.drop_table("fact_source_links")
    op.drop_table("fact_assertions")


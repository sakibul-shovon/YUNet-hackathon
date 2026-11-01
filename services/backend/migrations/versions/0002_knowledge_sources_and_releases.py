"""Knowledge sources, versions, provisions, approvals, releases and retrieval chunks

Revision ID: 0002_knowledge
Revises: 0001_initial
Create Date: 2026-11-01 11:12:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002_knowledge"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Source Families
    op.create_table(
        "source_families",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("issuer", sa.String(length=255), nullable=False),
        sa.Column("jurisdiction", sa.String(length=8), nullable=False, server_default="BD"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_source_families_slug", "source_families", ["slug"], unique=True)

    # 2. Source Candidates
    op.create_table(
        "source_candidates",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("family_id", sa.Uuid(), sa.ForeignKey("source_families.id", ondelete="CASCADE"), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("origin_chain", sa.JSON(), nullable=False),
        sa.Column("raw_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="candidate"),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_source_candidates_family_id", "source_candidates", ["family_id"])

    # 3. Source Versions
    op.create_table(
        "source_versions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("family_id", sa.Uuid(), sa.ForeignKey("source_families.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_tag", sa.String(length=64), nullable=False),
        sa.Column("raw_bytes_hash", sa.String(length=64), nullable=False),
        sa.Column("text_content", sa.Text(), nullable=False),
        sa.Column("clean_text_hash", sa.String(length=64), nullable=False),
        sa.Column("issuer", sa.String(length=255), nullable=False),
        sa.Column("document_type", sa.String(length=32), nullable=False),
        sa.Column("publication_date", sa.String(length=32), nullable=True),
        sa.Column("commencement_date", sa.String(length=32), nullable=True),
        sa.Column("effective_from", sa.String(length=32), nullable=True),
        sa.Column("effective_to", sa.String(length=32), nullable=True),
        sa.Column("applicability_status", sa.String(length=32), nullable=False, server_default="candidate"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_source_versions_family_id", "source_versions", ["family_id"])
    op.create_index("ix_source_versions_status", "source_versions", ["applicability_status"])

    # 4. Source Provisions
    op.create_table(
        "source_provisions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("source_version_id", sa.Uuid(), sa.ForeignKey("source_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provision_path", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("text_content", sa.Text(), nullable=False),
        sa.Column("normalized_text", sa.Text(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("parent_provision_id", sa.Uuid(), sa.ForeignKey("source_provisions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("source_version_id", "provision_path", name="uq_source_provision_path"),
    )
    op.create_index("ix_source_provisions_version_id", "source_provisions", ["source_version_id"])
    op.create_index("ix_source_provisions_path", "source_provisions", ["provision_path"])

    # 5. Source Approvals
    op.create_table(
        "source_approvals",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("source_version_id", sa.Uuid(), sa.ForeignKey("source_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provision_id", sa.Uuid(), sa.ForeignKey("source_provisions.id", ondelete="CASCADE"), nullable=True),
        sa.Column("reviewer_id", sa.Uuid(), nullable=False),
        sa.Column("reviewer_name", sa.String(length=128), nullable=False),
        sa.Column("scope", sa.String(length=64), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("limitations", sa.Text(), nullable=True),
        sa.Column("decision", sa.String(length=32), nullable=False, server_default="approved"),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_source_approvals_version_id", "source_approvals", ["source_version_id"])

    # 6. Knowledge Releases
    op.create_table(
        "knowledge_releases",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("release_id", sa.String(length=64), nullable=False),
        sa.Column("release_mode", sa.String(length=32), nullable=False, server_default="procedure_guidance"),
        sa.Column("manifest_hash", sa.String(length=64), nullable=False),
        sa.Column("manifest_data", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("promoted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_knowledge_releases_release_id", "knowledge_releases", ["release_id"], unique=True)
    op.create_index("ix_knowledge_releases_is_active", "knowledge_releases", ["is_active"])

    # 7. Retrieval Chunks
    op.create_table(
        "retrieval_chunks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("release_id", sa.String(length=64), nullable=False),
        sa.Column("provision_id", sa.Uuid(), sa.ForeignKey("source_provisions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("normalized_text", sa.Text(), nullable=False),
        sa.Column("is_approved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_retrieval_chunks_release_id", "retrieval_chunks", ["release_id"])
    op.create_index("ix_retrieval_chunks_is_approved", "retrieval_chunks", ["is_approved"])


def downgrade() -> None:
    op.drop_table("retrieval_chunks")
    op.drop_table("knowledge_releases")
    op.drop_table("source_approvals")
    op.drop_table("source_provisions")
    op.drop_table("source_versions")
    op.drop_table("source_candidates")
    op.drop_table("source_families")


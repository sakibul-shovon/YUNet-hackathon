"""Initial identity, session, case, consent, event and outbox tables

Revision ID: 0001_initial
Revises: 
Create Date: 2026-11-01 03:36:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Principals
    op.create_table(
        "principals",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("kind", sa.String(length=32), nullable=False, server_default="anonymous"),
        sa.Column("locale", sa.String(length=16), nullable=False, server_default="en-BD"),
        sa.Column("consent_revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 2. Web Sessions
    op.create_table(
        "web_sessions",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_token_hash", sa.String(length=64), nullable=False),
        sa.Column("principal_id", sa.UUID(as_uuid=True), sa.ForeignKey("principals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("encrypted_refresh_token", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refresh_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_web_sessions_token_hash", "web_sessions", ["session_token_hash"], unique=True)
    op.create_index("ix_web_sessions_principal_id", "web_sessions", ["principal_id"])
    op.create_index("ix_web_sessions_expires_at", "web_sessions", ["expires_at"])

    # 3. Actor Roles
    op.create_table(
        "actor_roles",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("principal_id", sa.UUID(as_uuid=True), sa.ForeignKey("principals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("grant_origin", sa.String(length=64), nullable=False),
        sa.Column("scope", sa.String(length=64), nullable=False, server_default="global"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("principal_id", "role", "scope", name="uq_actor_roles_principal_role_scope"),
    )
    op.create_index("ix_actor_roles_principal_id", "actor_roles", ["principal_id"])

    # 4. Cases
    op.create_table(
        "cases",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("principal_id", sa.UUID(as_uuid=True), sa.ForeignKey("principals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("display_reference", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("jurisdiction", sa.String(length=8), nullable=False, server_default="BD"),
        sa.Column("locale", sa.String(length=16), nullable=False, server_default="en-BD"),
        sa.Column("desired_outcomes", sa.JSON(), nullable=False),
        sa.Column("lifecycle_status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("row_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_demo", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("incident_date", sa.String(length=32), nullable=True),
        sa.Column("merchant_name", sa.String(length=255), nullable=True),
        sa.Column("story_narrative", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_cases_display_reference", "cases", ["display_reference"], unique=True)
    op.create_index("ix_cases_principal_id", "cases", ["principal_id"])
    op.create_index("ix_cases_lifecycle_status", "cases", ["lifecycle_status"])
    op.create_index("ix_cases_created_at", "cases", ["created_at"])
    op.create_index("ix_cases_principal_lifecycle", "cases", ["principal_id", "lifecycle_status"])

    # 5. Case Snapshots
    op.create_table(
        "case_snapshots",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", sa.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("principal_id", sa.UUID(as_uuid=True), sa.ForeignKey("principals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("canonical_input_hash", sa.String(length=64), nullable=False),
        sa.Column("fact_assertion_ids", sa.JSON(), nullable=False),
        sa.Column("issue_state", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("case_id", "version", name="uq_case_snapshots_case_version"),
    )
    op.create_index("ix_case_snapshots_case_id", "case_snapshots", ["case_id"])
    op.create_index("ix_case_snapshots_principal_id", "case_snapshots", ["principal_id"])

    # 6. Issue Tracks
    op.create_table(
        "issue_tracks",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", sa.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("principal_id", sa.UUID(as_uuid=True), sa.ForeignKey("principals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("canonical_taxonomy", sa.String(length=128), nullable=False),
        sa.Column("hypothesis_state", sa.String(length=32), nullable=False, server_default="hypothesis"),
        sa.Column("user_review", sa.String(length=32), nullable=True),
        sa.Column("desired_remedy", sa.String(length=64), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_issue_tracks_case_id", "issue_tracks", ["case_id"])
    op.create_index("ix_issue_tracks_principal_id", "issue_tracks", ["principal_id"])
    op.create_index("ix_issue_tracks_active", "issue_tracks", ["active"])

    # 7. Case Events
    op.create_table(
        "case_events",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", sa.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("principal_id", sa.UUID(as_uuid=True), sa.ForeignKey("principals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_sequence", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("actor_type", sa.String(length=32), nullable=False),
        sa.Column("actor_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("case_id", "event_sequence", name="uq_case_events_case_seq"),
    )
    op.create_index("ix_case_events_case_id", "case_events", ["case_id"])
    op.create_index("ix_case_events_principal_id", "case_events", ["principal_id"])
    op.create_index("ix_case_events_created_at", "case_events", ["created_at"])

    # 8. External References
    op.create_table(
        "external_references",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", sa.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("principal_id", sa.UUID(as_uuid=True), sa.ForeignKey("principals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("authority_or_channel", sa.String(length=64), nullable=False),
        sa.Column("encrypted_reference", sa.Text(), nullable=True),
        sa.Column("origin", sa.String(length=32), nullable=False),
        sa.Column("reported_event_date", sa.String(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_external_references_case_id", "external_references", ["case_id"])
    op.create_index("ix_external_references_principal_id", "external_references", ["principal_id"])

    # 9. Consents
    op.create_table(
        "consents",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("principal_id", sa.UUID(as_uuid=True), sa.ForeignKey("principals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("case_id", sa.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=True),
        sa.Column("purpose", sa.String(length=64), nullable=False),
        sa.Column("policy_version", sa.String(length=32), nullable=False),
        sa.Column("processor_version", sa.String(length=64), nullable=True),
        sa.Column("affirmative_action", sa.String(length=64), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_consents_principal_id", "consents", ["principal_id"])
    op.create_index("ix_consents_case_id", "consents", ["case_id"])

    # 10. Deletion Requests
    op.create_table(
        "deletion_requests",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("principal_id", sa.UUID(as_uuid=True), sa.ForeignKey("principals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("case_id", sa.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=True),
        sa.Column("scope", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("access_revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retries", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("exceptional_retention_reason", sa.Text(), nullable=True),
    )
    op.create_index("ix_deletion_requests_principal_id", "deletion_requests", ["principal_id"])
    op.create_index("ix_deletion_requests_case_id", "deletion_requests", ["case_id"])

    # 11. Outbox
    op.create_table(
        "outbox",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("aggregate_type", sa.String(length=64), nullable=False),
        sa.Column("aggregate_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("dispatched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
    )
    op.create_index("ix_outbox_aggregate_id", "outbox", ["aggregate_id"])
    op.create_index("ix_outbox_created_at", "outbox", ["created_at"])

    # PostgreSQL RLS Configuration
    bind = op.get_bind()
    if bind and bind.dialect.name == "postgresql":
        tenant_tables = [
            "cases",
            "case_snapshots",
            "issue_tracks",
            "case_events",
            "external_references",
            "consents",
            "deletion_requests",
            "web_sessions",
        ]
        for tbl in tenant_tables:
            op.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY;")
            op.execute(
                f"CREATE POLICY {tbl}_tenant_isolation ON {tbl} "
                f"FOR ALL USING (principal_id = NULLIF(current_setting('app.current_principal_id', true), '')::uuid);"
            )


def downgrade() -> None:
    bind = op.get_bind()
    if bind and bind.dialect.name == "postgresql":
        tenant_tables = [
            "cases",
            "case_snapshots",
            "issue_tracks",
            "case_events",
            "external_references",
            "consents",
            "deletion_requests",
            "web_sessions",
        ]
        for tbl in tenant_tables:
            op.execute(f"DROP POLICY IF EXISTS {tbl}_tenant_isolation ON {tbl};")

    op.drop_table("outbox")
    op.drop_table("deletion_requests")
    op.drop_table("consents")
    op.drop_table("external_references")
    op.drop_table("case_events")
    op.drop_table("issue_tracks")
    op.drop_table("case_snapshots")
    op.drop_table("cases")
    op.drop_table("actor_roles")
    op.drop_table("web_sessions")
    op.drop_table("principals")


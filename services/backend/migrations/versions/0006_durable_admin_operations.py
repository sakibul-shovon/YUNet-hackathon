"""Ebarki durable administrative records and action receipts."""
from alembic import op
import sqlalchemy as sa

revision = '0006_durable_admin_operations'
down_revision = '0005_living_case_reminders'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('admin_records',
        sa.Column('key', sa.String(240), primary_key=True),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False))
    op.create_table('admin_audit_entries',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_index('ix_admin_audit_entries_created_at', 'admin_audit_entries', ['created_at'])


def downgrade():
    op.drop_index('ix_admin_audit_entries_created_at', table_name='admin_audit_entries')
    op.drop_table('admin_audit_entries')
    op.drop_table('admin_records')

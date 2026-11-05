"""Ebarki schema coverage for registered users, runs, documents and consent state."""
from alembic import op
import sqlalchemy as sa

revision = '0007_workspace_persistence'
down_revision = '0006_durable_admin_operations'
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if 'consent_status' not in {column['name'] for column in inspector.get_columns('cases')}:
        op.add_column('cases', sa.Column('consent_status', sa.String(32), nullable=False, server_default='active'))
    if 'user_accounts' not in tables:
        op.create_table('user_accounts',
            sa.Column('id', sa.Uuid(), primary_key=True),
            sa.Column('principal_id', sa.Uuid(), sa.ForeignKey('principals.id', ondelete='CASCADE'), nullable=False),
            sa.Column('email', sa.String(255), nullable=False),
            sa.Column('full_name', sa.String(255), nullable=False),
            sa.Column('phone', sa.String(32), nullable=True),
            sa.Column('password_hash', sa.String(255), nullable=False),
            sa.Column('is_demo_judge', sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
        op.create_index('ix_user_accounts_principal_id', 'user_accounts', ['principal_id'], unique=True)
        op.create_index('ix_user_accounts_email', 'user_accounts', ['email'], unique=True)
    if 'case_processing_runs' not in tables:
        op.create_table('case_processing_runs',
            sa.Column('id', sa.Uuid(), primary_key=True),
            sa.Column('case_id', sa.Uuid(), sa.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False),
            sa.Column('principal_id', sa.Uuid(), sa.ForeignKey('principals.id', ondelete='CASCADE'), nullable=False),
            sa.Column('operation', sa.String(32), nullable=False),
            sa.Column('locale', sa.String(8), nullable=False),
            sa.Column('status', sa.String(32), nullable=False),
            sa.Column('case_version', sa.Integer(), nullable=False),
            sa.Column('cancel_requested', sa.Boolean(), nullable=False),
            sa.Column('stages', sa.JSON(), nullable=False),
            sa.Column('result', sa.JSON(), nullable=False),
            sa.Column('error_code', sa.String(64), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True))
        op.create_index('ix_case_processing_runs_case_id', 'case_processing_runs', ['case_id'])
        op.create_index('ix_case_processing_runs_principal_id', 'case_processing_runs', ['principal_id'])
    if 'prepared_document_versions' not in tables:
        op.create_table('prepared_document_versions',
            sa.Column('id', sa.Uuid(), primary_key=True),
            sa.Column('case_id', sa.Uuid(), sa.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False),
            sa.Column('principal_id', sa.Uuid(), sa.ForeignKey('principals.id', ondelete='CASCADE'), nullable=False),
            sa.Column('document_type', sa.String(64), nullable=False),
            sa.Column('locale', sa.String(8), nullable=False),
            sa.Column('case_version', sa.Integer(), nullable=False),
            sa.Column('revision', sa.Integer(), nullable=False),
            sa.Column('content', sa.JSON(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
        op.create_index('ix_prepared_document_versions_case_id', 'prepared_document_versions', ['case_id'])
        op.create_index('ix_prepared_document_versions_principal_id', 'prepared_document_versions', ['principal_id'])


def downgrade():
    op.drop_table('prepared_document_versions')
    op.drop_table('case_processing_runs')
    op.drop_table('user_accounts')
    with op.batch_alter_table('cases') as batch:
        batch.drop_column('consent_status')

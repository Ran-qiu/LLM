"""Cleanup templates/shares and add rpm_limit to api_keys

Revision ID: 003
Revises: 002
Create Date: 2025-12-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add rpm_limit to api_keys
    op.add_column('api_keys', sa.Column('rpm_limit', sa.Integer(), nullable=False, server_default='60'))
    
    # Drop templates table
    op.drop_index('idx_templates_user_updated', table_name='templates')
    op.drop_index('ix_templates_user_id', table_name='templates')
    op.drop_index('ix_templates_id', table_name='templates')
    op.drop_table('templates')

    # Drop shares table
    op.drop_index('idx_shares_conv_active', table_name='shares')
    op.drop_index('idx_shares_user_created', table_name='shares')
    op.drop_index('ix_shares_user_id', table_name='shares')
    op.drop_index('ix_shares_conversation_id', table_name='shares')
    op.drop_index('ix_shares_share_token', table_name='shares')
    op.drop_index('ix_shares_id', table_name='shares')
    op.drop_table('shares')


def downgrade() -> None:
    # Re-create shares table (simplified for downgrade)
    op.create_table(
        'shares',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('share_token', sa.String(length=36), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Re-create templates table (simplified for downgrade)
    op.create_table(
        'templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Remove rpm_limit
    op.drop_column('api_keys', 'rpm_limit')

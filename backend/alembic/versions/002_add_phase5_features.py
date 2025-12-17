"""Add Phase 5 features: tags, shares, templates

Revision ID: 002
Revises: 001
Create Date: 2025-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tags_id'), 'tags', ['id'], unique=False)
    op.create_index(op.f('ix_tags_user_id'), 'tags', ['user_id'], unique=False)

    # Create conversation_tags association table
    op.create_table(
        'conversation_tags',
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('conversation_id', 'tag_id')
    )

    # Create shares table
    op.create_table(
        'shares',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('share_token', sa.String(length=36), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('access_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shares_id'), 'shares', ['id'], unique=False)
    op.create_index(op.f('ix_shares_share_token'), 'shares', ['share_token'], unique=True)
    op.create_index(op.f('ix_shares_conversation_id'), 'shares', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_shares_user_id'), 'shares', ['user_id'], unique=False)

    # Create templates table
    op.create_table(
        'templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('title_template', sa.String(length=200), nullable=False, server_default='New Conversation'),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_templates_id'), 'templates', ['id'], unique=False)
    op.create_index(op.f('ix_templates_user_id'), 'templates', ['user_id'], unique=False)

    # Add performance indexes for common query patterns
    # Conversations: user-based queries with sorting
    op.create_index('idx_conversations_user_updated', 'conversations', ['user_id', 'updated_at'], unique=False)

    # Messages: conversation-based queries
    op.create_index('idx_messages_conv_created', 'messages', ['conversation_id', 'created_at'], unique=False)

    # Tags: user-based queries
    op.create_index('idx_tags_user_name', 'tags', ['user_id', 'name'], unique=False)

    # Shares: user-based and conversation-based queries
    op.create_index('idx_shares_user_created', 'shares', ['user_id', 'created_at'], unique=False)
    op.create_index('idx_shares_conv_active', 'shares', ['conversation_id', 'is_active'], unique=False)

    # Templates: user-based and public templates
    op.create_index('idx_templates_user_updated', 'templates', ['user_id', 'updated_at'], unique=False)
    # Note: SQLite doesn't support partial indexes with WHERE clause in Alembic
    # For PostgreSQL/MySQL, add: op.create_index('idx_templates_public_usage', 'templates', ['is_public', 'usage_count'], unique=False)


def downgrade() -> None:
    # Drop performance indexes
    op.drop_index('idx_templates_user_updated', table_name='templates')
    op.drop_index('idx_shares_conv_active', table_name='shares')
    op.drop_index('idx_shares_user_created', table_name='shares')
    op.drop_index('idx_tags_user_name', table_name='tags')
    op.drop_index('idx_messages_conv_created', table_name='messages')
    op.drop_index('idx_conversations_user_updated', table_name='conversations')

    # Drop tables
    op.drop_index(op.f('ix_templates_user_id'), table_name='templates')
    op.drop_index(op.f('ix_templates_id'), table_name='templates')
    op.drop_table('templates')

    op.drop_index(op.f('ix_shares_user_id'), table_name='shares')
    op.drop_index(op.f('ix_shares_conversation_id'), table_name='shares')
    op.drop_index(op.f('ix_shares_share_token'), table_name='shares')
    op.drop_index(op.f('ix_shares_id'), table_name='shares')
    op.drop_table('shares')

    op.drop_table('conversation_tags')

    op.drop_index(op.f('ix_tags_user_id'), table_name='tags')
    op.drop_index(op.f('ix_tags_id'), table_name='tags')
    op.drop_table('tags')

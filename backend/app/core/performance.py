"""
Database Performance Optimization Guide

This module documents database optimization strategies and provides
utilities for improving query performance.
"""

# ==========================================
# Current Optimizations
# ==========================================

"""
1. INDEXES
----------
All models have indexes on:
- Primary keys (id) - automatic
- Foreign keys (user_id, conversation_id, etc.)
- Unique fields (username, email, share_token)
- Frequently queried fields (created_at, updated_at)

2. CASCADE DELETES
------------------
Proper cascade configurations prevent orphaned records:
- User → Conversations, APIKeys, Tags, Shares, Templates
- Conversation → Messages, Shares
- All use "CASCADE" or "all, delete-orphan"

3. RELATIONSHIP LOADING
-----------------------
- Default: lazy loading (prevents unnecessary joins)
- For list endpoints: should use joinedload() where needed
- Message ordering uses order_by in relationship definition
"""

# ==========================================
# Recommended Query Optimizations
# ==========================================

"""
1. EAGER LOADING FOR COMMON PATTERNS
------------------------------------
For endpoints that always need related data, use eager loading:

from sqlalchemy.orm import joinedload, selectinload

# Example: Load conversation with messages
conversation = db.query(Conversation).options(
    selectinload(Conversation.messages)
).filter(Conversation.id == conv_id).first()

# Example: Load conversation with tags and API key
conversation = db.query(Conversation).options(
    selectinload(Conversation.tags),
    joinedload(Conversation.api_key)
).filter(Conversation.id == conv_id).first()

2. COMPOSITE INDEXES
-------------------
For complex queries, add composite indexes in migrations:

# Example: Index for getting user's active conversations
CREATE INDEX idx_conversations_user_updated
ON conversations(user_id, updated_at DESC);

# Example: Index for searching messages
CREATE INDEX idx_messages_conversation_created
ON messages(conversation_id, created_at ASC);

# Example: Index for tag-based queries
CREATE INDEX idx_conversation_tags_lookup
ON conversation_tags(tag_id, conversation_id);

3. QUERY OPTIMIZATION PATTERNS
------------------------------

# BAD: N+1 query problem
conversations = db.query(Conversation).filter(
    Conversation.user_id == user_id
).all()
for conv in conversations:
    msg_count = len(conv.messages)  # Triggers separate query each time!

# GOOD: Use subquery or aggregate
from sqlalchemy import func
conversations = db.query(
    Conversation,
    func.count(Message.id).label('msg_count')
).outerjoin(Message).filter(
    Conversation.user_id == user_id
).group_by(Conversation.id).all()

4. PAGINATION BEST PRACTICES
----------------------------
Always use skip/limit for large result sets:
- Default limit: 50-100 items
- Maximum limit: Enforce upper bound (e.g., 1000)
- Use cursor-based pagination for very large datasets

5. DATABASE-LEVEL OPTIMIZATIONS
-------------------------------
# Connection pooling (already configured in database.py)
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,  # For SQLite
    # For PostgreSQL/MySQL:
    # pool_size=10,
    # max_overflow=20,
    # pool_pre_ping=True
)

# Query result caching
# See caching.py for implementation

6. MONITORING AND PROFILING
---------------------------
# Enable SQL query logging for development
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Profile slow queries
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement,
                          parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement,
                         parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    if total > 0.1:  # Log queries slower than 100ms
        logger.warning(f"Slow query ({total:.2f}s): {statement}")
"""

# ==========================================
# Migration Script for Additional Indexes
# ==========================================

MIGRATION_SQL = """
-- Add composite indexes for common query patterns

-- Conversations: user-based queries with sorting
CREATE INDEX IF NOT EXISTS idx_conversations_user_updated
ON conversations(user_id, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversations_user_model
ON conversations(user_id, model);

-- Messages: conversation-based queries
CREATE INDEX IF NOT EXISTS idx_messages_conv_created
ON messages(conversation_id, created_at ASC);

CREATE INDEX IF NOT EXISTS idx_messages_conv_role
ON messages(conversation_id, role);

-- Tags: user-based queries
CREATE INDEX IF NOT EXISTS idx_tags_user_name
ON tags(user_id, name);

-- Shares: token-based and user-based lookups
CREATE INDEX IF NOT EXISTS idx_shares_user_created
ON shares(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_shares_conv_active
ON shares(conversation_id, is_active);

-- Templates: user-based and public templates
CREATE INDEX IF NOT EXISTS idx_templates_user_updated
ON templates(user_id, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_templates_public_usage
ON templates(is_public, usage_count DESC)
WHERE is_public = 1;

-- API Keys: user-based and provider filtering
CREATE INDEX IF NOT EXISTS idx_apikeys_user_provider
ON api_keys(user_id, provider, is_active);

-- Statistics queries: time-based aggregations
CREATE INDEX IF NOT EXISTS idx_messages_created_tokens
ON messages(created_at, conversation_id, total_tokens, cost);
"""

# To apply these indexes, create an Alembic migration:
# alembic revision -m "add_performance_indexes"
# Then add the SQL above to the upgrade() function

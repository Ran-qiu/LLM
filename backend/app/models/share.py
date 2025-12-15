from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Share(Base):
    """Share model for sharing conversations"""
    __tablename__ = "shares"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Share details
    share_token = Column(String(36), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    password = Column(String(255), nullable=True)  # Hashed password for protected shares
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Optional expiration
    is_active = Column(Boolean, default=True, nullable=False)

    # Tracking
    access_count = Column(Integer, default=0, nullable=False)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="shares")
    user = relationship("User", back_populates="shares")

    def __repr__(self):
        return f"<Share(id={self.id}, token='{self.share_token}', conversation_id={self.conversation_id})>"

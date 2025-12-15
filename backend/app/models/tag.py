from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


# Association table for many-to-many relationship between conversations and tags
conversation_tags = Table(
    'conversation_tags',
    Base.metadata,
    Column('conversation_id', Integer, ForeignKey('conversations.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
)


class Tag(Base):
    """Tag model for organizing conversations"""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    color = Column(String(7), nullable=True)  # Hex color code, e.g., #FF5733
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="tags")
    conversations = relationship("Conversation", secondary=conversation_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', user_id={self.user_id})>"

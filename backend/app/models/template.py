from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Template(Base):
    """Template model for conversation templates"""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Template details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    title_template = Column(String(200), nullable=False, default="New Conversation")
    model = Column(String(100), nullable=False)  # Default model for this template
    system_prompt = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)  # Whether template is shared publicly

    # Usage tracking
    usage_count = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="templates")

    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}', user_id={self.user_id})>"

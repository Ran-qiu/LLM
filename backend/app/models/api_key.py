from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Provider information
    provider = Column(String(50), nullable=False, index=True)  # openai, claude, gemini, ollama, custom, etc.
    name = Column(String(100), nullable=False)  # User-friendly name for this API key

    # Encrypted API key
    encrypted_key = Column(Text, nullable=True)  # Encrypted API key (nullable for Ollama)

    # Custom configuration (for Ollama, LangChain, custom models)
    custom_config = Column(JSON, nullable=True)  # Store base_url, model_type, etc.

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    rpm_limit = Column(Integer, default=60, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="api_keys")
    conversations = relationship("Conversation", back_populates="api_key")

    def __repr__(self):
        return f"<APIKey(id={self.id}, provider='{self.provider}', name='{self.name}')>"

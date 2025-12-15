from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class APIKeyBase(BaseModel):
    provider: str = Field(..., max_length=50, description="LLM provider name (openai, claude, gemini, ollama, custom, etc.)")
    name: str = Field(..., max_length=100, description="User-friendly name for this API key")


class APIKeyCreate(APIKeyBase):
    api_key: Optional[str] = Field(None, description="API key (optional for Ollama)")
    custom_config: Optional[Dict[str, Any]] = Field(None, description="Custom configuration for Ollama, LangChain, etc.")


class APIKeyUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    api_key: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class APIKeyInDB(APIKeyBase):
    id: int
    user_id: int
    encrypted_key: Optional[str]
    custom_config: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class APIKeyResponse(BaseModel):
    id: int
    provider: str
    name: str
    is_active: bool
    custom_config: Optional[Dict[str, Any]]
    created_at: datetime
    last_used_at: Optional[datetime]
    # Note: We don't return the encrypted_key for security

    model_config = ConfigDict(from_attributes=True)

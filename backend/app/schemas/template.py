from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TemplateBase(BaseModel):
    """Base schema for template"""
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    title_template: str = Field(..., max_length=200, description="Default conversation title")
    model: str = Field(..., max_length=100, description="Default model (e.g., gpt-4, claude-3-opus)")
    system_prompt: Optional[str] = Field(None, description="System prompt/instructions")
    is_public: bool = Field(False, description="Whether template is publicly visible")


class TemplateCreate(TemplateBase):
    """Schema for creating a template"""
    pass


class TemplateUpdate(BaseModel):
    """Schema for updating a template"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    title_template: Optional[str] = Field(None, max_length=200)
    model: Optional[str] = Field(None, max_length=100)
    system_prompt: Optional[str] = None
    is_public: Optional[bool] = None


class TemplateResponse(TemplateBase):
    """Schema for template response"""
    id: int
    user_id: int
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateUsageRequest(BaseModel):
    """Schema for creating a conversation from a template"""
    api_key_id: int = Field(..., description="API key to use for the conversation")
    custom_title: Optional[str] = Field(None, description="Override the template's default title")

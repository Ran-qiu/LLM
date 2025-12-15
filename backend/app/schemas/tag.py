from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class TagBase(BaseModel):
    """Base schema for tag"""
    name: str = Field(..., min_length=1, max_length=50, description="Tag name")
    color: Optional[str] = Field(None, description="Hex color code (e.g., #FF5733)")

    @field_validator('color')
    @classmethod
    def validate_color(cls, v):
        if v is not None:
            # Validate hex color format
            if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
                raise ValueError('Color must be a valid hex color code (e.g., #FF5733)')
        return v


class TagCreate(TagBase):
    """Schema for creating a tag"""
    pass


class TagUpdate(BaseModel):
    """Schema for updating a tag"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = None

    @field_validator('color')
    @classmethod
    def validate_color(cls, v):
        if v is not None:
            if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
                raise ValueError('Color must be a valid hex color code (e.g., #FF5733)')
        return v


class TagResponse(TagBase):
    """Schema for tag response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

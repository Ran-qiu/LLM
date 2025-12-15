from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ShareBase(BaseModel):
    """Base schema for share"""
    password: Optional[str] = Field(None, description="Optional password to protect the share")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date")


class ShareCreate(ShareBase):
    """Schema for creating a share"""
    pass


class ShareUpdate(BaseModel):
    """Schema for updating a share"""
    password: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class ShareResponse(BaseModel):
    """Schema for share response"""
    id: int
    conversation_id: int
    share_token: str
    expires_at: Optional[datetime]
    is_active: bool
    access_count: int
    last_accessed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    has_password: bool = Field(False, description="Whether the share is password protected")

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        """Custom from_orm to set has_password"""
        data = super().model_validate(obj)
        data.has_password = obj.password is not None
        return data


class ShareAccessRequest(BaseModel):
    """Schema for accessing a shared conversation"""
    password: Optional[str] = Field(None, description="Password if the share is protected")

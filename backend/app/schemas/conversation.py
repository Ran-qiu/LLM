from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.schemas.tag import TagResponse


class ConversationBase(BaseModel):
    title: str = Field(..., max_length=200)
    model: str = Field(..., max_length=100, description="Model name (e.g., gpt-4, claude-3-opus)")
    system_prompt: Optional[str] = Field(None, description="System message/instructions")


class ConversationCreate(ConversationBase):
    api_key_id: int = Field(..., description="ID of the API key to use")


class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    system_prompt: Optional[str] = None


class ConversationInDB(ConversationBase):
    id: int
    user_id: int
    api_key_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    id: int
    title: str
    model: str
    system_prompt: Optional[str]
    api_key_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = None  # Can be populated separately
    tags: List["TagResponse"] = []

    model_config = ConfigDict(from_attributes=True)


# For listing conversations with message preview
class ConversationListItem(BaseModel):
    id: int
    title: str
    model: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message: Optional[str] = None
    tags: List["TagResponse"] = []

    model_config = ConfigDict(from_attributes=True)


# Resolve forward references
from app.schemas.tag import TagResponse  # noqa: E402
ConversationResponse.model_rebuild()
ConversationListItem.model_rebuild()

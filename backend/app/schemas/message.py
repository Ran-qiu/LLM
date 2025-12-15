from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, Literal
from datetime import datetime


class MessageBase(BaseModel):
    role: Literal["system", "user", "assistant"] = Field(..., description="Message role")
    content: str = Field(..., description="Message content")


class MessageCreate(MessageBase):
    conversation_id: int = Field(..., description="Conversation ID")
    metadata: Optional[Dict[str, Any]] = None


class MessageUpdate(BaseModel):
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MessageInDB(MessageBase):
    id: int
    conversation_id: int
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]
    cost: Optional[float]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]
    cost: Optional[float]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# For chat completion requests
class ChatCompletionRequest(BaseModel):
    conversation_id: int
    message: str = Field(..., description="User message")
    stream: bool = Field(default=False, description="Whether to stream the response")


# For chat completion responses
class ChatCompletionResponse(BaseModel):
    conversation_id: int
    message: MessageResponse
    usage: Optional[Dict[str, int]] = None

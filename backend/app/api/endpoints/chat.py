from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationListItem
)
from app.schemas.message import MessageResponse, ChatCompletionRequest, ChatCompletionResponse
from app.services.conversation_service import ConversationService
from app.services.llm_service import LLMService
from app.models.user import User
from app.models.message import Message
from app.models.conversation import Conversation

router = APIRouter()


# Conversation management endpoints
@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new conversation.

    - **api_key_id**: ID of the API key to use
    - **title**: Conversation title
    - **model**: Model name to use
    - **system_prompt**: Optional system prompt
    """
    conversation = ConversationService.create_conversation(
        db, current_user.id, conversation_data
    )
    return conversation


@router.get("/conversations", response_model=List[ConversationListItem])
async def get_conversations(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get list of user's conversations.

    Returns conversations with message count and last message preview.
    """
    conversations = ConversationService.get_conversations(
        db, current_user.id, skip, limit
    )
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific conversation details."""
    conversation = ConversationService.get_conversation(
        db, conversation_id, current_user.id
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return conversation


@router.put("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    conversation_update: ConversationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update conversation title or system prompt.
    """
    conversation = ConversationService.update_conversation(
        db, conversation_id, current_user.id, conversation_update
    )
    return conversation


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete conversation and all its messages."""
    ConversationService.delete_conversation(
        db, conversation_id, current_user.id
    )
    return {"message": "Conversation deleted successfully"}


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all messages in a conversation."""
    messages = ConversationService.get_conversation_messages(
        db, conversation_id, current_user.id, skip, limit
    )
    return messages


# Chat message endpoints
@router.post("/conversations/{conversation_id}/messages", response_model=ChatCompletionResponse)
async def send_message(
    conversation_id: int,
    request: ChatCompletionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the LLM and get response.

    - **message**: User message content
    - **stream**: Whether to stream the response (use /stream endpoint instead)
    """
    if request.stream:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use /conversations/{conversation_id}/stream endpoint for streaming"
        )

    # Override conversation_id from path
    request.conversation_id = conversation_id

    response = await LLMService.chat(
        db=db,
        conversation_id=conversation_id,
        user_message=request.message,
        user_id=current_user.id
    )

    # Get the last assistant message from DB
    messages = ConversationService.get_conversation_messages(
        db, conversation_id, current_user.id, skip=0, limit=1
    )

    assistant_msg = None
    for msg in reversed(messages):
        if msg.role == "assistant":
            assistant_msg = msg
            break

    return ChatCompletionResponse(
        conversation_id=conversation_id,
        message=assistant_msg,
        usage=response.usage
    )


@router.post("/conversations/{conversation_id}/stream")
async def stream_message(
    conversation_id: int,
    request: ChatCompletionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Send a message and stream the LLM response.

    Returns Server-Sent Events (SSE) stream.
    """
    async def generate():
        try:
            async for chunk in LLMService.stream_chat(
                db=db,
                conversation_id=conversation_id,
                user_message=request.message,
                user_id=current_user.id
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


# Advanced features
@router.get("/search", response_model=List[MessageResponse])
async def search_messages(
    query: str,
    conversation_id: int = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Search messages by content.

    - **query**: Search query string
    - **conversation_id**: Optional conversation ID to limit search
    - **skip**: Pagination offset
    - **limit**: Max results (default 50)
    """
    messages = ConversationService.search_messages(
        db, current_user.id, query, conversation_id, skip, limit
    )
    return messages


@router.get("/conversations/{conversation_id}/export")
async def export_conversation(
    conversation_id: int,
    format: str = "json",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Export conversation in specified format.

    - **format**: Export format (json or markdown)

    Returns the conversation with all messages and statistics.
    """
    export_data = ConversationService.export_conversation(
        db, conversation_id, current_user.id, format
    )
    return export_data


# Message editing and management
@router.put("/messages/{message_id}", response_model=MessageResponse)
async def edit_message(
    message_id: int,
    content: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Edit a user message.

    - **content**: New message content

    Only user messages can be edited. System and assistant messages cannot be modified.
    """
    message = ConversationService.edit_message(
        db, message_id, current_user.id, content
    )
    return message


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: int,
    delete_subsequent: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a message.

    - **delete_subsequent**: If true, also delete all messages after this one

    Useful for pruning conversation history or removing unwanted responses.
    """
    ConversationService.delete_message(
        db, message_id, current_user.id, delete_subsequent
    )
    return {"message": "Message deleted successfully"}


@router.post("/messages/{message_id}/regenerate", response_model=ChatCompletionResponse)
async def regenerate_response(
    message_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate the assistant response after a specific user message.

    This will:
    1. Delete all messages after the specified message
    2. Generate a new response from the LLM

    The message_id should be a user message.
    """
    # Get the message and verify it's a user message
    message = db.query(Message).join(
        Conversation,
        Message.conversation_id == Conversation.id
    ).filter(
        Message.id == message_id,
        Conversation.user_id == current_user.id
    ).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    if message.role != "user":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only regenerate responses for user messages"
        )

    conversation_id = message.conversation_id

    # Delete all messages after this one
    all_messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()

    delete_from_index = None
    for idx, msg in enumerate(all_messages):
        if msg.id == message_id:
            delete_from_index = idx + 1  # Delete from the next message
            break

    if delete_from_index is not None and delete_from_index < len(all_messages):
        messages_to_delete = all_messages[delete_from_index:]
        for msg in messages_to_delete:
            db.delete(msg)
        db.commit()

    # Generate new response
    response = await LLMService.chat(
        db=db,
        conversation_id=conversation_id,
        user_message=message.content,
        user_id=current_user.id
    )

    # Get the newly generated assistant message
    messages = ConversationService.get_conversation_messages(
        db, conversation_id, current_user.id, skip=0, limit=1
    )

    assistant_msg = None
    for msg in reversed(messages):
        if msg.role == "assistant":
            assistant_msg = msg
            break

    return ChatCompletionResponse(
        conversation_id=conversation_id,
        message=assistant_msg,
        usage=response.usage
    )

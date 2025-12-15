from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.schemas.tag import TagCreate, TagUpdate, TagResponse
from app.schemas.conversation import ConversationListItem
from app.services.tag_service import TagService
from app.services.conversation_service import ConversationService
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[TagResponse])
async def get_tags(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all tags for current user.

    Returns list of all tags with their IDs, names, and colors.
    """
    tags = TagService.get_tags(db, current_user.id, skip, limit)
    return tags


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new tag.

    - **name**: Tag name (1-50 characters, unique per user)
    - **color**: Optional hex color code (e.g., #FF5733)
    """
    tag = TagService.create_tag(db, current_user.id, tag_data)
    return tag


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific tag details."""
    tag = TagService.get_tag(db, tag_id, current_user.id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update tag name or color.

    - **name**: New tag name (optional)
    - **color**: New hex color code (optional)
    """
    tag = TagService.update_tag(db, tag_id, current_user.id, tag_update)
    return tag


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete tag. This will remove the tag from all conversations."""
    TagService.delete_tag(db, tag_id, current_user.id)
    return {"message": "Tag deleted successfully"}


@router.post("/{tag_id}/conversations/{conversation_id}")
async def add_tag_to_conversation(
    tag_id: int,
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add tag to conversation."""
    conversation = TagService.add_tag_to_conversation(
        db, conversation_id, tag_id, current_user.id
    )
    return {"message": "Tag added to conversation successfully"}


@router.delete("/{tag_id}/conversations/{conversation_id}")
async def remove_tag_from_conversation(
    tag_id: int,
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove tag from conversation."""
    conversation = TagService.remove_tag_from_conversation(
        db, conversation_id, tag_id, current_user.id
    )
    return {"message": "Tag removed from conversation successfully"}


@router.get("/{tag_id}/conversations", response_model=List[ConversationListItem])
async def get_conversations_by_tag(
    tag_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all conversations with a specific tag.

    Returns conversations filtered by tag, with message count and preview.
    """
    conversations = TagService.get_conversations_by_tag(
        db, tag_id, current_user.id, skip, limit
    )

    # Convert to ConversationListItem format
    result = []
    for conv in conversations:
        # Get message count
        message_count = len(conv.messages)

        # Get last assistant message
        last_message = None
        for msg in reversed(conv.messages):
            if msg.role == "assistant":
                last_msg_content = msg.content[:100]
                if len(msg.content) > 100:
                    last_msg_content += "..."
                last_message = last_msg_content
                break

        result.append(ConversationListItem(
            id=conv.id,
            title=conv.title,
            model=conv.model,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=message_count,
            last_message=last_message
        ))

    return result

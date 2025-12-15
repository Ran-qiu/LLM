from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.schemas.share import ShareCreate, ShareUpdate, ShareResponse, ShareAccessRequest
from app.services.share_service import ShareService
from app.services.conversation_service import ConversationService
from app.models.user import User

router = APIRouter()


# Authenticated endpoints (require login)
@router.post("/conversations/{conversation_id}/share", response_model=ShareResponse, status_code=status.HTTP_201_CREATED)
async def create_share(
    conversation_id: int,
    share_data: ShareCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a share link for a conversation.

    - **password**: Optional password to protect the share
    - **expires_at**: Optional expiration datetime

    Returns a shareable link that can be accessed without authentication.
    """
    share = ShareService.create_share(
        db, conversation_id, current_user.id, share_data
    )
    return share


@router.get("/me", response_model=List[ShareResponse])
async def get_my_shares(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all shares created by current user.

    Returns list of all share links with their statistics and settings.
    """
    shares = ShareService.get_user_shares(db, current_user.id, skip, limit)
    return shares


@router.get("/conversations/{conversation_id}", response_model=List[ShareResponse])
async def get_conversation_shares(
    conversation_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all shares for a specific conversation.

    Returns list of share links for the conversation.
    """
    shares = ShareService.get_conversation_shares(
        db, conversation_id, current_user.id, skip, limit
    )
    return shares


@router.put("/{share_id}", response_model=ShareResponse)
async def update_share(
    share_id: int,
    share_update: ShareUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update share settings.

    - **password**: Update password protection
    - **expires_at**: Update expiration datetime
    - **is_active**: Enable or disable the share
    """
    share = ShareService.update_share(db, share_id, current_user.id, share_update)
    return share


@router.delete("/{share_id}")
async def delete_share(
    share_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a share link."""
    ShareService.delete_share(db, share_id, current_user.id)
    return {"message": "Share deleted successfully"}


@router.delete("/token/{share_token}")
async def delete_share_by_token(
    share_token: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a share link by token."""
    ShareService.delete_share_by_token(db, share_token, current_user.id)
    return {"message": "Share deleted successfully"}


# Public endpoints (no authentication required)
@router.post("/{share_token}/access")
async def access_shared_conversation(
    share_token: str,
    access_request: ShareAccessRequest,
    db: Session = Depends(get_db)
):
    """
    Access a shared conversation (public endpoint).

    - **password**: Required if the share is password protected

    Returns the conversation data if access is granted.
    This endpoint does NOT require authentication.
    """
    # Validate share and check password
    share = ShareService.get_share_by_token(
        db, share_token, access_request.password
    )

    # Get conversation with messages
    conversation = ConversationService.get_conversation(
        db, share.conversation_id, share.user_id
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get messages
    messages = ConversationService.get_conversation_messages(
        db, share.conversation_id, share.user_id
    )

    # Return conversation data (similar to export format)
    return {
        "conversation": {
            "id": conversation.id,
            "title": conversation.title,
            "model": conversation.model,
            "system_prompt": conversation.system_prompt,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
        },
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ],
        "share_info": {
            "access_count": share.access_count,
            "created_at": share.created_at.isoformat(),
        }
    }


@router.get("/{share_token}/info")
async def get_share_info(
    share_token: str,
    db: Session = Depends(get_db)
):
    """
    Get basic information about a share (public endpoint).

    Returns share metadata without requiring password.
    Useful for displaying share preview before accessing.
    """
    share = db.query(Share).filter(
        Share.share_token == share_token
    ).first()

    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found"
        )

    # Get conversation title
    conversation = db.query(Conversation).filter(
        Conversation.id == share.conversation_id
    ).first()

    return {
        "conversation_title": conversation.title if conversation else "Unknown",
        "has_password": share.password is not None,
        "is_active": share.is_active,
        "expires_at": share.expires_at.isoformat() if share.expires_at else None,
        "is_expired": share.expires_at < datetime.utcnow() if share.expires_at else False,
    }


# Import datetime for the last endpoint
from datetime import datetime
from app.models.share import Share
from app.models.conversation import Conversation

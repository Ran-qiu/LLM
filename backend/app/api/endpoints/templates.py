from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse, TemplateUsageRequest
from app.schemas.conversation import ConversationResponse
from app.services.template_service import TemplateService
from app.models.user import User

router = APIRouter()


# User templates
@router.get("/me", response_model=List[TemplateResponse])
async def get_my_templates(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all templates created by current user.

    Returns list of all user's templates with usage statistics.
    """
    templates = TemplateService.get_user_templates(db, current_user.id, skip, limit)
    return templates


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new conversation template.

    - **name**: Template name
    - **description**: Optional template description
    - **title_template**: Default title for conversations created from this template
    - **model**: Default model to use
    - **system_prompt**: System prompt/instructions
    - **is_public**: Whether to share this template publicly
    """
    template = TemplateService.create_template(db, current_user.id, template_data)
    return template


@router.get("/public", response_model=List[TemplateResponse])
async def get_public_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all public templates.

    Returns list of publicly shared templates, sorted by popularity.
    """
    templates = TemplateService.get_public_templates(db, skip, limit)
    return templates


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get specific template details.

    Can access own templates or public templates.
    """
    template = TemplateService.get_template(db, template_id, current_user.id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    return template


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_update: TemplateUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update template settings.

    Can only update templates you own.
    """
    template = TemplateService.update_template(
        db, template_id, current_user.id, template_update
    )
    return template


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a template.

    Can only delete templates you own.
    """
    TemplateService.delete_template(db, template_id, current_user.id)
    return {"message": "Template deleted successfully"}


@router.post("/{template_id}/use", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation_from_template(
    template_id: int,
    usage_request: TemplateUsageRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new conversation from a template.

    - **api_key_id**: API key to use for the conversation
    - **custom_title**: Optional custom title (overrides template's default)

    Returns the created conversation.
    Template usage count is automatically incremented.
    """
    conversation = TemplateService.create_conversation_from_template(
        db=db,
        template_id=template_id,
        user_id=current_user.id,
        api_key_id=usage_request.api_key_id,
        custom_title=usage_request.custom_title
    )
    return conversation

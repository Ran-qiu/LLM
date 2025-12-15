from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.template import Template
from app.models.conversation import Conversation
from app.models.api_key import APIKey
from app.schemas.template import TemplateCreate, TemplateUpdate
from app.core.logger import get_logger

logger = get_logger("template_service")


class TemplateService:
    """Service for managing conversation templates"""

    @staticmethod
    def create_template(
        db: Session,
        user_id: int,
        template_data: TemplateCreate
    ) -> Template:
        """
        Create a new template.

        Args:
            db: Database session
            user_id: User ID
            template_data: Template creation data

        Returns:
            Created template object
        """
        template = Template(
            user_id=user_id,
            name=template_data.name,
            description=template_data.description,
            title_template=template_data.title_template,
            model=template_data.model,
            system_prompt=template_data.system_prompt,
            is_public=template_data.is_public
        )

        db.add(template)
        db.commit()
        db.refresh(template)

        logger.info(
            f"Template created: id={template.id}, name='{template.name}', "
            f"user_id={user_id}, public={template.is_public}"
        )

        return template

    @staticmethod
    def get_template(
        db: Session,
        template_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Template]:
        """
        Get template by ID.

        Args:
            db: Database session
            template_id: Template ID
            user_id: Optional user ID for ownership validation

        Returns:
            Template object or None
        """
        query = db.query(Template).filter(Template.id == template_id)

        # If user_id is provided, check ownership or public status
        if user_id is not None:
            query = query.filter(
                (Template.user_id == user_id) | (Template.is_public == True)
            )

        return query.first()

    @staticmethod
    def get_user_templates(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Template]:
        """
        Get all templates for a user.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Template objects
        """
        templates = db.query(Template).filter(
            Template.user_id == user_id
        ).order_by(
            Template.updated_at.desc()
        ).offset(skip).limit(limit).all()

        logger.info(f"Retrieved {len(templates)} templates for user {user_id}")
        return templates

    @staticmethod
    def get_public_templates(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Template]:
        """
        Get all public templates.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of public Template objects
        """
        templates = db.query(Template).filter(
            Template.is_public == True
        ).order_by(
            Template.usage_count.desc(),
            Template.updated_at.desc()
        ).offset(skip).limit(limit).all()

        logger.info(f"Retrieved {len(templates)} public templates")
        return templates

    @staticmethod
    def update_template(
        db: Session,
        template_id: int,
        user_id: int,
        template_update: TemplateUpdate
    ) -> Template:
        """
        Update a template.

        Args:
            db: Database session
            template_id: Template ID
            user_id: User ID for ownership validation
            template_update: Update data

        Returns:
            Updated template object

        Raises:
            HTTPException: If template not found
        """
        template = db.query(Template).filter(
            Template.id == template_id,
            Template.user_id == user_id
        ).first()

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )

        # Update fields
        update_data = template_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(template, field, value)

        db.commit()
        db.refresh(template)

        logger.info(f"Template updated: id={template_id}")
        return template

    @staticmethod
    def delete_template(
        db: Session,
        template_id: int,
        user_id: int
    ) -> bool:
        """
        Delete a template.

        Args:
            db: Database session
            template_id: Template ID
            user_id: User ID for ownership validation

        Returns:
            True if deleted

        Raises:
            HTTPException: If template not found
        """
        template = db.query(Template).filter(
            Template.id == template_id,
            Template.user_id == user_id
        ).first()

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )

        db.delete(template)
        db.commit()

        logger.info(f"Template deleted: id={template_id}")
        return True

    @staticmethod
    def create_conversation_from_template(
        db: Session,
        template_id: int,
        user_id: int,
        api_key_id: int,
        custom_title: Optional[str] = None
    ) -> Conversation:
        """
        Create a conversation from a template.

        Args:
            db: Database session
            template_id: Template ID
            user_id: User ID
            api_key_id: API key ID to use
            custom_title: Optional custom title (overrides template)

        Returns:
            Created conversation object

        Raises:
            HTTPException: If template or API key not found
        """
        # Get template (must be owned by user or public)
        template = TemplateService.get_template(db, template_id, user_id)

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )

        # Verify API key belongs to user
        api_key = db.query(APIKey).filter(
            APIKey.id == api_key_id,
            APIKey.user_id == user_id,
            APIKey.is_active == True
        ).first()

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found or not active"
            )

        # Create conversation using template settings
        conversation = Conversation(
            user_id=user_id,
            api_key_id=api_key_id,
            title=custom_title or template.title_template,
            model=template.model,
            system_prompt=template.system_prompt
        )

        db.add(conversation)

        # Increment template usage count
        template.usage_count += 1

        db.commit()
        db.refresh(conversation)

        logger.info(
            f"Conversation created from template: conversation_id={conversation.id}, "
            f"template_id={template_id}, user_id={user_id}"
        )

        return conversation

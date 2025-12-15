from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status

from app.models.tag import Tag
from app.models.conversation import Conversation
from app.schemas.tag import TagCreate, TagUpdate
from app.core.logger import get_logger

logger = get_logger("tag_service")


class TagService:
    """Service for managing tags"""

    @staticmethod
    def create_tag(
        db: Session,
        user_id: int,
        tag_data: TagCreate
    ) -> Tag:
        """
        Create a new tag for a user.

        Args:
            db: Database session
            user_id: User ID
            tag_data: Tag creation data

        Returns:
            Created tag object

        Raises:
            HTTPException: If tag with same name already exists for user
        """
        # Check if tag with same name already exists for this user
        existing_tag = db.query(Tag).filter(
            Tag.user_id == user_id,
            Tag.name == tag_data.name
        ).first()

        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag with name '{tag_data.name}' already exists"
            )

        # Create tag
        tag = Tag(
            user_id=user_id,
            name=tag_data.name,
            color=tag_data.color
        )

        db.add(tag)
        db.commit()
        db.refresh(tag)

        logger.info(f"Tag created: id={tag.id}, name='{tag.name}', user_id={user_id}")
        return tag

    @staticmethod
    def get_tag(
        db: Session,
        tag_id: int,
        user_id: int
    ) -> Optional[Tag]:
        """
        Get tag by ID.

        Args:
            db: Database session
            tag_id: Tag ID
            user_id: User ID for ownership validation

        Returns:
            Tag object or None
        """
        return db.query(Tag).filter(
            Tag.id == tag_id,
            Tag.user_id == user_id
        ).first()

    @staticmethod
    def get_tags(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tag]:
        """
        Get all tags for a user.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Tag objects
        """
        tags = db.query(Tag).filter(
            Tag.user_id == user_id
        ).order_by(
            Tag.name
        ).offset(skip).limit(limit).all()

        logger.info(f"Retrieved {len(tags)} tags for user {user_id}")
        return tags

    @staticmethod
    def update_tag(
        db: Session,
        tag_id: int,
        user_id: int,
        tag_update: TagUpdate
    ) -> Tag:
        """
        Update a tag.

        Args:
            db: Database session
            tag_id: Tag ID
            user_id: User ID for ownership validation
            tag_update: Update data

        Returns:
            Updated tag object

        Raises:
            HTTPException: If tag not found or name conflict
        """
        tag = TagService.get_tag(db, tag_id, user_id)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )

        # Check for name conflict if name is being updated
        if tag_update.name and tag_update.name != tag.name:
            existing_tag = db.query(Tag).filter(
                Tag.user_id == user_id,
                Tag.name == tag_update.name,
                Tag.id != tag_id
            ).first()

            if existing_tag:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tag with name '{tag_update.name}' already exists"
                )

        # Update fields
        update_data = tag_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tag, field, value)

        db.commit()
        db.refresh(tag)

        logger.info(f"Tag updated: id={tag_id}")
        return tag

    @staticmethod
    def delete_tag(
        db: Session,
        tag_id: int,
        user_id: int
    ) -> bool:
        """
        Delete a tag.

        Args:
            db: Database session
            tag_id: Tag ID
            user_id: User ID for ownership validation

        Returns:
            True if deleted

        Raises:
            HTTPException: If tag not found
        """
        tag = TagService.get_tag(db, tag_id, user_id)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )

        db.delete(tag)
        db.commit()

        logger.info(f"Tag deleted: id={tag_id}")
        return True

    @staticmethod
    def add_tag_to_conversation(
        db: Session,
        conversation_id: int,
        tag_id: int,
        user_id: int
    ) -> Conversation:
        """
        Add a tag to a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            tag_id: Tag ID
            user_id: User ID for ownership validation

        Returns:
            Updated conversation object

        Raises:
            HTTPException: If conversation or tag not found
        """
        # Verify conversation belongs to user
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Verify tag belongs to user
        tag = TagService.get_tag(db, tag_id, user_id)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )

        # Check if tag is already added
        if tag in conversation.tags:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag already added to conversation"
            )

        # Add tag
        conversation.tags.append(tag)
        db.commit()
        db.refresh(conversation)

        logger.info(f"Tag {tag_id} added to conversation {conversation_id}")
        return conversation

    @staticmethod
    def remove_tag_from_conversation(
        db: Session,
        conversation_id: int,
        tag_id: int,
        user_id: int
    ) -> Conversation:
        """
        Remove a tag from a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            tag_id: Tag ID
            user_id: User ID for ownership validation

        Returns:
            Updated conversation object

        Raises:
            HTTPException: If conversation or tag not found
        """
        # Verify conversation belongs to user
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Verify tag belongs to user
        tag = TagService.get_tag(db, tag_id, user_id)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )

        # Check if tag is in conversation
        if tag not in conversation.tags:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag not found in conversation"
            )

        # Remove tag
        conversation.tags.remove(tag)
        db.commit()
        db.refresh(conversation)

        logger.info(f"Tag {tag_id} removed from conversation {conversation_id}")
        return conversation

    @staticmethod
    def get_conversations_by_tag(
        db: Session,
        tag_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Conversation]:
        """
        Get all conversations with a specific tag.

        Args:
            db: Database session
            tag_id: Tag ID
            user_id: User ID for ownership validation
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Conversation objects

        Raises:
            HTTPException: If tag not found
        """
        # Verify tag belongs to user
        tag = TagService.get_tag(db, tag_id, user_id)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )

        # Get conversations with this tag
        conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.tags.contains(tag)
        ).order_by(
            Conversation.updated_at.desc()
        ).offset(skip).limit(limit).all()

        logger.info(f"Retrieved {len(conversations)} conversations for tag {tag_id}")
        return conversations

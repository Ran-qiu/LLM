from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.api_key import APIKey
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationListItem
)
from app.core.logger import get_logger

logger = get_logger("conversation_service")


class ConversationService:
    """Service for managing conversations"""

    @staticmethod
    def create_conversation(
        db: Session,
        user_id: int,
        conversation_data: ConversationCreate
    ) -> Conversation:
        """
        Create a new conversation.

        Args:
            db: Database session
            user_id: User ID
            conversation_data: Conversation creation data

        Returns:
            Created conversation object

        Raises:
            HTTPException: If API key not found or invalid
        """
        # Verify API key belongs to user
        api_key = db.query(APIKey).filter(
            APIKey.id == conversation_data.api_key_id,
            APIKey.user_id == user_id,
            APIKey.is_active == True
        ).first()

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found or not active"
            )

        # Create conversation
        conversation = Conversation(
            user_id=user_id,
            api_key_id=conversation_data.api_key_id,
            title=conversation_data.title,
            model=conversation_data.model,
            system_prompt=conversation_data.system_prompt
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        logger.info(
            f"Conversation created: id={conversation.id}, "
            f"user_id={user_id}, model={conversation.model}"
        )

        return conversation

    @staticmethod
    def get_conversation(
        db: Session,
        conversation_id: int,
        user_id: int
    ) -> Optional[Conversation]:
        """
        Get conversation by ID.

        Args:
            db: Database session
            conversation_id: Conversation ID
            user_id: User ID for ownership validation

        Returns:
            Conversation object or None
        """
        return db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()

    @staticmethod
    def get_conversations(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[ConversationListItem]:
        """
        Get list of conversations for user with message count and preview.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ConversationListItem objects
        """
        # Query conversations with message count
        conversations = db.query(
            Conversation,
            func.count(Message.id).label("message_count")
        ).outerjoin(
            Message,
            Conversation.id == Message.conversation_id
        ).filter(
            Conversation.user_id == user_id
        ).group_by(
            Conversation.id
        ).order_by(
            Conversation.updated_at.desc()
        ).offset(skip).limit(limit).all()

        # Build result list
        result = []
        for conv, msg_count in conversations:
            # Get last message
            last_message = db.query(Message).filter(
                Message.conversation_id == conv.id,
                Message.role == "assistant"
            ).order_by(
                Message.created_at.desc()
            ).first()

            last_msg_content = None
            if last_message:
                # Truncate to 100 characters
                last_msg_content = last_message.content[:100]
                if len(last_message.content) > 100:
                    last_msg_content += "..."

            result.append(ConversationListItem(
                id=conv.id,
                title=conv.title,
                model=conv.model,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=msg_count,
                last_message=last_msg_content
            ))

        logger.info(f"Retrieved {len(result)} conversations for user {user_id}")
        return result

    @staticmethod
    def update_conversation(
        db: Session,
        conversation_id: int,
        user_id: int,
        conversation_update: ConversationUpdate
    ) -> Conversation:
        """
        Update conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            user_id: User ID for ownership validation
            conversation_update: Update data

        Returns:
            Updated conversation object

        Raises:
            HTTPException: If conversation not found
        """
        conversation = ConversationService.get_conversation(
            db, conversation_id, user_id
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Update fields
        update_data = conversation_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(conversation, field, value)

        db.commit()
        db.refresh(conversation)

        logger.info(f"Conversation updated: id={conversation_id}")
        return conversation

    @staticmethod
    def delete_conversation(
        db: Session,
        conversation_id: int,
        user_id: int
    ) -> bool:
        """
        Delete conversation and all its messages.

        Args:
            db: Database session
            conversation_id: Conversation ID
            user_id: User ID for ownership validation

        Returns:
            True if deleted

        Raises:
            HTTPException: If conversation not found
        """
        conversation = ConversationService.get_conversation(
            db, conversation_id, user_id
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        db.delete(conversation)
        db.commit()

        logger.info(f"Conversation deleted: id={conversation_id}")
        return True

    @staticmethod
    def get_conversation_messages(
        db: Session,
        conversation_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """
        Get messages for a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            user_id: User ID for ownership validation
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Message objects

        Raises:
            HTTPException: If conversation not found
        """
        # Verify conversation belongs to user
        conversation = ConversationService.get_conversation(
            db, conversation_id, user_id
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(
            Message.created_at.asc()
        ).offset(skip).limit(limit).all()

        return messages

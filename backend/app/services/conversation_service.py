from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from fastapi import HTTPException, status
import json

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

    @staticmethod
    def search_messages(
        db: Session,
        user_id: int,
        query: str,
        conversation_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Message]:
        """
        Search messages by content.

        Args:
            db: Database session
            user_id: User ID
            query: Search query
            conversation_id: Optional conversation ID to limit search
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching Message objects
        """
        # Base query - join with conversations to filter by user
        search_query = db.query(Message).join(
            Conversation,
            Message.conversation_id == Conversation.id
        ).filter(
            Conversation.user_id == user_id,
            Message.content.ilike(f"%{query}%")
        )

        # Filter by conversation if specified
        if conversation_id:
            search_query = search_query.filter(
                Message.conversation_id == conversation_id
            )

        messages = search_query.order_by(
            Message.created_at.desc()
        ).offset(skip).limit(limit).all()

        logger.info(
            f"Search completed: query='{query}', "
            f"results={len(messages)}, user_id={user_id}"
        )

        return messages

    @staticmethod
    def export_conversation(
        db: Session,
        conversation_id: int,
        user_id: int,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export conversation in specified format.

        Args:
            db: Database session
            conversation_id: Conversation ID
            user_id: User ID for ownership validation
            format: Export format (json or markdown)

        Returns:
            Dictionary with conversation data

        Raises:
            HTTPException: If conversation not found
        """
        # Get conversation
        conversation = ConversationService.get_conversation(
            db, conversation_id, user_id
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Get all messages
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(
            Message.created_at.asc()
        ).all()

        if format == "json":
            return ConversationService._export_as_json(conversation, messages)
        elif format == "markdown":
            return ConversationService._export_as_markdown(conversation, messages)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format: {format}"
            )

    @staticmethod
    def _export_as_json(
        conversation: Conversation,
        messages: List[Message]
    ) -> Dict[str, Any]:
        """Export conversation as JSON."""
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
                    "tokens": {
                        "prompt": msg.prompt_tokens,
                        "completion": msg.completion_tokens,
                        "total": msg.total_tokens,
                    } if msg.total_tokens else None,
                    "cost": msg.cost,
                }
                for msg in messages
            ],
            "statistics": {
                "total_messages": len(messages),
                "total_tokens": sum(msg.total_tokens or 0 for msg in messages),
                "total_cost": sum(msg.cost or 0 for msg in messages),
            }
        }

    @staticmethod
    def _export_as_markdown(
        conversation: Conversation,
        messages: List[Message]
    ) -> Dict[str, Any]:
        """Export conversation as Markdown."""
        lines = [
            f"# {conversation.title}",
            "",
            f"**Model:** {conversation.model}",
            f"**Created:** {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]

        if conversation.system_prompt:
            lines.extend([
                "## System Prompt",
                "",
                conversation.system_prompt,
                "",
            ])

        lines.append("## Conversation")
        lines.append("")

        for msg in messages:
            if msg.role == "system":
                continue

            role_label = "**User:**" if msg.role == "user" else "**Assistant:**"
            lines.extend([
                f"### {role_label}",
                "",
                msg.content,
                "",
            ])

        # Add statistics
        total_tokens = sum(msg.total_tokens or 0 for msg in messages)
        total_cost = sum(msg.cost or 0 for msg in messages)

        lines.extend([
            "---",
            "",
            "## Statistics",
            "",
            f"- **Total Messages:** {len(messages)}",
            f"- **Total Tokens:** {total_tokens}",
            f"- **Total Cost:** ${total_cost:.4f}",
        ])

        markdown_content = "\n".join(lines)

        return {
            "format": "markdown",
            "content": markdown_content
        }

    @staticmethod
    def delete_message(
        db: Session,
        message_id: int,
        user_id: int,
        delete_subsequent: bool = False
    ) -> bool:
        """
        Delete a message and optionally all subsequent messages.

        Args:
            db: Database session
            message_id: Message ID to delete
            user_id: User ID for ownership validation
            delete_subsequent: If True, delete all messages after this one

        Returns:
            True if deleted

        Raises:
            HTTPException: If message not found or unauthorized
        """
        # Get message and verify ownership
        message = db.query(Message).join(
            Conversation,
            Message.conversation_id == Conversation.id
        ).filter(
            Message.id == message_id,
            Conversation.user_id == user_id
        ).first()

        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )

        conversation_id = message.conversation_id

        if delete_subsequent:
            # Delete this message and all subsequent ones
            # Get all messages in the conversation ordered by creation time
            all_messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.asc()).all()

            # Find the index of the target message
            delete_from_index = None
            for idx, msg in enumerate(all_messages):
                if msg.id == message_id:
                    delete_from_index = idx
                    break

            if delete_from_index is not None:
                # Delete all messages from this point onward
                messages_to_delete = all_messages[delete_from_index:]
                for msg in messages_to_delete:
                    db.delete(msg)

                logger.info(
                    f"Deleted {len(messages_to_delete)} messages from "
                    f"conversation {conversation_id} starting from message {message_id}"
                )
        else:
            # Delete only this specific message
            db.delete(message)
            logger.info(f"Deleted message {message_id}")

        db.commit()
        return True

    @staticmethod
    def edit_message(
        db: Session,
        message_id: int,
        user_id: int,
        new_content: str
    ) -> Message:
        """
        Edit a message content.

        Args:
            db: Database session
            message_id: Message ID to edit
            user_id: User ID for ownership validation
            new_content: New message content

        Returns:
            Updated message object

        Raises:
            HTTPException: If message not found, unauthorized, or not a user message
        """
        # Get message and verify ownership
        message = db.query(Message).join(
            Conversation,
            Message.conversation_id == Conversation.id
        ).filter(
            Message.id == message_id,
            Conversation.user_id == user_id
        ).first()

        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )

        # Only allow editing user messages
        if message.role != "user":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only user messages can be edited"
            )

        # Update content
        message.content = new_content
        db.commit()
        db.refresh(message)

        logger.info(f"Message {message_id} edited")
        return message

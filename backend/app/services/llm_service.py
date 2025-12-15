from typing import List, Optional, AsyncIterator
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.api_key import APIKey
from app.models.conversation import Conversation
from app.models.message import Message
from app.adapters.adapter_factory import AdapterFactory
from app.adapters.base_adapter import ChatMessage, ChatCompletionResponse
from app.core.logger import get_logger

logger = get_logger("llm_service")


class LLMService:
    """Service for handling LLM interactions"""

    @staticmethod
    def get_api_key(db: Session, api_key_id: int, user_id: int) -> APIKey:
        """
        Get and validate API key.

        Args:
            db: Database session
            api_key_id: API key ID
            user_id: User ID for ownership validation

        Returns:
            APIKey object

        Raises:
            HTTPException: If API key not found or not active
        """
        api_key = db.query(APIKey).filter(
            APIKey.id == api_key_id,
            APIKey.user_id == user_id
        ).first()

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        if not api_key.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key is not active"
            )

        return api_key

    @staticmethod
    def build_message_history(
        conversation: Conversation,
        db: Session
    ) -> List[ChatMessage]:
        """
        Build message history for a conversation.

        Args:
            conversation: Conversation object
            db: Database session

        Returns:
            List of ChatMessage objects
        """
        messages = []

        # Add system message if present
        if conversation.system_prompt:
            messages.append(ChatMessage(
                role="system",
                content=conversation.system_prompt
            ))

        # Add conversation messages
        db_messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).all()

        for msg in db_messages:
            messages.append(ChatMessage(
                role=msg.role,
                content=msg.content
            ))

        return messages

    @staticmethod
    async def chat(
        db: Session,
        conversation_id: int,
        user_message: str,
        user_id: int,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> ChatCompletionResponse:
        """
        Send a chat message and get response.

        Args:
            db: Database session
            conversation_id: Conversation ID
            user_message: User message content
            user_id: User ID
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            ChatCompletionResponse

        Raises:
            HTTPException: If conversation not found or unauthorized
        """
        # Get conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Get API key
        api_key = LLMService.get_api_key(db, conversation.api_key_id, user_id)

        # Create adapter
        adapter = AdapterFactory.create_adapter_from_db(api_key)

        # Build message history
        messages = LLMService.build_message_history(conversation, db)

        # Add user message
        messages.append(ChatMessage(role="user", content=user_message))

        # Save user message to database
        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=user_message
        )
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)

        logger.info(
            f"Chat request: conversation_id={conversation_id}, "
            f"model={conversation.model}, "
            f"provider={api_key.provider}"
        )

        try:
            # Get response from LLM
            response = await adapter.chat(
                messages=messages,
                model=conversation.model,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Save assistant message to database
            assistant_msg = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=response.content,
                prompt_tokens=response.usage.get("prompt_tokens") if response.usage else None,
                completion_tokens=response.usage.get("completion_tokens") if response.usage else None,
                total_tokens=response.usage.get("total_tokens") if response.usage else None,
                cost=response.metadata.get("cost") if response.metadata else None,
                metadata=response.metadata
            )
            db.add(assistant_msg)

            # Update API key last used time
            from datetime import datetime
            api_key.last_used_at = datetime.utcnow()

            db.commit()

            logger.info(
                f"Chat completed: conversation_id={conversation_id}, "
                f"tokens={response.usage.get('total_tokens') if response.usage else 'unknown'}"
            )

            return response

        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Chat failed: {str(e)}"
            )

    @staticmethod
    async def stream_chat(
        db: Session,
        conversation_id: int,
        user_message: str,
        user_id: int,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncIterator[str]:
        """
        Send a chat message and stream response.

        Args:
            db: Database session
            conversation_id: Conversation ID
            user_message: User message content
            user_id: User ID
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Response content chunks

        Raises:
            HTTPException: If conversation not found or unauthorized
        """
        # Get conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Get API key
        api_key = LLMService.get_api_key(db, conversation.api_key_id, user_id)

        # Create adapter
        adapter = AdapterFactory.create_adapter_from_db(api_key)

        # Build message history
        messages = LLMService.build_message_history(conversation, db)

        # Add user message
        messages.append(ChatMessage(role="user", content=user_message))

        # Save user message to database
        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=user_message
        )
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)

        logger.info(
            f"Stream chat request: conversation_id={conversation_id}, "
            f"model={conversation.model}"
        )

        try:
            # Collect full response for saving
            full_response = ""

            # Stream response
            async for chunk in adapter.stream_chat(
                messages=messages,
                model=conversation.model,
                temperature=temperature,
                max_tokens=max_tokens
            ):
                full_response += chunk
                yield chunk

            # Save assistant message to database
            assistant_msg = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=full_response
            )
            db.add(assistant_msg)

            # Update API key last used time
            from datetime import datetime
            api_key.last_used_at = datetime.utcnow()

            db.commit()

            logger.info(f"Stream chat completed: conversation_id={conversation_id}")

        except Exception as e:
            logger.error(f"Stream chat error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Stream chat failed: {str(e)}"
            )

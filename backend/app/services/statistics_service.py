from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.api_key import APIKey
from app.core.logger import get_logger

logger = get_logger("statistics_service")


class StatisticsService:
    """Service for generating usage statistics"""

    @staticmethod
    def get_user_statistics(
        db: Session,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a user.

        Args:
            db: Database session
            user_id: User ID
            days: Number of days to include in statistics

        Returns:
            Dictionary with statistics matching frontend interface
        """
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get conversation count
        total_conversations = db.query(func.count(Conversation.id)).filter(
            Conversation.user_id == user_id
        ).scalar() or 0

        # Get message count and token usage
        message_stats = db.query(
            func.count(Message.id).label("count"),
            func.sum(Message.total_tokens).label("total_tokens"),
            func.sum(Message.cost).label("total_cost")
        ).join(
            Conversation,
            Message.conversation_id == Conversation.id
        ).filter(
            Conversation.user_id == user_id
        ).first()

        # Get API key count
        api_key_count = db.query(func.count(APIKey.id)).filter(
            APIKey.user_id == user_id,
            APIKey.is_active == True
        ).scalar() or 0

        # Get usage by provider
        provider_stats = db.query(
            APIKey.provider,
            func.count(Conversation.id).label("conversation_count"),
            func.count(Message.id).label("message_count"),
            func.sum(Message.total_tokens).label("total_tokens"),
            func.sum(Message.cost).label("total_cost")
        ).join(
            Conversation,
            APIKey.id == Conversation.api_key_id
        ).join(
            Message,
            Conversation.id == Message.conversation_id
        ).filter(
            APIKey.user_id == user_id,
            Message.created_at >= start_date
        ).group_by(
            APIKey.provider
        ).all()

        # Get usage by model
        model_stats = db.query(
            Conversation.model,
            func.count(Conversation.id).label("conversation_count"),
            func.count(Message.id).label("message_count"),
            func.sum(Message.total_tokens).label("total_tokens"),
            func.sum(Message.cost).label("total_cost")
        ).join(
            Message,
            Conversation.id == Message.conversation_id
        ).filter(
            Conversation.user_id == user_id,
            Message.created_at >= start_date
        ).group_by(
            Conversation.model
        ).all()

        # Get daily usage for the period
        daily_stats = db.query(
            func.date(Message.created_at).label("date"),
            func.count(Message.id).label("message_count"),
            func.sum(Message.total_tokens).label("total_tokens"),
            func.sum(Message.cost).label("total_cost")
        ).join(
            Conversation,
            Message.conversation_id == Conversation.id
        ).filter(
            Conversation.user_id == user_id,
            Message.created_at >= start_date
        ).group_by(
            func.date(Message.created_at)
        ).order_by(
            func.date(Message.created_at)
        ).all()

        logger.info(f"Generated statistics for user {user_id} (last {days} days)")

        # Format by_provider as Record
        by_provider = {}
        for stat in provider_stats:
            by_provider[stat.provider] = {
                "conversations": stat.conversation_count,
                "messages": stat.message_count,
                "tokens": stat.total_tokens or 0,
                "cost": float(stat.total_cost or 0),
            }

        # Format by_model as Record
        by_model = {}
        for stat in model_stats:
            by_model[stat.model] = {
                "conversations": stat.conversation_count,
                "messages": stat.message_count,
                "tokens": stat.total_tokens or 0,
                "cost": float(stat.total_cost or 0),
            }

        return {
            "summary": {
                "total_conversations": total_conversations,
                "total_messages": message_stats.count or 0,
                "total_tokens": message_stats.total_tokens or 0,
                "total_cost": float(message_stats.total_cost or 0),
                "active_api_keys": api_key_count,
            },
            "by_provider": by_provider,
            "by_model": by_model,
            "by_date": [
                {
                    "date": stat.date.isoformat() if hasattr(stat.date, 'isoformat') else str(stat.date),
                    "messages": stat.message_count,
                    "tokens": stat.total_tokens or 0,
                    "cost": float(stat.total_cost or 0),
                }
                for stat in daily_stats
            ]
        }

    @staticmethod
    def get_conversation_statistics(
        db: Session,
        conversation_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get statistics for a specific conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            user_id: User ID for ownership validation

        Returns:
            Dictionary with conversation statistics
        """
        # Verify conversation belongs to user
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()

        if not conversation:
            return None

        # Get message statistics
        message_stats = db.query(
            func.count(Message.id).label("count"),
            func.sum(Message.prompt_tokens).label("prompt_tokens"),
            func.sum(Message.completion_tokens).label("completion_tokens"),
            func.sum(Message.total_tokens).label("total_tokens"),
            func.sum(Message.cost).label("total_cost")
        ).filter(
            Message.conversation_id == conversation_id
        ).first()

        # Count by role
        user_messages = db.query(func.count(Message.id)).filter(
            Message.conversation_id == conversation_id,
            Message.role == "user"
        ).scalar() or 0

        assistant_messages = db.query(func.count(Message.id)).filter(
            Message.conversation_id == conversation_id,
            Message.role == "assistant"
        ).scalar() or 0

        return {
            "conversation_id": conversation_id,
            "title": conversation.title,
            "model": conversation.model,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": {
                "total": message_stats.count or 0,
                "user": user_messages,
                "assistant": assistant_messages,
            },
            "usage": {
                "prompt_tokens": message_stats.prompt_tokens or 0,
                "completion_tokens": message_stats.completion_tokens or 0,
                "total_tokens": message_stats.total_tokens or 0,
                "total_cost": float(message_stats.total_cost or 0),
            }
        }

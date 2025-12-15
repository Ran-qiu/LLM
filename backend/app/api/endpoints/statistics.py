from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.services.statistics_service import StatisticsService
from app.models.user import User

router = APIRouter()


@router.get("/me", response_model=Dict[str, Any])
async def get_my_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in statistics"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive usage statistics for current user.

    Returns statistics including:
    - Overview: conversation and message counts, active API keys
    - Usage: token usage and cost totals
    - By Provider: breakdown per LLM provider
    - By Model: breakdown per model used
    - Daily: time-series data for the specified period

    - **days**: Number of days to include (1-365, default 30)
    """
    statistics = StatisticsService.get_user_statistics(
        db, current_user.id, days
    )
    return statistics


@router.get("/conversations/{conversation_id}", response_model=Dict[str, Any])
async def get_conversation_statistics(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific conversation.

    Returns:
    - Conversation metadata
    - Message counts by role (user/assistant)
    - Token usage totals
    - Total cost
    """
    statistics = StatisticsService.get_conversation_statistics(
        db, conversation_id, current_user.id
    )

    if not statistics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return statistics

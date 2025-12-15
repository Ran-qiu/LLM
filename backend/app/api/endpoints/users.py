from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_superuser
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.api_key import APIKeyCreate, APIKeyUpdate, APIKeyResponse
from app.services.user_service import UserService
from app.services.api_key_service import APIKeyService
from app.models.user import User

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user information.

    - **email**: Update email address
    - **full_name**: Update full name
    - **password**: Update password (optional)
    """
    updated_user = UserService.update_user(db, current_user, user_update)
    return updated_user


@router.delete("/me")
async def delete_current_user(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user account.
    """
    UserService.delete_user(db, current_user)
    return {"message": "User account deleted successfully"}


# Admin endpoints
@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Get list of all users (admin only).

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    users = UserService.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (admin only).
    """
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.delete("/{user_id}")
async def delete_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Delete user by ID (admin only).
    """
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    UserService.delete_user(db, user)
    return {"message": f"User {user_id} deleted successfully"}


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Deactivate user (admin only).
    """
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    updated_user = UserService.deactivate_user(db, user)
    return updated_user


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Activate user (admin only).
    """
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    updated_user = UserService.activate_user(db, user)
    return updated_user


# API Key management endpoints
@router.get("/me/api-keys", response_model=List[APIKeyResponse])
async def get_user_api_keys(
    provider: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's API keys.

    - **provider**: Filter by provider (optional)
    """
    api_keys = APIKeyService.get_api_keys(
        db, current_user.id, provider=provider
    )
    return api_keys


@router.post("/me/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a new API key for LLM provider.

    - **provider**: Provider name (openai, claude, gemini, ollama, custom)
    - **name**: Friendly name for this key
    - **api_key**: API key (optional for Ollama)
    - **custom_config**: Custom configuration (e.g., base_url for custom providers)
    """
    api_key = APIKeyService.create_api_key(
        db, current_user.id, api_key_data
    )
    return api_key


@router.get("/me/api-keys/{api_key_id}", response_model=APIKeyResponse)
async def get_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific API key details."""
    api_key = APIKeyService.get_api_key(db, api_key_id, current_user.id)

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    return api_key


@router.put("/me/api-keys/{api_key_id}", response_model=APIKeyResponse)
async def update_api_key(
    api_key_id: int,
    api_key_update: APIKeyUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update API key."""
    api_key = APIKeyService.update_api_key(
        db, api_key_id, current_user.id, api_key_update
    )
    return api_key


@router.delete("/me/api-keys/{api_key_id}")
async def delete_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete API key."""
    APIKeyService.delete_api_key(db, api_key_id, current_user.id)
    return {"message": "API key deleted successfully"}


@router.post("/me/api-keys/{api_key_id}/toggle", response_model=APIKeyResponse)
async def toggle_api_key(
    api_key_id: int,
    is_active: bool,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enable or disable an API key."""
    api_key = APIKeyService.toggle_api_key(
        db, api_key_id, current_user.id, is_active
    )
    return api_key

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate, APIKeyUpdate
from app.core.security import encrypt_api_key
from app.core.logger import get_logger

logger = get_logger("api_key_service")


class APIKeyService:
    """Service for managing API keys"""

    @staticmethod
    def create_api_key(
        db: Session,
        user_id: int,
        api_key_data: APIKeyCreate
    ) -> APIKey:
        """
        Create a new API key.

        Args:
            db: Database session
            user_id: User ID
            api_key_data: API key creation data

        Returns:
            Created API key object
        """
        # Encrypt API key if provided
        encrypted_key = None
        if api_key_data.api_key:
            encrypted_key = encrypt_api_key(api_key_data.api_key)

        # Create API key
        db_api_key = APIKey(
            user_id=user_id,
            provider=api_key_data.provider,
            name=api_key_data.name,
            encrypted_key=encrypted_key,
            custom_config=api_key_data.custom_config,
            is_active=True
        )

        db.add(db_api_key)
        db.commit()
        db.refresh(db_api_key)

        logger.info(
            f"API key created: id={db_api_key.id}, "
            f"provider={db_api_key.provider}, "
            f"user_id={user_id}"
        )

        return db_api_key

    @staticmethod
    def get_api_key(
        db: Session,
        api_key_id: int,
        user_id: int
    ) -> Optional[APIKey]:
        """
        Get API key by ID.

        Args:
            db: Database session
            api_key_id: API key ID
            user_id: User ID for ownership validation

        Returns:
            API key object or None
        """
        return db.query(APIKey).filter(
            APIKey.id == api_key_id,
            APIKey.user_id == user_id
        ).first()

    @staticmethod
    def get_api_keys(
        db: Session,
        user_id: int,
        provider: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[APIKey]:
        """
        Get list of API keys for user.

        Args:
            db: Database session
            user_id: User ID
            provider: Filter by provider (optional)
            is_active: Filter by active status (optional)

        Returns:
            List of API key objects
        """
        query = db.query(APIKey).filter(APIKey.user_id == user_id)

        if provider:
            query = query.filter(APIKey.provider == provider)

        if is_active is not None:
            query = query.filter(APIKey.is_active == is_active)

        api_keys = query.order_by(APIKey.created_at.desc()).all()

        logger.info(
            f"Retrieved {len(api_keys)} API keys for user {user_id}"
        )

        return api_keys

    @staticmethod
    def update_api_key(
        db: Session,
        api_key_id: int,
        user_id: int,
        api_key_update: APIKeyUpdate
    ) -> APIKey:
        """
        Update API key.

        Args:
            db: Database session
            api_key_id: API key ID
            user_id: User ID for ownership validation
            api_key_update: Update data

        Returns:
            Updated API key object

        Raises:
            HTTPException: If API key not found
        """
        api_key = APIKeyService.get_api_key(db, api_key_id, user_id)

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        # Update fields
        update_data = api_key_update.model_dump(exclude_unset=True)

        # Handle API key encryption
        if "api_key" in update_data and update_data["api_key"]:
            update_data["encrypted_key"] = encrypt_api_key(update_data["api_key"])
            del update_data["api_key"]

        for field, value in update_data.items():
            setattr(api_key, field, value)

        db.commit()
        db.refresh(api_key)

        logger.info(f"API key updated: id={api_key_id}")
        return api_key

    @staticmethod
    def delete_api_key(
        db: Session,
        api_key_id: int,
        user_id: int
    ) -> bool:
        """
        Delete API key.

        Args:
            db: Database session
            api_key_id: API key ID
            user_id: User ID for ownership validation

        Returns:
            True if deleted

        Raises:
            HTTPException: If API key not found
        """
        api_key = APIKeyService.get_api_key(db, api_key_id, user_id)

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        db.delete(api_key)
        db.commit()

        logger.info(f"API key deleted: id={api_key_id}")
        return True

    @staticmethod
    def toggle_api_key(
        db: Session,
        api_key_id: int,
        user_id: int,
        is_active: bool
    ) -> APIKey:
        """
        Toggle API key active status.

        Args:
            db: Database session
            api_key_id: API key ID
            user_id: User ID for ownership validation
            is_active: New active status

        Returns:
            Updated API key object

        Raises:
            HTTPException: If API key not found
        """
        api_key = APIKeyService.get_api_key(db, api_key_id, user_id)

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        api_key.is_active = is_active
        db.commit()
        db.refresh(api_key)

        logger.info(
            f"API key {'activated' if is_active else 'deactivated'}: "
            f"id={api_key_id}"
        )

        return api_key

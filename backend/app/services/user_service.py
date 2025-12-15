from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserUpdate
from app.core.security import get_password_hash
from app.core.logger import get_logger

logger = get_logger("user_service")


class UserService:
    """Service for handling user management operations"""

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User object or None
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            db: Database session
            username: Username

        Returns:
            User object or None
        """
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            db: Database session
            email: Email address

        Returns:
            User object or None
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get list of users with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of User objects
        """
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(
        db: Session,
        user: User,
        user_update: UserUpdate
    ) -> User:
        """
        Update user information.

        Args:
            db: Database session
            user: User object to update
            user_update: Update data

        Returns:
            Updated user object

        Raises:
            HTTPException: If email already exists
        """
        update_data = user_update.model_dump(exclude_unset=True)

        # Check if email is being updated and already exists
        if "email" in update_data:
            existing_user = db.query(User).filter(
                User.email == update_data["email"],
                User.id != user.id
            ).first()
            if existing_user:
                logger.warning(
                    f"Update failed: email '{update_data['email']}' already exists"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

        # Update password if provided
        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data["password"])
            del update_data["password"]

        # Update user fields
        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)

        logger.info(f"User updated successfully: {user.username}")
        return user

    @staticmethod
    def delete_user(db: Session, user: User) -> bool:
        """
        Delete a user.

        Args:
            db: Database session
            user: User object to delete

        Returns:
            True if deleted successfully
        """
        username = user.username
        db.delete(user)
        db.commit()

        logger.info(f"User deleted successfully: {username}")
        return True

    @staticmethod
    def deactivate_user(db: Session, user: User) -> User:
        """
        Deactivate a user (soft delete).

        Args:
            db: Database session
            user: User object to deactivate

        Returns:
            Updated user object
        """
        user.is_active = False
        db.commit()
        db.refresh(user)

        logger.info(f"User deactivated: {user.username}")
        return user

    @staticmethod
    def activate_user(db: Session, user: User) -> User:
        """
        Activate a user.

        Args:
            db: Database session
            user: User object to activate

        Returns:
            Updated user object
        """
        user.is_active = True
        db.commit()
        db.refresh(user)

        logger.info(f"User activated: {user.username}")
        return user

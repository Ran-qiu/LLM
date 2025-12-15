from datetime import timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate, Token
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
)
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger("auth_service")


class AuthService:
    """Service for handling user authentication"""

    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """
        Register a new user.

        Args:
            db: Database session
            user_data: User registration data

        Returns:
            Created user object

        Raises:
            HTTPException: If username or email already exists
        """
        # Check if username already exists
        existing_user = db.query(User).filter(
            User.username == user_data.username
        ).first()
        if existing_user:
            logger.warning(f"Registration failed: username '{user_data.username}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Check if email already exists
        existing_email = db.query(User).filter(
            User.email == user_data.email
        ).first()
        if existing_email:
            logger.warning(f"Registration failed: email '{user_data.email}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            is_active=True,
            is_superuser=False,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"User registered successfully: {user_data.username} ({user_data.email})")
        return db_user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user by username and password.

        Args:
            db: Database session
            username: Username or email
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        # Try to find user by username or email
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()

        if not user:
            logger.warning(f"Authentication failed: user '{username}' not found")
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: invalid password for user '{username}'")
            return None

        if not user.is_active:
            logger.warning(f"Authentication failed: user '{username}' is inactive")
            return None

        logger.info(f"User authenticated successfully: {username}")
        return user

    @staticmethod
    def create_access_token_for_user(user: User) -> Token:
        """
        Create access token for a user.

        Args:
            user: User object

        Returns:
            Token object with access_token and token_type
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )

        logger.info(f"Access token created for user: {user.username}")
        return Token(access_token=access_token, token_type="bearer")

    @staticmethod
    def change_password(
        db: Session,
        user: User,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password.

        Args:
            db: Database session
            user: User object
            old_password: Current password
            new_password: New password

        Returns:
            True if password changed successfully

        Raises:
            HTTPException: If old password is incorrect
        """
        # Verify old password
        if not verify_password(old_password, user.hashed_password):
            logger.warning(f"Password change failed: incorrect old password for user '{user.username}'")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )

        # Update password
        user.hashed_password = get_password_hash(new_password)
        db.commit()

        logger.info(f"Password changed successfully for user: {user.username}")
        return True

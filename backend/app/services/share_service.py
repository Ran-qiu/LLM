from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from datetime import datetime
from passlib.context import CryptContext

from app.models.share import Share
from app.models.conversation import Conversation
from app.schemas.share import ShareCreate, ShareUpdate
from app.core.logger import get_logger

logger = get_logger("share_service")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class ShareService:
    """Service for managing conversation shares"""

    @staticmethod
    def create_share(
        db: Session,
        conversation_id: int,
        user_id: int,
        share_data: ShareCreate
    ) -> Share:
        """
        Create a share link for a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID to share
            user_id: User ID for ownership validation
            share_data: Share creation data

        Returns:
            Created share object

        Raises:
            HTTPException: If conversation not found
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

        # Hash password if provided
        hashed_password = None
        if share_data.password:
            hashed_password = pwd_context.hash(share_data.password)

        # Create share
        share = Share(
            conversation_id=conversation_id,
            user_id=user_id,
            password=hashed_password,
            expires_at=share_data.expires_at
        )

        db.add(share)
        db.commit()
        db.refresh(share)

        logger.info(
            f"Share created: id={share.id}, token='{share.share_token}', "
            f"conversation_id={conversation_id}, protected={hashed_password is not None}"
        )

        return share

    @staticmethod
    def get_share_by_token(
        db: Session,
        share_token: str,
        password: Optional[str] = None
    ) -> Optional[Share]:
        """
        Get share by token and validate access.

        Args:
            db: Database session
            share_token: Share token
            password: Password if the share is protected

        Returns:
            Share object if valid

        Raises:
            HTTPException: If share not found, expired, inactive, or password incorrect
        """
        share = db.query(Share).filter(
            Share.share_token == share_token
        ).first()

        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share not found"
            )

        # Check if share is active
        if not share.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This share has been disabled"
            )

        # Check if share is expired
        if share.expires_at and share.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This share has expired"
            )

        # Check password if required
        if share.password:
            if not password:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Password required to access this share"
                )
            if not pwd_context.verify(password, share.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect password"
                )

        # Update access tracking
        share.access_count += 1
        share.last_accessed_at = datetime.utcnow()
        db.commit()

        logger.info(f"Share accessed: token='{share_token}', access_count={share.access_count}")

        return share

    @staticmethod
    def get_user_shares(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Share]:
        """
        Get all shares created by a user.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Share objects
        """
        shares = db.query(Share).filter(
            Share.user_id == user_id
        ).order_by(
            Share.created_at.desc()
        ).offset(skip).limit(limit).all()

        logger.info(f"Retrieved {len(shares)} shares for user {user_id}")
        return shares

    @staticmethod
    def get_conversation_shares(
        db: Session,
        conversation_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Share]:
        """
        Get all shares for a specific conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            user_id: User ID for ownership validation
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Share objects

        Raises:
            HTTPException: If conversation not found
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

        shares = db.query(Share).filter(
            Share.conversation_id == conversation_id
        ).order_by(
            Share.created_at.desc()
        ).offset(skip).limit(limit).all()

        logger.info(f"Retrieved {len(shares)} shares for conversation {conversation_id}")
        return shares

    @staticmethod
    def update_share(
        db: Session,
        share_id: int,
        user_id: int,
        share_update: ShareUpdate
    ) -> Share:
        """
        Update a share.

        Args:
            db: Database session
            share_id: Share ID
            user_id: User ID for ownership validation
            share_update: Update data

        Returns:
            Updated share object

        Raises:
            HTTPException: If share not found
        """
        share = db.query(Share).filter(
            Share.id == share_id,
            Share.user_id == user_id
        ).first()

        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share not found"
            )

        # Update fields
        update_data = share_update.model_dump(exclude_unset=True)

        # Hash new password if provided
        if "password" in update_data and update_data["password"]:
            update_data["password"] = pwd_context.hash(update_data["password"])

        for field, value in update_data.items():
            setattr(share, field, value)

        db.commit()
        db.refresh(share)

        logger.info(f"Share updated: id={share_id}")
        return share

    @staticmethod
    def delete_share(
        db: Session,
        share_id: int,
        user_id: int
    ) -> bool:
        """
        Delete a share.

        Args:
            db: Database session
            share_id: Share ID
            user_id: User ID for ownership validation

        Returns:
            True if deleted

        Raises:
            HTTPException: If share not found
        """
        share = db.query(Share).filter(
            Share.id == share_id,
            Share.user_id == user_id
        ).first()

        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share not found"
            )

        db.delete(share)
        db.commit()

        logger.info(f"Share deleted: id={share_id}")
        return True

    @staticmethod
    def delete_share_by_token(
        db: Session,
        share_token: str,
        user_id: int
    ) -> bool:
        """
        Delete a share by token.

        Args:
            db: Database session
            share_token: Share token
            user_id: User ID for ownership validation

        Returns:
            True if deleted

        Raises:
            HTTPException: If share not found
        """
        share = db.query(Share).filter(
            Share.share_token == share_token,
            Share.user_id == user_id
        ).first()

        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share not found"
            )

        db.delete(share)
        db.commit()

        logger.info(f"Share deleted: token='{share_token}'")
        return True

"""
User service for ADOGENT platform.
Handles user management operations and business logic.
"""

from typing import Optional, List, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, update, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.models.user import User, UserRole, UserStatus
from app.schemas.user_schemas import UserCreateRequest, UserUpdateRequest
from app.utils.security import hash_password
from app.utils.exceptions import ConflictError, ValidationError
from app.logging.log import logger, log_user_action


class UserService:
    """Service for user-related operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize user service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def create_user(
        self,
        user_data: UserCreateRequest,
        role: UserRole = UserRole.CUSTOMER
    ) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            role: User role (defaults to CUSTOMER)
            
        Returns:
            Created user
            
        Raises:
            ConflictError: If user already exists
            ValidationError: If data validation fails
        """
        # Check if user already exists
        existing_user = await self._get_user_by_email_or_username(
            user_data.email, user_data.username
        )
        if existing_user:
            if existing_user.email == user_data.email:
                raise ConflictError("User with this email already exists")
            else:
                raise ConflictError("Username already taken")
        
        # Hash the password
        hashed_password = hash_password(user_data.password)
        
        # Create user instance with all required fields - ENSURE timestamps are set
        current_time = datetime.utcnow()
        user = User(
            email=user_data.email.lower(),
            username=user_data.username.lower(),
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone_number=user_data.phone_number,
            role=role,
            status=UserStatus.ACTIVE,
            preferred_language=user_data.preferred_language or "en",
            preferred_currency=user_data.preferred_currency or "USD",
            ai_interaction_style="friendly",  # Set default value
            allow_personalization=user_data.allow_personalization,
            allow_marketing_emails=user_data.allow_marketing_emails,
            allow_voice_data_storage=user_data.allow_voice_data_storage,
            # CRITICAL: Explicitly set both timestamps
            created_at=current_time,
            updated_at=current_time,
        )
        
        # Add to session and flush to get the ID
        self.db.add(user)
        await self.db.flush()
        
        # Explicitly refresh to ensure all database defaults are loaded
        await self.db.refresh(user)
        
        # Final commit
        await self.db.commit()
        
        # Log user creation
        log_user_action(
            action="user_created",
            user_id=str(user.id),
            details={
                "email": user.email,
                "username": user.username,
                "role": role.value
            }
        )
        
        logger.info(f"User created: {user.id}")
        return user
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User if found, None otherwise
        """
        query = select(User).where(
            and_(
                User.id == user_id,
                User.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User if found, None otherwise
        """
        query = select(User).where(
            and_(
                User.email == email.lower(),
                User.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User if found, None otherwise
        """
        query = select(User).where(
            and_(
                User.username == username.lower(),
                User.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_user(
        self,
        user_id: UUID,
        user_data: UserUpdateRequest
    ) -> Optional[User]:
        """
        Update user information.
        
        Args:
            user_id: User ID
            user_data: Updated user data
            
        Returns:
            Updated user if found, None otherwise
        """
        # Get user
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Update fields from provided data
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Handle password separately if provided
        if 'password' in update_data:
            update_data['password_hash'] = hash_password(update_data.pop('password'))
        
        # Update user attributes
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        # Always update the updated_at timestamp
        user.updated_at = datetime.utcnow()
        
        # Save changes
        await self.db.commit()
        await self.db.refresh(user)
        
        # Log user update
        log_user_action(
            action="user_updated",
            user_id=str(user.id),
            details={"updated_fields": list(update_data.keys())}
        )
        
        logger.info(f"User updated: {user.id}")
        return user
    
    async def delete_user(
        self,
        user_id: UUID,
        permanent: bool = False
    ) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: User ID
            permanent: If True, permanently delete from database
            
        Returns:
            True if successful, False if user not found
        """
        # Get user
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        if permanent:
            # Hard delete
            await self.db.delete(user)
        else:
            # Soft delete
            user.is_deleted = True
            user.deleted_at = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            user.status = UserStatus.INACTIVE
        
        # Save changes
        await self.db.commit()
        
        # Log user deletion
        log_user_action(
            action="user_deleted",
            user_id=str(user_id),
            details={"permanent": permanent}
        )
        
        logger.info(f"User deleted: {user_id} (permanent: {permanent})")
        return True
    
    def get_users_query(
        self,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        search_query: Optional[str] = None
    ) -> Select:
        """
        Build a query for users with filtering.
        
        Args:
            role: Filter by user role
            status: Filter by user status
            search_query: Search in email, username, first_name, last_name
            
        Returns:
            SQLAlchemy select query
        """
        # Base query - only non-deleted users
        query = select(User).where(User.is_deleted == False)
        
        # Apply filters
        if role:
            query = query.where(User.role == role)
            
        if status:
            query = query.where(User.status == status)
            
        if search_query:
            search_filter = or_(
                User.email.ilike(f"%{search_query}%"),
                User.username.ilike(f"%{search_query}%"),
                User.first_name.ilike(f"%{search_query}%"),
                User.last_name.ilike(f"%{search_query}%")
            )
            query = query.where(search_filter)
            
        # Default sorting by newest first
        query = query.order_by(User.created_at.desc())
        
        return query
    
    async def update_login_stats(
        self,
        user_id: UUID,
        successful: bool
    ) -> None:
        """
        Update user login statistics.
        
        Args:
            user_id: User ID
            successful: Whether login was successful
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return
        
        if successful:
            # Reset failed login attempts and update last login
            user.failed_login_attempts = 0
            user.last_login = datetime.utcnow()
        else:
            # Increment failed login attempts
            user.failed_login_attempts += 1
            
            # Lock account if too many failed attempts
            if user.failed_login_attempts >= 5:
                user.status = UserStatus.SUSPENDED
                logger.warning(f"User account suspended due to failed login attempts: {user_id}")
        
        # Always update timestamp
        user.updated_at = datetime.utcnow()
        await self.db.commit()
    
    async def _get_user_by_email_or_username(self, email: str, username: Optional[str]) -> Optional[User]:
        """
        Get user by email or username.
        
        Args:
            email: User email
            username: Username (optional)
            
        Returns:
            User if found, None otherwise
        """
        conditions = [User.email == email.lower()]
        if username:
            conditions.append(User.username == username.lower())
        
        query = select(User).where(
            and_(
                or_(*conditions),
                User.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
"""
Authentication service for ADOGENT platform.
Handles user authentication, JWT token management, and session management.
"""
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.config.config import settings
from app.models.user import User, UserStatus
from app.models.user_session import UserSession
from app.schemas.auth_schemas import TokenResponse, UserResponse
from app.schemas.user_schemas import UserCreateRequest, UserLoginRequest, RefreshTokenRequest
from app.services.user_service import UserService
from app.utils.exceptions import AuthenticationError, ValidationError
from app.utils.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_jwt_token,
    validate_password_strength,
    generate_secure_token,
)
from app.logging.log import log_user_action, log_error


class TokenData:
    """Token data class for JWT verification."""
    def __init__(self, user_id: UUID, username: str, email: str, role: str, is_verified: bool = False):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.is_verified = is_verified


class AuthService:
    """Authentication service handling user auth, JWT tokens, and session management."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.user_service = UserService(db_session)
    
    async def register_user(self, user_data: UserCreateRequest) -> Tuple[UserResponse, TokenResponse]:
        """
        Register a new user with email and password.
        
        Args:
            user_data: User registration data
            
        Returns:
            Tuple of user response and token response
            
        Raises:
            ValidationError: If data validation fails
            ConflictError: If user already exists
        """
        try:
            # Validate password strength
            if not validate_password_strength(user_data.password):
                raise ValidationError("Password does not meet strength requirements")
            
            # Create user through user service
            new_user = await self.user_service.create_user(user_data)
            
            # Generate tokens and session
            token_response = await self._create_user_tokens(new_user)
            
            await self.db.commit()
            
            # Log successful registration
            log_user_action(
                action="user_registration",
                user_id=str(new_user.id),
                details={
                    "email": user_data.email,
                    "username": user_data.username,
                    "registration_source": "email"
                }
            )
            
            user_response = self._create_user_response(new_user)
            return user_response, token_response
            
        except Exception as e:
            await self.db.rollback()
            log_error(e, {"action": "user_registration", "email": user_data.email})
            raise
    
    async def authenticate_user(self, login_data: UserLoginRequest) -> Tuple[UserResponse, TokenResponse]:
        """
        Authenticate user with email and password.
        
        Args:
            login_data: User login credentials
            
        Returns:
            Tuple of user response and token response
            
        Raises:
            AuthenticationError: If credentials are invalid
        """
        try:
            # Find user by email
            user = await self.user_service.get_user_by_email(login_data.email)
            
            if not user:
                raise AuthenticationError("Invalid credentials")
            
            # Verify password
            if not verify_password(login_data.password, user.password_hash):
                await self.user_service.update_login_stats(user.id, successful=False)
                raise AuthenticationError("Invalid credentials")
            
            # Check if user is active
            if not user.is_account_active:
                raise AuthenticationError("Account is deactivated or suspended")
            
            # Update successful login stats
            await self.user_service.update_login_stats(user.id, successful=True)
            
            # Generate tokens and session
            token_response = await self._create_user_tokens(user)
            
            await self.db.commit()
            
            # Log successful login
            log_user_action(
                action="user_login",
                user_id=str(user.id),
                details={
                    "email": user.email,
                    "login_method": "password",
                }
            )
            
            user_response = self._create_user_response(user)
            return user_response, token_response
            
        except Exception as e:
            await self.db.rollback()
            log_error(e, {"action": "user_login", "email": login_data.email})
            raise
    
    async def refresh_token(self, refresh_data: RefreshTokenRequest) -> TokenResponse:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_data: Refresh token request
            
        Returns:
            New token response
            
        Raises:
            AuthenticationError: If refresh token is invalid
        """
        try:
            # Verify refresh token
            payload = decode_jwt_token(
                refresh_data.refresh_token,
                settings.JWT_SECRET_KEY,
                settings.JWT_ALGORITHM
            )
            
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            if not user_id or token_type != "refresh":
                raise AuthenticationError("Invalid refresh token")
            
            # Find user session
            session = await self._get_active_session(UUID(user_id), refresh_data.refresh_token)
            if not session:
                raise AuthenticationError("Invalid or expired refresh token")
            
            # Get user
            user = await self.user_service.get_user_by_id(UUID(user_id))
            if not user or not user.is_account_active:
                raise AuthenticationError("User not found or inactive")
            
            # Create new tokens
            access_token = create_access_token(
                user_id=user.id,
                username=user.username,
                email=user.email,
                role=user.role.value,
                is_verified=False
            )
            new_refresh_token = create_refresh_token(user.id)
            
            # Update session with new refresh token
            session.refresh_token = new_refresh_token
            session.expires_at = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
            session.last_accessed = datetime.utcnow()
            
            await self.db.commit()
            
            # Log token refresh
            log_user_action(
                action="token_refresh",
                user_id=str(user.id),
                details={"session_id": str(session.id)}
            )
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )
            
        except Exception as e:
            await self.db.rollback()
            log_error(e, {"action": "token_refresh"})
            raise
    
    async def verify_token(self, token: str) -> TokenData:
        """
        Verify and decode JWT access token.
        
        Args:
            token: JWT access token
            
        Returns:
            Token data
            
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = decode_jwt_token(
                token,
                settings.JWT_SECRET_KEY,
                settings.JWT_ALGORITHM
            )
            
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            if not user_id or token_type != "access":
                raise AuthenticationError("Invalid token")
            
            # Verify user exists and is active
            user = await self.user_service.get_user_by_id(UUID(user_id))
            if not user or not user.is_account_active:
                raise AuthenticationError("User not found or inactive")
            
            return TokenData(
                user_id=UUID(user_id),
                username=user.username,
                email=user.email,
                role=user.role.value,
                is_verified=False,
            )
            
        except Exception as e:
            log_error(e, {"action": "token_verification"})
            raise
    
    async def logout_user(self, user_id: UUID, refresh_token: str) -> bool:
        """
        Logout user by revoking their session.
        
        Args:
            user_id: User ID
            refresh_token: Refresh token to revoke
            
        Returns:
            True if successful
        """
        try:
            session = await self._get_active_session(user_id, refresh_token)
            
            if session:
                session.revoke()
                await self.db.commit()
                
                log_user_action(
                    action="user_logout",
                    user_id=str(user_id),
                    details={"session_id": str(session.id)}
                )
                
            return True
            
        except Exception as e:
            await self.db.rollback()
            log_error(e, {"action": "user_logout", "user_id": str(user_id)})
            return False
    
    # Private helper methods
    
    async def _create_user_tokens(self, user: User) -> TokenResponse:
        """Create JWT tokens and user session."""
        access_token = create_access_token(
            user_id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            is_verified=False
        )
        refresh_token = create_refresh_token(user.id)
        
        # Create user session
        await self._create_user_session(
            user_id=user.id,
            refresh_token=refresh_token,
            device_info=None,
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    
    async def _create_user_session(
        self,
        user_id: UUID,
        refresh_token: str,
        device_info: Optional[Dict[str, Any]] = None,
    ) -> UserSession:
        """Create user session for refresh token tracking."""
        device_info_json = json.dumps(device_info) if device_info is not None else None
        session_token = generate_secure_token(32)
        
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            refresh_token=refresh_token,
            device_info=device_info_json,
            ip_address=None,  # Will be set by middleware
            user_agent=None,  # Will be set by middleware
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )
        
        self.db.add(session)
        return session
    
    async def _get_active_session(self, user_id: UUID, refresh_token: str) -> Optional[UserSession]:
        """Get active user session by refresh token."""
        result = await self.db.execute(
            select(UserSession)
            .where(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.refresh_token == refresh_token,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow()
                )
            )
        )
        return result.scalar_one_or_none()
    
    def _create_user_response(self, user: User) -> UserResponse:
            """Create user response schema from user model with bulletproof field handling."""
            # Get current time for any missing timestamps
            current_time = datetime.utcnow()
            
            # Debug: Log the actual user data to see what's happening
            log_user_action(
                action="debug_user_response_creation",
                user_id=str(user.id),
                details={
                    "created_at": str(user.created_at),
                    "updated_at": str(user.updated_at),
                    "last_login": str(user.last_login),
                    "ai_interaction_style": user.ai_interaction_style,
                }
            )
            
            # BULLETPROOF: Ensure all required fields have values
            return UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role.value,
                status=user.status.value,
                preferred_language=user.preferred_language or "en",
                preferred_currency=user.preferred_currency or "USD",
                # CRITICAL: Handle timestamps with bulletproof defaults
                created_at=user.created_at or current_time,
                updated_at=user.updated_at or user.created_at or current_time,
                last_login=user.last_login,  # Can be None
                ai_interaction_style=user.ai_interaction_style or "friendly",
                phone_number=user.phone_number,
                date_of_birth=user.date_of_birth,
                voice_preference=user.voice_preference,
                price_range_preference=user.price_range_preference,
                allow_personalization=user.allow_personalization if user.allow_personalization is not None else True,
                allow_marketing_emails=user.allow_marketing_emails if user.allow_marketing_emails is not None else False,
                allow_voice_data_storage=user.allow_voice_data_storage if user.allow_voice_data_storage is not None else True,
            )
"""
Authentication service for ADOGENT platform.
Handles user registration, login, JWT token management, and OAuth integration.
"""
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.config.config import settings
from app.models.user import User, UserStatus
from app.models.user_session import UserSession
from app.schemas.auth_schemas import (
    TokenResponse,
    UserResponse,
)
from app.schemas.user_schemas import UserCreateRequest, UserLoginRequest, RefreshTokenRequest
from app.utils.exceptions import (
    AuthenticationError,
    ValidationError,
    ConflictError,
)
from app.utils.security import (
    hash_password,
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
    def __init__(self, user_id: UUID, username: str, email: str, role: str, is_verified: bool):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.is_verified = False


class AuthService:
    """Authentication service handling user auth, JWT tokens, and OAuth."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def register_user(self, user_data: UserCreateRequest) -> Tuple[UserResponse, TokenResponse]:
        """
        Register a new user with email and password.
        
        Args:
            user_data: User registration data
            
        Returns:
            Tuple of user response and token response
            
        Raises:
            ConflictError: If user already exists
            ValidationError: If data validation fails
        """
        try:
            # Validate password strength
            if not validate_password_strength(user_data.password):
                raise ValidationError("Password does not meet strength requirements")
            
            # Check if user already exists
            existing_user = await self._get_user_by_email_or_username(
                user_data.email, user_data.username
            )
            if existing_user:
                if existing_user.email == user_data.email:
                    raise ConflictError("User with this email already exists")
                else:
                    raise ConflictError("Username already taken")
            
            # Hash password
            hashed_password = hash_password(user_data.password)
            
            # Create new user
            new_user = User(
                    email=user_data.email,
                    username=user_data.username,
                    first_name=user_data.first_name,
                    last_name=user_data.last_name,
                    phone_number=user_data.phone_number,
                    password_hash=hashed_password,
                    status=UserStatus.ACTIVE,  # This will effectively make the user active
                    preferred_language=user_data.preferred_language,
                    preferred_currency=user_data.preferred_currency,
                    allow_marketing_emails=user_data.allow_marketing_emails,
                    allow_personalization=user_data.allow_personalization,
                    allow_voice_data_storage=user_data.allow_voice_data_storage,
                )
            
            self.db.add(new_user)
            await self.db.flush()  # Get the user ID
            
            # Create JWT tokens
            access_token = create_access_token(
                user_id=new_user.id,
                username=new_user.username,
                email=new_user.email,
                role=new_user.role.value,
                is_verified=False
            )
            refresh_token = create_refresh_token(new_user.id)
            
            # Create user session
            await self._create_user_session(
                user_id=new_user.id,
                refresh_token=refresh_token,
                device_info=None,
            )
            
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
            
            # Convert to response schemas
            user_response = UserResponse(
                id=new_user.id,
                email=new_user.email,
                username=new_user.username,
                first_name=new_user.first_name,
                last_name=new_user.last_name,
                role=new_user.role.value,
                status=new_user.status.value,
                preferred_language=new_user.preferred_language,
                preferred_currency=new_user.preferred_currency,
                created_at=new_user.created_at,
                last_login=new_user.last_login,
                updated_at=new_user.updated_at,
                ai_interaction_style=new_user.ai_interaction_style
            )
            
            token_response = TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )
            
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
            user = await self._get_user_by_email_or_username(login_data.email, None)
            
            if not user or not verify_password(login_data.password, user.password_hash):
                raise AuthenticationError("Invalid credentials")
            
            if not user.is_active:
                raise AuthenticationError("Account is deactivated")
            
            # Update last login
            user.last_login = datetime.utcnow()
            
            
            # Create JWT tokens
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
            
            # Convert to response schemas
            user_response = UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role.value,
                status=user.status.value,
                preferred_language=user.preferred_language,
                preferred_currency=user.preferred_currency,
                created_at=user.created_at,
                last_login=user.last_login,
                updated_at=user.updated_at,
                ai_interaction_style=user.ai_interaction_style
                
            )
            
            token_response = TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )
            
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
            session = await self.db.execute(
                select(UserSession)
                .where(
                    and_(
                        UserSession.user_id == UUID(user_id),
                        UserSession.refresh_token == refresh_data.refresh_token,
                        UserSession.is_active == True,
                        UserSession.expires_at > datetime.utcnow()
                    )
                )
            )
            session = session.scalar_one_or_none()
            
            if not session:
                raise AuthenticationError("Invalid or expired refresh token")
            
            # Get user
            user = await self.db.get(User, UUID(user_id))
            if not user or not user.is_active:
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
            user = await self.db.get(User, UUID(user_id))
            if not user or not user.is_active:
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
    
    # Private helper methods
    
    async def _get_user_by_email_or_username(self, email: str, username: Optional[str]) -> Optional[User]:
        """Get user by email or username."""
        conditions = [User.email == email]
        if username:
            conditions.append(User.username == username)
        
        result = await self.db.execute(
            select(User).where(or_(*conditions))
        )
        return result.scalar_one_or_none()
    
    async def _create_user_session(
        self,
        user_id: UUID,
        refresh_token: str,
        device_info: Optional[Dict[str, Any]] = None,
    ) -> UserSession:
        """Create user session for refresh token tracking."""
        
        # Convert device_info dictionary to JSON string
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
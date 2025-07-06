"""
Authentication API endpoints for ADOGENT platform.
Handles user registration, login, logout, token refresh, and OAuth.
"""

from typing import Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.auth_service import AuthService, TokenData
from app.schemas.auth_schemas import TokenResponse
from app.schemas.user_schemas import (
    UserCreateRequest,
    UserLoginRequest, 
    RefreshTokenRequest,
    UserResponse
)
from app.utils.exceptions import AuthenticationError, ConflictError, ValidationError
from app.logging.log import logger, log_api_request
from app.models.user import User

# Initialize router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme for JWT tokens
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> TokenData:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: JWT token from Authorization header
        db: Database session
        
    Returns:
        Token data with user information
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        auth_service = AuthService(db)
        token_data = await auth_service.verify_token(credentials.credentials)
        return token_data
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register_user(
    request: Request,
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user with email and password.
    
    Args:
        request: FastAPI request object
        user_data: User registration data
        db: Database session
        
    Returns:
        Dictionary containing user and token information
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        auth_service = AuthService(db)
        user_response, token_response = await auth_service.register_user(user_data)
        
        # Log API request
        log_api_request(
            method="POST",
            endpoint="/auth/register",
            status_code=201,
            response_time=0.0,  # Will be set by middleware
            user_id=str(user_response.id),
        )
        
        return {
            "message": "User registered successfully",
            "user": user_response.dict(),
            "tokens": token_response.dict(),
        }
        
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/login", response_model=Dict[str, Any])
async def login_user(
    request: Request,
    login_data: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user with email and password.
    
    Args:
        request: FastAPI request object
        login_data: User login credentials
        db: Database session
        
    Returns:
        Dictionary containing user and token information
        
    Raises:
        HTTPException: If login fails
    """
    try:
        auth_service = AuthService(db)
        user_response, token_response = await auth_service.authenticate_user(login_data)
        
        # Log API request
        log_api_request(
            method="POST",
            endpoint="/auth/login",
            status_code=200,
            response_time=0.0,  # Will be set by middleware
            user_id=str(user_response.id),
        )
        
        return {
            "message": "Login successful",
            "user": user_response.dict(),
            "tokens": token_response.dict(),
        }
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token.
    
    Args:
        request: FastAPI request object
        refresh_data: Refresh token request
        db: Database session
        
    Returns:
        New token response
        
    Raises:
        HTTPException: If refresh fails
    """
    try:
        auth_service = AuthService(db)
        token_response = await auth_service.refresh_token(refresh_data)
        
        # Log API request
        log_api_request(
            method="POST",
            endpoint="/auth/refresh",
            status_code=200,
            response_time=0.0,  # Will be set by middleware
        )
        
        return token_response
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user profile information.
    
    Args:
        request: FastAPI request object
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        User profile information
        
    Raises:
        HTTPException: If profile retrieval fails
    """
    try:
        # Get full user information from database
        user = await db.get(User, current_user.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        # Log API request
        log_api_request(
            method="GET",
            endpoint="/auth/me",
            status_code=200,
            response_time=0.0,  # Will be set by middleware
            user_id=str(current_user.user_id),
        )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            status=user.status,
            preferred_language=user.preferred_language,
            preferred_currency=user.preferred_currency,
            created_at=user.created_at,
            last_login=user.last_login,
            updated_at=user.updated_at,
            ai_interaction_style=user.ai_interaction_style
        )
        
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile",
        )
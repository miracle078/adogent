"""
Authentication API endpoints for ADOGENT platform.
Handles user registration, login, logout, token refresh, and OAuth.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth_schemas import TokenResponse
from app.schemas.user_schemas import (
    UserCreateRequest,
    UserLoginRequest, 
    RefreshTokenRequest,
    AuthTokenResponse
)
from app.utils.exceptions import AuthenticationError, ConflictError, ValidationError
from app.logging.log import logger, log_api_request

# Initialize router
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
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
            response_time=0.0,
            user_id=str(user_response.id),
        )
        
        return AuthTokenResponse(
            access_token=token_response.access_token,
            refresh_token=token_response.refresh_token,
            token_type=token_response.token_type,
            expires_in=token_response.expires_in,
            user=user_response
        )
        
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


@router.post("/login", response_model=AuthTokenResponse)
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
            response_time=0.0,
            user_id=str(user_response.id),
        )
        
        return AuthTokenResponse(
            access_token=token_response.access_token,
            refresh_token=token_response.refresh_token,
            token_type=token_response.token_type,
            expires_in=token_response.expires_in,
            user=user_response
        )
        
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
        refresh_data: Refresh token request data
        db: Database session
        
    Returns:
        New token response
        
    Raises:
        HTTPException: If token refresh fails
    """
    try:
        auth_service = AuthService(db)
        new_token_response = await auth_service.refresh_token(refresh_data)
        
        # Log API request
        log_api_request(
            method="POST",
            endpoint="/auth/refresh",
            status_code=200,
            response_time=0.0,
        )
        
        return new_token_response
        
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


@router.post("/logout", response_model=Dict[str, str])
async def logout_user(
    request: Request,
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Logout user by revoking refresh token.
    
    Args:
        request: FastAPI request object
        refresh_data: Refresh token to revoke
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If logout fails
    """
    try:
        auth_service = AuthService(db)
        
        # Extract user ID from refresh token first
        token_data = await auth_service.verify_token(refresh_data.refresh_token)
        success = await auth_service.logout_user(token_data.user_id, refresh_data.refresh_token)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Logout failed"
            )
        
        # Log API request
        log_api_request(
            method="POST",
            endpoint="/auth/logout",
            status_code=200,
            response_time=0.0,
            user_id=str(token_data.user_id),
        )
        
        return {"message": "Successfully logged out"}
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed",
        )
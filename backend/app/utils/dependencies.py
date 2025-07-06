"""
Shared API dependencies for ADOGENT platform.
Provides reusable dependency functions for authentication and authorization.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.auth_service import AuthService, TokenData
from app.models.user import UserRole
from app.utils.exceptions import AuthenticationError
from app.logging.log import logger
from app.config.config import settings

# Security schemes
security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> TokenData:
    """
    Get current user from JWT token.
    Returns TokenData object with user information.
    """
    try:
        auth_service = AuthService(db)
        token_data = await auth_service.verify_token(credentials.credentials)
        
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Get current active user.
    Additional validation layer for active users.
    """
    # TokenData already verified by get_current_user
    return current_user


async def require_admin(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Require admin role for endpoint access.
    """
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_moderator_or_admin(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Require moderator or admin role for endpoint access.
    """
    if current_user.role not in [UserRole.ADMIN.value, UserRole.MODERATOR.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator or admin access required"
        )
    return current_user


async def require_user_or_admin(
    current_user: TokenData = Depends(get_current_user),
    target_user_id: Optional[str] = None
) -> TokenData:
    """
    Require user access (own account) or admin access.
    """
    if current_user.role == UserRole.ADMIN.value:
        return current_user
    
    if target_user_id and str(current_user.user_id) != target_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: can only access your own account"
        )
    
    return current_user


async def verify_bootstrap_api_key(
    api_key: Optional[str] = Depends(api_key_header)
) -> bool:
    """
    Verify bootstrap API key for initial admin setup.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bootstrap API key required",
            headers={"X-API-Key": "Required"},
        )
    
    if api_key != settings.ADMIN_BOOTSTRAP_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bootstrap API key",
            headers={"X-API-Key": "Invalid"},
        )
    
    return True


async def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[TokenData]:
    """
    Optional authentication dependency.
    Returns TokenData if valid token provided, None otherwise.
    """
    if not credentials:
        return None
    
    try:
        auth_service = AuthService(db)
        token_data = await auth_service.verify_token(credentials.credentials)
        return token_data
        
    except Exception as e:
        logger.warning(f"Optional auth failed: {e}")
        return None
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
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Dependency to get current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Token data for active user
    """
    return current_user


async def require_admin(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Dependency to ensure user has admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Token data for admin user
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != UserRole.ADMIN.value:
        logger.warning(f"Access denied for user {current_user.user_id}: insufficient permissions")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource",
        )
    return current_user


async def require_moderator_or_admin(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Dependency to ensure user has moderator or admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Token data for moderator/admin user
        
    Raises:
        HTTPException: If user is not a moderator or admin
    """
    allowed_roles = [UserRole.ADMIN.value, UserRole.MODERATOR.value]
    if current_user.role not in allowed_roles:
        logger.warning(f"Access denied for user {current_user.user_id}: insufficient permissions")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource",
        )
    return current_user


async def require_user_or_admin(
    current_user: TokenData = Depends(get_current_user),
    target_user_id: Optional[str] = None
) -> TokenData:
    """
    Dependency to ensure user can access their own resources or is an admin.
    
    Args:
        current_user: Current authenticated user
        target_user_id: ID of the user being accessed
        
    Returns:
        Token data for authorized user
        
    Raises:
        HTTPException: If user is not authorized
    """
    if current_user.role == UserRole.ADMIN.value:
        return current_user
    
    if target_user_id and str(current_user.user_id) != target_user_id:
        logger.warning(f"Access denied for user {current_user.user_id}: unauthorized resource access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own resources",
        )
    return current_user


async def verify_bootstrap_api_key(
    api_key: Optional[str] = Depends(api_key_header)
) -> bool:
    """
    Verify bootstrap API key for initial admin creation.
    
    Args:
        api_key: API key from request header
        
    Returns:
        True if valid
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not api_key:
        logger.warning("Bootstrap API key missing in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bootstrap API key required",
        )
    
    if api_key != settings.ADMIN_BOOTSTRAP_API_KEY:
        logger.warning("Invalid bootstrap API key attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bootstrap API key",
        )
    return True


async def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[TokenData]:
    """
    Optional authentication dependency.
    Returns user data if authenticated, None otherwise.
    
    Args:
        credentials: Optional JWT token from Authorization header
        db: Database session
        
    Returns:
        Token data if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        auth_service = AuthService(db)
        token_data = await auth_service.verify_token(credentials.credentials)
        return token_data
    except Exception:
        # Silently fail for optional auth
        return None
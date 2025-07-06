"""
User management API endpoints for ADOGENT platform.
Handles user CRUD operations and administrative functions.
"""

from typing import Dict, Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import UserRole, UserStatus, User
from app.schemas.user_schemas import (
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
    UserListResponse,
    PasswordChangeRequest,
    MessageResponse,
    PromoteToAdminRequest
)
from app.services.user_service import UserService
from app.utils.dependencies import (
    get_current_user, 
    require_admin, 
    require_user_or_admin, 
    verify_bootstrap_api_key
)
from app.utils.pagination_utils import paginate_query, PaginationParams
from app.logging.log import logger
from app.config.config import settings

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/bootstrap-admin",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def bootstrap_admin_user(
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_bootstrap_api_key),
):
    """
    Bootstrap the first admin user when no admins exist in the system.
    
    This endpoint requires a special API key and only works if no admin users exist yet.
    """
    try:
        # Check if any admin users already exist
        query = select(User).where(
            (User.role == UserRole.ADMIN) & 
            (User.is_deleted == False)
        )
        result = await db.execute(query)
        existing_admin = result.scalars().first()
        
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin user already exists. Bootstrap not allowed."
            )
        
        # Create the first admin user
        user_service = UserService(db)
        admin_user = await user_service.create_user(
            user_data=user_data,
            role=UserRole.ADMIN
        )
        
        logger.info(f"First admin user created via bootstrap: {admin_user.id}")
        
        return admin_user
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error bootstrapping admin user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bootstrap admin user: {str(e)}"
        )


@router.post(
    "/promote-to-admin",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def promote_user_to_admin(
    request_data: PromoteToAdminRequest,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_bootstrap_api_key),
):
    """
    Promote an existing user to admin role.
    
    This endpoint requires a special API key and only works if no admin users exist yet.
    It finds the user by email and promotes them to admin role.
    
    Args:
        request_data: Request containing email of user to promote
        db: Database session
        
    Returns:
        Updated user with admin role
        
    Raises:
        HTTPException: If admin exists, user not found, or promotion fails
    """
    try:
        # Check if any admin users already exist
        query = select(User).where(
            (User.role == UserRole.ADMIN) & 
            (User.is_deleted == False)
        )
        result = await db.execute(query)
        existing_admin = result.scalars().first()
        
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin user already exists. Promotion not allowed."
            )
        
        # Find the user by email
        user_service = UserService(db)
        user = await user_service.get_user_by_email(request_data.email.lower())
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{request_data.email}' not found"
            )
        
        # Check if user is already an admin (shouldn't happen due to check above, but safety first)
        if user.role == UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already an admin"
            )
        
        # Promote user to admin
        user.role = UserRole.ADMIN
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"User promoted to admin: {user.id} ({user.email})")
        
        return user
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error promoting user to admin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to promote user to admin: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current user's profile information.
    
    This endpoint allows users to view their own profile.
    """
    try:
        user_service = UserService(db)
        user = await user_service.get_user_by_id(current_user.user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return user
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        )


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdateRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the current user's profile information.
    
    This endpoint allows users to update their own profile.
    """
    try:
        user_service = UserService(db)
        
        # Ensure role cannot be changed
        if hasattr(user_data, 'role'):
            delattr(user_data, 'role')
            
        updated_user = await user_service.update_user(
            user_id=current_user.user_id,
            user_data=user_data
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return updated_user
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )


@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
async def get_user(
    user_id: UUID = Path(..., description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific user by ID.
    
    This endpoint is restricted to administrators.
    """
    try:
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user"
        )


@router.get("/", response_model=UserListResponse, dependencies=[Depends(require_admin)])
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    role: UserRole = Query(None, description="Filter by user role"),
    status_filter: UserStatus = Query(None, description="Filter by user status"),
    search: str = Query(None, description="Search users by email/username"),
    db: AsyncSession = Depends(get_db)
):
    """
    List users with optional filtering and pagination.
    
    This endpoint is restricted to administrators.
    """
    try:
        user_service = UserService(db)
        
        # Get base query with filters
        query = user_service.get_users_query(
            role=role,
            status=status_filter,
            search_query=search
        )
        
        # Apply pagination
        pagination_params = PaginationParams(page=page, size=size)
        paginated_result = await paginate_query(db, query, pagination_params)
        
        return UserListResponse(
            users=paginated_result.items,
            total=paginated_result.total,
            page=paginated_result.page,
            size=paginated_result.size,
            pages=paginated_result.pages,
        )
        
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )
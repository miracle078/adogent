"""
Category management API endpoints for ADOGENT platform.
Handles category CRUD operations and hierarchical management.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.category_schemas import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
    CategoryListResponse,
    CategoryTreeResponse
)
from app.services.category_service import CategoryService
from app.utils.dependencies import require_admin, optional_auth
from app.utils.pagination_utils import paginate_query, PaginationParams
from app.logging.log import logger

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_admin)
):
    """
    Create a new category.
    
    This endpoint is restricted to administrators.
    """
    try:
        category_service = CategoryService(db)
        category = await category_service.create_category(category_data)
        
        # Get product count for response
        product_count = await category_service.get_category_product_count(category.id)
        
        # Convert to response model
        response_data = CategoryResponse.model_validate(category)
        response_data.product_count = product_count
        
        return response_data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create category"
        )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID = Path(..., description="Category ID"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(optional_auth)
):
    """
    Get a specific category by ID.
    
    This endpoint is publicly accessible.
    """
    try:
        category_service = CategoryService(db)
        category = await category_service.get_category_by_id(category_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Get product count for response
        product_count = await category_service.get_category_product_count(category.id)
        
        # Convert to response model
        response_data = CategoryResponse.model_validate(category)
        response_data.product_count = product_count
        
        return response_data
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve category"
        )


@router.get("/slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(
    slug: str = Path(..., description="Category slug"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(optional_auth)
):
    """
    Get a specific category by slug.
    
    This endpoint is publicly accessible.
    """
    try:
        category_service = CategoryService(db)
        category = await category_service.get_category_by_slug(slug)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Get product count for response
        product_count = await category_service.get_category_product_count(category.id)
        
        # Convert to response model
        response_data = CategoryResponse.model_validate(category)
        response_data.product_count = product_count
        
        return response_data
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving category by slug: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve category"
        )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    data: CategoryUpdateRequest,
    category_id: UUID = Path(..., description="Category ID"),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_admin)
):
    """
    Update a category.
    
    This endpoint is restricted to administrators.
    """
    try:
        category_service = CategoryService(db)
        category = await category_service.update_category(category_id, data)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Get product count for response
        product_count = await category_service.get_category_product_count(category.id)
        
        # Convert to response model
        response_data = CategoryResponse.model_validate(category)
        response_data.product_count = product_count
        
        return response_data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update category"
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID = Path(..., description="Category ID"),
    permanent: bool = Query(False, description="Permanently delete category"),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_admin)
):
    """
    Delete a category.
    
    This endpoint is restricted to administrators.
    Categories with products or subcategories cannot be deleted.
    """
    try:
        category_service = CategoryService(db)
        success = await category_service.delete_category(category_id, permanent=permanent)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete category"
        )


@router.get("/", response_model=CategoryListResponse)
async def list_categories(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    parent_id: Optional[UUID] = Query(None, description="Filter by parent category ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: str = Query(None, description="Search categories"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(optional_auth)
):
    """
    List categories with pagination and filtering.
    
    This endpoint is publicly accessible.
    Returns 200 with empty array when no categories found.
    """
    try:
        category_service = CategoryService(db)
        query = category_service.get_categories_query(
            parent_id=parent_id,
            is_active=is_active,
            search_query=search
        )
        
        pagination_params = PaginationParams(page=page, size=size)
        result = await paginate_query(db, query, pagination_params)
        
        # Enrich categories with product counts
        enriched_categories = []
        for category in result.items:
            product_count = await category_service.get_category_product_count(category.id)
            category_response = CategoryResponse.model_validate(category)
            category_response.product_count = product_count
            enriched_categories.append(category_response)
        
        return CategoryListResponse(
            categories=enriched_categories,
            total=result.total,
            page=result.page,
            size=result.size,
            pages=result.pages,
        )
        
    except Exception as e:
        logger.error(f"Error listing categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve categories"
        )


@router.get("/tree/all", response_model=CategoryTreeResponse)
async def get_category_tree(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(optional_auth)
):
    """
    Get all categories in a hierarchical tree structure.
    
    This endpoint is publicly accessible and returns categories
    organized in a parent-child hierarchy.
    """
    try:
        category_service = CategoryService(db)
        categories = await category_service.get_category_tree()
        
        # Enrich categories with product counts
        enriched_categories = []
        for category in categories:
            product_count = await category_service.get_category_product_count(category.id)
            category_response = CategoryResponse.model_validate(category)
            category_response.product_count = product_count
            enriched_categories.append(category_response)
        
        return CategoryTreeResponse(
            categories=enriched_categories,
            total=len(categories)
        )
        
    except Exception as e:
        logger.error(f"Error retrieving category tree: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve category tree"
        )
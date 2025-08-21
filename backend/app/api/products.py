"""
Product management API endpoints for ADOGENT platform.
Handles product CRUD operations, search, and recommendations.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.product import Product
from app.schemas.product_schemas import (
    ProductCreateRequest,
    ProductResponse,
    ProductUpdateRequest,
    ProductListResponse
)
from app.services.product_service import ProductService
from app.services.image_service import get_image_service, ImageService
from app.utils.dependencies import require_admin, optional_auth
from app.utils.pagination_utils import paginate_query, PaginationParams
from app.logging.log import logger
import json

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: str = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_admin),
    image_service: ImageService = Depends(get_image_service)
):
    """
    Create a new product with optional images.
    
    This endpoint is restricted to administrators.
    Product data should be sent as a JSON string in the 'product_data' form field.
    Images are optional and can be sent as multipart/form-data files.
    """
    try:
        product_json = json.loads(product_data)
        product_request = ProductCreateRequest(**product_json)
        
        product_service = ProductService(db)
        product = await product_service.create_product(product_request)
        
        if images:
            for idx, image in enumerate(images):
                try:
                    upload_result = await image_service.upload_image(
                        image, 
                        folder=f"products/{product.id}"
                    )
                    
                    await product_service.add_product_image(
                        product_id=product.id,
                        url=upload_result["url"],
                        storage_path=upload_result["public_id"],
                        thumbnail_url=upload_result["thumbnail_url"],
                        is_primary=(idx == 0),
                        display_order=idx
                    )
                except Exception as img_error:
                    logger.error(f"Failed to upload image for product {product.id}: {str(img_error)}")
        
        await db.refresh(product)
        return ProductResponse.from_product(product)
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product data JSON"
        )
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID = Path(..., description="Product ID"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(optional_auth)
):
    """
    Get a specific product by ID.
    
    This endpoint is publicly accessible.
    Returns 404 if the product is not found.
    """
    try:
        product_service = ProductService(db)
        product = await product_service.get_product_by_id(product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return ProductResponse.from_product(product)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve product"
        )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID = Path(..., description="Product ID"),
    product_data: str = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    replace_images: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_admin),
    image_service: ImageService = Depends(get_image_service)
):
    """
    Update a product with optional new images.
    
    This endpoint is restricted to administrators.
    Returns 404 if the product is not found.
    
    Args:
        product_data: JSON string with product update data
        images: Optional new images to add
        replace_images: If true, delete existing images before adding new ones
    """
    try:
        product_json = json.loads(product_data)
        update_request = ProductUpdateRequest(**product_json)
        
        product_service = ProductService(db)
        product = await product_service.update_product(product_id, update_request)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        if images:
            if replace_images:
                existing_images = await product_service.get_product_images(product_id)
                for img in existing_images:
                    if img.storage_path:
                        image_service.delete_image(img.storage_path)
                await product_service.delete_product_images(product_id)
            
            current_count = await product_service.get_product_image_count(product_id)
            for idx, image in enumerate(images):
                try:
                    upload_result = await image_service.upload_image(
                        image, 
                        folder=f"products/{product_id}"
                    )
                    
                    await product_service.add_product_image(
                        product_id=product_id,
                        url=upload_result["url"],
                        storage_path=upload_result["public_id"],
                        thumbnail_url=upload_result["thumbnail_url"],
                        is_primary=(current_count == 0 and idx == 0),
                        display_order=current_count + idx
                    )
                except Exception as img_error:
                    logger.error(f"Failed to upload image for product {product_id}: {str(img_error)}")
        
        await db.refresh(product)
        return ProductResponse.from_product(product)
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product data JSON"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product"
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID = Path(..., description="Product ID"),
    permanent: bool = Query(False, description="Permanently delete product"),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(require_admin)
):
    """
    Delete a product.
    
    This endpoint is restricted to administrators.
    Returns 404 if the product is not found.
    """
    try:
        product_service = ProductService(db)
        success = await product_service.delete_product(product_id, permanent=permanent)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product"
        )


@router.get("/", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: str = Query(None, description="Filter by category"),
    search: str = Query(None, description="Search products"),
    min_price: float = Query(None, ge=0, description="Minimum price"),
    max_price: float = Query(None, ge=0, description="Maximum price"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(optional_auth)
):
    """
    List products with pagination and filtering.
    
    This endpoint is publicly accessible.
    
    **IMPORTANT**: This endpoint returns 200 even when no products are found.
    An empty list with total=0 is the correct response for "no products found".
    
    404 is used for:
    - GET /products/{id} when a specific product doesn't exist
    - When the endpoint itself doesn't exist
    
    200 with empty array is used for:
    - GET /products when no products match the criteria
    - This follows REST API best practices
    """
    try:
        product_service = ProductService(db)
        query = product_service.get_products_query(
            search_query=search,
            min_price=min_price,
            max_price=max_price
        )
        
        pagination_params = PaginationParams(page=page, size=size)
        result = await paginate_query(db, query, pagination_params)
        
        # Convert products to response format with images
        products_with_images = [
            ProductResponse.from_product(product) for product in result.items
        ]
        
        # IMPORTANT: Always return 200 with empty array when no products found
        # This is correct REST API behavior for collection endpoints
        response = ProductListResponse(
            products=products_with_images,
            total=result.total,
            page=result.page,
            size=result.size,
            pages=result.pages,
        )
        
        logger.info(f"Listed {len(result.items)} products (total: {result.total})")
        return response
        
    except Exception as e:
        logger.error(f"Error listing products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve products"
        )
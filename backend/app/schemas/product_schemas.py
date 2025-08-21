"""
Product schemas for ADOGENT e-commerce platform.
Defines Pydantic models for product-related API operations.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator


class ProductStatus(str, Enum):
    """Product status enum - FIXED: Use uppercase to match model and database."""
    DRAFT = "DRAFT"           
    ACTIVE = "ACTIVE"         
    ARCHIVED = "ARCHIVED"     
    OUT_OF_STOCK = "OUT_OF_STOCK"  


class ProductCondition(str, Enum):
    """Product condition enum for second-hand items - FIXED: Use uppercase to match model and database."""
    NEW = "NEW"               
    LIKE_NEW = "LIKE_NEW"     
    EXCELLENT = "EXCELLENT"   
    GOOD = "GOOD"             
    FAIR = "FAIR"             


class ProductBase(BaseModel):
    """Base schema for product data."""
    name: str = Field(..., min_length=3, max_length=255, description="Product name")
    slug: str = Field(..., min_length=3, max_length=275, description="URL-friendly name")
    description: Optional[str] = Field(None, description="Detailed product description")
    short_description: Optional[str] = Field(None, max_length=500, description="Short product description")
    category_id: UUID = Field(..., description="Category ID")
    price: float = Field(..., gt=0, description="Product price")
    compare_at_price: Optional[float] = Field(None, gt=0, description="Compare at price (original price)")
    cost_price: Optional[float] = Field(None, gt=0, description="Cost price")
    currency: str = Field(default="USD", min_length=3, max_length=3, description="Currency code")
    sku: Optional[str] = Field(None, max_length=50, description="Stock keeping unit")
    barcode: Optional[str] = Field(None, max_length=50, description="Product barcode")
    quantity: int = Field(default=0, ge=0, description="Available inventory quantity")
    low_stock_threshold: int = Field(default=5, ge=1, description="Low stock warning threshold")
    status: ProductStatus = Field(default=ProductStatus.DRAFT, description="Product status")
    is_featured: bool = Field(default=False, description="Whether product is featured")
    is_visible: bool = Field(default=True, description="Whether product is visible to customers")
    weight: Optional[float] = Field(None, gt=0, description="Product weight")
    weight_unit: Optional[str] = Field(default="kg", description="Weight unit")
    dimensions: Optional[Dict[str, float]] = Field(None, description="Product dimensions (length, width, height)")
    is_second_hand: bool = Field(default=False, description="Whether product is second-hand")
    condition: Optional[ProductCondition] = Field(None, description="Product condition for second-hand items")
    condition_description: Optional[str] = Field(None, description="Detailed condition description")
    meta_title: Optional[str] = Field(None, max_length=100, description="SEO meta title")
    meta_description: Optional[str] = Field(None, max_length=255, description="SEO meta description")
    meta_keywords: Optional[str] = Field(None, max_length=255, description="SEO meta keywords")

    @field_validator('dimensions')
    @classmethod
    def validate_dimensions(cls, v):
        """Validate product dimensions."""
        if v is not None:
            required_keys = ['length', 'width', 'height']
            if not all(key in v for key in required_keys):
                raise ValueError('Dimensions must include length, width, and height')
            if any(value <= 0 for value in v.values()):
                raise ValueError('Dimension values must be positive numbers')
        return v

    @model_validator(mode='after')
    def check_condition_fields(self):
        """Ensure condition is set when is_second_hand is True."""
        is_second_hand = self.is_second_hand
        condition = self.condition
        
        if is_second_hand is True and condition is None:
            raise ValueError('Condition must be specified for second-hand products')
        
        return self


class ProductCreateRequest(ProductBase):
    """Schema for product creation request."""
    pass


class ProductUpdateRequest(BaseModel):
    """Schema for product update request."""
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    slug: Optional[str] = Field(None, min_length=3, max_length=275)
    description: Optional[str] = Field(None)
    short_description: Optional[str] = Field(None, max_length=500)
    category_id: Optional[UUID] = Field(None)
    price: Optional[float] = Field(None, gt=0)
    compare_at_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    sku: Optional[str] = Field(None, max_length=50)
    barcode: Optional[str] = Field(None, max_length=50)
    quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=1)
    status: Optional[ProductStatus] = Field(None)
    is_featured: Optional[bool] = Field(None)
    is_visible: Optional[bool] = Field(None)
    weight: Optional[float] = Field(None, gt=0)
    weight_unit: Optional[str] = Field(None)
    dimensions: Optional[Dict[str, float]] = Field(None)
    is_second_hand: Optional[bool] = Field(None)
    condition: Optional[ProductCondition] = Field(None)
    condition_description: Optional[str] = Field(None)
    meta_title: Optional[str] = Field(None, max_length=100)
    meta_description: Optional[str] = Field(None, max_length=255)
    meta_keywords: Optional[str] = Field(None, max_length=255)


class ProductResponse(ProductBase):
    """Schema for product response."""
    id: UUID = Field(..., description="Product ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_in_stock: bool = Field(..., description="Whether product is in stock")
    is_low_stock: bool = Field(..., description="Whether product is low in stock")
    discount_percentage: Optional[int] = Field(None, description="Discount percentage if applicable")
    images: List[Dict[str, Any]] = Field(default_factory=list, description="Product images")
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_product(cls, product) -> "ProductResponse":
        """
        Safely convert a Product model to ProductResponse, handling the images relationship.
        This prevents MissingGreenlet errors when accessing relationships in async context.
        """
        # Extract all the basic product attributes
        product_data = {
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'description': product.description,
            'short_description': product.short_description,
            'category_id': product.category_id,
            'price': product.price,
            'compare_at_price': product.compare_at_price,
            'cost_price': product.cost_price,
            'currency': product.currency,
            'sku': product.sku,
            'barcode': product.barcode,
            'quantity': product.quantity,
            'low_stock_threshold': product.low_stock_threshold,
            'status': product.status,
            'is_featured': product.is_featured,
            'is_visible': product.is_visible,
            'weight': product.weight,
            'weight_unit': product.weight_unit,
            'dimensions': product.dimensions,
            'is_second_hand': product.is_second_hand,
            'condition': product.condition,
            'condition_description': product.condition_description,
            'meta_title': product.meta_title,
            'meta_description': product.meta_description,
            'meta_keywords': product.meta_keywords,
            'created_at': product.created_at,
            'updated_at': product.updated_at,
            'is_in_stock': product.is_in_stock,
            'is_low_stock': product.is_low_stock,
            'discount_percentage': product.discount_percentage,
            'images': []
        }
        
        # Safely handle images relationship
        try:
            if hasattr(product, 'images') and product.images is not None:
                product_data['images'] = [
                    {
                        'id': str(img.id),
                        'url': img.url,
                        'alt_text': img.alt_text,
                        'thumbnail_url': img.thumbnail_url,
                        'is_primary': img.is_primary,
                        'display_order': img.display_order,
                        'content_type': img.content_type,
                        'file_size': img.file_size
                    }
                    for img in product.images
                ]
        except Exception:
            # If there's any issue accessing images, just use empty list
            product_data['images'] = []
        
        return cls(**product_data)


class ProductListResponse(BaseModel):
    """Schema for paginated product list response."""
    
    products: List[ProductResponse] = Field(..., description="List of products")
    total: int = Field(..., description="Total number of products")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
"""
Product detail schemas for request/response validation in ADOGENT application.
Defines Pydantic models for product detail-related API operations.
"""

from typing import List
from pydantic import BaseModel, Field

from .category_schemas import CategoryResponse
from .product_schemas import ProductResponse
from .product_image_schemas import ProductImageResponse
from .product_variant_schemas import ProductVariantResponse
from .product_attribute_schemas import ProductAttributeResponse


class ProductDetailResponse(ProductResponse):
    """Schema for detailed product response including relationships."""
    category: CategoryResponse = Field(..., description="Product category")
    images: List[ProductImageResponse] = Field(default_factory=list, description="Product images")
    variants: List[ProductVariantResponse] = Field(default_factory=list, description="Product variants")
    attributes: List[ProductAttributeResponse] = Field(default_factory=list, description="Product attributes")
    
    class Config:
        from_attributes = True
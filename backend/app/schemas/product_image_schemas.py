"""
Product image schemas for request/response validation in ADOGENT application.
Defines Pydantic models for product image-related API operations.
"""

from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID
from pydantic import BaseModel, Field


class ProductImageBase(BaseModel):
    """Base schema for product image data."""
    product_id: UUID = Field(..., description="Product ID")
    url: str = Field(..., description="Image URL")
    alt_text: Optional[str] = Field(None, max_length=255, description="Alternative text for image")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail image URL")
    responsive_urls: Optional[Dict[str, str]] = Field(None, description="Responsive image URLs (sm, md, lg)")
    display_order: int = Field(default=0, description="Display order position")
    is_primary: bool = Field(default=False, description="Whether this is the primary product image")


class ProductImageCreateRequest(ProductImageBase):
    """Schema for product image creation request."""
    pass


class ProductImageUpdateRequest(BaseModel):
    """Schema for product image update request."""
    url: Optional[str] = Field(None, description="Image URL")
    alt_text: Optional[str] = Field(None, max_length=255, description="Alternative text for image")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail image URL")
    responsive_urls: Optional[Dict[str, str]] = Field(None, description="Responsive image URLs")
    display_order: Optional[int] = Field(None, description="Display order position")
    is_primary: Optional[bool] = Field(None, description="Whether this is the primary product image")


class ProductImageResponse(ProductImageBase):
    """Schema for product image response."""
    id: UUID = Field(..., description="Image ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class ProductImageListResponse(BaseModel):
    """Schema for product image list response."""
    items: List[ProductImageResponse] = Field(..., description="List of product images")
    total: int = Field(..., description="Total number of images")
"""
Category schemas for ADOGENT e-commerce platform.
Defines Pydantic models for category-related API operations.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class CategoryBase(BaseModel):
    """Base schema for category data."""
    name: str = Field(..., min_length=2, max_length=100, description="Category name")
    slug: str = Field(..., min_length=2, max_length=120, description="URL-friendly name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    parent_id: Optional[UUID] = Field(None, description="Parent category ID for hierarchical structure")
    is_active: bool = Field(default=True, description="Whether category is active")
    sort_order: int = Field(default=0, description="Sort order for display")
    meta_title: Optional[str] = Field(None, max_length=100, description="SEO meta title")
    meta_description: Optional[str] = Field(None, max_length=255, description="SEO meta description")
    meta_keywords: Optional[str] = Field(None, max_length=255, description="SEO meta keywords")


class CategoryCreateRequest(CategoryBase):
    """Schema for category creation request."""
    
    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        """Validate slug format."""
        if not all(c.isalnum() or c in '-_' for c in v):
            raise ValueError('Slug can only contain letters, numbers, hyphens, and underscores')
        return v.lower()


class CategoryUpdateRequest(BaseModel):
    """Schema for category update request."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    slug: Optional[str] = Field(None, min_length=2, max_length=120)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[UUID] = Field(None)
    is_active: Optional[bool] = Field(None)
    sort_order: Optional[int] = Field(None)
    meta_title: Optional[str] = Field(None, max_length=100)
    meta_description: Optional[str] = Field(None, max_length=255)
    meta_keywords: Optional[str] = Field(None, max_length=255)
    
    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        """Validate slug format."""
        if v is not None:
            if not all(c.isalnum() or c in '-_' for c in v):
                raise ValueError('Slug can only contain letters, numbers, hyphens, and underscores')
            return v.lower()
        return v


class CategoryResponse(CategoryBase):
    """Schema for category response."""
    id: UUID = Field(..., description="Category ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    product_count: int = Field(default=0, description="Number of products in this category")
    
    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Schema for paginated category list response."""
    categories: List[CategoryResponse] = Field(..., description="List of categories")
    total: int = Field(..., description="Total number of categories")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class CategoryTreeResponse(BaseModel):
    """Schema for hierarchical category tree response."""
    categories: List[CategoryResponse] = Field(..., description="Hierarchical list of categories")
    total: int = Field(..., description="Total number of categories")
"""
Product attribute schemas for request/response validation in ADOGENT application.
Defines Pydantic models for product attribute-related API operations.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class ProductAttributeBase(BaseModel):
    """Base schema for product attribute data."""
    product_id: UUID = Field(..., description="Product ID")
    name: str = Field(..., min_length=1, max_length=100, description="Attribute name")
    value: str = Field(..., description="Attribute value")
    display_name: Optional[str] = Field(None, max_length=100, description="Display name for the attribute")
    is_visible: bool = Field(default=True, description="Whether attribute is visible to customers")
    is_filterable: bool = Field(default=False, description="Whether attribute can be used for filtering")
    is_comparable: bool = Field(default=False, description="Whether attribute can be used for comparison")
    group: Optional[str] = Field(None, max_length=50, description="Attribute group for organization")


class ProductAttributeCreateRequest(ProductAttributeBase):
    """Schema for product attribute creation request."""
    pass


class ProductAttributeUpdateRequest(BaseModel):
    """Schema for product attribute update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    value: Optional[str] = Field(None)
    display_name: Optional[str] = Field(None, max_length=100)
    is_visible: Optional[bool] = Field(None)
    is_filterable: Optional[bool] = Field(None)
    is_comparable: Optional[bool] = Field(None)
    group: Optional[str] = Field(None, max_length=50)


class ProductAttributeResponse(ProductAttributeBase):
    """Schema for product attribute response."""
    id: UUID = Field(..., description="Attribute ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class ProductAttributeListResponse(BaseModel):
    """Schema for product attribute list response."""
    items: List[ProductAttributeResponse] = Field(..., description="List of product attributes")
    total: int = Field(..., description="Total number of attributes")
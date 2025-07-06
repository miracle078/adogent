"""
Product variant schemas for request/response validation in ADOGENT application.
Defines Pydantic models for product variant-related API operations.
"""

from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID
from pydantic import BaseModel, Field, model_validator


class ProductVariantBase(BaseModel):
    """Base schema for product variant data."""
    product_id: UUID = Field(..., description="Product ID")
    title: str = Field(..., min_length=1, max_length=100, description="Variant title")
    sku: Optional[str] = Field(None, max_length=50, description="Stock keeping unit")
    barcode: Optional[str] = Field(None, max_length=50, description="Barcode")
    options: Dict[str, str] = Field(..., description="Variant options (e.g., {color: 'red', size: 'M'})")
    price: Optional[float] = Field(None, gt=0, description="Variant-specific price")
    compare_at_price: Optional[float] = Field(None, gt=0, description="Variant-specific compare-at price")
    quantity: int = Field(default=0, ge=0, description="Available inventory quantity")
    is_available: bool = Field(default=True, description="Whether variant is available for purchase")
    image_url: Optional[str] = Field(None, description="Variant-specific image URL")

    @model_validator(mode='after')
    def validate_prices(self):
        """Validate price relationships."""
        if self.compare_at_price is not None and self.price is not None:
            if self.compare_at_price < self.price:
                raise ValueError('Compare-at price must be greater than or equal to current price')
        return self


class ProductVariantCreateRequest(ProductVariantBase):
    """Schema for product variant creation request."""
    pass


class ProductVariantUpdateRequest(BaseModel):
    """Schema for product variant update request."""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    sku: Optional[str] = Field(None, max_length=50)
    barcode: Optional[str] = Field(None, max_length=50)
    options: Optional[Dict[str, str]] = Field(None)
    price: Optional[float] = Field(None, gt=0)
    compare_at_price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = Field(None)
    image_url: Optional[str] = Field(None)

    @model_validator(mode='after')
    def validate_prices(self):
        """Validate price relationships if both are provided."""
        if self.compare_at_price is not None and self.price is not None:
            if self.compare_at_price < self.price:
                raise ValueError('Compare-at price must be greater than or equal to current price')
        return self


class ProductVariantResponse(ProductVariantBase):
    """Schema for product variant response."""
    id: UUID = Field(..., description="Variant ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_in_stock: bool = Field(..., description="Whether variant is in stock")
    effective_price: float = Field(..., description="Effective price (variant price or product price)")
    
    class Config:
        from_attributes = True


class ProductVariantListResponse(BaseModel):
    """Schema for product variant list response."""
    items: List[ProductVariantResponse] = Field(..., description="List of product variants")
    total: int = Field(..., description="Total number of variants")
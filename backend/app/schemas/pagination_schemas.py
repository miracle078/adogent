"""
Pagination schemas for ADOGENT e-commerce platform.
Defines Pydantic models for pagination-related API operations.
"""

from typing import TypeVar, List, Generic, Type
from pydantic import BaseModel, Field, create_model

T = TypeVar('T')

class PageMetadata(BaseModel):
    """Pagination metadata."""
    
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


def create_paginated_response_model(item_model: Type[BaseModel]) -> Type[BaseModel]:
    """
    Create a paginated response model for a specific item type.
    
    Args:
        item_model: Pydantic model for items
        
    Returns:
        Paginated response model
    """
    return create_model(
        f"Paginated{item_model.__name__}Response",
        items=(List[item_model], ...),
        metadata=(PageMetadata, ...),
        __module__=item_model.__module__,
    )
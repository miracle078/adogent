"""
Pagination utilities for ADOGENT platform.
Provides async pagination for SQLAlchemy queries with proper result objects.
"""

from typing import TypeVar, Generic, List, Any
from math import ceil
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = 1
    size: int = 20
    
    def offset(self) -> int:
        """Calculate offset from page and size."""
        return (self.page - 1) * self.size


class PaginatedResult(BaseModel, Generic[T]):
    """Paginated result with proper attributes."""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        arbitrary_types_allowed = True


async def paginate_query(
    db: AsyncSession,
    query: Select,
    pagination: PaginationParams
) -> PaginatedResult:
    """
    Paginate a SQLAlchemy query with async support.
    
    Args:
        db: Async database session
        query: SQLAlchemy select query
        pagination: Pagination parameters
        
    Returns:
        PaginatedResult with items and pagination info
    """
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    # Apply pagination to query
    paginated_query = query.offset(pagination.offset()).limit(pagination.size)
    
    # Execute paginated query
    result = await db.execute(paginated_query)
    items = result.scalars().all()
    
    # Calculate total pages
    pages = ceil(total / pagination.size) if pagination.size > 0 else 0
    
    return PaginatedResult(
        items=items,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages
    )
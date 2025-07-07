"""
Category service for ADOGENT e-commerce platform.
Handles core category operations and business logic.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.models.category import Category
from app.schemas.category_schemas import CategoryCreateRequest, CategoryUpdateRequest
from app.logging.log import logger


class CategoryService:
    """Service for category operations following ADOGENT async patterns."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize category service.
        
        Args:
            db: Database session
        """
        self.db = db

    async def create_category(
        self,
        data: CategoryCreateRequest,
        user_id: Optional[UUID] = None
    ) -> Category:
        """
        Create a new category.
        
        Args:
            data: Category data
            user_id: ID of user creating the category
            
        Returns:
            Newly created category
            
        Raises:
            ValueError: If parent category doesn't exist or circular reference detected
        """
        # Validate parent category exists if provided
        if data.parent_id:
            parent = await self.get_category_by_id(data.parent_id)
            if not parent:
                raise ValueError("Parent category does not exist")
        
        # Check for slug uniqueness
        existing = await self.get_category_by_slug(data.slug)
        if existing:
            raise ValueError(f"Category with slug '{data.slug}' already exists")
        
        # Create category data dict
        category_data = data.model_dump(exclude_unset=True)
        
        if user_id:
            category_data["created_by"] = user_id
            
        # ✅ FIXED: Create category with proper field handling
        category = Category(**category_data)
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        
        logger.info(f"Category created: {category.id} ({category.name})")
        return category

    async def get_category_by_id(self, category_id: UUID) -> Optional[Category]:
        """
        Get a category by ID.
        
        Args:
            category_id: Category ID
            
        Returns:
            Category if found, None otherwise
        """
        query = select(Category).where(
            and_(
                Category.id == category_id,
                Category.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_category_by_slug(self, slug: str) -> Optional[Category]:
        """
        Get a category by slug.
        
        Args:
            slug: Category slug
            
        Returns:
            Category if found, None otherwise
        """
        query = select(Category).where(
            and_(
                Category.slug == slug.lower(),
                Category.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def update_category(
        self,
        category_id: UUID, 
        data: CategoryUpdateRequest
    ) -> Optional[Category]:
        """
        Update a category.
        
        Args:
            category_id: Category ID
            data: Updated category data
            
        Returns:
            Updated category if found, None otherwise
            
        Raises:
            ValueError: If slug conflicts or parent category issues
        """
        # Get category
        category = await self.get_category_by_id(category_id)
        if not category:
            return None
        
        # Check slug uniqueness if being updated
        update_data = data.model_dump(exclude_unset=True)
        if 'slug' in update_data:
            existing = await self.get_category_by_slug(update_data['slug'])
            if existing and existing.id != category_id:
                raise ValueError(f"Category with slug '{update_data['slug']}' already exists")
        
        # Validate parent category if being updated
        if 'parent_id' in update_data and update_data['parent_id']:
            parent = await self.get_category_by_id(update_data['parent_id'])
            if not parent:
                raise ValueError("Parent category does not exist")
            # Prevent circular references
            if parent.id == category_id:
                raise ValueError("Category cannot be its own parent")
        
        # Update category attributes
        for key, value in update_data.items():
            if hasattr(category, key):
                setattr(category, key, value)
        
        # Always update the updated_at timestamp
        category.updated_at = datetime.utcnow()
        
        # Save changes
        await self.db.commit()
        await self.db.refresh(category)
        
        logger.info(f"Category updated: {category.id} ({category.name})")
        return category

    async def delete_category(
        self,
        category_id: UUID,
        permanent: bool = False
    ) -> bool:
        """
        Delete a category.
        
        Args:
            category_id: Category ID
            permanent: If True, permanently delete from database
            
        Returns:
            True if successful, False if category not found
            
        Raises:
            ValueError: If category has products or child categories
        """
        # Get category
        category = await self.get_category_by_id(category_id)
        if not category:
            return False
        
        # Check if category has products
        product_count = await self.get_category_product_count(category_id)
        if product_count > 0:
            raise ValueError("Cannot delete category with products. Move products to another category first.")
        
        # Check if category has child categories
        children = await self.get_child_categories(category_id)
        if children:
            raise ValueError("Cannot delete category with subcategories. Delete or move subcategories first.")
        
        if permanent:
            # Hard delete
            await self.db.delete(category)
        else:
            # Soft delete
            category.is_deleted = True
            category.deleted_at = datetime.utcnow()
            category.updated_at = datetime.utcnow()
        
        # Save changes
        await self.db.commit()
        
        logger.info(f"Category deleted: {category_id} (permanent: {permanent})")
        return True

    async def get_category_product_count(self, category_id: UUID) -> int:
        """
        Get the number of products in a category.
        
        Args:
            category_id: Category ID
            
        Returns:
            Number of products in the category
        """
        from app.models.product import Product  # Import here to avoid circular imports
        
        query = select(func.count(Product.id)).where(
            and_(
                Product.category_id == category_id,
                Product.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_child_categories(self, parent_id: UUID) -> List[Category]:
        """
        Get child categories of a parent category.
        
        Args:
            parent_id: Parent category ID
            
        Returns:
            List of child categories
        """
        query = select(Category).where(
            and_(
                Category.parent_id == parent_id,
                Category.is_deleted == False
            )
        ).order_by(Category.sort_order, Category.name)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    def get_categories_query(
        self,
        parent_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        search_query: Optional[str] = None,
        sort_by: str = "sort_order",
        sort_order: str = "asc"
    ) -> Select:
        """
        Build a query for categories with filtering.
        
        Args:
            parent_id: Filter by parent category ID (None for root categories)
            is_active: Filter by active status
            search_query: Search in name/description
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            
        Returns:
            SQLAlchemy select query
        """
        # Base query - only non-deleted categories
        query = select(Category).where(Category.is_deleted == False)
        
        # Apply filters
        if parent_id is not None:
            query = query.where(Category.parent_id == parent_id)
            
        if is_active is not None:
            query = query.where(Category.is_active == is_active)
            
        if search_query:
            search_filter = or_(
                Category.name.ilike(f"%{search_query}%"),
                Category.description.ilike(f"%{search_query}%")
            )
            query = query.where(search_filter)
            
        # Apply sorting
        sort_column = getattr(Category, sort_by, Category.sort_order)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc(), Category.name.asc())
        else:
            query = query.order_by(sort_column.asc(), Category.name.asc())
            
        return query

    async def get_category_tree(self) -> List[Category]:
        """
        Get all categories in a hierarchical tree structure.
        
        Returns:
            List of root categories with their children populated
        """
        # Get all categories
        query = select(Category).where(Category.is_deleted == False).order_by(Category.sort_order, Category.name)
        result = await self.db.execute(query)
        all_categories = result.scalars().all()
        
        # Build tree structure
        category_map = {cat.id: cat for cat in all_categories}
        root_categories = []
        
        for category in all_categories:
            if category.parent_id is None:
                root_categories.append(category)
            else:
                parent = category_map.get(category.parent_id)
                if parent:
                    if not hasattr(parent, 'children'):
                        parent.children = []
                    parent.children.append(category)
        
        return root_categories
    
"""
Category service pour ADOGENT e-commerce platform.
CRUD et arbre hiérarchique.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category_schemas import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
)
from app.logging.log import logger


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: CategoryCreateRequest) -> Category:
        db_obj = Category(**payload.model_dump())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        logger.info(f"Categorie créée: {db_obj.id}")
        return db_obj

    async def get_by_id(self, category_id: UUID) -> Optional[Category]:
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        result = await self.db.execute(
            select(Category).where(Category.slug == slug)
        )
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> List[Category]:
        result = await self.db.execute(
            select(Category).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update(
        self, category_id: UUID, payload: CategoryUpdateRequest
    ) -> Optional[Category]:
        db_obj = await self.get_by_id(category_id)
        if not db_obj:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        await self.db.commit()
        await self.db.refresh(db_obj)
        logger.info(f"Categorie mise à jour: {db_obj.id}")
        return db_obj

    async def delete(self, category_id: UUID) -> None:
        await self.db.execute(delete(Category).where(Category.id == category_id))
        await self.db.commit()
        logger.info(f"Categorie supprimée: {category_id}")

    async def get_tree(self) -> List[Category]:
        all_cats = (await self.db.execute(select(Category))).scalars().all()
        by_id = {c.id: c for c in all_cats}
        tree: List[Category] = []
        for c in all_cats:
            if c.parent_id and c.parent_id in by_id:
                by_id[c.parent_id].children.append(c)
            else:
                tree.append(c)
        return tree

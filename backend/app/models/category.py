"""
Category model for ADOGENT e-commerce platform.
Handles product categorization and hierarchical organization.
"""

from typing import Optional, List
from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base_model import BaseModel


class Category(BaseModel):
    """
    Category model for organizing products hierarchically.
    
    Supports nested categories with parent-child relationships.
    """
    
    __tablename__ = "categories"
    
    # Basic Information
    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(120), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Hierarchy
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    
    # Status and Organization
    is_active = Column(Boolean, default=True, nullable=False) 
    sort_order = Column(Integer, default=0, nullable=False)
    
    # SEO Fields
    meta_title = Column(String(100), nullable=True)
    meta_description = Column(String(255), nullable=True)
    meta_keywords = Column(String(255), nullable=True)
    
    # Relationships
    parent = relationship("Category", remote_side="Category.id", back_populates="children")
    children = relationship("Category", back_populates="parent")
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', slug='{self.slug}')>"
    
    def get_full_path(self) -> str:
        """Get the full category path (e.g., 'Electronics > Phones > Smartphones')."""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
    
    def get_all_children(self) -> List["Category"]:
        """Get all descendant categories recursively."""
        all_children = []
        for child in self.children:
            all_children.append(child)
            all_children.extend(child.get_all_children())
        return all_children
    
    def is_descendant_of(self, potential_ancestor: "Category") -> bool:
        """Check if this category is a descendant of another category."""
        if not self.parent:
            return False
        if self.parent == potential_ancestor:
            return True
        return self.parent.is_descendant_of(potential_ancestor)
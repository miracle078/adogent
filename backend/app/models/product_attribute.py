"""
ProductAttribute model for ADOGENT e-commerce platform.
Handles product specifications and custom attributes.
"""

from sqlalchemy import Column, String, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base_model import BaseModel


class ProductAttribute(BaseModel):
    """
    ProductAttribute model for product specifications.
    
    Stores product attributes like material, dimensions,
    technical specifications, or any custom attributes.
    """
    
    __tablename__ = "product_attributes"
    
    # Product Reference
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    
    # Attribute Data
    name = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    
    # Display properties
    display_name = Column(String(100), nullable=True)
    is_visible = Column(Boolean, default=True, nullable=False)
    is_filterable = Column(Boolean, default=False, nullable=False)
    is_comparable = Column(Boolean, default=False, nullable=False)
    
    # Grouping
    group = Column(String(50), nullable=True)  # e.g., "Technical", "Physical", "Materials"
    
    # Relationships
    product = relationship("Product", back_populates="attributes")
    
    def __repr__(self):
        return f"<ProductAttribute(id={self.id}, product_id={self.product_id}, name='{self.name}')>"
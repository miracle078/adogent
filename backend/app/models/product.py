"""
Product model for ADOGENT e-commerce platform.
Core model for all product data.
"""

from typing import Optional
from sqlalchemy import Column, String, Text, Float, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from .base_model import BaseModel


class ProductStatus(enum.Enum):
    """Product status enumeration - FIXED: Use uppercase to match database."""
    DRAFT = "DRAFT"           
    ACTIVE = "ACTIVE"         
    ARCHIVED = "ARCHIVED"    
    OUT_OF_STOCK = "OUT_OF_STOCK" 


class ProductCondition(enum.Enum):
    """Product condition enumeration for second-hand items - FIXED: Use uppercase to match database."""
    NEW = "NEW"              
    LIKE_NEW = "LIKE_NEW"     
    EXCELLENT = "EXCELLENT"   
    GOOD = "GOOD"            
    FAIR = "FAIR"


class Product(BaseModel):
    """
    Product model for the e-commerce platform.
    
    Stores all core product information, pricing, and inventory data.
    Supports both new and second-hand products.
    """
    
    __tablename__ = "products"
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(275), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    
    # Category
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False, index=True)
    
    # Pricing
    price = Column(Float, nullable=False)
    compare_at_price = Column(Float, nullable=True)
    cost_price = Column(Float, nullable=True)
    currency = Column(String(3), nullable=False, default="USD")
    
    # Inventory
    sku = Column(String(50), nullable=True, unique=True, index=True)
    barcode = Column(String(50), nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, nullable=False, default=5)
    
    # Status and Visibility
    status = Column(Enum(ProductStatus), nullable=False, default=ProductStatus.DRAFT)
    is_featured = Column(Boolean, nullable=False, default=False)
    is_visible = Column(Boolean, nullable=False, default=True)
    
    # Physical Properties
    weight = Column(Float, nullable=True)
    weight_unit = Column(String(10), nullable=True, default="kg")
    dimensions = Column(JSONB, nullable=True)
    
    # Second-hand Features
    is_second_hand = Column(Boolean, nullable=False, default=False)
    condition = Column(Enum(ProductCondition), nullable=True)
    condition_description = Column(Text, nullable=True)
    
    # SEO
    meta_title = Column(String(100), nullable=True)
    meta_description = Column(String(255), nullable=True)
    meta_keywords = Column(String(255), nullable=True)
    
    # Advanced Features
    search_vector = Column(String(500), nullable=True)
    ai_summary = Column(Text, nullable=True)
    
    # Relationships - ONLY include what exists in the current system
    category = relationship("Category", back_populates="products")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
    
    @property
    def is_in_stock(self) -> bool:
        """Check if product is in stock."""
        return self.quantity > 0 and self.status == ProductStatus.ACTIVE
    
    @property
    def is_low_stock(self) -> bool:
        """Check if product is low in stock."""
        return 0 < self.quantity <= self.low_stock_threshold
    
    @property
    def discount_percentage(self) -> Optional[int]:
        """Calculate discount percentage if compare_at_price is set."""
        if self.compare_at_price and self.compare_at_price > self.price:
            return int(((self.compare_at_price - self.price) / self.compare_at_price) * 100)
        return None
"""
ProductVariant model for ADOGENT e-commerce platform.
Handles product variations like size, color, etc.
"""

from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base_model import BaseModel


class ProductVariant(BaseModel):
    """
    ProductVariant model for product variations.
    
    Handles different variations of a product such as
    size, color, material, etc. with separate pricing
    and inventory tracking.
    """
    
    __tablename__ = "product_variants"
    
    # Product Reference
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    
    # Variant Information
    title = Column(String(100), nullable=False)
    sku = Column(String(50), nullable=True, unique=True, index=True)
    barcode = Column(String(50), nullable=True, unique=True)
    
    # Variant Options
    options = Column(JSONB, nullable=False)  # {color: "red", size: "M", etc.}
    
    # Pricing (if different from main product)
    price = Column(Float, nullable=True)
    compare_at_price = Column(Float, nullable=True)
    
    # Inventory
    quantity = Column(Integer, default=0, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    
    # Media
    image_url = Column(String(255), nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="variants")
    
    def __repr__(self):
        return f"<ProductVariant(id={self.id}, product_id={self.product_id}, title='{self.title}')>"
    
    @property
    def is_in_stock(self) -> bool:
        """Check if variant is in stock."""
        return self.quantity > 0
    
    @property
    def effective_price(self) -> float:
        """Get the effective price, falling back to product price if not set."""
        return self.price if self.price is not None else self.product.price
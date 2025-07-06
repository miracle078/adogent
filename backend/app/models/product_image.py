"""
ProductImage model for ADOGENT e-commerce platform.
"""

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base_model import BaseModel


class ProductImage(BaseModel):
    """ProductImage model for storing product images."""
    
    __tablename__ = "product_images"
    
    # Existing fields
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    url = Column(String(255), nullable=False)
    
    # Enhanced fields for better image management
    storage_path = Column(String(255), nullable=True)  # S3 path or Cloudinary public_id
    storage_provider = Column(String(20), default="cloudinary", nullable=False)  # "s3" or "cloudinary"
    content_type = Column(String(50), nullable=True)  # e.g., "image/jpeg"
    file_size = Column(Integer, nullable=True)  
    
  
    alt_text = Column(String(255), nullable=True)
    thumbnail_url = Column(String(255), nullable=True)
    responsive_urls = Column(JSONB, nullable=True) 
    display_order = Column(Integer, default=0, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)

    product = relationship("Product", back_populates="images")
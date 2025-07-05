import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base


class BaseModel(Base):
    """
    Base model class with common fields for all database tables.
    
    Provides:
    - UUID primary key
    - Created/updated timestamps
    - Soft delete functionality
    - Common utility methods
    """
    
    __abstract__ = True
    
    # Primary Key - UUID4
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Soft Delete
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def soft_delete(self):
        """Mark record as deleted without removing from database."""
        self.is_deleted = True
        self.deleted_at = func.now()
    
    def restore(self):
        """Restore soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
    
    @property
    def is_active(self) -> bool:
        """Check if record is active (not soft-deleted)."""
        return not self.is_deleted and self.deleted_at is None
    
    def to_dict(self) -> dict:
        """Convert model to dictionary representation."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

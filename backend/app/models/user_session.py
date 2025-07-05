"""
User session model for ADOGENT application.
Handles JWT tokens and session management.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base_model import BaseModel


class UserSession(BaseModel):
    """
    User session model for tracking active sessions and JWT tokens.
    
    This model helps manage user sessions, token blacklisting,
    and provides security tracking for user authentication.
    """
    
    __tablename__ = "user_sessions"
    
    # User Reference
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    
    # Session Information
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    refresh_token = Column(String(255), unique=True, index=True, nullable=False)
    
    # Device and Location Information
    device_info = Column(Text, nullable=True)  # JSON string with device details
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    
    # Session Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    expires_at = Column(DateTime, nullable=False)
    last_accessed = Column(DateTime, default=func.now(), nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, active={self.is_active})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if session is valid (active and not expired)."""
        return self.is_active and not self.is_revoked and not self.is_expired
    
    def revoke(self):
        """Revoke the session."""
        self.is_active = False
        self.is_revoked = True
        self.revoked_at = func.now()
    
    def update_last_accessed(self):
        """Update last accessed timestamp."""
        self.last_accessed = func.now()

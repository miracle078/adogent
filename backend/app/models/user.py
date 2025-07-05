"""
User model for ADOGENT application.
Handles user authentication, profiles, and preferences.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from .base_model import BaseModel


class UserRole(enum.Enum):
    """User role enumeration."""
    CUSTOMER = "customer"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserStatus(enum.Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(BaseModel):
    """
    User model for authentication and profile management.
    
    This model handles user authentication, basic profile information,
    and user preferences for the AI-powered e-commerce platform.
    """
    
    __tablename__ = "users"
    
    # Authentication Fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Profile Information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    
    # User Status and Role
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    
    # Preferences for AI Personalization
    preferred_language = Column(String(10), default="en", nullable=False)
    preferred_currency = Column(String(5), default="USD", nullable=False)
    
    # AI Interaction Preferences
    voice_preference = Column(String(50), nullable=True)  # Voice assistant preferences
    ai_interaction_style = Column(String(50), default="friendly", nullable=False)  # casual, professional, friendly
    
    # Shopping Preferences
    shopping_categories = Column(Text, nullable=True)  # JSON string of preferred categories
    price_range_preference = Column(String(20), nullable=True)  # budget, mid-range, luxury
    
    # Privacy Settings
    allow_personalization = Column(Boolean, default=True, nullable=False)
    allow_marketing_emails = Column(Boolean, default=False, nullable=False)
    allow_voice_data_storage = Column(Boolean, default=True, nullable=False)
    
    # Security Fields
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    last_login = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return self.username
    
    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN
    
    @property
    def is_customer(self) -> bool:
        """Check if user is a customer."""
        return self.role == UserRole.CUSTOMER
    
    @property
    def is_moderator(self) -> bool:
        """Check if user is a moderator."""
        return self.role == UserRole.MODERATOR
    
    @property
    def is_account_active(self) -> bool:
        """Check if account is active and not suspended."""
        return (
            self.is_active and 
            self.status == UserStatus.ACTIVE
        )
    
    def can_login(self) -> bool:
        """Check if user can login."""
        return (
            self.is_account_active and 
            self.failed_login_attempts < 5  # Max 5 failed attempts
        )
    
    def reset_failed_login_attempts(self):
        """Reset failed login attempts counter."""
        self.failed_login_attempts = 0
    
    def increment_failed_login_attempts(self):
        """Increment failed login attempts."""
        self.failed_login_attempts += 1
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = func.now()

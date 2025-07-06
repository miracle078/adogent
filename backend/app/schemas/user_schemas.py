"""
User schemas for request/response validation in ADOGENT application.
Defines Pydantic models for user-related API operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration for API."""
    CUSTOMER = "customer"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserStatus(str, Enum):
    """User status enumeration for API."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class AIInteractionStyle(str, Enum):
    """AI interaction style preferences."""
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"


class PriceRangePreference(str, Enum):
    """Price range preference for shopping."""
    BUDGET = "budget"
    MID_RANGE = "mid-range"
    LUXURY = "luxury"


# Base schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=100, description="Unique username")
    first_name: Optional[str] = Field(None, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User's last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="User's phone number")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v.lower()
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Phone number can only contain digits, spaces, hyphens, and plus sign')
        return v


# Request schemas
class UserCreateRequest(UserBase):
    """Schema for user registration request."""
    
    password: str = Field(..., min_length=8, description="User's password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    # Optional preference fields
    preferred_language: str = Field(default="en", max_length=10, description="Preferred language code")
    preferred_currency: str = Field(default="USD", max_length=5, description="Preferred currency code")
    allow_marketing_emails: bool = Field(default=False, description="Allow marketing emails")
    allow_personalization: bool = Field(default=True, description="Allow AI personalization")
    allow_voice_data_storage: bool = Field(default=True, description="Allow voice data storage")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLoginRequest(BaseModel):
    """Schema for user login request."""
    
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    remember_me: bool = Field(default=False, description="Remember user for extended session")


class UserUpdateRequest(BaseModel):
    """Schema for user profile update request."""
    
    first_name: Optional[str] = Field(None, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User's last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="User's phone number")
    date_of_birth: Optional[datetime] = Field(None, description="User's date of birth")
    
    # Preferences
    preferred_language: Optional[str] = Field(None, max_length=10, description="Preferred language code")
    preferred_currency: Optional[str] = Field(None, max_length=5, description="Preferred currency code")
    voice_preference: Optional[str] = Field(None, max_length=50, description="Voice assistant preference")
    ai_interaction_style: Optional[AIInteractionStyle] = Field(None, description="AI interaction style")
    price_range_preference: Optional[PriceRangePreference] = Field(None, description="Price range preference")
    
    # Privacy settings
    allow_personalization: Optional[bool] = Field(None, description="Allow AI personalization")
    allow_marketing_emails: Optional[bool] = Field(None, description="Allow marketing emails")
    allow_voice_data_storage: Optional[bool] = Field(None, description="Allow voice data storage")


class PasswordChangeRequest(BaseModel):
    """Schema for password change request."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_new_password: str = Field(..., description="New password confirmation")
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


# Response schemas
class UserResponse(BaseModel):
    """Schema for user response."""
    
    id: UUID = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="Username")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    phone_number: Optional[str] = Field(None, description="User's phone number")
    role: UserRole = Field(..., description="User role")
    status: UserStatus = Field(..., description="User status")
    
    # Preferences
    preferred_language: str = Field(..., description="Preferred language")
    preferred_currency: str = Field(..., description="Preferred currency")
    ai_interaction_style: str = Field(..., description="AI interaction style")
    
    # Timestamps
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    
    class Config:
        from_attributes = True


class UserProfileResponse(UserResponse):
    """Extended user profile response with additional details."""
    
    full_name: str = Field(..., description="User's full name")
    date_of_birth: Optional[datetime] = Field(None, description="User's date of birth")
    voice_preference: Optional[str] = Field(None, description="Voice preference")
    price_range_preference: Optional[str] = Field(None, description="Price range preference")
    
    # Privacy settings
    allow_personalization: bool = Field(..., description="Allow personalization")
    allow_marketing_emails: bool = Field(..., description="Allow marketing emails")
    allow_voice_data_storage: bool = Field(..., description="Allow voice data storage")


class AuthTokenResponse(BaseModel):
    """Schema for authentication token response."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""
    
    refresh_token: str = Field(..., description="Refresh token")


class UserListResponse(BaseModel):
    """Schema for user list response with pagination."""
    
    users: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class MessageResponse(BaseModel):
    """Schema for simple message responses."""
    
    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Operation success status")


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    success: bool = Field(default=False, description="Operation success status")


class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses."""
    
    error: str = Field(default="validation_error", description="Error type")
    message: str = Field(..., description="Error message")
    errors: list[dict] = Field(..., description="List of validation errors")
    success: bool = Field(default=False, description="Operation success status")

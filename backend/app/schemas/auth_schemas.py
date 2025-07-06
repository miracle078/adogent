"""
Authentication schemas for ADOGENT application.
Defines Pydantic models for authentication-related API operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="User's username")
    first_name: Optional[str] = Field(None, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User's last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="User's phone number")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only letters, numbers, hyphens, and underscores')
        return v.lower()


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=100, 
        description="User's password (min 8 characters)"
    )
    confirm_password: str = Field(
        ..., 
        min_length=8, 
        max_length=100, 
        description="Confirm password (must match password)"
    )
    
    # User preferences (from user_schemas.py structure)
    preferred_language: str = Field(default="en", max_length=10, description="User's preferred language")
    preferred_currency: str = Field(default="USD", max_length=5, description="User's preferred currency")
    allow_marketing_emails: bool = Field(default=False, description="Allow marketing emails")
    allow_personalization: bool = Field(default=True, description="Allow personalization")
    allow_voice_data_storage: bool = Field(default=True, description="Allow voice data storage")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @model_validator(mode='after')
    def validate_passwords_match(self):
        """Validate that password and confirm_password match."""
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class UserResponse(UserBase):
    """Schema for user response (public user data)."""
    
    id: UUID = Field(..., description="User's unique identifier")
    role: str = Field(..., description="User's role")
    status: str = Field(..., description="User's status")
    preferred_language: str = Field(..., description="User's preferred language")
    preferred_currency: str = Field(..., description="User's preferred currency")
    created_at: datetime = Field(..., description="User creation timestamp")
    last_login: Optional[datetime] = Field(None, description="User's last login timestamp")
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    preferred_language: Optional[str] = Field(None, max_length=10)
    preferred_currency: Optional[str] = Field(None, max_length=5)
    voice_preference: Optional[str] = Field(None, max_length=50)
    ai_interaction_style: Optional[str] = Field(None, max_length=50)
    price_range_preference: Optional[str] = Field(None, max_length=20)
    allow_personalization: Optional[bool] = None
    allow_marketing_emails: Optional[bool] = None
    allow_voice_data_storage: Optional[bool] = None


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenRefresh(BaseModel):
    """Schema for refreshing JWT tokens."""
    
    refresh_token: str = Field(..., description="Refresh token")


class TokenData(BaseModel):
    """Schema for JWT token data."""
    
    user_id: UUID = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email")
    role: str = Field(..., description="User role")
    is_verified: bool = Field(..., description="User verification status")


class PasswordChange(BaseModel):
    """Schema for changing user password."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., 
        min_length=8, 
        max_length=100, 
        description="New password (min 8 characters)"
    )
    confirm_new_password: str = Field(
        ..., 
        min_length=8, 
        max_length=100, 
        description="Confirm new password"
    )
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @model_validator(mode='after')
    def validate_new_passwords_match(self):
        """Validate that new_password and confirm_new_password match."""
        if self.new_password != self.confirm_new_password:
            raise ValueError('New passwords do not match')
        return self


class UserPreferences(BaseModel):
    """Schema for user AI and shopping preferences."""
    
    voice_preference: Optional[str] = Field(None, max_length=50)
    ai_interaction_style: str = Field(default="friendly", max_length=50)
    shopping_categories: Optional[str] = Field(None, description="JSON string of preferred categories")
    price_range_preference: Optional[str] = Field(None, max_length=20)
    allow_personalization: bool = Field(default=True)
    allow_marketing_emails: bool = Field(default=False)
    allow_voice_data_storage: bool = Field(default=True)
    
    class Config:
        from_attributes = True


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


class AuthErrorResponse(BaseModel):
    """Schema for authentication error responses."""
    
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
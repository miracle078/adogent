"""
Custom exception classes for ADOGENT platform.
Provides specific exceptions for different error scenarios.
"""

from typing import Optional, Dict, Any


class ADOGENTException(Exception):
    """Base exception class for ADOGENT application."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(ADOGENTException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(ADOGENTException):
    """Raised when user lacks required permissions."""
    pass


class ValidationError(ADOGENTException):
    """Raised when data validation fails."""
    pass


class NotFoundError(ADOGENTException):
    """Raised when requested resource is not found."""
    pass


class ConflictError(ADOGENTException):
    """Raised when resource already exists or conflicts."""
    pass


class DatabaseError(ADOGENTException):
    """Raised when database operations fail."""
    pass


class ExternalServiceError(ADOGENTException):
    """Raised when external service calls fail."""
    pass


class AIAgentError(ADOGENTException):
    """Raised when AI agent operations fail."""
    pass


class GroqAPIError(ExternalServiceError):
    """Raised when Groq API calls fail."""
    pass


class RateLimitError(ADOGENTException):
    """Raised when rate limits are exceeded."""
    pass


class ConfigurationError(ADOGENTException):
    """Raised when configuration is invalid."""
    pass
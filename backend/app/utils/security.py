"""
Security utilities for ADOGENT platform.
Handles password hashing, JWT token operations, and security helpers.
"""

import secrets
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID
from jose import JWTError, jwt

from app.config.config import settings

class AuthenticationError(Exception):
    """Exception raised for authentication errors."""
    pass

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    # Use a version-independent approach
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def generate_jwt_token(
    payload: Dict[str, Any],
    secret_key: str,
    algorithm: str = "HS256",
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate JWT token with payload.
    
    Args:
        payload: Token payload
        secret_key: Secret key for signing
        algorithm: JWT algorithm
        expires_delta: Token expiration time
        
    Returns:
        JWT token string
    """
    to_encode = payload.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def decode_jwt_token(token: str, secret_key: str, algorithm: str) -> dict:
    """
    Decode and validate JWT token.
    
    Args:
        token: JWT token to decode
        secret_key: Secret key for validation
        algorithm: JWT algorithm
        
    Returns:
        Decoded token payload
        
    Raises:
        AuthenticationError: If token is invalid
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        
        # Map short claim names back to standard claims if they exist
        if "u" in payload:
            payload["sub"] = payload.pop("u")
        if "t" in payload:
            payload["type"] = "refresh" if payload.pop("t") == "r" else "access"
        if "i" in payload:
            payload["jti"] = payload.pop("i")
            
        return payload
    except jwt.PyJWTError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")


def create_access_token(
    user_id: UUID,
    username: str,
    email: str,
    role: str,
    is_verified: bool
) -> str:
    """
    Create access token for user.
    
    Args:
        user_id: User ID
        username: Username
        email: User email
        role: User role
        is_verified: User verification status
        
    Returns:
        Access token
    """
    payload = {
        "sub": str(user_id),
        "type": "access",
        "username": username,
        "email": email,
        "role": role,
        "is_verified": is_verified,
        "jti": secrets.token_urlsafe(32),
    }
    
    return generate_jwt_token(
        payload=payload,
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def create_refresh_token(user_id: UUID) -> str:
    """
    Create a refresh token with optimized size to fit within VARCHAR(255).
    
    Args:
        user_id: The user ID to encode in the token
        
    Returns:
        JWT refresh token string
    """
    # Create optimized payload with shorter claim names
    payload = {
        "u": str(user_id),  # sub -> u (subject/user_id)
        "t": "r",           # type -> t, "refresh" -> "r"
        "i": secrets.token_urlsafe(16),  # jti -> i (JWT ID, using shorter random string)
        "exp": datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        # Removed "iat" (issued at) claim to save space
    }
    
    # Generate token with optimized payload
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return token


def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token.
    
    Args:
        length: Token length
        
    Returns:
        Secure random token
    """
    return secrets.token_urlsafe(length)


def validate_password_strength(password: str) -> bool:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        True if password meets strength requirements
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    return has_upper and has_lower and has_digit and has_special
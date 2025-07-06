"""
Configuration settings for ADOGENT application.
All environment variables and application settings are managed here.
"""

from decouple import config
from typing import Optional


class Settings:
    """Application settings with environment variable support."""
    
    # Application Settings
    APP_NAME: str = config("APP_NAME", default="ADOGENT")
    APP_VERSION: str = config("APP_VERSION", default="1.0.0")
    DEBUG: bool = config("DEBUG", default=False, cast=bool)
    ENVIRONMENT: str = config("ENV", default="development")
    
    # Database Configuration
    USER: str = config("USER")
    PASSWORD: str = config("PASSWORD")
    HOST: str = config("HOST")
    PORT: int = config("PORT", cast=int)
    DB_NAME: str = config("DB_NAME")

    # Security Settings
    JWT_SECRET_KEY: str = config("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = config("JWT_ALGORITHM", default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = config("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = config("JWT_REFRESH_TOKEN_EXPIRE_DAYS", default=7, cast=int)
    
    # Password Security
    PASSWORD_MIN_LENGTH: int = config("PASSWORD_MIN_LENGTH", default=8, cast=int)
    BCRYPT_ROUNDS: int = config("BCRYPT_ROUNDS", default=12, cast=int)
    ADMIN_BOOTSTRAP_API_KEY: str = config("ADMIN_BOOTSTRAP_API_KEY")    
    # Groq API Configuration
    GROQ_API_KEY: str = config("GROQ_API_KEY")
    GROQ_MODEL: str = config("GROQ_MODEL", default="llama3-70b-8192")
    GROQ_MAX_TOKENS: int = config("GROQ_MAX_TOKENS", default=1024, cast=int)
    GROQ_TEMPERATURE: float = config("GROQ_TEMPERATURE", default=0.7, cast=float)
    GROQ_TIMEOUT: int = config("GROQ_TIMEOUT", default=30, cast=int)
    
    # Ollama Configuration (simplified for LangChain)
    OLLAMA_MODEL: str = config("OLLAMA_MODEL", default="llava:7b")
    OLLAMA_TEMPERATURE: float = config("OLLAMA_TEMPERATURE", default=0.7, cast=float)
    OLLAMA_TIMEOUT: int = config("OLLAMA_TIMEOUT", default=60, cast=int)
    
    # AI Agent Configuration
    MAX_CONVERSATION_HISTORY: int = config("MAX_CONVERSATION_HISTORY", default=10, cast=int)
    ENABLE_CONVERSATION_CONTEXT: bool = config("ENABLE_CONVERSATION_CONTEXT", default=True, cast=bool)
    PRODUCT_RECOMMENDATION_LIMIT: int = config("PRODUCT_RECOMMENDATION_LIMIT", default=5, cast=int)
    
    # API Settings
    API_V1_PREFIX: str = config("API_V1_PREFIX", default="/api/v1")
    CORS_ORIGINS: list = config("CORS_ORIGINS", default="*").split(",")
    RATE_LIMIT_PER_MINUTE: int = config("RATE_LIMIT_PER_MINUTE", default=60, cast=int)
    
    # File Upload Settings
    MAX_FILE_SIZE: int = config("MAX_FILE_SIZE", default=10 * 1024 * 1024, cast=int)  # 10MB
    ALLOWED_FILE_TYPES: list[str] = config("ALLOWED_FILE_TYPES", default="image/jpeg,image/png,image/webp").split(",")
    
    # Logging Configuration
    LOG_LEVEL: str = config("LOG_LEVEL", default="INFO")
    LOG_FORMAT: str = config("LOG_FORMAT", default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Future configurations (commented out for now)
    # Redis Configuration
    # REDIS_URL: Optional[str] = config("REDIS_URL", default=None)
    # CACHE_TTL: int = config("CACHE_TTL", default=3600, cast=int)
    
    # AWS Configuration
    # AWS_REGION: str = config("AWS_REGION", default="us-east-1")
    # AWS_ACCESS_KEY_ID: Optional[str] = config("AWS_ACCESS_KEY_ID", default=None)
    # AWS_SECRET_ACCESS_KEY: Optional[str] = config("AWS_SECRET_ACCESS_KEY", default=None)
    # AWS_S3_BUCKET: Optional[str] = config("AWS_S3_BUCKET", default=None)
    
    # Email Configuration
    # EMAIL_HOST: Optional[str] = config("EMAIL_HOST", default=None)
    # EMAIL_PORT: int = config("EMAIL_PORT", default=587, cast=int)
    # EMAIL_USERNAME: Optional[str] = config("EMAIL_USERNAME", default=None)
    # EMAIL_PASSWORD: Optional[str] = config("EMAIL_PASSWORD", default=None)
    # EMAIL_USE_TLS: bool = config("EMAIL_USE_TLS", default=True, cast=bool)
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic migrations."""
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings

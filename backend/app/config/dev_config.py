"""
Development configuration override for ADOGENT application.
This file forces SQLite usage for local development.
"""

import os
from app.config.config import Settings


class DevSettings(Settings):
    """Development settings that override production settings."""
    
    # Force SQLite for development
    USE_SQLITE: bool = True
    SQLITE_DB_PATH: str = "adogent.db"
    
    # Override database settings for local development
    USER: str = "john.doe@example.com"
    PASSWORD: str = "SecurePass123!"
    HOST: str = "localhost"
    PORT: int = 5432
    DB_NAME: str = "adogent_db"
    
    # Enable debug mode
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    @property
    def database_url(self) -> str:
        """Get SQLite database URL for development."""
        return f"sqlite:///./{self.SQLITE_DB_PATH}"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous SQLite database URL for Alembic migrations."""
        return f"sqlite:///./{self.SQLITE_DB_PATH}"


# Override the global settings for development
if os.getenv("ENV", "development") == "development":
    settings = DevSettings()
else:
    from app.config.config import settings 
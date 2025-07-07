from decouple import config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import create_database, database_exists
from app.config.dev_config import settings

Base = declarative_base()


def get_engine():
    """Get database engine based on configuration."""
    if settings.USE_SQLITE and settings.is_development:
        # Use SQLite for development
        url = f"sqlite+aiosqlite:///./{settings.SQLITE_DB_PATH}"
        engine = create_async_engine(
            url,
            connect_args={"check_same_thread": False},  # Required for SQLite
            echo=settings.DEBUG
        )
    else:
        # Use PostgreSQL for production
        user = config("USER")
        password = config("PASSWORD")
        host = config("HOST")
        port = int(config("PORT"))
        db_name = config("DB_NAME")
        
        # Use async driver for PostgreSQL
        url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"
        
        # Create database if it doesn't exist (sync operation)
        sync_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
        if not database_exists(sync_url):
            create_database(sync_url)

        # Create async engine with your existing settings
        engine = create_async_engine(
            url,
            pool_size=20,  # Increased from 5 to 20 connections per worker
            max_overflow=30,  # Increased from 10 to 30 additional connections
            pool_timeout=60,  # Increased timeout to 60 seconds
            pool_recycle=1800,  # Recycle connections after 30 minutes
            pool_pre_ping=True,  # Enable connection health checks
            echo=settings.DEBUG
        )
    
    return engine


# Create engine using the new configuration
engine = get_engine()

# Create async session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

sync_session = SessionLocal

async def get_db() -> AsyncSession:
    """Get async database session dependency."""
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
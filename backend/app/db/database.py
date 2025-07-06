from decouple import config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import create_database, database_exists

Base = declarative_base()


def get_engine(user, passwd, host, port, db):
    # Use async driver for PostgreSQL
    url = f"postgresql+asyncpg://{user}:{passwd}@{host}:{port}/{db}"
    
    # Create database if it doesn't exist (sync operation)
    sync_url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
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
        echo=False
    )
    return engine


settings = {
    "user": config("USER"),
    "password": config("PASSWORD"),
    "host": config("HOST"),
    "port": int(config("PORT")),
    "db_name": config("DB_NAME"),
}

engine = get_engine(
    user=settings["user"],
    passwd=settings["password"],
    host=settings["host"],
    port=settings["port"],
    db=settings["db_name"],
)

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
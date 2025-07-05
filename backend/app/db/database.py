
from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists

Base = declarative_base()


def get_engine(user, passwd, host, port, db):
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    if not database_exists(url):
        create_database(url)

    # Create the SQLAlchemy engine with optimized pool settings
    engine = create_engine(
        url,
        pool_size=20,  # Increased from 5 to 20 connections per worker
        max_overflow=30,  # Increased from 10 to 30 additional connections
        pool_timeout=60,  # Increased timeout to 60 seconds
        pool_recycle=1800,  # Recycle connections after 30 minutes
        pool_pre_ping=True,  # Enable connection health checks
        echo=False
    )
    # Create all tables in the database using the model files
    Base.metadata.create_all(bind=engine)
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

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

sync_session = SessionLocal

def get_sync_session() -> Session:
    """Get a synchronous database session."""
    return SessionLocal()

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

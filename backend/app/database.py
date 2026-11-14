"""Database connection and session configuration using SQLAlchemy."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Load environment variables from .env file
load_dotenv()

# Retrieve database connection string
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in backend/.env")

# Create database engine with connection health check (pool_pre_ping)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create session factory for incoming requests
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy ORM models."""
    pass


def get_db():
    """Dependency generator that yields a database session per request and ensures proper closing."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

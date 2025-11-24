# backend/database/config.py
"""
Database configuration and connection management.
"""

import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()
logger = logging.getLogger(__name__)

# Database configuration from environment variables
# Supports both PostgreSQL and SQLite
# PostgreSQL: postgresql://user:password@host:port/database
# SQLite: sqlite:///./database.db
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
# Supports both SQLite and PostgreSQL (if psycopg2 is installed)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10 if "postgresql" in DATABASE_URL else 5,  # Smaller pool for SQLite
    max_overflow=20 if "postgresql" in DATABASE_URL else 10,
    echo=False,  # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Use with FastAPI Depends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def check_connection():
    """
    Check if database connection is working.
    """
    try:
        from sqlalchemy import text

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

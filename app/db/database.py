"""
Database Configuration and Session Management.

This module handles database connection, session management,
and table creation for the Cohere Chat application.

Author: Cohere THA Project
Created: September 2025
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.chat import Base

# Configure logging for database operations
logger = logging.getLogger(__name__)

# Database connection
logger.info(f"Initializing database connection to: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'local database'}")

try:
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database engine and session factory created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise


def get_db():
    """
    Database dependency for FastAPI endpoints.

    Creates a database session for each request and ensures proper cleanup.
    Used as a dependency injection in FastAPI route handlers.

    Yields:
        Session: SQLAlchemy database session

    Usage:
        @app.get("/endpoint")
        async def endpoint(db: Session = Depends(get_db)):
            # Use db session for database operations
    """
    logger.debug("Creating new database session")
    db = SessionLocal()
    try:
        yield db
        logger.debug("Database session completed successfully")
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        db.close()
        logger.debug("Database session closed")


def create_tables():
    """
    Initialize database tables based on SQLAlchemy models.

    Creates all tables defined in the Base metadata if they don't exist.
    Should be called once during application startup.

    Usage:
        Called automatically during FastAPI startup event.
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise

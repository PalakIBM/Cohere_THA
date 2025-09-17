"""
Main FastAPI Application Entry Point.

This module initializes and configures the FastAPI application with
all necessary middleware, routes, and startup/shutdown events.

Author: Cohere THA Project
Created: September 2025
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.database import create_tables
from app.api.v1.chat import router as chat_router
from app.api.v1.debug import router as debug_router
from app.utils.logging import log_application_start, log_application_shutdown


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.log_file, mode='a')
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    log_application_start("main", "3.0.0")
    logger.info("Application startup initiated")
    
    try:
        create_tables()
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise
    
    logger.info("Application startup completed successfully")
    
    yield
    
    # Shutdown
    log_application_shutdown("main")
    logger.info("Application shutdown completed")


# Initialize FastAPI app
app = FastAPI(
    title="Cohere Chat API with Wikipedia Tool and PostgreSQL",
    description=(
        "A comprehensive API that interfaces with Cohere's Chat API, "
        "Wikipedia, and stores data in PostgreSQL. Features include "
        "AI-powered conversations, Wikipedia tool integration, and "
        "persistent chat history storage."
    ),
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(chat_router, prefix="/api/v1")
app.include_router(debug_router, prefix="/api/v1")


@app.get("/")
async def root():
    """
    Root endpoint with basic application information.
    
    Returns:
        Basic information about the API and its features
    """
    logger.info("Root endpoint accessed")
    return {
        "message": "Cohere Chat API with Wikipedia Tool is running",
        "version": "3.0.0",
        "docs": "/docs",
        "features": [
            "Chat with Cohere AI",
            "Wikipedia Tool Integration", 
            "Persistent Chat History",
            "PostgreSQL Storage",
            "RESTful API"
        ],
        "api_prefix": "/api/v1"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting Cohere Chat API server on {settings.host}:{settings.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

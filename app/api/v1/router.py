"""
API Router Configuration.

This module configures the main API router that includes
all endpoint routers for the application.

Author: Cohere THA Project
Created: September 2025
"""

from fastapi import APIRouter
from app.api.v1.chat import router as chat_router
from app.api.v1.debug import router as debug_router

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(chat_router)
api_router.include_router(debug_router)

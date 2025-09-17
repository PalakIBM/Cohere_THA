"""
Debug and Health Check API Endpoints.

This module contains debugging and monitoring endpoints for the application,
including health checks, database status, and Wikipedia testing.

Author: Cohere THA Project
Created: September 2025
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.chat import ChatHistory
from app.schemas.chat import HealthCheckResponse
from app.services.wikipedia import wikipedia_service
from app.services.cohere_client import cohere_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["debug", "health"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connectivity."""
    logger.info("Health check endpoint called")
    try:
        # Test database connection
        total_conversations = db.query(ChatHistory).count()
        db_status = "connected"
        logger.info(f"Health check successful - Database connected, {total_conversations} conversations")
    except Exception as e:
        total_conversations = "unknown"
        db_status = f"error: {str(e)}"
        logger.warning(f"Health check database connectivity issue: {str(e)}")

    health_response = HealthCheckResponse(
        status="healthy",
        service="cohere-chat-api-with-wikipedia-postgresql",
        total_conversations=total_conversations,
        database_status=db_status,
        features={
            "wikipedia_integration": True,
            "chat_history": True,
            "tool_calling": True,
            "postgresql_storage": True,
        },
    )
    
    logger.debug(f"Health check response: {health_response}")
    return health_response


@router.get("/debug/wikipedia")
async def debug_wikipedia_search(query: str = "Albert Einstein"):
    """
    Debug endpoint to test Wikipedia search functionality.

    Args:
        query: Search query for Wikipedia

    Returns:
        Raw Wikipedia search results for debugging
    """
    logger.info(f"Debug Wikipedia search for: {query}")
    try:
        results = wikipedia_service.search_wikipedia(query, limit=3)
        return {
            "query": query,
            "results_found": len(results),
            "results": results,
            "status": "success" if results else "no_results",
        }
    except Exception as e:
        logger.error(f"Debug Wikipedia search error: {str(e)}")
        return {"query": query, "error": str(e), "status": "error"}


@router.get("/debug/database")
async def debug_database(db: Session = Depends(get_db)):
    """Debug endpoint to test database connectivity and show recent chats."""
    logger.info("Database debug endpoint called")
    try:
        # Test basic connectivity
        total_chats = db.query(ChatHistory).count()
        logger.info(f"Database connectivity test successful, total chats: {total_chats}")

        # Get latest 5 chats
        recent_chats = (
            db.query(ChatHistory).order_by(ChatHistory.timestamp.desc()).limit(5).all()
        )

        recent_data = [
            {
                "id": chat.id,
                "query_preview": (
                    chat.query[:50] + "..." if len(chat.query) > 50 else chat.query
                ),
                "timestamp": chat.timestamp.isoformat(),
                "wikipedia_sources_count": (
                    len(chat.wikipedia_sources) if chat.wikipedia_sources else 0
                ),
            }
            for chat in recent_chats
        ]

        return {
            "database_status": "connected",
            "total_conversations": total_chats,
            "recent_chats": recent_data,
            "status": "success",
        }
    except Exception as e:
        logger.error(f"Database debug error: {str(e)}")
        return {"database_status": "error", "error": str(e), "status": "error"}


@router.get("/debug/cohere")
async def debug_cohere():
    """Debug endpoint to test Cohere service connectivity."""
    logger.info("Cohere debug endpoint called")
    try:
        health_status = cohere_service.health_check()
        return {
            "cohere_status": health_status,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Cohere debug error: {str(e)}")
        return {
            "cohere_status": {"status": "error", "message": str(e)},
            "status": "error"
        }

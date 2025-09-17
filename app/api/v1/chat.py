"""
Chat API Endpoints.

This module contains all chat-related API endpoints including
chat conversations, history management, and Wikipedia integration.

Author: Cohere THA Project
Created: September 2025
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.models.chat import ChatHistory
from app.schemas.chat import (
    QueryRequest, 
    QueryResponse, 
    ChatHistoryResponse, 
    ChatHistoryItem
)
from app.services.cohere_client import cohere_service
from app.services.wikipedia import wikipedia_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Enhanced chat endpoint with Wikipedia tool integration and PostgreSQL storage.

    Args:
        request: QueryRequest containing the user's query and optional parameters
        db: Database session

    Returns:
        QueryResponse containing the original query, Cohere's response, and Wikipedia sources
    """
    logger.info(
        f"Chat endpoint called with query: '{request.query[:50]}...', "
        f"max_tokens: {request.max_tokens}, temperature: {request.temperature}, "
        f"use_wikipedia: {request.use_wikipedia}"
    )
    
    try:
        wikipedia_sources = []
        wikipedia_context = None

        # If Wikipedia is enabled, search for relevant information
        if request.use_wikipedia:
            logger.info("Wikipedia integration enabled, searching for context...")
            wiki_results = wikipedia_service.search_wikipedia(request.query, limit=2)

            if wiki_results:
                logger.info(f"Found {len(wiki_results)} Wikipedia sources")
                
                # Collect Wikipedia sources
                wikipedia_sources = [
                    result.get("url", "") for result in wiki_results 
                    if result.get("url")
                ]
                
                # Create context from Wikipedia results
                wikipedia_context = cohere_service.format_wikipedia_context(wiki_results)
                logger.debug(f"Wikipedia context created with {len(wikipedia_context)} characters")
            else:
                logger.info("No Wikipedia results found, using regular chat")
        else:
            logger.info("Wikipedia integration disabled, using regular chat")

        # Generate response using Cohere service
        response_text = cohere_service.generate_response(
            query=request.query,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            wikipedia_context=wikipedia_context
        )

        logger.info("Successfully received response from Cohere API")
        logger.debug(f"Response length: {len(response_text)} characters")

        # Create response object
        timestamp = datetime.utcnow()
        chat_response = QueryResponse(
            response=response_text,
            query=request.query,
            wikipedia_sources=wikipedia_sources,
            timestamp=timestamp,
        )

        # Save to PostgreSQL database
        logger.info("Saving conversation to PostgreSQL database")
        try:
            db_chat = ChatHistory(
                query=request.query,
                response=response_text,
                wikipedia_sources=wikipedia_sources,
                timestamp=timestamp,
                max_tokens=request.max_tokens,
                temperature=str(request.temperature),
                use_wikipedia=str(request.use_wikipedia),
            )
            db.add(db_chat)
            db.commit()
            db.refresh(db_chat)
            logger.info(f"Chat conversation saved to database with ID: {db_chat.id}")
        except Exception as db_error:
            logger.error(f"Failed to save conversation to database: {str(db_error)}")
            db.rollback()
            # Continue without failing the API call

        logger.info("Chat endpoint completed successfully")
        return chat_response

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
):
    """
    Retrieve chat history from PostgreSQL database.

    Args:
        limit: Maximum number of records to return (default: 100)
        offset: Number of records to skip (default: 0)
        db: Database session

    Returns:
        ChatHistoryResponse containing chat conversations from database
    """
    logger.info(f"Chat history requested with limit: {limit}, offset: {offset}")
    try:
        # Get total count
        total_count = db.query(ChatHistory).count()
        logger.info(f"Total conversations in database: {total_count}")

        # Get paginated results, ordered by timestamp (newest first)
        db_chats = (
            db.query(ChatHistory)
            .order_by(ChatHistory.timestamp.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        logger.info(f"Retrieved {len(db_chats)} chat records from database")

        history_items = [
            ChatHistoryItem(
                id=chat.id,
                query=chat.query,
                response=chat.response,
                wikipedia_sources=chat.wikipedia_sources or [],
                timestamp=chat.timestamp,
            )
            for chat in db_chats
        ]

        logger.info(f"Successfully prepared {len(history_items)} chat history items")

        return ChatHistoryResponse(
            history=history_items, total_conversations=total_count
        )

    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving chat history: {str(e)}"
        )


@router.delete("/history")
async def clear_chat_history(db: Session = Depends(get_db)):
    """Clear all chat history from PostgreSQL database."""
    logger.info("Chat history clear operation requested")
    try:
        deleted_count = db.query(ChatHistory).count()
        db.query(ChatHistory).delete()
        db.commit()
        logger.info(f"Cleared {deleted_count} chat records from database")
        return {
            "message": f"Chat history cleared successfully. Deleted {deleted_count} records."
        }
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error clearing chat history: {str(e)}"
        )

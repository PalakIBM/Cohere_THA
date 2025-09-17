"""
Database Models for Cohere Chat Application.

This module defines the SQLAlchemy models for storing chat conversations
and related data in PostgreSQL.

Author: Cohere THA Project
Created: September 2025
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class ChatHistory(Base):
    """
    SQLAlchemy model for storing chat conversation history in PostgreSQL.

    This model represents individual chat conversations including the user's query,
    AI's response, Wikipedia sources used, and metadata about the conversation.

    Attributes:
        id (int): Primary key, auto-incrementing unique identifier
        query (str): User's original chat query or question
        response (str): AI-generated response from Cohere API
        wikipedia_sources (list): JSON array of Wikipedia URLs used in response
        timestamp (datetime): UTC timestamp when conversation occurred
        max_tokens (int): Maximum tokens limit used for the AI response
        temperature (str): Temperature parameter used for AI response generation
        use_wikipedia (str): Whether Wikipedia was used for this response

    Table Name:
        chat_history

    Indexes:
        - Primary key on id column for fast lookups

    Usage:
        Used by FastAPI endpoints to store and retrieve chat history
        with persistent PostgreSQL storage.
    """

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    wikipedia_sources = Column(JSON, default=[])
    timestamp = Column(DateTime, default=datetime.utcnow)
    max_tokens = Column(Integer, default=300)
    temperature = Column(String(10), default="0.7")
    use_wikipedia = Column(String(10), default="true")

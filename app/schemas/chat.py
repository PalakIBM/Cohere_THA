"""
Pydantic Schemas for Request/Response Validation.

This module defines the Pydantic models used for API request
and response validation in the Cohere Chat application.

Author: Cohere THA Project
Created: September 2025
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class QueryRequest(BaseModel):
    """
    Request model for chat API endpoint.

    Attributes:
        query (str): The user's chat message or question
        max_tokens (int): Maximum tokens for AI response (default: 300)
        temperature (float): AI response creativity level 0.0-1.0 (default: 0.7)
        use_wikipedia (bool): Whether to use Wikipedia tool for enhanced
            responses (default: True)
    """

    query: str = Field(..., min_length=1, max_length=2000, description="User's chat query")
    max_tokens: int = Field(300, ge=1, le=2000, description="Maximum tokens for response")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="Response creativity level")
    use_wikipedia: bool = Field(True, description="Enable Wikipedia tool integration")

    @validator("query")
    def validate_query(cls, v):
        """Ensure query is not just whitespace."""
        if not v.strip():
            raise ValueError("Query cannot be empty or just whitespace")
        return v.strip()


class QueryResponse(BaseModel):
    """
    Response model for chat API endpoint.

    Attributes:
        response (str): AI-generated response to the user's query
        query (str): Original user query for reference
        wikipedia_sources (List[str]): URLs of Wikipedia sources used (if any)
        timestamp (datetime): UTC timestamp when response was generated
    """

    response: str = Field(..., description="AI-generated response")
    query: str = Field(..., description="Original user query")
    wikipedia_sources: List[str] = Field(default=[], description="Wikipedia source URLs")
    timestamp: datetime = Field(..., description="Response timestamp")

    class Config:
        schema_extra = {
            "example": {
                "response": "The solar system has 8 planets...",
                "query": "How many planets are in the solar system?",
                "wikipedia_sources": ["https://en.wikipedia.org/wiki/Solar_System"],
                "timestamp": "2025-09-16T22:30:00Z"
            }
        }


class ChatHistoryItem(BaseModel):
    """
    Model for individual chat history item.

    Attributes:
        id (int): Unique identifier for the chat conversation
        query (str): User's original query
        response (str): AI's response
        wikipedia_sources (List[str]): Wikipedia URLs used in response
        timestamp (datetime): When the conversation occurred
    """

    id: int = Field(..., description="Unique conversation ID")
    query: str = Field(..., description="User's original query")
    response: str = Field(..., description="AI's response")
    wikipedia_sources: List[str] = Field(default=[], description="Wikipedia sources used")
    timestamp: datetime = Field(..., description="Conversation timestamp")

    class Config:
        orm_mode = True


class ChatHistoryResponse(BaseModel):
    """
    Response model for chat history endpoint.

    Attributes:
        history (List[ChatHistoryItem]): List of all chat conversations
        total_conversations (int): Total number of conversations in database
    """

    history: List[ChatHistoryItem] = Field(..., description="List of chat conversations")
    total_conversations: int = Field(..., description="Total conversation count")

    class Config:
        schema_extra = {
            "example": {
                "history": [
                    {
                        "id": 1,
                        "query": "What is artificial intelligence?",
                        "response": "Artificial intelligence (AI) is...",
                        "wikipedia_sources": ["https://en.wikipedia.org/wiki/Artificial_intelligence"],
                        "timestamp": "2025-09-16T22:30:00Z"
                    }
                ],
                "total_conversations": 1
            }
        }


class WikipediaSearchResult(BaseModel):
    """
    Model for Wikipedia search results.

    Attributes:
        title (str): Wikipedia article title
        content (str): Article content/summary
        url (str): Wikipedia article URL
    """

    title: str = Field(..., description="Wikipedia article title")
    content: str = Field(..., description="Article content summary")
    url: str = Field(..., description="Wikipedia article URL")


class HealthCheckResponse(BaseModel):
    """
    Response model for health check endpoint.

    Attributes:
        status (str): Overall health status
        service (str): Service name
        total_conversations (int): Total conversations in database
        database_status (str): Database connectivity status
        features (dict): Available features
    """

    status: str = Field(..., description="Overall health status")
    service: str = Field(..., description="Service name")
    total_conversations: int = Field(..., description="Total conversations")
    database_status: str = Field(..., description="Database status")
    features: dict = Field(..., description="Available features")

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "service": "cohere-chat-api-with-wikipedia-postgresql",
                "total_conversations": 42,
                "database_status": "connected",
                "features": {
                    "wikipedia_integration": True,
                    "chat_history": True,
                    "tool_calling": True,
                    "postgresql_storage": True
                }
            }
        }

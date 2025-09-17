"""
Cohere AI Service Integration.

This module handles interactions with the Cohere AI API for chat functionality
and response generation.

Author: Cohere THA Project
Created: September 2025
"""

import logging
import cohere
from typing import Dict, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class CohereService:
    """
    Service class for Cohere AI API interactions.
    
    Handles chat API calls, response generation, and integration
    with Wikipedia tool calling functionality.
    """

    def __init__(self):
        """Initialize Cohere service with API client."""
        logger.info("Initializing Cohere client")
        try:
            self.client = cohere.Client(settings.api_key)
            logger.info("Cohere client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Cohere client: {str(e)}")
            raise

    def generate_response(
        self,
        query: str,
        max_tokens: int = None,
        temperature: float = None,
        wikipedia_context: str = None
    ) -> str:
        """
        Generate AI response using Cohere API.

        Args:
            query: User's chat query
            max_tokens: Maximum tokens for response
            temperature: Response creativity level
            wikipedia_context: Optional Wikipedia context for enhanced responses

        Returns:
            AI-generated response text
        """
        if max_tokens is None:
            max_tokens = settings.default_max_tokens
        if temperature is None:
            temperature = settings.default_temperature

        try:
            # Prepare the message with optional Wikipedia context
            message = self._prepare_message(query, wikipedia_context)
            
            logger.info(f"Calling Cohere API - tokens: {max_tokens}, temp: {temperature}")
            logger.debug(f"Message length: {len(message)} characters")

            response = self.client.chat(
                message=message,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            response_text = response.text
            logger.info(f"Cohere API response received - length: {len(response_text)} characters")
            
            return response_text

        except Exception as e:
            logger.error(f"Cohere API call failed: {str(e)}")
            raise

    def _prepare_message(self, query: str, wikipedia_context: str = None) -> str:
        """
        Prepare the message for Cohere API with optional Wikipedia context.

        Args:
            query: User's original query
            wikipedia_context: Optional Wikipedia information

        Returns:
            Formatted message for Cohere API
        """
        if wikipedia_context:
            logger.debug("Including Wikipedia context in message")
            return f"""Based on the following Wikipedia information, please answer the user's question comprehensively and mention that you're using Wikipedia sources:

Wikipedia Context:
{wikipedia_context}

User Question: {query}

Please provide a detailed answer using the Wikipedia information provided above. Start your response by acknowledging that you found relevant information from Wikipedia."""
        else:
            logger.debug("Using direct query without Wikipedia context")
            return query

    def format_wikipedia_context(self, wikipedia_results: List[Dict[str, str]]) -> str:
        """
        Format Wikipedia search results into context for AI.

        Args:
            wikipedia_results: List of Wikipedia search results

        Returns:
            Formatted context string for AI consumption
        """
        if not wikipedia_results:
            return ""

        logger.debug(f"Formatting {len(wikipedia_results)} Wikipedia results for context")
        
        context_parts = []
        for result in wikipedia_results:
            title = result.get("title", "Unknown")
            content = result.get("content", "")
            
            # Truncate content to avoid token limits
            truncated_content = content[:800] + "..." if len(content) > 800 else content
            context_parts.append(f"Wikipedia Article: {title}\n{truncated_content}")

        formatted_context = "\n\n".join(context_parts)
        logger.debug(f"Wikipedia context formatted - total length: {len(formatted_context)} characters")
        
        return formatted_context

    def health_check(self) -> Dict[str, str]:
        """
        Perform health check on Cohere service.

        Returns:
            Dictionary with health status information
        """
        try:
            # Simple test call to verify API connectivity
            test_response = self.client.chat(
                message="Test",
                max_tokens=10,
                temperature=0.1
            )
            
            if test_response and test_response.text:
                logger.info("Cohere service health check passed")
                return {
                    "status": "healthy",
                    "service": "cohere_api",
                    "message": "API connection successful"
                }
            else:
                logger.warning("Cohere service health check failed - no response")
                return {
                    "status": "unhealthy",
                    "service": "cohere_api",
                    "message": "API returned empty response"
                }
                
        except Exception as e:
            logger.error(f"Cohere service health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "service": "cohere_api",
                "message": f"API error: {str(e)}"
            }


# Global Cohere service instance
cohere_service = CohereService()

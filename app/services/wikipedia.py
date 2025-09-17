"""
Wikipedia Integration Service.

This module handles Wikipedia API interactions for the Cohere Chat application,
providing search functionality and content extraction.

Author: Cohere THA Project
Created: September 2025
"""

import logging
import requests
from typing import List, Dict
from app.core.config import settings

logger = logging.getLogger(__name__)


class WikipediaService:
    """
    Service class for Wikipedia API interactions.
    
    Provides methods to search Wikipedia articles and extract content
    for use in AI-powered chat responses.
    """

    def __init__(self):
        """Initialize Wikipedia service with configuration."""
        self.base_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        self.search_url = "https://en.wikipedia.org/w/api.php"
        self.headers = {
            "User-Agent": "CohereChat/3.0 (https://github.com/PalakIBM/Cohere_THA) Python/Requests"
        }
        self.timeout = settings.wikipedia_timeout
        self.max_results = settings.wikipedia_max_results

    def search_wikipedia(self, query: str, limit: int = None) -> List[Dict[str, str]]:
        """
        Search Wikipedia using the MediaWiki API.

        Args:
            query: Search query string
            limit: Maximum number of results to return (defaults to settings)

        Returns:
            List of dictionaries containing title, content, and URL for each result
        """
        if limit is None:
            limit = self.max_results

        logger.info(f"Starting Wikipedia search for query: '{query}' with limit: {limit}")
        
        try:
            return self._perform_search(query, limit)
        except requests.RequestException as e:
            logger.error(f"Wikipedia API request failed: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Wikipedia search: {str(e)}")
            return []

    def _perform_search(self, query: str, limit: int) -> List[Dict[str, str]]:
        """
        Perform the actual Wikipedia search.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of search results
        """
        # Search for relevant pages
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "srprop": "snippet",
        }

        search_response = requests.get(
            self.search_url, 
            params=search_params, 
            headers=self.headers, 
            timeout=self.timeout
        )
        search_response.raise_for_status()
        logger.debug(f"Wikipedia search API response status: {search_response.status_code}")

        search_data = search_response.json()
        
        if not ("query" in search_data and "search" in search_data["query"]):
            logger.warning(f"No Wikipedia search results found for query: {query}")
            return []

        search_results = search_data["query"]["search"]
        logger.info(f"Found {len(search_results)} Wikipedia search results")

        return self._extract_article_content(search_results)

    def _extract_article_content(self, search_results: List[Dict]) -> List[Dict[str, str]]:
        """
        Extract detailed content from Wikipedia articles.

        Args:
            search_results: Raw search results from Wikipedia API

        Returns:
            List of processed articles with content
        """
        results = []
        
        for item in search_results:
            title = item["title"]
            logger.debug(f"Processing Wikipedia page: {title}")
            
            snippet = self._clean_snippet(item.get("snippet", ""))
            
            try:
                article_content = self._get_article_summary(title)
                if article_content:
                    results.append(article_content)
                    logger.debug(f"Successfully retrieved summary for: {title}")
                else:
                    results.append(self._create_fallback_result(title, snippet))
                    
            except Exception as e:
                logger.warning(f"Failed to get summary for {title}: {str(e)}")
                results.append(self._create_fallback_result(title, snippet))

        logger.info(f"Successfully processed {len(results)} Wikipedia articles")
        return results

    def _clean_snippet(self, snippet: str) -> str:
        """Clean HTML tags from snippet."""
        return (
            snippet.replace('<span class="searchmatch">', "")
            .replace("</span>", "")
        )

    def _get_article_summary(self, title: str) -> Dict[str, str]:
        """
        Get detailed summary for a Wikipedia article.

        Args:
            title: Wikipedia article title

        Returns:
            Dictionary with article details or None if failed
        """
        summary_response = requests.get(
            f"{self.base_url}{title.replace(' ', '_')}", 
            headers=self.headers, 
            timeout=self.timeout
        )
        
        if summary_response.status_code != 200:
            return None

        summary_data = summary_response.json()
        extract = summary_data.get("extract", "")
        
        return {
            "title": title,
            "content": extract,
            "url": summary_data.get("content_urls", {})
                  .get("desktop", {})
                  .get("page", ""),
        }

    def _create_fallback_result(self, title: str, snippet: str) -> Dict[str, str]:
        """Create fallback result when summary extraction fails."""
        return {
            "title": title,
            "content": snippet,
            "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
        }

    def get_tool_definition(self) -> Dict:
        """
        Get the Wikipedia tool definition for Cohere API.

        Returns:
            Tool definition dictionary for Cohere integration
        """
        return {
            "name": "search_wikipedia",
            "description": (
                "Search Wikipedia for information on a given topic. Use this when you "
                "need factual information about people, places, events, concepts, or "
                "any topic that might be found on Wikipedia."
            ),
            "parameter_definitions": {
                "query": {
                    "description": "The search query to find relevant Wikipedia articles",
                    "type": "str",
                    "required": True,
                },
                "limit": {
                    "description": f"Maximum number of Wikipedia articles to retrieve (default: {self.max_results})",
                    "type": "int",
                    "required": False,
                },
            },
        }


# Global Wikipedia service instance
wikipedia_service = WikipediaService()

"""
Application Configuration and Settings.

This module contains all configuration settings for the Cohere Chat application,
including environment variables, database settings, and application constants.

Author: Cohere THA Project
Created: September 2025
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator, Field
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        api_key: Cohere API key
        database_url: PostgreSQL connection string
        host: Server host address
        port: Server port
        log_level: Logging level
        debug: Debug mode flag
        cors_origins: Allowed CORS origins
    """
    
    # API Configuration
    api_key: str = Field(alias="API")
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/cohere_chat",
        alias="DATABASE_URL"
    )
    
    # Server Configuration
    host: str = Field(default="127.0.0.1", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    debug: bool = Field(default=False, alias="DEBUG")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = "logs/cohere_chat.log"
    
    # CORS Configuration
    cors_origins: list = ["http://localhost:3000", "http://localhost:8501"]
    
    # Wikipedia API Configuration
    wikipedia_timeout: int = 10
    wikipedia_max_results: int = 3
    
    # Cohere API Configuration
    cohere_timeout: int = 30
    default_max_tokens: int = 300
    default_temperature: float = 0.7
    
    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v):
        """Validate that API key is provided."""
        if not v:
            raise ValueError("Cohere API key is required")
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Returns:
        Settings instance with environment variables loaded
    """
    return Settings()


# Global settings instance
settings = get_settings()

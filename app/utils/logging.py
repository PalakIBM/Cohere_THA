"""
Centralized Logging Configuration for Cohere Chat Application.

This module provides a standardized logging configuration for all components
of the Cohere Chat application including FastAPI backend, Streamlit frontend,
and database operations.

Features:
    - Consistent log format across all components
    - File and console logging
    - Configurable log levels
    - Automatic log rotation
    - Structured logging for better debugging

Author: Cohere THA Project
Created: September 2025
"""

import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(
    name: str,
    log_file: str = None,
    level: str = "INFO",
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5
):
    """
    Set up standardized logging configuration.
    
    Args:
        name: Logger name (usually __name__)
        log_file: Optional log file path. If None, uses {name}.log
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file is None:
        log_file = f"{name.replace('.', '_')}.log"
    
    # Ensure logs directory exists
    log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else "logs"
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # Full path for log file
    if not os.path.dirname(log_file):
        log_file = os.path.join(log_dir, log_file)
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(getattr(logging, level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Log the logger setup
    logger.info(f"Logging configured for {name} - Level: {level}, File: {log_file}")
    
    return logger


def get_app_logger(component: str = "main"):
    """
    Get a pre-configured logger for application components.
    
    Args:
        component: Component name (main, database, wikipedia, streamlit, etc.)
        
    Returns:
        Configured logger instance
    """
    log_level = os.getenv("LOG_LEVEL", "INFO")
    return setup_logging(
        name=f"cohere_chat.{component}",
        log_file=f"logs/cohere_chat_{component}.log",
        level=log_level
    )


# Pre-configured loggers for common components
def get_main_logger():
    """Get logger for main application."""
    return get_app_logger("main")


def get_database_logger():
    """Get logger for database operations."""
    return get_app_logger("database")


def get_wikipedia_logger():
    """Get logger for Wikipedia integration."""
    return get_app_logger("wikipedia")


def get_streamlit_logger():
    """Get logger for Streamlit applications."""
    return get_app_logger("streamlit")


def get_api_logger():
    """Get logger for API operations."""
    return get_app_logger("api")


# Application startup logging
def log_application_start(component: str, version: str = "3.0.0"):
    """
    Log application startup information.
    
    Args:
        component: Component name
        version: Application version
    """
    logger = get_app_logger(component)
    logger.info("=" * 60)
    logger.info(f"STARTING {component.upper()} - Version {version}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Log Level: {os.getenv('LOG_LEVEL', 'INFO')}")
    logger.info("=" * 60)


# Cleanup function
def log_application_shutdown(component: str):
    """
    Log application shutdown information.
    
    Args:
        component: Component name
    """
    logger = get_app_logger(component)
    logger.info("=" * 60)
    logger.info(f"SHUTTING DOWN {component.upper()}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 60)

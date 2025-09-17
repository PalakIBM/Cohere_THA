#!/usr/bin/env python3
"""
Application Startup Script.

This script starts the Cohere Chat API server with proper configuration.
It can be used for development, testing, or production deployment.

Usage:
    python run.py [--dev] [--host HOST] [--port PORT]

Author: Cohere THA Project
Created: September 2025
"""

import argparse
import uvicorn
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.config import settings


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Start Cohere Chat API server")
    parser.add_argument(
        "--dev", 
        action="store_true", 
        help="Run in development mode with auto-reload"
    )
    parser.add_argument(
        "--host", 
        default=settings.host, 
        help=f"Host to bind to (default: {settings.host})"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=settings.port, 
        help=f"Port to bind to (default: {settings.port})"
    )
    parser.add_argument(
        "--log-level", 
        default=settings.log_level.lower(), 
        choices=["debug", "info", "warning", "error", "critical"],
        help=f"Log level (default: {settings.log_level.lower()})"
    )
    
    args = parser.parse_args()
    
    # Override settings with command line arguments
    host = args.host
    port = args.port
    log_level = args.log_level
    reload = args.dev
    
    print(f"🚀 Starting Cohere Chat API server...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"📝 Log Level: {log_level.upper()}")
    print(f"🔄 Auto-reload: {'ON' if reload else 'OFF'}")
    print(f"📚 Documentation: http://{host}:{port}/docs")
    print("-" * 50)
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True
    )


if __name__ == "__main__":
    main()

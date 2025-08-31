#!/usr/bin/env python3
"""
SmartHistory API Server - Main Entry Point

Run the FastAPI server for the SmartHistory backend API.
Provides REST endpoints for frontend consumption of activity processing capabilities.

Usage:
    python run_api.py [--host HOST] [--port PORT] [--reload]
"""

import os
import sys
import argparse
import uvicorn
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.api import get_api_app


def main():
    """Main entry point for the API server."""
    parser = argparse.ArgumentParser(
        description='SmartHistory API Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_api.py                           # Start server on localhost:8000
  python run_api.py --host 0.0.0.0           # Allow external connections
  python run_api.py --port 8080              # Use custom port
  python run_api.py --reload                 # Development mode with auto-reload
        """
    )
    
    parser.add_argument('--host', 
                       default='127.0.0.1',
                       help='Host to bind the server (default: 127.0.0.1)')
    
    parser.add_argument('--port', 
                       type=int,
                       default=8000,
                       help='Port to bind the server (default: 8000)')
    
    parser.add_argument('--reload',
                       action='store_true',
                       help='Enable auto-reload for development')
    
    parser.add_argument('--log-level',
                       default='info',
                       choices=['critical', 'error', 'warning', 'info', 'debug', 'trace'],
                       help='Log level (default: info)')
    
    args = parser.parse_args()
    
    print("🚀 SmartHistory API Server")
    print("=" * 50)
    print(f"Starting server on http://{args.host}:{args.port}")
    print(f"API Documentation: http://{args.host}:{args.port}/docs")
    print(f"Redoc Documentation: http://{args.host}:{args.port}/redoc")
    
    if args.reload:
        print("Development mode: Auto-reload enabled")
    
    print("=" * 50)
    
    # Check database availability
    try:
        from src.backend.database import get_db_manager
        db = get_db_manager()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"⚠️  Database warning: {e}")
        print("API will start but some endpoints may fail")
    
    # Start the server
    try:
        uvicorn.run(
            "src.backend.api:get_api_app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            factory=True,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server shutdown requested")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
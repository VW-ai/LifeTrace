#!/usr/bin/env python3
"""
SmartHistory API Startup Script
Industry-ready startup with environment detection and configuration
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from api.server import run_server

if __name__ == "__main__":
    # Set environment from command line or default to development
    if len(sys.argv) > 1:
        os.environ["ENVIRONMENT"] = sys.argv[1]
    
    env = os.getenv("ENVIRONMENT", "development")
    print(f"🚀 Starting SmartHistory API in {env.upper()} mode...")
    
    # Load environment-specific .env file if it exists
    env_file = Path(f".env.{env}")
    if env_file.exists():
        print(f"📁 Loading configuration from {env_file}")
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    run_server()
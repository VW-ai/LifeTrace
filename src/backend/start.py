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

    from dotenv import load_dotenv

    # Load root .env file first (for API keys)
    root_env_file = Path(__file__).parent.parent.parent / ".env"
    if root_env_file.exists():
        print(f"📁 Loading API keys from {root_env_file}")
        load_dotenv(root_env_file)

    # Load environment-specific .env file if it exists (can override root .env)
    env_file = Path(f".env.{env}")
    if env_file.exists():
        print(f"📁 Loading configuration from {env_file}")
        load_dotenv(env_file, override=True)

    run_server()
#!/usr/bin/env python3
"""Debug .env loading"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

def debug_env_loading():
    print("Debugging .env file loading...")
    
    # Check current working directory
    print(f"Current working directory: {os.getcwd()}")
    
    # Check where the script thinks the project root is
    script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(script_path)
    env_path = os.path.join(project_root, '.env')
    
    print(f"Script path: {script_path}")
    print(f"Project root: {project_root}")
    print(f"Expected .env path: {env_path}")
    print(f".env file exists: {os.path.exists(env_path)}")
    
    # Try loading the .env file
    try:
        from dotenv import load_dotenv
        result = load_dotenv(env_path)
        print(f"load_dotenv result: {result}")
        
        # Check if the key is now available
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            print(f"✅ API key loaded: sk-...{api_key[-10:]}")
        else:
            print("❌ API key still not found after loading .env")
            
        # Check all environment variables with OPENAI
        openai_vars = {k: v for k, v in os.environ.items() if 'OPENAI' in k.upper()}
        print(f"OpenAI-related env vars: {list(openai_vars.keys())}")
        
    except Exception as e:
        print(f"Error loading .env: {e}")

if __name__ == "__main__":
    debug_env_loading()
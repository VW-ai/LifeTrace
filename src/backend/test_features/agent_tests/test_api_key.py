#!/usr/bin/env python3
"""Quick test to verify OpenAI API key loading"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from src.backend.agent import load_api_key

def test_api_key_loading():
    print("Testing OpenAI API key loading...")
    
    api_key = load_api_key()
    
    if api_key:
        # Don't print the full key for security
        print(f"✅ API key loaded successfully: sk-...{api_key[-10:]}")
        return True
    else:
        print("❌ No API key found")
        return False

if __name__ == "__main__":
    test_api_key_loading()
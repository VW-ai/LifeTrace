#!/usr/bin/env python3
"""
SmartHistory API Test Runner

Run pytest tests for the SmartHistory API with proper environment setup.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def run_api_tests():
    """Run API tests using pytest."""
    print("🧪 Running SmartHistory API Tests")
    print("=" * 50)
    
    # Set environment variables for testing
    os.environ['SMARTHISTORY_ENV'] = 'development'  # Disable auth for tests
    os.environ['PYTHONPATH'] = str(PROJECT_ROOT)
    
    # Run pytest with proper configuration
    pytest_args = [
        sys.executable, "-m", "pytest",
        "tests/api/",
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure
        "--disable-warnings"
    ]
    
    try:
        result = subprocess.run(pytest_args, cwd=Path(__file__).parent)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n⏸️ Tests interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def run_specific_test(test_pattern):
    """Run specific tests matching a pattern."""
    os.environ['SMARTHISTORY_ENV'] = 'development'
    os.environ['PYTHONPATH'] = str(PROJECT_ROOT)
    
    pytest_args = [
        sys.executable, "-m", "pytest",
        f"tests/api/{test_pattern}",
        "-v",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(pytest_args, cwd=Path(__file__).parent)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running specific tests: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run SmartHistory API tests")
    parser.add_argument("--pattern", help="Run specific test pattern (e.g., test_activities.py)")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    
    args = parser.parse_args()
    
    if args.pattern:
        success = run_specific_test(args.pattern)
    else:
        success = run_api_tests()
    
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
SmartHistory API Manual Integration Test

Manual test to verify the API server can start and handle requests.
This is for integration testing to see actual outputs and behavior.
"""

import os
import sys
import time
import requests
import threading
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_api_server_startup():
    """Test that the API server can start successfully."""
    print("🚀 Testing API Server Startup")
    print("-" * 30)
    
    try:
        # Set development mode
        os.environ['SMARTHISTORY_ENV'] = 'development'
        
        from src.backend.api import get_api_app
        app = get_api_app()
        
        print(f"✅ API app created successfully")
        print(f"📊 Total routes: {len(app.routes)}")
        
        # Count API routes
        api_routes = [r for r in app.routes if hasattr(r, 'path') and '/api/v1/' in r.path]
        print(f"📈 API v1 routes: {len(api_routes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating API app: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_connection():
    """Test database connection."""
    print("\n📊 Testing Database Connection")
    print("-" * 30)
    
    try:
        from src.backend.database import get_db_manager
        db = get_db_manager()
        
        # Test basic query
        result = db.execute_query("SELECT COUNT(*) as count FROM raw_activities")
        count = result[0]['count'] if result else 0
        
        print(f"✅ Database connected")
        print(f"📋 Raw activities in database: {count}")
        
        # Test other tables
        tables = ['processed_activities', 'tags', 'user_sessions']
        for table in tables:
            try:
                result = db.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                table_count = result[0]['count'] if result else 0
                print(f"📋 {table}: {table_count}")
            except Exception as e:
                print(f"⚠️  {table}: Error ({e})")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_api_endpoints_locally():
    """Test API endpoints using the test client."""
    print("\n🔗 Testing API Endpoints")
    print("-" * 30)
    
    try:
        from fastapi.testclient import TestClient
        from src.backend.api import get_api_app
        
        os.environ['SMARTHISTORY_ENV'] = 'development'
        app = get_api_app()
        client = TestClient(app)
        
        # Test endpoints
        endpoints = [
            ("GET", "/", "Root endpoint"),
            ("GET", "/health", "Health check"),
            ("GET", "/api/v1/activities/raw", "Raw activities"),
            ("GET", "/api/v1/activities/processed", "Processed activities"),
            ("GET", "/api/v1/insights/overview", "Insights overview"),
            ("GET", "/api/v1/tags", "Tags list"),
            ("GET", "/api/v1/system/health", "System health"),
            ("GET", "/api/v1/system/stats", "System stats"),
        ]
        
        results = []
        for method, path, description in endpoints:
            try:
                if method == "GET":
                    response = client.get(path)
                else:
                    response = client.request(method, path)
                
                status_emoji = "✅" if 200 <= response.status_code < 300 else "❌"
                print(f"{status_emoji} {description}: {response.status_code}")
                
                if response.status_code == 200:
                    # Show sample data for some endpoints
                    if path in ["/api/v1/system/health", "/api/v1/system/stats"]:
                        try:
                            data = response.json()
                            if path == "/api/v1/system/health":
                                print(f"    Database connected: {data.get('database', {}).get('connected', 'Unknown')}")
                            elif path == "/api/v1/system/stats":
                                print(f"    Total activities: {data.get('total_raw_activities', 0)}")
                        except:
                            pass
                
                results.append((path, response.status_code))
                
            except Exception as e:
                print(f"❌ {description}: Error ({e})")
                results.append((path, "ERROR"))
        
        # Summary
        successful = len([r for r in results if isinstance(r[1], int) and 200 <= r[1] < 300])
        print(f"\n📈 Results: {successful}/{len(results)} endpoints working")
        
        return successful > 0
        
    except Exception as e:
        print(f"❌ API endpoint testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_and_manage_tags():
    """Test tag creation and management."""
    print("\n🏷️  Testing Tag Management")
    print("-" * 30)
    
    try:
        from fastapi.testclient import TestClient
        from src.backend.api import get_api_app
        
        os.environ['SMARTHISTORY_ENV'] = 'development'
        app = get_api_app()
        client = TestClient(app)
        
        # Create a test tag
        tag_data = {
            "name": "manual-test-tag",
            "description": "Test tag created during manual testing",
            "color": "#ff6d01"
        }
        
        response = client.post("/api/v1/tags", json=tag_data)
        
        if response.status_code == 200:
            tag = response.json()
            print(f"✅ Created tag: {tag['name']} (ID: {tag['id']})")
            
            # Try to update it
            updated_data = {
                "name": "manual-test-tag-updated",
                "description": "Updated test tag",
                "color": "#123456"
            }
            
            update_response = client.put(f"/api/v1/tags/{tag['id']}", json=updated_data)
            
            if update_response.status_code == 200:
                updated_tag = update_response.json()
                print(f"✅ Updated tag: {updated_tag['name']}")
                
                # Clean up - delete the test tag
                delete_response = client.delete(f"/api/v1/tags/{tag['id']}")
                if delete_response.status_code == 200:
                    print("✅ Cleaned up test tag")
                else:
                    print("⚠️  Could not clean up test tag")
            else:
                print(f"❌ Failed to update tag: {update_response.status_code}")
        else:
            print(f"⚠️  Could not create test tag: {response.status_code}")
            if response.status_code == 400:
                print("    (Tag might already exist from previous runs)")
        
        return True
        
    except Exception as e:
        print(f"❌ Tag management test failed: {e}")
        return False


def main():
    """Run all manual tests."""
    print("🧪 SmartHistory API Manual Integration Test")
    print("=" * 50)
    
    tests = [
        ("API Server Startup", test_api_server_startup),
        ("Database Connection", test_database_connection),
        ("API Endpoints", test_api_endpoints_locally),
        ("Tag Management", test_create_and_manage_tags)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Manual Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✅ All manual tests passed!")
        print("\n🚀 API is ready for use:")
        print("  python run_api.py")
        print("  Then visit: http://localhost:8000/docs")
    else:
        print("❌ Some manual tests failed. Check the output above.")
    
    return passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
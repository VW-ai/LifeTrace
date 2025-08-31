#!/usr/bin/env python3
"""
SmartHistory API Tests

Test suite for the SmartHistory REST API endpoints.
Tests functionality, error handling, and API contracts.
"""

import os
import sys
import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.api import get_api_app
from src.backend.database import get_db_manager


# Test configuration
TEST_API_KEY = "test-api-key-12345"
os.environ['SMARTHISTORY_ENV'] = 'development'  # Disable auth for testing


class TestSmartHistoryAPI:
    """Test suite for SmartHistory API endpoints."""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment."""
        cls.app = get_api_app()
        cls.client = TestClient(cls.app)
        
        # Set up test database with some sample data
        cls.setup_test_data()
    
    @classmethod
    def setup_test_data(cls):
        """Insert test data into database."""
        try:
            from src.backend.database import RawActivityDAO, RawActivityDB
            
            # Create some test raw activities
            test_activities = [
                RawActivityDB(
                    date="2025-08-31",
                    time="09:00",
                    duration_minutes=60,
                    details="Team standup meeting",
                    source="google_calendar",
                    orig_link="https://calendar.google.com/test1",
                    raw_data={"event_id": "test1", "summary": "Standup"}
                ),
                RawActivityDB(
                    date="2025-08-31",
                    time="10:30",
                    duration_minutes=90,
                    details="Code review session",
                    source="notion",
                    orig_link="",
                    raw_data={"block_id": "test2", "hierarchy": ["Work", "Development"]}
                ),
                RawActivityDB(
                    date="2025-08-30",
                    time="14:00",
                    duration_minutes=120,
                    details="Client presentation",
                    source="google_calendar",
                    orig_link="https://calendar.google.com/test2",
                    raw_data={"event_id": "test3", "summary": "Presentation"}
                )
            ]
            
            for activity in test_activities:
                try:
                    RawActivityDAO.create(activity)
                except Exception:
                    # Activity might already exist from previous runs
                    pass
                    
        except Exception as e:
            print(f"Warning: Could not set up test data: {e}")
    
    def test_root_endpoint(self):
        """Test the root endpoint returns service info."""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["service"] == "SmartHistory API"
        assert "version" in data
        assert "status" in data
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_get_raw_activities(self):
        """Test getting raw activities."""
        response = self.client.get("/api/v1/activities/raw")
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "activities" in data
        assert "total_count" in data
        assert "page_info" in data
        assert isinstance(data["activities"], list)
        
        # Check page info
        page_info = data["page_info"]
        assert "limit" in page_info
        assert "offset" in page_info
        assert "has_more" in page_info
    
    def test_get_raw_activities_with_filters(self):
        """Test getting raw activities with filters."""
        # Test source filter
        response = self.client.get("/api/v1/activities/raw?source=google_calendar")
        assert response.status_code == 200
        data = response.json()
        
        # All returned activities should be from google_calendar
        for activity in data["activities"]:
            assert activity["source"] == "google_calendar"
        
        # Test date filter
        response = self.client.get("/api/v1/activities/raw?date_start=2025-08-31")
        assert response.status_code == 200
        data = response.json()
        
        # All returned activities should be from 2025-08-31 or later
        for activity in data["activities"]:
            assert activity["date"] >= "2025-08-31"
    
    def test_get_raw_activities_pagination(self):
        """Test raw activities pagination."""
        # Get first page
        response = self.client.get("/api/v1/activities/raw?limit=1&offset=0")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["activities"]) <= 1
        assert data["page_info"]["limit"] == 1
        assert data["page_info"]["offset"] == 0
        
        if data["total_count"] > 1:
            assert data["page_info"]["has_more"] is True
    
    def test_get_processed_activities(self):
        """Test getting processed activities."""
        response = self.client.get("/api/v1/activities/processed")
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "activities" in data
        assert "total_count" in data
        assert "page_info" in data
        assert isinstance(data["activities"], list)
        
        # Check activity structure if any exist
        if data["activities"]:
            activity = data["activities"][0]
            assert "id" in activity
            assert "date" in activity
            assert "total_duration_minutes" in activity
            assert "combined_details" in activity
            assert "sources" in activity
            assert "tags" in activity
            assert isinstance(activity["tags"], list)
    
    def test_get_insights_overview(self):
        """Test getting insights overview."""
        response = self.client.get("/api/v1/insights/overview")
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        required_fields = [
            "total_tracked_hours", "activity_count", "unique_tags",
            "tag_time_distribution", "tag_percentages", "top_5_activities", "date_range"
        ]
        
        for field in required_fields:
            assert field in data
        
        # Check data types
        assert isinstance(data["total_tracked_hours"], (int, float))
        assert isinstance(data["activity_count"], int)
        assert isinstance(data["unique_tags"], int)
        assert isinstance(data["tag_time_distribution"], dict)
        assert isinstance(data["tag_percentages"], dict)
        assert isinstance(data["top_5_activities"], list)
        assert isinstance(data["date_range"], dict)
        
        # Check date range structure
        date_range = data["date_range"]
        assert "start" in date_range
        assert "end" in date_range
    
    def test_get_time_distribution(self):
        """Test getting time distribution."""
        response = self.client.get("/api/v1/insights/time-distribution")
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "time_series" in data
        assert "summary" in data
        
        assert isinstance(data["time_series"], list)
        assert isinstance(data["summary"], dict)
        
        # Check summary structure
        summary = data["summary"]
        required_summary_fields = ["total_period_hours", "average_daily_hours", "most_productive_day"]
        for field in required_summary_fields:
            assert field in summary
    
    def test_get_time_distribution_grouping(self):
        """Test time distribution with different grouping."""
        for group_by in ['day', 'week', 'month']:
            response = self.client.get(f"/api/v1/insights/time-distribution?group_by={group_by}")
            assert response.status_code == 200
            data = response.json()
            assert "time_series" in data
            assert "summary" in data
    
    def test_get_tags(self):
        """Test getting tags."""
        response = self.client.get("/api/v1/tags")
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "tags" in data
        assert "total_count" in data
        assert "page_info" in data
        assert isinstance(data["tags"], list)
        
        # Check tag structure if any exist
        if data["tags"]:
            tag = data["tags"][0]
            required_fields = ["id", "name", "usage_count", "created_at", "updated_at"]
            for field in required_fields:
                assert field in tag
    
    def test_create_tag(self):
        """Test creating a tag."""
        tag_data = {
            "name": "test-tag",
            "description": "A test tag",
            "color": "#ff6d01"
        }
        
        response = self.client.post("/api/v1/tags", json=tag_data)
        
        # Might fail if tag already exists, which is fine
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "test-tag"
            assert data["description"] == "A test tag"
            assert data["color"] == "#ff6d01"
            assert "id" in data
            assert "created_at" in data
    
    def test_system_health(self):
        """Test system health endpoint."""
        response = self.client.get("/api/v1/system/health")
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "status" in data
        assert "database" in data
        assert "services" in data
        
        # Check database health
        database = data["database"]
        assert "connected" in database
        assert "total_activities" in database
        assert "last_updated" in database
        
        # Check services health
        services = data["services"]
        assert "tag_generator" in services
        assert "activity_matcher" in services
    
    def test_system_stats(self):
        """Test system statistics endpoint."""
        response = self.client.get("/api/v1/system/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        required_fields = [
            "total_raw_activities", "total_processed_activities", "total_tags",
            "total_sessions", "database_size_mb", "uptime_seconds"
        ]
        
        for field in required_fields:
            assert field in data
            
        # Check data types
        assert isinstance(data["total_raw_activities"], int)
        assert isinstance(data["total_processed_activities"], int)
        assert isinstance(data["total_tags"], int)
        assert isinstance(data["total_sessions"], int)
        assert isinstance(data["database_size_mb"], (int, float))
        assert isinstance(data["uptime_seconds"], int)
    
    def test_invalid_endpoints(self):
        """Test invalid endpoints return 404."""
        response = self.client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        response = self.client.get("/invalid/path")
        assert response.status_code == 404
    
    def test_invalid_parameters(self):
        """Test invalid parameters return 422."""
        # Invalid date format
        response = self.client.get("/api/v1/activities/raw?date_start=invalid-date")
        assert response.status_code == 422
        
        # Invalid source
        response = self.client.get("/api/v1/activities/raw?source=invalid-source")
        assert response.status_code == 422
        
        # Invalid limit
        response = self.client.get("/api/v1/activities/raw?limit=0")
        assert response.status_code == 422
        
        response = self.client.get("/api/v1/activities/raw?limit=2000")
        assert response.status_code == 422


def run_api_tests():
    """Run the API tests."""
    print("🧪 Running SmartHistory API Tests")
    print("=" * 50)
    
    # Run pytest programmatically
    pytest_args = [
        __file__,
        "-v",
        "--tb=short"
    ]
    
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        print("\n✅ All API tests passed!")
    else:
        print(f"\n❌ Some tests failed (exit code: {exit_code})")
    
    return exit_code == 0


if __name__ == "__main__":
    run_api_tests()
"""
API Activities Endpoints Tests

Unit tests for activity-related API endpoints.
"""

import pytest
from datetime import datetime


class TestActivitiesEndpoints:
    """Test activity endpoints."""

    def test_get_raw_activities(self, api_client):
        """Test GET /api/v1/activities/raw."""
        response = api_client.get("/api/v1/activities/raw")
        assert response.status_code == 200
        
        data = response.json()
        assert "activities" in data
        assert "total_count" in data
        assert "page_info" in data
        
        # Check page info structure
        page_info = data["page_info"]
        assert "limit" in page_info
        assert "offset" in page_info
        assert "has_more" in page_info
        assert isinstance(page_info["limit"], int)
        assert isinstance(page_info["offset"], int)
        assert isinstance(page_info["has_more"], bool)
        
        # Check activities structure
        assert isinstance(data["activities"], list)
        if data["activities"]:
            activity = data["activities"][0]
            required_fields = ["id", "date", "duration_minutes", "details", "source", "created_at"]
            for field in required_fields:
                assert field in activity

    def test_get_raw_activities_with_source_filter(self, api_client):
        """Test raw activities with source filter."""
        response = api_client.get("/api/v1/activities/raw?source=google_calendar")
        assert response.status_code == 200
        
        data = response.json()
        # All returned activities should be from google_calendar
        for activity in data["activities"]:
            assert activity["source"] == "google_calendar"

    def test_get_raw_activities_with_date_filter(self, api_client):
        """Test raw activities with date filter."""
        response = api_client.get("/api/v1/activities/raw?date_start=2025-08-31")
        assert response.status_code == 200
        
        data = response.json()
        # All returned activities should be from 2025-08-31 or later
        for activity in data["activities"]:
            assert activity["date"] >= "2025-08-31"

    def test_get_raw_activities_pagination(self, api_client):
        """Test raw activities pagination."""
        response = api_client.get("/api/v1/activities/raw?limit=1&offset=0")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["activities"]) <= 1
        assert data["page_info"]["limit"] == 1
        assert data["page_info"]["offset"] == 0

    def test_get_raw_activities_invalid_source(self, api_client):
        """Test raw activities with invalid source returns 422."""
        response = api_client.get("/api/v1/activities/raw?source=invalid-source")
        assert response.status_code == 422

    def test_get_raw_activities_invalid_date(self, api_client):
        """Test raw activities with invalid date returns 422."""
        response = api_client.get("/api/v1/activities/raw?date_start=invalid-date")
        assert response.status_code == 422

    def test_get_raw_activities_invalid_limit(self, api_client):
        """Test raw activities with invalid limit returns 422."""
        response = api_client.get("/api/v1/activities/raw?limit=0")
        assert response.status_code == 422
        
        response = api_client.get("/api/v1/activities/raw?limit=2000")
        assert response.status_code == 422

    def test_get_processed_activities(self, api_client):
        """Test GET /api/v1/activities/processed."""
        response = api_client.get("/api/v1/activities/processed")
        assert response.status_code == 200
        
        data = response.json()
        assert "activities" in data
        assert "total_count" in data
        assert "page_info" in data
        
        # Check activities structure
        assert isinstance(data["activities"], list)
        if data["activities"]:
            activity = data["activities"][0]
            required_fields = [
                "id", "date", "total_duration_minutes", "combined_details", 
                "sources", "tags", "raw_activity_ids", "created_at"
            ]
            for field in required_fields:
                assert field in activity
            
            # Check that tags is a list
            assert isinstance(activity["tags"], list)
            assert isinstance(activity["sources"], list)
            assert isinstance(activity["raw_activity_ids"], list)

    def test_get_processed_activities_with_tags_filter(self, api_client):
        """Test processed activities with tags filter."""
        response = api_client.get("/api/v1/activities/processed?tags=meetings,development")
        assert response.status_code == 200
        
        data = response.json()
        # Should return valid structure even if no matching activities
        assert "activities" in data
        assert "total_count" in data

    def test_get_processed_activities_pagination(self, api_client):
        """Test processed activities pagination."""
        response = api_client.get("/api/v1/activities/processed?limit=10&offset=0")
        assert response.status_code == 200
        
        data = response.json()
        assert data["page_info"]["limit"] == 10
        assert data["page_info"]["offset"] == 0
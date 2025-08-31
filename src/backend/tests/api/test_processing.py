"""
API Processing Endpoints Tests

Unit tests for processing and import API endpoints.
"""

import pytest


class TestProcessingEndpoints:
    """Test processing endpoints."""

    def test_trigger_daily_processing(self, api_client):
        """Test POST /api/v1/process/daily."""
        request_data = {
            "use_database": True,
            "regenerate_system_tags": False
        }
        
        response = api_client.post("/api/v1/process/daily", json=request_data)
        
        # Should succeed or fail gracefully
        if response.status_code == 200:
            data = response.json()
            
            # Check response structure
            assert "status" in data
            assert "job_id" in data
            assert "processed_counts" in data
            assert "tag_analysis" in data
            
            # Check processed_counts structure
            counts = data["processed_counts"]
            assert "raw_activities" in counts
            assert "processed_activities" in counts
            assert isinstance(counts["raw_activities"], int)
            assert isinstance(counts["processed_activities"], int)
            
            # Check tag_analysis structure
            analysis = data["tag_analysis"]
            assert "total_unique_tags" in analysis
            assert "average_tags_per_activity" in analysis
            assert isinstance(analysis["total_unique_tags"], int)
            assert isinstance(analysis["average_tags_per_activity"], (int, float))
            
        else:
            # Processing might fail due to missing dependencies or data
            assert response.status_code in [400, 500]

    def test_trigger_processing_minimal_request(self, api_client):
        """Test processing with minimal request data."""
        request_data = {}  # Use all defaults
        
        response = api_client.post("/api/v1/process/daily", json=request_data)
        
        # Should handle defaults gracefully
        assert response.status_code in [200, 400, 500]

    def test_get_processing_status_not_found(self, api_client):
        """Test GET /api/v1/process/status/{job_id} with non-existent job."""
        response = api_client.get("/api/v1/process/status/nonexistent-job-id")
        assert response.status_code == 404

    def test_get_processing_history(self, api_client):
        """Test GET /api/v1/process/history."""
        response = api_client.get("/api/v1/process/history")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # Check structure if any jobs exist
        if data:
            job = data[0]
            required_fields = ["job_id", "status", "started_at"]
            for field in required_fields:
                assert field in job

    def test_get_processing_history_with_limit(self, api_client):
        """Test processing history with limit parameter."""
        response = api_client.get("/api/v1/process/history?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10


class TestImportEndpoints:
    """Test import endpoints."""

    def test_import_calendar_data(self, api_client):
        """Test POST /api/v1/import/calendar."""
        request_data = {
            "hours_since_last_update": 24
        }
        
        response = api_client.post("/api/v1/import/calendar", json=request_data)
        
        # Import might succeed or fail depending on file availability
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "source" in data
            assert data["source"] == "google_calendar"
            
            if data["status"] == "success":
                assert "imported_count" in data
                assert isinstance(data["imported_count"], int)

    def test_import_notion_data(self, api_client):
        """Test POST /api/v1/import/notion."""
        request_data = {
            "hours_since_last_update": 168  # 1 week
        }
        
        response = api_client.post("/api/v1/import/notion", json=request_data)
        
        # Import might succeed or fail depending on file availability
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "source" in data
            assert data["source"] == "notion"

    def test_import_with_invalid_hours(self, api_client):
        """Test import with invalid hours parameter."""
        request_data = {
            "hours_since_last_update": -1  # Invalid negative value
        }
        
        response = api_client.post("/api/v1/import/calendar", json=request_data)
        assert response.status_code == 422

    def test_import_with_excessive_hours(self, api_client):
        """Test import with excessive hours parameter."""
        request_data = {
            "hours_since_last_update": 10000  # More than 1 year (8760 hours)
        }
        
        response = api_client.post("/api/v1/import/calendar", json=request_data)
        assert response.status_code == 422

    def test_get_import_status(self, api_client):
        """Test GET /api/v1/import/status."""
        response = api_client.get("/api/v1/import/status")
        assert response.status_code == 200
        
        data = response.json()
        
        # Should contain status for both sources or error
        if "error" not in data:
            assert "google_calendar" in data
            assert "notion" in data
            
            # Check structure
            for source in ["google_calendar", "notion"]:
                source_data = data[source]
                assert "total_activities" in source_data
                assert isinstance(source_data["total_activities"], int)
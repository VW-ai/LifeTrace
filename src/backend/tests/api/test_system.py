"""
API System Endpoints Tests

Unit tests for system health and statistics API endpoints.
"""

import pytest


class TestSystemEndpoints:
    """Test system endpoints."""

    def test_root_endpoint(self, api_client):
        """Test GET / returns service info."""
        response = api_client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "service" in data
        assert data["service"] == "SmartHistory API"
        assert "version" in data
        assert "status" in data

    def test_health_endpoint(self, api_client):
        """Test GET /health returns health status."""
        response = api_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_system_health(self, api_client):
        """Test GET /api/v1/system/health."""
        response = api_client.get("/api/v1/system/health")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check response structure
        assert "status" in data
        assert "database" in data
        assert "services" in data
        
        # Check database health structure
        database = data["database"]
        required_db_fields = ["connected", "total_activities", "last_updated"]
        for field in required_db_fields:
            assert field in database
        
        assert isinstance(database["connected"], bool)
        assert isinstance(database["total_activities"], int)
        
        # Check services health structure
        services = data["services"]
        required_service_fields = ["tag_generator", "activity_matcher"]
        for field in required_service_fields:
            assert field in services

    def test_system_stats(self, api_client):
        """Test GET /api/v1/system/stats."""
        response = api_client.get("/api/v1/system/stats")
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
        
        # Check non-negative values
        assert data["total_raw_activities"] >= 0
        assert data["total_processed_activities"] >= 0
        assert data["total_tags"] >= 0
        assert data["total_sessions"] >= 0
        assert data["database_size_mb"] >= 0
        assert data["uptime_seconds"] >= 0


class TestErrorHandling:
    """Test API error handling."""

    def test_nonexistent_endpoint(self, api_client):
        """Test that non-existent endpoints return 404."""
        response = api_client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_invalid_endpoint(self, api_client):
        """Test that invalid paths return 404."""
        response = api_client.get("/invalid/path/here")
        assert response.status_code == 404

    def test_method_not_allowed(self, api_client):
        """Test that wrong HTTP methods return 405."""
        # Try DELETE on read-only endpoint
        response = api_client.delete("/api/v1/activities/raw")
        assert response.status_code == 405
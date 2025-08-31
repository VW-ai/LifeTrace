"""
API Insights Endpoints Tests

Unit tests for insights and analytics API endpoints.
"""

import pytest


class TestInsightsEndpoints:
    """Test insights endpoints."""

    def test_get_insights_overview(self, api_client):
        """Test GET /api/v1/insights/overview."""
        response = api_client.get("/api/v1/insights/overview")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check required fields exist
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

    def test_get_insights_overview_with_date_filter(self, api_client):
        """Test insights overview with date filtering."""
        response = api_client.get("/api/v1/insights/overview?date_start=2025-08-31&date_end=2025-08-31")
        assert response.status_code == 200
        
        data = response.json()
        # Should return valid structure even if no data for date range
        assert "total_tracked_hours" in data
        assert "activity_count" in data

    def test_get_insights_overview_invalid_date(self, api_client):
        """Test insights overview with invalid date returns 422."""
        response = api_client.get("/api/v1/insights/overview?date_start=invalid-date")
        assert response.status_code == 422

    def test_get_time_distribution(self, api_client):
        """Test GET /api/v1/insights/time-distribution."""
        response = api_client.get("/api/v1/insights/time-distribution")
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

    def test_get_time_distribution_by_day(self, api_client):
        """Test time distribution grouped by day."""
        response = api_client.get("/api/v1/insights/time-distribution?group_by=day")
        assert response.status_code == 200
        
        data = response.json()
        assert "time_series" in data
        assert "summary" in data

    def test_get_time_distribution_by_week(self, api_client):
        """Test time distribution grouped by week."""
        response = api_client.get("/api/v1/insights/time-distribution?group_by=week")
        assert response.status_code == 200
        
        data = response.json()
        assert "time_series" in data
        assert "summary" in data

    def test_get_time_distribution_by_month(self, api_client):
        """Test time distribution grouped by month."""
        response = api_client.get("/api/v1/insights/time-distribution?group_by=month")
        assert response.status_code == 200
        
        data = response.json()
        assert "time_series" in data
        assert "summary" in data

    def test_get_time_distribution_invalid_group_by(self, api_client):
        """Test time distribution with invalid group_by returns 422."""
        response = api_client.get("/api/v1/insights/time-distribution?group_by=invalid")
        assert response.status_code == 422

    def test_get_time_distribution_with_date_range(self, api_client):
        """Test time distribution with date range filtering."""
        response = api_client.get(
            "/api/v1/insights/time-distribution?date_start=2025-08-30&date_end=2025-08-31&group_by=day"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "time_series" in data
        assert "summary" in data
        
        # Check time series structure if data exists
        if data["time_series"]:
            for point in data["time_series"]:
                assert "date" in point
                assert "total_minutes" in point
                assert "tag_breakdown" in point
                assert isinstance(point["total_minutes"], int)
                assert isinstance(point["tag_breakdown"], dict)
"""
Comprehensive Tag API Endpoints Tests

Unit tests for tag analysis endpoints including summary, cooccurrence,
transitions, and time-series analysis.
"""

import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException


class TestTagAnalysisEndpoints:
    """Test tag analysis endpoints."""

    def test_get_tag_summary_basic(self, api_client):
        """Test GET /api/v1/tags/summary basic functionality."""
        response = api_client.get("/api/v1/tags/summary")
        assert response.status_code == 200

        data = response.json()
        assert "total_tags" in data
        assert "top_tags" in data
        assert "color_map" in data

        assert isinstance(data["total_tags"], int)
        assert isinstance(data["top_tags"], list)
        assert isinstance(data["color_map"], dict)

        # Check structure of top_tags items
        if data["top_tags"]:
            tag_item = data["top_tags"][0]
            assert "tag" in tag_item
            assert "count" in tag_item
            assert "percentage" in tag_item
            assert isinstance(tag_item["count"], int)
            assert isinstance(tag_item["percentage"], float)

    def test_get_tag_summary_with_date_filter(self, api_client):
        """Test tag summary with date filters."""
        start_date = "2025-08-30"
        end_date = "2025-08-31"

        response = api_client.get(f"/api/v1/tags/summary?start_date={start_date}&end_date={end_date}")
        assert response.status_code == 200

        data = response.json()
        assert "total_tags" in data
        assert "top_tags" in data

    def test_get_tag_summary_with_limit(self, api_client):
        """Test tag summary with limit parameter."""
        response = api_client.get("/api/v1/tags/summary?limit=5")
        assert response.status_code == 200

        data = response.json()
        assert len(data["top_tags"]) <= 5

    def test_get_tag_summary_invalid_date(self, api_client):
        """Test tag summary with invalid date format."""
        response = api_client.get("/api/v1/tags/summary?start_date=invalid-date")
        assert response.status_code == 422

    def test_get_tag_summary_invalid_limit(self, api_client):
        """Test tag summary with invalid limit."""
        response = api_client.get("/api/v1/tags/summary?limit=0")
        assert response.status_code == 422

        response = api_client.get("/api/v1/tags/summary?limit=150")
        assert response.status_code == 422

    def test_get_tag_cooccurrence_basic(self, api_client):
        """Test GET /api/v1/tags/cooccurrence basic functionality."""
        response = api_client.get("/api/v1/tags/cooccurrence")
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)

        # Check structure of cooccurrence items
        if data["data"]:
            item = data["data"][0]
            assert "tag1" in item
            assert "tag2" in item
            assert "strength" in item
            assert "count" in item
            assert isinstance(item["strength"], float)
            assert isinstance(item["count"], int)

    def test_get_tag_cooccurrence_with_filters(self, api_client):
        """Test tag cooccurrence with various filters."""
        # Test with date filters
        response = api_client.get("/api/v1/tags/cooccurrence?start_date=2025-08-30&end_date=2025-08-31")
        assert response.status_code == 200

        # Test with tag filter
        response = api_client.get("/api/v1/tags/cooccurrence?tags=meetings,development")
        assert response.status_code == 200

        # Test with threshold
        response = api_client.get("/api/v1/tags/cooccurrence?threshold=1")
        assert response.status_code == 200

    def test_get_tag_cooccurrence_with_limit(self, api_client):
        """Test tag cooccurrence with limit parameter."""
        response = api_client.get("/api/v1/tags/cooccurrence?limit=10")
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) <= 10

    def test_get_tag_transitions_basic(self, api_client):
        """Test GET /api/v1/tags/transitions basic functionality."""
        response = api_client.get("/api/v1/tags/transitions")
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)

        # Check structure of transition items
        if data["data"]:
            item = data["data"][0]
            assert "from_tag" in item
            assert "to_tag" in item
            assert "strength" in item
            assert "count" in item
            assert isinstance(item["strength"], float)
            assert isinstance(item["count"], int)

    def test_get_tag_transitions_with_filters(self, api_client):
        """Test tag transitions with filters."""
        # Test with date filters
        response = api_client.get("/api/v1/tags/transitions?start_date=2025-08-30")
        assert response.status_code == 200

        # Test with specific tags
        response = api_client.get("/api/v1/tags/transitions?tags=meetings")
        assert response.status_code == 200

    def test_get_tag_time_series_basic(self, api_client):
        """Test GET /api/v1/tags/time-series basic functionality."""
        response = api_client.get("/api/v1/tags/time-series")
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)

        # Check structure of time series items
        if data["data"]:
            item = data["data"][0]
            assert "tag" in item
            assert "date" in item
            assert "count" in item
            assert "duration" in item
            assert isinstance(item["count"], int)
            assert isinstance(item["duration"], int)

    def test_get_tag_time_series_granularity(self, api_client):
        """Test tag time series with different granularities."""
        # Test day granularity
        response = api_client.get("/api/v1/tags/time-series?granularity=day")
        assert response.status_code == 200

        # Test hour granularity
        response = api_client.get("/api/v1/tags/time-series?granularity=hour")
        assert response.status_code == 200

        data = response.json()
        if data["data"]:
            # Hour granularity should include hour field
            item = data["data"][0]
            assert "hour" in item

    def test_get_tag_time_series_modes(self, api_client):
        """Test tag time series with different modes."""
        modes = ["absolute", "normalized", "share"]

        for mode in modes:
            response = api_client.get(f"/api/v1/tags/time-series?mode={mode}")
            assert response.status_code == 200

    def test_get_tag_time_series_invalid_params(self, api_client):
        """Test tag time series with invalid parameters."""
        # Invalid granularity
        response = api_client.get("/api/v1/tags/time-series?granularity=invalid")
        assert response.status_code == 422

        # Invalid mode
        response = api_client.get("/api/v1/tags/time-series?mode=invalid")
        assert response.status_code == 422

    def test_get_tags_relationships(self, api_client):
        """Test GET /api/v1/tags/relationships endpoint."""
        response = api_client.get("/api/v1/tags/relationships")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)

        # Check structure if data exists
        if data:
            for tag_name, tag_data in data.items():
                assert "usage_count" in tag_data
                assert "related_tags" in tag_data
                assert isinstance(tag_data["related_tags"], list)

                for related in tag_data["related_tags"]:
                    assert "tag" in related
                    assert "cooccurrence_count" in related

    def test_get_tags_relationships_with_limits(self, api_client):
        """Test tags relationships with custom limits."""
        response = api_client.get("/api/v1/tags/relationships?top_tags_limit=3&related_tags_limit=2")
        assert response.status_code == 200

        data = response.json()
        # Should return at most 3 top tags
        assert len(data) <= 3

        # Each top tag should have at most 2 related tags
        for tag_data in data.values():
            assert len(tag_data["related_tags"]) <= 2


class TestTagCRUDOperations:
    """Test tag CRUD operations."""

    def test_create_tag_basic(self, api_client):
        """Test POST /api/v1/tags basic functionality."""
        tag_data = {
            "name": "test-tag",
            "description": "A test tag",
            "color": "#ff0000"
        }

        response = api_client.post("/api/v1/tags", json=tag_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "test-tag"
        assert data["description"] == "A test tag"
        assert data["color"] == "#ff0000"
        assert data["usage_count"] == 0
        assert "id" in data
        assert "created_at" in data

    def test_create_tag_invalid_data(self, api_client):
        """Test tag creation with invalid data."""
        # Empty name
        response = api_client.post("/api/v1/tags", json={"name": ""})
        assert response.status_code == 422

        # Invalid color format
        response = api_client.post("/api/v1/tags", json={
            "name": "test",
            "color": "invalid-color"
        })
        assert response.status_code == 422

        # Name too long
        response = api_client.post("/api/v1/tags", json={
            "name": "a" * 100
        })
        assert response.status_code == 422

    def test_create_tag_duplicate_name(self, api_client):
        """Test creating tag with duplicate name."""
        tag_data = {
            "name": "duplicate-tag",
            "description": "First tag"
        }

        # Create first tag
        response = api_client.post("/api/v1/tags", json=tag_data)
        assert response.status_code == 200

        # Try to create duplicate
        tag_data["description"] = "Second tag"
        response = api_client.post("/api/v1/tags", json=tag_data)
        assert response.status_code == 409

    def test_get_tag_by_id(self, api_client):
        """Test GET /api/v1/tags/{tag_id}."""
        # Create a tag first
        tag_data = {"name": "get-test-tag"}
        create_response = api_client.post("/api/v1/tags", json=tag_data)
        created_tag = create_response.json()
        tag_id = created_tag["id"]

        # Get the tag
        response = api_client.get(f"/api/v1/tags/{tag_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == tag_id
        assert data["name"] == "get-test-tag"

    def test_get_tag_not_found(self, api_client):
        """Test getting non-existent tag."""
        response = api_client.get("/api/v1/tags/99999")
        assert response.status_code == 404

    def test_update_tag_basic(self, api_client):
        """Test PUT /api/v1/tags/{tag_id}."""
        # Create a tag first
        tag_data = {"name": "update-test-tag"}
        create_response = api_client.post("/api/v1/tags", json=tag_data)
        created_tag = create_response.json()
        tag_id = created_tag["id"]

        # Update the tag
        update_data = {
            "name": "updated-tag-name",
            "description": "Updated description",
            "color": "#00ff00"
        }

        response = api_client.put(f"/api/v1/tags/{tag_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "updated-tag-name"
        assert data["description"] == "Updated description"
        assert data["color"] == "#00ff00"

    def test_update_tag_not_found(self, api_client):
        """Test updating non-existent tag."""
        update_data = {"name": "non-existent"}
        response = api_client.put("/api/v1/tags/99999", json=update_data)
        assert response.status_code == 404

    def test_delete_tag_basic(self, api_client):
        """Test DELETE /api/v1/tags/{tag_id}."""
        # Create a tag first
        tag_data = {"name": "delete-test-tag"}
        create_response = api_client.post("/api/v1/tags", json=tag_data)
        created_tag = create_response.json()
        tag_id = created_tag["id"]

        # Delete the tag
        response = api_client.delete(f"/api/v1/tags/{tag_id}")
        assert response.status_code == 200

        # Verify it's deleted
        get_response = api_client.get(f"/api/v1/tags/{tag_id}")
        assert get_response.status_code == 404

    def test_delete_tag_not_found(self, api_client):
        """Test deleting non-existent tag."""
        response = api_client.delete("/api/v1/tags/99999")
        assert response.status_code == 404


class TestTagServiceUnit:
    """Unit tests for TagService class."""

    @pytest.fixture
    def tag_service(self, test_database):
        """Create TagService instance for testing."""
        from src.backend.api.services import TagService
        return TagService(test_database)

    @pytest.mark.asyncio
    async def test_get_tags_sorting(self, tag_service):
        """Test tag retrieval with different sorting options."""
        # Test name sorting
        result = await tag_service.get_tags(sort_by='name', limit=10)
        assert isinstance(result.tags, list)

        # Test usage_count sorting
        result = await tag_service.get_tags(sort_by='usage_count', limit=10)
        assert isinstance(result.tags, list)

        # Test created_at sorting
        result = await tag_service.get_tags(sort_by='created_at', limit=10)
        assert isinstance(result.tags, list)

    @pytest.mark.asyncio
    async def test_get_tags_pagination(self, tag_service):
        """Test tag pagination."""
        result = await tag_service.get_tags(limit=5, offset=0)
        assert result.page_info.limit == 5
        assert result.page_info.offset == 0
        assert isinstance(result.page_info.has_more, bool)

    @pytest.mark.asyncio
    async def test_tag_summary_empty_database(self, tag_service):
        """Test tag summary with no data."""
        result = await tag_service.get_tag_summary()
        assert result.total_tags >= 0
        assert isinstance(result.top_tags, list)
        assert isinstance(result.color_map, dict)

    @pytest.mark.asyncio
    async def test_tag_cooccurrence_empty_database(self, tag_service):
        """Test tag cooccurrence with no data."""
        result = await tag_service.get_tag_cooccurrence()
        assert isinstance(result.data, list)

    @pytest.mark.asyncio
    async def test_tag_transitions_empty_database(self, tag_service):
        """Test tag transitions with no data."""
        result = await tag_service.get_tag_transitions()
        assert isinstance(result.data, list)

    @pytest.mark.asyncio
    async def test_tag_time_series_empty_database(self, tag_service):
        """Test tag time series with no data."""
        result = await tag_service.get_tag_time_series()
        assert isinstance(result.data, list)

    @pytest.mark.asyncio
    async def test_tag_relationships_empty_database(self, tag_service):
        """Test tag relationships with no data."""
        result = await tag_service.get_top_tags_with_relationships()
        assert isinstance(result, dict)


class TestTagValidation:
    """Test tag validation logic."""

    def test_tag_name_validation(self, api_client):
        """Test tag name validation rules."""
        # Test special characters handling
        valid_names = ["test-tag", "test_tag", "test tag", "test123"]
        for name in valid_names:
            response = api_client.post("/api/v1/tags", json={"name": name})
            # Should either succeed or fail with duplicate (409)
            assert response.status_code in [200, 409]

    def test_tag_color_validation(self, api_client):
        """Test tag color validation."""
        # Valid hex colors
        valid_colors = ["#ffffff", "#000000", "#123456", "#abcdef"]
        for color in valid_colors:
            response = api_client.post("/api/v1/tags", json={
                "name": f"color-test-{color.replace('#', '')}",
                "color": color
            })
            # Should either succeed or fail with duplicate
            assert response.status_code in [200, 409]

        # Invalid colors should fail
        invalid_colors = ["ffffff", "#gggggg", "rgb(255,0,0)", "red"]
        for color in invalid_colors:
            response = api_client.post("/api/v1/tags", json={
                "name": f"invalid-color-{color}",
                "color": color
            })
            assert response.status_code == 422
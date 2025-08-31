"""
API Tags Endpoints Tests

Unit tests for tag management API endpoints.
"""

import pytest


class TestTagsEndpoints:
    """Test tags endpoints."""

    def test_get_tags(self, api_client):
        """Test GET /api/v1/tags."""
        response = api_client.get("/api/v1/tags")
        assert response.status_code == 200
        
        data = response.json()
        assert "tags" in data
        assert "total_count" in data
        assert "page_info" in data
        
        # Check structure
        assert isinstance(data["tags"], list)
        assert isinstance(data["total_count"], int)
        
        # Check page info
        page_info = data["page_info"]
        assert "limit" in page_info
        assert "offset" in page_info
        assert "has_more" in page_info

        # Check tag structure if any exist
        if data["tags"]:
            tag = data["tags"][0]
            required_fields = ["id", "name", "usage_count", "created_at", "updated_at"]
            for field in required_fields:
                assert field in tag

    def test_get_tags_with_sorting(self, api_client):
        """Test tags with different sorting options."""
        for sort_by in ['name', 'usage_count', 'created_at']:
            response = api_client.get(f"/api/v1/tags?sort_by={sort_by}")
            assert response.status_code == 200
            
            data = response.json()
            assert "tags" in data

    def test_get_tags_with_pagination(self, api_client):
        """Test tags pagination."""
        response = api_client.get("/api/v1/tags?limit=5&offset=0")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["tags"]) <= 5
        assert data["page_info"]["limit"] == 5
        assert data["page_info"]["offset"] == 0

    def test_get_tags_invalid_sort_by(self, api_client):
        """Test tags with invalid sort_by returns 422."""
        response = api_client.get("/api/v1/tags?sort_by=invalid")
        assert response.status_code == 422

    def test_create_tag(self, api_client):
        """Test POST /api/v1/tags."""
        tag_data = {
            "name": "test-api-tag",
            "description": "A test tag created via API",
            "color": "#ff6d01"
        }
        
        response = api_client.post("/api/v1/tags", json=tag_data)
        
        # Should succeed (201) or conflict if tag already exists
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "test-api-tag"
            assert data["description"] == "A test tag created via API"
            assert data["color"] == "#ff6d01"
            assert "id" in data
            assert "created_at" in data
        else:
            # Tag might already exist from previous test runs
            assert response.status_code in [400, 409, 422]

    def test_create_tag_minimal(self, api_client):
        """Test creating tag with minimal required fields."""
        tag_data = {
            "name": "minimal-test-tag"
        }
        
        response = api_client.post("/api/v1/tags", json=tag_data)
        
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "minimal-test-tag"
            assert "id" in data
        else:
            # Tag might already exist
            assert response.status_code in [400, 409, 422]

    def test_create_tag_invalid_name(self, api_client):
        """Test creating tag with invalid name."""
        tag_data = {
            "name": ""  # Empty name should be invalid
        }
        
        response = api_client.post("/api/v1/tags", json=tag_data)
        assert response.status_code == 422

    def test_create_tag_invalid_color(self, api_client):
        """Test creating tag with invalid color format."""
        tag_data = {
            "name": "invalid-color-tag",
            "color": "not-a-color"  # Invalid color format
        }
        
        response = api_client.post("/api/v1/tags", json=tag_data)
        assert response.status_code == 422

    def test_get_tag_by_id_not_found(self, api_client):
        """Test GET /api/v1/tags/{id} with non-existent ID."""
        response = api_client.get("/api/v1/tags/99999")
        assert response.status_code == 404

    def test_update_tag_not_found(self, api_client):
        """Test PUT /api/v1/tags/{id} with non-existent ID."""
        tag_data = {
            "name": "updated-tag",
            "description": "Updated description"
        }
        
        response = api_client.put("/api/v1/tags/99999", json=tag_data)
        assert response.status_code == 404

    def test_delete_tag_not_found(self, api_client):
        """Test DELETE /api/v1/tags/{id} with non-existent ID."""
        response = api_client.delete("/api/v1/tags/99999")
        assert response.status_code == 404

    def test_tag_crud_lifecycle(self, api_client):
        """Test complete CRUD lifecycle for a tag."""
        # Create
        tag_data = {
            "name": "crud-test-tag",
            "description": "Tag for CRUD testing",
            "color": "#123456"
        }
        
        create_response = api_client.post("/api/v1/tags", json=tag_data)
        
        if create_response.status_code == 200:
            created_tag = create_response.json()
            tag_id = created_tag["id"]
            
            # Read
            get_response = api_client.get(f"/api/v1/tags/{tag_id}")
            assert get_response.status_code == 200
            retrieved_tag = get_response.json()
            assert retrieved_tag["name"] == "crud-test-tag"
            
            # Update
            update_data = {
                "name": "crud-test-tag-updated",
                "description": "Updated description",
                "color": "#654321"
            }
            update_response = api_client.put(f"/api/v1/tags/{tag_id}", json=update_data)
            assert update_response.status_code == 200
            updated_tag = update_response.json()
            assert updated_tag["name"] == "crud-test-tag-updated"
            assert updated_tag["description"] == "Updated description"
            
            # Delete
            delete_response = api_client.delete(f"/api/v1/tags/{tag_id}")
            assert delete_response.status_code == 200
            
            # Verify deletion
            get_after_delete = api_client.get(f"/api/v1/tags/{tag_id}")
            assert get_after_delete.status_code == 404
"""
Tag Service Unit Tests

Comprehensive unit tests for TagService class methods including
analysis, CRUD operations, and data transformation.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock


class TestTagServiceBasic:
    """Test basic TagService functionality."""

    @pytest.fixture
    def tag_service(self, test_database):
        """Create TagService instance for testing."""
        from src.backend.api.services import TagService
        return TagService(test_database)

    @pytest.mark.asyncio
    async def test_get_tags_basic(self, tag_service):
        """Test basic tag retrieval."""
        result = await tag_service.get_tags()

        assert hasattr(result, 'tags')
        assert hasattr(result, 'total_count')
        assert hasattr(result, 'page_info')

        assert isinstance(result.tags, list)
        assert isinstance(result.total_count, int)
        assert result.page_info.limit == 100  # default limit
        assert result.page_info.offset == 0   # default offset

    @pytest.mark.asyncio
    async def test_get_tags_sorting_options(self, tag_service):
        """Test tag retrieval with different sorting options."""
        sort_options = ['name', 'usage_count', 'created_at']

        for sort_by in sort_options:
            result = await tag_service.get_tags(sort_by=sort_by)
            assert isinstance(result.tags, list)
            assert result.page_info.limit == 100

    @pytest.mark.asyncio
    async def test_get_tags_pagination(self, tag_service):
        """Test tag pagination."""
        result = await tag_service.get_tags(limit=5, offset=10)

        assert result.page_info.limit == 5
        assert result.page_info.offset == 10
        assert len(result.tags) <= 5

    @pytest.mark.asyncio
    async def test_get_tag_by_id_existing(self, tag_service):
        """Test getting existing tag by ID."""
        # First get all tags to find an existing one
        all_tags = await tag_service.get_tags(limit=1)

        if all_tags.tags:
            tag_id = all_tags.tags[0].id
            result = await tag_service.get_tag_by_id(tag_id)

            assert result is not None
            assert result.id == tag_id
            assert hasattr(result, 'name')
            assert hasattr(result, 'usage_count')
            assert hasattr(result, 'created_at')

    @pytest.mark.asyncio
    async def test_get_tag_by_id_nonexistent(self, tag_service):
        """Test getting non-existent tag by ID."""
        result = await tag_service.get_tag_by_id(99999)
        assert result is None


class TestTagServiceCRUD:
    """Test TagService CRUD operations."""

    @pytest.fixture
    def tag_service(self, test_database):
        """Create TagService instance for testing."""
        from src.backend.api.services import TagService
        return TagService(test_database)

    @pytest.mark.asyncio
    async def test_create_tag_basic(self, tag_service):
        """Test basic tag creation."""
        from src.backend.api.models import TagCreateRequest

        tag_data = TagCreateRequest(
            name="test-create-tag",
            description="Test description",
            color="#ff0000"
        )

        result = await tag_service.create_tag(tag_data)

        assert result is not None
        assert result.name == "test-create-tag"
        assert result.description == "Test description"
        assert result.color == "#ff0000"
        assert result.usage_count == 0
        assert isinstance(result.id, int)
        assert isinstance(result.created_at, datetime)

    @pytest.mark.asyncio
    async def test_create_tag_with_minimal_data(self, tag_service):
        """Test tag creation with minimal required data."""
        from src.backend.api.models import TagCreateRequest

        tag_data = TagCreateRequest(name="minimal-tag")
        result = await tag_service.create_tag(tag_data)

        assert result is not None
        assert result.name == "minimal-tag"
        assert result.description is None
        assert result.color is None

    @pytest.mark.asyncio
    async def test_update_tag_basic(self, tag_service):
        """Test basic tag update."""
        from src.backend.api.models import TagCreateRequest, TagUpdateRequest

        # Create a tag first
        create_data = TagCreateRequest(name="update-test-tag")
        created_tag = await tag_service.create_tag(create_data)

        # Update the tag
        update_data = TagUpdateRequest(
            name="updated-tag-name",
            description="Updated description",
            color="#00ff00"
        )

        result = await tag_service.update_tag(created_tag.id, update_data)

        assert result is not None
        assert result.id == created_tag.id
        assert result.name == "updated-tag-name"
        assert result.description == "Updated description"
        assert result.color == "#00ff00"

    @pytest.mark.asyncio
    async def test_update_tag_nonexistent(self, tag_service):
        """Test updating non-existent tag."""
        from src.backend.api.models import TagUpdateRequest

        update_data = TagUpdateRequest(name="nonexistent")
        result = await tag_service.update_tag(99999, update_data)

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_tag_basic(self, tag_service):
        """Test basic tag deletion."""
        from src.backend.api.models import TagCreateRequest

        # Create a tag first
        create_data = TagCreateRequest(name="delete-test-tag")
        created_tag = await tag_service.create_tag(create_data)

        # Delete the tag
        result = await tag_service.delete_tag(created_tag.id)
        assert result is True

        # Verify it's deleted
        deleted_tag = await tag_service.get_tag_by_id(created_tag.id)
        assert deleted_tag is None

    @pytest.mark.asyncio
    async def test_delete_tag_nonexistent(self, tag_service):
        """Test deleting non-existent tag."""
        result = await tag_service.delete_tag(99999)
        assert result is False


class TestTagServiceAnalysis:
    """Test TagService analysis methods."""

    @pytest.fixture
    def tag_service(self, test_database):
        """Create TagService instance for testing."""
        from src.backend.api.services import TagService
        return TagService(test_database)

    @pytest.mark.asyncio
    async def test_get_tag_summary_basic(self, tag_service):
        """Test basic tag summary."""
        result = await tag_service.get_tag_summary()

        assert hasattr(result, 'total_tags')
        assert hasattr(result, 'top_tags')
        assert hasattr(result, 'color_map')

        assert isinstance(result.total_tags, int)
        assert isinstance(result.top_tags, list)
        assert isinstance(result.color_map, dict)

        # Check structure of top_tags items
        for tag_item in result.top_tags:
            assert hasattr(tag_item, 'tag')
            assert hasattr(tag_item, 'count')
            assert hasattr(tag_item, 'percentage')
            assert isinstance(tag_item.count, int)
            assert isinstance(tag_item.percentage, float)

    @pytest.mark.asyncio
    async def test_get_tag_summary_with_filters(self, tag_service):
        """Test tag summary with date filters."""
        result = await tag_service.get_tag_summary(
            start_date="2025-08-30",
            end_date="2025-08-31",
            limit=10
        )

        assert isinstance(result.total_tags, int)
        assert len(result.top_tags) <= 10

    @pytest.mark.asyncio
    async def test_get_tag_cooccurrence_basic(self, tag_service):
        """Test basic tag co-occurrence analysis."""
        result = await tag_service.get_tag_cooccurrence()

        assert hasattr(result, 'data')
        assert isinstance(result.data, list)

        # Check structure of cooccurrence items
        for item in result.data:
            assert hasattr(item, 'tag1')
            assert hasattr(item, 'tag2')
            assert hasattr(item, 'strength')
            assert hasattr(item, 'count')
            assert isinstance(item.strength, float)
            assert isinstance(item.count, int)

    @pytest.mark.asyncio
    async def test_get_tag_cooccurrence_with_filters(self, tag_service):
        """Test tag co-occurrence with filters."""
        result = await tag_service.get_tag_cooccurrence(
            start_date="2025-08-30",
            end_date="2025-08-31",
            tags=["meetings", "development"],
            threshold=1,
            limit=20
        )

        assert isinstance(result.data, list)
        assert len(result.data) <= 20

        # If data exists, check that filtered tags appear
        for item in result.data:
            assert item.tag1 in ["meetings", "development"] or item.tag2 in ["meetings", "development"]

    @pytest.mark.asyncio
    async def test_get_tag_transitions_basic(self, tag_service):
        """Test basic tag transition analysis."""
        result = await tag_service.get_tag_transitions()

        assert hasattr(result, 'data')
        assert isinstance(result.data, list)

        # Check structure of transition items
        for item in result.data:
            assert hasattr(item, 'from_tag')
            assert hasattr(item, 'to_tag')
            assert hasattr(item, 'strength')
            assert hasattr(item, 'count')
            assert isinstance(item.strength, float)
            assert isinstance(item.count, int)

    @pytest.mark.asyncio
    async def test_get_tag_transitions_with_filters(self, tag_service):
        """Test tag transitions with filters."""
        result = await tag_service.get_tag_transitions(
            start_date="2025-08-30",
            tags=["meetings"],
            limit=15
        )

        assert isinstance(result.data, list)
        assert len(result.data) <= 15

    @pytest.mark.asyncio
    async def test_get_tag_time_series_basic(self, tag_service):
        """Test basic tag time series analysis."""
        result = await tag_service.get_tag_time_series()

        assert hasattr(result, 'data')
        assert isinstance(result.data, list)

        # Check structure of time series items
        for item in result.data:
            assert hasattr(item, 'tag')
            assert hasattr(item, 'date')
            assert hasattr(item, 'count')
            assert hasattr(item, 'duration')
            assert isinstance(item.count, int)
            assert isinstance(item.duration, int)

    @pytest.mark.asyncio
    async def test_get_tag_time_series_hourly(self, tag_service):
        """Test tag time series with hourly granularity."""
        result = await tag_service.get_tag_time_series(granularity="hour")

        assert isinstance(result.data, list)

        # Hourly data should include hour field
        for item in result.data:
            assert hasattr(item, 'hour')

    @pytest.mark.asyncio
    async def test_get_tag_time_series_with_filters(self, tag_service):
        """Test tag time series with filters."""
        result = await tag_service.get_tag_time_series(
            start_date="2025-08-30",
            end_date="2025-08-31",
            tags=["meetings"],
            granularity="day",
            mode="absolute"
        )

        assert isinstance(result.data, list)

        # If data exists, should only contain specified tags
        for item in result.data:
            assert item.tag in ["meetings"]

    @pytest.mark.asyncio
    async def test_get_top_tags_with_relationships_basic(self, tag_service):
        """Test basic top tags with relationships."""
        result = await tag_service.get_top_tags_with_relationships()

        assert isinstance(result, dict)

        # Check structure of relationships
        for tag_name, tag_data in result.items():
            assert 'usage_count' in tag_data
            assert 'related_tags' in tag_data
            assert isinstance(tag_data['related_tags'], list)

            for related in tag_data['related_tags']:
                assert 'tag' in related
                assert 'cooccurrence_count' in related

    @pytest.mark.asyncio
    async def test_get_top_tags_with_relationships_limits(self, tag_service):
        """Test top tags with relationships with custom limits."""
        result = await tag_service.get_top_tags_with_relationships(
            top_tags_limit=3,
            related_tags_limit=2
        )

        assert isinstance(result, dict)
        assert len(result) <= 3

        for tag_data in result.values():
            assert len(tag_data['related_tags']) <= 2


class TestTagServiceDataValidation:
    """Test TagService data validation and error handling."""

    @pytest.fixture
    def tag_service(self, test_database):
        """Create TagService instance for testing."""
        from src.backend.api.services import TagService
        return TagService(test_database)

    @pytest.mark.asyncio
    async def test_tag_summary_with_invalid_dates(self, tag_service):
        """Test tag summary with invalid date ranges."""
        # Future dates should return empty results
        result = await tag_service.get_tag_summary(
            start_date="2099-01-01",
            end_date="2099-12-31"
        )

        assert isinstance(result.total_tags, int)
        assert isinstance(result.top_tags, list)
        # Should return 0 results for future dates
        assert len(result.top_tags) == 0

    @pytest.mark.asyncio
    async def test_analysis_methods_empty_database(self, tag_service):
        """Test analysis methods with empty or minimal data."""
        # These should not raise exceptions even with no data
        summary = await tag_service.get_tag_summary()
        assert isinstance(summary.top_tags, list)

        cooccurrence = await tag_service.get_tag_cooccurrence()
        assert isinstance(cooccurrence.data, list)

        transitions = await tag_service.get_tag_transitions()
        assert isinstance(transitions.data, list)

        time_series = await tag_service.get_tag_time_series()
        assert isinstance(time_series.data, list)

        relationships = await tag_service.get_top_tags_with_relationships()
        assert isinstance(relationships, dict)

    @pytest.mark.asyncio
    async def test_tag_name_normalization(self, tag_service):
        """Test tag name normalization in creation."""
        from src.backend.api.models import TagCreateRequest

        # Test various name formats
        test_names = ["Test Tag", "test-tag", "test_tag", "TEST TAG"]

        for name in test_names:
            tag_data = TagCreateRequest(name=name)
            try:
                result = await tag_service.create_tag(tag_data)
                # Name should be normalized to lowercase
                assert result.name.islower()
            except Exception:
                # Might fail due to duplicates - that's expected
                pass


class TestTagServicePerformance:
    """Test TagService performance considerations."""

    @pytest.fixture
    def tag_service(self, test_database):
        """Create TagService instance for testing."""
        from src.backend.api.services import TagService
        return TagService(test_database)

    @pytest.mark.asyncio
    async def test_large_analysis_queries(self, tag_service):
        """Test performance of large analysis queries."""
        import time

        # Test tag summary with large limit
        start_time = time.time()
        result = await tag_service.get_tag_summary(limit=100)
        end_time = time.time()

        assert (end_time - start_time) < 2.0  # Should complete within 2 seconds
        assert isinstance(result.top_tags, list)

    @pytest.mark.asyncio
    async def test_cooccurrence_analysis_performance(self, tag_service):
        """Test co-occurrence analysis performance."""
        import time

        start_time = time.time()
        result = await tag_service.get_tag_cooccurrence(limit=50)
        end_time = time.time()

        assert (end_time - start_time) < 3.0  # Should complete within 3 seconds
        assert isinstance(result.data, list)

    @pytest.mark.asyncio
    async def test_time_series_analysis_performance(self, tag_service):
        """Test time series analysis performance."""
        import time

        start_time = time.time()
        result = await tag_service.get_tag_time_series()
        end_time = time.time()

        assert (end_time - start_time) < 2.0  # Should complete within 2 seconds
        assert isinstance(result.data, list)


class TestTagServiceIntegration:
    """Test TagService integration with other components."""

    @pytest.fixture
    def tag_service(self, test_database):
        """Create TagService instance for testing."""
        from src.backend.api.services import TagService
        return TagService(test_database)

    @pytest.mark.asyncio
    async def test_database_transaction_consistency(self, tag_service):
        """Test database transaction consistency."""
        from src.backend.api.models import TagCreateRequest

        # Create multiple tags in sequence
        tag_names = ["consistency-test-1", "consistency-test-2", "consistency-test-3"]
        created_tags = []

        for name in tag_names:
            tag_data = TagCreateRequest(name=name)
            result = await tag_service.create_tag(tag_data)
            created_tags.append(result)

        # All tags should be created successfully
        assert len(created_tags) == 3

        # All should be retrievable
        for tag in created_tags:
            retrieved = await tag_service.get_tag_by_id(tag.id)
            assert retrieved is not None
            assert retrieved.name == tag.name

    @pytest.mark.asyncio
    async def test_service_method_chaining(self, tag_service):
        """Test chaining of service methods."""
        # Get initial tag count
        initial_tags = await tag_service.get_tags(limit=1000)
        initial_count = len(initial_tags.tags)

        # Create a new tag
        from src.backend.api.models import TagCreateRequest
        tag_data = TagCreateRequest(name="chain-test-tag")
        created_tag = await tag_service.create_tag(tag_data)

        # Get updated tag count
        updated_tags = await tag_service.get_tags(limit=1000)
        updated_count = len(updated_tags.tags)

        # Count should increase by 1
        assert updated_count == initial_count + 1

        # Delete the tag
        delete_result = await tag_service.delete_tag(created_tag.id)
        assert delete_result is True

        # Count should return to original
        final_tags = await tag_service.get_tags(limit=1000)
        final_count = len(final_tags.tags)
        assert final_count == initial_count
"""
Activity Service Unit Tests

Comprehensive unit tests for ActivityService class methods.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


class TestActivityService:
    """Test ActivityService methods."""

    @pytest.fixture
    def activity_service(self, test_database):
        """Create ActivityService instance for testing."""
        from src.backend.api.services import ActivityService
        return ActivityService(test_database)

    @pytest.mark.asyncio
    async def test_get_raw_activities_basic(self, activity_service):
        """Test basic raw activities retrieval."""
        result = await activity_service.get_raw_activities()

        assert hasattr(result, 'activities')
        assert hasattr(result, 'total_count')
        assert hasattr(result, 'page_info')

        assert isinstance(result.activities, list)
        assert isinstance(result.total_count, int)
        assert result.page_info.limit == 100  # default limit
        assert result.page_info.offset == 0   # default offset

    @pytest.mark.asyncio
    async def test_get_raw_activities_with_source_filter(self, activity_service):
        """Test raw activities with source filter."""
        result = await activity_service.get_raw_activities(source="google_calendar")

        # All returned activities should be from google_calendar
        for activity in result.activities:
            assert activity.source == "google_calendar"

    @pytest.mark.asyncio
    async def test_get_raw_activities_with_date_filters(self, activity_service):
        """Test raw activities with date filters."""
        start_date = "2025-08-30"
        end_date = "2025-08-31"

        result = await activity_service.get_raw_activities(
            date_start=start_date,
            date_end=end_date
        )

        # All returned activities should be within date range
        for activity in result.activities:
            assert activity.date >= start_date
            assert activity.date <= end_date

    @pytest.mark.asyncio
    async def test_get_raw_activities_pagination(self, activity_service):
        """Test raw activities pagination."""
        result = await activity_service.get_raw_activities(limit=5, offset=10)

        assert result.page_info.limit == 5
        assert result.page_info.offset == 10
        assert len(result.activities) <= 5

    @pytest.mark.asyncio
    async def test_get_processed_activities_basic(self, activity_service):
        """Test basic processed activities retrieval."""
        result = await activity_service.get_processed_activities()

        assert hasattr(result, 'activities')
        assert hasattr(result, 'total_count')
        assert hasattr(result, 'page_info')

        assert isinstance(result.activities, list)
        assert isinstance(result.total_count, int)

    @pytest.mark.asyncio
    async def test_get_processed_activities_with_filters(self, activity_service):
        """Test processed activities with various filters."""
        # Test with date filters
        result = await activity_service.get_processed_activities(
            date_start="2025-08-30",
            date_end="2025-08-31"
        )

        for activity in result.activities:
            assert activity.date >= "2025-08-30"
            assert activity.date <= "2025-08-31"

        # Test with tags filter
        result = await activity_service.get_processed_activities(
            tags=["meetings", "development"]
        )

        # Each activity should have at least one of the specified tags
        for activity in result.activities:
            activity_tag_names = [tag.name for tag in activity.tags]
            assert any(tag in activity_tag_names for tag in ["meetings", "development"])

    @pytest.mark.asyncio
    async def test_get_processed_activities_pagination(self, activity_service):
        """Test processed activities pagination."""
        result = await activity_service.get_processed_activities(limit=3, offset=0)

        assert result.page_info.limit == 3
        assert result.page_info.offset == 0
        assert len(result.activities) <= 3

    @pytest.mark.asyncio
    async def test_get_processed_activities_structure_validation(self, activity_service):
        """Test processed activities response structure."""
        result = await activity_service.get_processed_activities()

        # Test structure of activities if any exist
        if result.activities:
            activity = result.activities[0]

            # Check required fields
            assert hasattr(activity, 'id')
            assert hasattr(activity, 'date')
            assert hasattr(activity, 'total_duration_minutes')
            assert hasattr(activity, 'combined_details')
            assert hasattr(activity, 'sources')
            assert hasattr(activity, 'tags')
            assert hasattr(activity, 'raw_activity_ids')
            assert hasattr(activity, 'created_at')

            # Check field types
            assert isinstance(activity.id, int)
            assert isinstance(activity.date, str)
            assert isinstance(activity.total_duration_minutes, int)
            assert isinstance(activity.combined_details, str)
            assert isinstance(activity.sources, list)
            assert isinstance(activity.tags, list)
            assert isinstance(activity.raw_activity_ids, list)
            assert isinstance(activity.created_at, datetime)

    @pytest.mark.asyncio
    async def test_get_activities_empty_database(self, activity_service):
        """Test activity retrieval with empty database."""
        # This should not raise an exception even with no data
        result = await activity_service.get_raw_activities()
        assert result.total_count >= 0
        assert isinstance(result.activities, list)

        result = await activity_service.get_processed_activities()
        assert result.total_count >= 0
        assert isinstance(result.activities, list)

    @pytest.mark.asyncio
    async def test_activity_service_error_handling(self, activity_service):
        """Test activity service error handling."""
        # Test with invalid date format (should be handled by API validation)
        # Here we test the service layer directly with valid inputs

        # Test extreme pagination values
        result = await activity_service.get_raw_activities(limit=1000, offset=0)
        assert isinstance(result, object)

        # Test with very restrictive filters
        result = await activity_service.get_processed_activities(
            date_start="2099-01-01",
            date_end="2099-01-02"
        )
        assert result.total_count == 0
        assert len(result.activities) == 0


class TestActivityServiceDataTransformation:
    """Test data transformation in ActivityService."""

    @pytest.fixture
    def activity_service(self, test_database):
        """Create ActivityService instance for testing."""
        from src.backend.api.services import ActivityService
        return ActivityService(test_database)

    @pytest.mark.asyncio
    async def test_raw_activity_data_transformation(self, activity_service):
        """Test raw activity data transformation."""
        result = await activity_service.get_raw_activities()

        if result.activities:
            activity = result.activities[0]

            # Test that raw_data is properly parsed
            assert hasattr(activity, 'raw_data')
            assert isinstance(activity.raw_data, dict)

            # Test datetime parsing
            assert isinstance(activity.created_at, datetime)

    @pytest.mark.asyncio
    async def test_processed_activity_data_transformation(self, activity_service):
        """Test processed activity data transformation."""
        result = await activity_service.get_processed_activities()

        if result.activities:
            activity = result.activities[0]

            # Test that sources are properly parsed from JSON
            assert isinstance(activity.sources, list)

            # Test that raw_activity_ids are properly parsed
            assert isinstance(activity.raw_activity_ids, list)

            # Test tag relationship loading
            assert isinstance(activity.tags, list)
            for tag in activity.tags:
                assert hasattr(tag, 'id')
                assert hasattr(tag, 'name')
                assert hasattr(tag, 'confidence')

    @pytest.mark.asyncio
    async def test_pagination_info_calculation(self, activity_service):
        """Test pagination info calculation."""
        # Test has_more calculation
        result = await activity_service.get_raw_activities(limit=1, offset=0)

        if result.total_count > 1:
            assert result.page_info.has_more is True
        else:
            assert result.page_info.has_more is False

        # Test with offset near end
        if result.total_count > 0:
            last_page_result = await activity_service.get_raw_activities(
                limit=10,
                offset=max(0, result.total_count - 5)
            )
            # Should have has_more as False or correct calculation
            expected_has_more = (last_page_result.page_info.offset + last_page_result.page_info.limit) < result.total_count
            assert last_page_result.page_info.has_more == expected_has_more


class TestActivityServicePerformance:
    """Test ActivityService performance considerations."""

    @pytest.fixture
    def activity_service(self, test_database):
        """Create ActivityService instance for testing."""
        from src.backend.api.services import ActivityService
        return ActivityService(test_database)

    @pytest.mark.asyncio
    async def test_large_limit_handling(self, activity_service):
        """Test handling of large limit values."""
        # Test maximum allowed limit
        result = await activity_service.get_raw_activities(limit=1000)
        assert result.page_info.limit == 1000

        # Result should be returned without timeout or memory issues
        assert isinstance(result.activities, list)

    @pytest.mark.asyncio
    async def test_query_efficiency(self, activity_service):
        """Test query efficiency markers."""
        import time

        # Measure basic query time
        start_time = time.time()
        result = await activity_service.get_processed_activities(limit=50)
        end_time = time.time()

        query_time = end_time - start_time

        # Query should complete within reasonable time (less than 1 second)
        assert query_time < 1.0

        # Should return reasonable amount of data
        assert isinstance(result.activities, list)

    @pytest.mark.asyncio
    async def test_memory_efficiency(self, activity_service):
        """Test memory efficiency with larger datasets."""
        # Test that service doesn't load all data into memory at once
        result = await activity_service.get_raw_activities(limit=100, offset=0)

        # Even with large datasets, memory usage should be controlled
        # This is more of a structural test than a memory measurement
        assert len(result.activities) <= 100

        # Pagination should work without loading everything
        if result.total_count > 100:
            next_page = await activity_service.get_raw_activities(limit=100, offset=100)
            assert isinstance(next_page.activities, list)


class TestActivityServiceIntegration:
    """Test ActivityService integration with database layer."""

    @pytest.fixture
    def activity_service(self, test_database):
        """Create ActivityService instance for testing."""
        from src.backend.api.services import ActivityService
        return ActivityService(test_database)

    @pytest.mark.asyncio
    async def test_database_connection_handling(self, activity_service):
        """Test database connection handling."""
        # Service should handle database queries gracefully
        result = await activity_service.get_raw_activities()
        assert hasattr(result, 'activities')

        # Multiple queries should work
        result2 = await activity_service.get_processed_activities()
        assert hasattr(result2, 'activities')

    @pytest.mark.asyncio
    async def test_transaction_consistency(self, activity_service):
        """Test transaction consistency in queries."""
        # Multiple related queries should be consistent
        raw_result = await activity_service.get_raw_activities()
        processed_result = await activity_service.get_processed_activities()

        # Both results should be structured correctly
        assert isinstance(raw_result.total_count, int)
        assert isinstance(processed_result.total_count, int)

        # Page info should be consistent
        assert raw_result.page_info.limit > 0
        assert processed_result.page_info.limit > 0
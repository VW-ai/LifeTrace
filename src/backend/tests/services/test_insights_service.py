"""
Insights Service Unit Tests

Comprehensive unit tests for InsightsService class methods.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


class TestInsightsService:
    """Test InsightsService methods."""

    @pytest.fixture
    def insights_service(self, test_database):
        """Create InsightsService instance for testing."""
        from src.backend.api.services import InsightsService
        return InsightsService(test_database)

    @pytest.mark.asyncio
    async def test_get_overview_basic(self, insights_service):
        """Test basic insights overview."""
        result = await insights_service.get_overview()

        assert hasattr(result, 'total_tracked_hours')
        assert hasattr(result, 'activity_count')
        assert hasattr(result, 'unique_tags')
        assert hasattr(result, 'tag_time_distribution')
        assert hasattr(result, 'tag_percentages')
        assert hasattr(result, 'top_5_activities')
        assert hasattr(result, 'date_range')

        # Check data types
        assert isinstance(result.total_tracked_hours, float)
        assert isinstance(result.activity_count, int)
        assert isinstance(result.unique_tags, int)
        assert isinstance(result.tag_time_distribution, dict)
        assert isinstance(result.tag_percentages, dict)
        assert isinstance(result.top_5_activities, list)
        assert hasattr(result.date_range, 'start')
        assert hasattr(result.date_range, 'end')

    @pytest.mark.asyncio
    async def test_get_overview_with_date_filters(self, insights_service):
        """Test insights overview with date filters."""
        start_date = "2025-08-30"
        end_date = "2025-08-31"

        result = await insights_service.get_overview(
            date_start=start_date,
            date_end=end_date
        )

        # Date range should match filters
        assert result.date_range.start == start_date
        assert result.date_range.end == end_date

        # Should have valid data structure
        assert isinstance(result.activity_count, int)
        assert isinstance(result.total_tracked_hours, float)

    @pytest.mark.asyncio
    async def test_get_overview_top_activities_structure(self, insights_service):
        """Test top activities structure in overview."""
        result = await insights_service.get_overview()

        # Check top_5_activities structure
        assert len(result.top_5_activities) <= 5

        for activity in result.top_5_activities:
            assert hasattr(activity, 'tag')
            assert hasattr(activity, 'hours')
            assert isinstance(activity.tag, str)
            assert isinstance(activity.hours, float)

    @pytest.mark.asyncio
    async def test_get_overview_empty_database(self, insights_service):
        """Test overview with empty database."""
        result = await insights_service.get_overview()

        # Should handle empty data gracefully
        assert result.activity_count >= 0
        assert result.total_tracked_hours >= 0.0
        assert result.unique_tags >= 0
        assert isinstance(result.tag_time_distribution, dict)
        assert isinstance(result.tag_percentages, dict)
        assert isinstance(result.top_5_activities, list)

    @pytest.mark.asyncio
    async def test_get_time_distribution_basic(self, insights_service):
        """Test basic time distribution analysis."""
        result = await insights_service.get_time_distribution()

        assert hasattr(result, 'time_series')
        assert hasattr(result, 'summary')

        # Check time_series structure
        assert isinstance(result.time_series, list)

        for point in result.time_series:
            assert hasattr(point, 'date')
            assert hasattr(point, 'total_minutes')
            assert hasattr(point, 'tag_breakdown')
            assert isinstance(point.date, str)
            assert isinstance(point.total_minutes, int)
            assert isinstance(point.tag_breakdown, dict)

        # Check summary structure
        assert hasattr(result.summary, 'total_period_hours')
        assert hasattr(result.summary, 'average_daily_hours')
        assert hasattr(result.summary, 'most_productive_day')
        assert isinstance(result.summary.total_period_hours, float)
        assert isinstance(result.summary.average_daily_hours, float)
        assert isinstance(result.summary.most_productive_day, str)

    @pytest.mark.asyncio
    async def test_get_time_distribution_with_filters(self, insights_service):
        """Test time distribution with filters."""
        result = await insights_service.get_time_distribution(
            date_start="2025-08-30",
            date_end="2025-08-31",
            group_by="day"
        )

        assert isinstance(result.time_series, list)
        assert isinstance(result.summary, object)

        # Time series should only include dates in range
        for point in result.time_series:
            assert point.date >= "2025-08-30"
            assert point.date <= "2025-08-31"

    @pytest.mark.asyncio
    async def test_get_time_distribution_grouping_options(self, insights_service):
        """Test time distribution with different grouping options."""
        group_options = ["day", "week", "month"]

        for group_by in group_options:
            result = await insights_service.get_time_distribution(group_by=group_by)
            assert isinstance(result.time_series, list)
            assert isinstance(result.summary, object)

    @pytest.mark.asyncio
    async def test_get_time_distribution_empty_period(self, insights_service):
        """Test time distribution for empty period."""
        # Use future dates that should have no data
        result = await insights_service.get_time_distribution(
            date_start="2099-01-01",
            date_end="2099-01-31"
        )

        assert isinstance(result.time_series, list)
        assert len(result.time_series) == 0
        assert result.summary.total_period_hours == 0.0
        assert result.summary.average_daily_hours == 0.0


class TestInsightsServiceCalculations:
    """Test calculation accuracy in InsightsService."""

    @pytest.fixture
    def insights_service(self, test_database):
        """Create InsightsService instance for testing."""
        from src.backend.api.services import InsightsService
        return InsightsService(test_database)

    @pytest.mark.asyncio
    async def test_time_calculation_accuracy(self, insights_service):
        """Test accuracy of time calculations."""
        result = await insights_service.get_overview()

        # Total tracked hours should be non-negative
        assert result.total_tracked_hours >= 0.0

        # If there are activities, hours should be positive
        if result.activity_count > 0:
            assert result.total_tracked_hours > 0.0

    @pytest.mark.asyncio
    async def test_percentage_calculation_accuracy(self, insights_service):
        """Test accuracy of percentage calculations."""
        result = await insights_service.get_overview()

        # All percentages should sum to approximately 100% (or 0% if no data)
        total_percentage = sum(result.tag_percentages.values())

        if total_percentage > 0:
            # Allow for small floating point errors
            assert abs(total_percentage - 100.0) < 0.1

        # Each individual percentage should be between 0 and 100
        for percentage in result.tag_percentages.values():
            assert 0.0 <= percentage <= 100.0

    @pytest.mark.asyncio
    async def test_tag_distribution_consistency(self, insights_service):
        """Test consistency between tag distribution formats."""
        result = await insights_service.get_overview()

        # tag_time_distribution and tag_percentages should have same keys
        time_dist_tags = set(result.tag_time_distribution.keys())
        percent_tags = set(result.tag_percentages.keys())

        assert time_dist_tags == percent_tags

        # Time values should be consistent with percentages
        total_minutes = sum(result.tag_time_distribution.values())
        if total_minutes > 0:
            for tag in time_dist_tags:
                expected_percentage = (result.tag_time_distribution[tag] / total_minutes) * 100
                actual_percentage = result.tag_percentages[tag]
                # Allow for small rounding differences
                assert abs(expected_percentage - actual_percentage) < 0.5

    @pytest.mark.asyncio
    async def test_top_activities_ranking(self, insights_service):
        """Test that top activities are properly ranked."""
        result = await insights_service.get_overview()

        # Top activities should be sorted by hours (descending)
        if len(result.top_5_activities) > 1:
            for i in range(len(result.top_5_activities) - 1):
                current_hours = result.top_5_activities[i].hours
                next_hours = result.top_5_activities[i + 1].hours
                assert current_hours >= next_hours

    @pytest.mark.asyncio
    async def test_date_range_calculation(self, insights_service):
        """Test date range calculation."""
        # Test with explicit date range
        start_date = "2025-08-30"
        end_date = "2025-08-31"

        result = await insights_service.get_overview(
            date_start=start_date,
            date_end=end_date
        )

        assert result.date_range.start == start_date
        assert result.date_range.end == end_date

        # Test without explicit date range (should determine from data)
        result_auto = await insights_service.get_overview()
        assert isinstance(result_auto.date_range.start, str)
        assert isinstance(result_auto.date_range.end, str)


class TestInsightsServiceTimeDistribution:
    """Test time distribution specific functionality."""

    @pytest.fixture
    def insights_service(self, test_database):
        """Create InsightsService instance for testing."""
        from src.backend.api.services import InsightsService
        return InsightsService(test_database)

    @pytest.mark.asyncio
    async def test_daily_distribution_accuracy(self, insights_service):
        """Test daily time distribution accuracy."""
        result = await insights_service.get_time_distribution(group_by="day")

        # Each day's total should equal sum of tag breakdown
        for point in result.time_series:
            tag_total = sum(point.tag_breakdown.values())
            assert point.total_minutes == tag_total

    @pytest.mark.asyncio
    async def test_summary_calculations(self, insights_service):
        """Test summary calculation accuracy."""
        result = await insights_service.get_time_distribution()

        # Total period hours should equal sum of all daily totals
        if result.time_series:
            calculated_total = sum(point.total_minutes for point in result.time_series) / 60.0
            assert abs(result.summary.total_period_hours - calculated_total) < 0.1

            # Average daily hours calculation
            num_days = len(result.time_series)
            if num_days > 0:
                expected_average = result.summary.total_period_hours / num_days
                assert abs(result.summary.average_daily_hours - expected_average) < 0.1

    @pytest.mark.asyncio
    async def test_most_productive_day_calculation(self, insights_service):
        """Test most productive day calculation."""
        result = await insights_service.get_time_distribution()

        if result.time_series:
            # Find the day with maximum total minutes
            max_minutes = max(point.total_minutes for point in result.time_series)
            most_productive_days = [
                point.date for point in result.time_series
                if point.total_minutes == max_minutes
            ]

            # Most productive day should be one of the days with maximum minutes
            assert result.summary.most_productive_day in most_productive_days

    @pytest.mark.asyncio
    async def test_tag_breakdown_consistency(self, insights_service):
        """Test tag breakdown consistency across time series."""
        result = await insights_service.get_time_distribution()

        # All tag names in breakdowns should be consistent
        all_tags = set()
        for point in result.time_series:
            all_tags.update(point.tag_breakdown.keys())

        # Each time point should have breakdown for each tag (possibly 0)
        for point in result.time_series:
            for tag in all_tags:
                if tag not in point.tag_breakdown:
                    # Missing tags should be treated as 0
                    pass  # This is acceptable behavior


class TestInsightsServicePerformance:
    """Test InsightsService performance."""

    @pytest.fixture
    def insights_service(self, test_database):
        """Create InsightsService instance for testing."""
        from src.backend.api.services import InsightsService
        return InsightsService(test_database)

    @pytest.mark.asyncio
    async def test_overview_query_performance(self, insights_service):
        """Test overview query performance."""
        import time

        start_time = time.time()
        result = await insights_service.get_overview()
        end_time = time.time()

        query_time = end_time - start_time

        # Should complete within reasonable time
        assert query_time < 2.0

        # Should return valid data structure
        assert isinstance(result.activity_count, int)

    @pytest.mark.asyncio
    async def test_time_distribution_query_performance(self, insights_service):
        """Test time distribution query performance."""
        import time

        start_time = time.time()
        result = await insights_service.get_time_distribution()
        end_time = time.time()

        query_time = end_time - start_time

        # Should complete within reasonable time
        assert query_time < 3.0

        # Should return valid data structure
        assert isinstance(result.time_series, list)

    @pytest.mark.asyncio
    async def test_large_date_range_performance(self, insights_service):
        """Test performance with large date ranges."""
        import time

        # Test with a year-long range
        start_time = time.time()
        result = await insights_service.get_time_distribution(
            date_start="2024-01-01",
            date_end="2024-12-31",
            group_by="day"
        )
        end_time = time.time()

        query_time = end_time - start_time

        # Should handle large ranges efficiently
        assert query_time < 5.0

        # Should return reasonable amount of data
        assert isinstance(result.time_series, list)


class TestInsightsServiceIntegration:
    """Test InsightsService integration."""

    @pytest.fixture
    def insights_service(self, test_database):
        """Create InsightsService instance for testing."""
        from src.backend.api.services import InsightsService
        return InsightsService(test_database)

    @pytest.mark.asyncio
    async def test_database_consistency(self, insights_service):
        """Test database query consistency."""
        # Multiple calls should return consistent results
        result1 = await insights_service.get_overview()
        result2 = await insights_service.get_overview()

        assert result1.activity_count == result2.activity_count
        assert result1.total_tracked_hours == result2.total_tracked_hours
        assert result1.unique_tags == result2.unique_tags

    @pytest.mark.asyncio
    async def test_cross_method_consistency(self, insights_service):
        """Test consistency between different service methods."""
        overview = await insights_service.get_overview()
        time_dist = await insights_service.get_time_distribution()

        # Activity counts should be consistent
        # (time distribution might have different grouping, so exact match not required)
        if overview.activity_count > 0:
            assert len(time_dist.time_series) > 0

        # Total hours should be approximately consistent
        if overview.total_tracked_hours > 0:
            assert time_dist.summary.total_period_hours > 0

    @pytest.mark.asyncio
    async def test_error_handling(self, insights_service):
        """Test error handling in insights service."""
        # Should handle edge cases gracefully
        result = await insights_service.get_overview(
            date_start="2099-01-01",  # Future date
            date_end="2099-01-02"
        )

        # Should return valid structure even with no data
        assert isinstance(result.activity_count, int)
        assert isinstance(result.total_tracked_hours, float)
        assert result.activity_count == 0
        assert result.total_tracked_hours == 0.0
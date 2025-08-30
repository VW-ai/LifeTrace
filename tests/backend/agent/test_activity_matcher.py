import pytest
from datetime import datetime, timedelta
from src.backend.agent import ActivityMatcher, RawActivity

class TestActivityMatcher:
    """Comprehensive tests for ActivityMatcher."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.matcher = ActivityMatcher(time_window_minutes=120)
        
        # Create test data
        self.notion_activity = RawActivity(
            date="2024-08-30",
            time=None,
            duration_minutes=0,
            details="Working on smartHistory project documentation",
            source="notion",
            orig_link="",
            raw_data={'block_id': 'test-block-123'}
        )
        
        self.calendar_activity = RawActivity(
            date="2024-08-30", 
            time="14:00",
            duration_minutes=90,
            details="Development work - smartHistory",
            source="google_calendar",
            orig_link="https://calendar.google.com/event/123",
            raw_data={'event_id': 'cal-event-123'}
        )
        
        self.unrelated_calendar = RawActivity(
            date="2024-08-30",
            time="16:00", 
            duration_minutes=30,
            details="Team standup meeting",
            source="google_calendar",
            orig_link="https://calendar.google.com/event/456",
            raw_data={'event_id': 'cal-event-456'}
        )
    
    def test_match_activities_with_good_match(self):
        """Test matching when activities have good content similarity."""
        activities = [self.notion_activity, self.calendar_activity, self.unrelated_calendar]
        result = self.matcher.match_activities(activities)
        
        # Should have 2 activities: 1 merged + 1 unmatched calendar
        assert len(result) == 2
        
        merged_activities = [a for a in result if a.source == "merged"]
        assert len(merged_activities) == 1
        
        merged = merged_activities[0]
        assert merged.date == "2024-08-30"
        assert merged.time == "14:00"
        assert merged.duration_minutes == 90
        assert "smartHistory" in merged.details
        assert merged.raw_data['merged_from'] == ['notion', 'google_calendar']
    
    def test_match_activities_no_matches(self):
        """Test when no activities match."""
        unrelated_notion = RawActivity(
            date="2024-08-30",
            time=None,
            duration_minutes=0,
            details="Grocery shopping list",
            source="notion",
            orig_link="",
            raw_data={'block_id': 'grocery-123'}
        )
        
        activities = [unrelated_notion, self.unrelated_calendar]
        result = self.matcher.match_activities(activities)
        
        # Should have 2 activities: original notion + calendar (no merging)
        assert len(result) == 2
        merged_activities = [a for a in result if a.source == "merged"]
        assert len(merged_activities) == 0
    
    def test_match_activities_empty_input(self):
        """Test with empty input."""
        result = self.matcher.match_activities([])
        assert result == []
    
    def test_match_activities_only_notion(self):
        """Test with only Notion activities."""
        activities = [self.notion_activity]
        result = self.matcher.match_activities(activities)
        
        assert len(result) == 1
        assert result[0].source == "notion"
        assert result[0].duration_minutes > 0  # Should have estimated duration
    
    def test_match_activities_only_calendar(self):
        """Test with only Calendar activities."""
        activities = [self.calendar_activity]
        result = self.matcher.match_activities(activities)
        
        assert len(result) == 1
        assert result[0].source == "google_calendar"
    
    def test_calculate_time_confidence_exact_match(self):
        """Test time confidence calculation for exact time matches."""
        notion_with_time = RawActivity(
            date="2024-08-30",
            time="14:00",
            duration_minutes=0,
            details="Test activity",
            source="notion"
        )
        
        confidence = self.matcher._calculate_time_confidence(notion_with_time, self.calendar_activity)
        assert confidence == 1.0
    
    def test_calculate_time_confidence_close_match(self):
        """Test time confidence for close time matches."""
        notion_with_time = RawActivity(
            date="2024-08-30",
            time="14:30",
            duration_minutes=0,
            details="Test activity",
            source="notion"
        )
        
        confidence = self.matcher._calculate_time_confidence(notion_with_time, self.calendar_activity)
        assert 0.6 <= confidence <= 0.8
    
    def test_calculate_time_confidence_no_notion_time(self):
        """Test time confidence when Notion has no time."""
        confidence = self.matcher._calculate_time_confidence(self.notion_activity, self.calendar_activity)
        assert confidence == 0.5  # Same date, no time
    
    def test_calculate_content_similarity_high(self):
        """Test content similarity calculation for similar content."""
        similarity = self.matcher._calculate_content_similarity(self.notion_activity, self.calendar_activity)
        assert similarity > 0.3  # Should detect "smartHistory" overlap
    
    def test_calculate_content_similarity_low(self):
        """Test content similarity for unrelated content."""
        unrelated = RawActivity(
            date="2024-08-30",
            time="14:00",
            duration_minutes=60,
            details="Completely different task about groceries",
            source="google_calendar"
        )
        
        similarity = self.matcher._calculate_content_similarity(self.notion_activity, unrelated)
        assert similarity < 0.5
    
    def test_calculate_content_similarity_empty_content(self):
        """Test content similarity with empty content."""
        empty_notion = RawActivity(
            date="2024-08-30",
            details="",
            source="notion"
        )
        
        similarity = self.matcher._calculate_content_similarity(empty_notion, self.calendar_activity)
        assert similarity == 0.3  # Neutral confidence
    
    def test_merge_activities(self):
        """Test activity merging functionality."""
        merged = self.matcher._merge_activities(self.notion_activity, self.calendar_activity)
        
        assert merged.source == "merged"
        assert merged.date == self.calendar_activity.date
        assert merged.time == self.calendar_activity.time
        assert merged.duration_minutes == self.calendar_activity.duration_minutes
        assert "smartHistory" in merged.details
        assert "|" in merged.details  # Should combine details
        assert 'merged_from' in merged.raw_data
        assert 'notion_data' in merged.raw_data
        assert 'match_confidence' in merged.raw_data
    
    def test_estimate_duration_short_content(self):
        """Test duration estimation for short content."""
        short_activity = RawActivity(
            date="2024-08-30",
            details="Quick note",
            source="notion"
        )
        duration = self.matcher._estimate_duration(short_activity)
        assert duration == 15
    
    def test_estimate_duration_medium_content(self):
        """Test duration estimation for medium content."""
        medium_activity = RawActivity(
            date="2024-08-30", 
            details="This is a medium length task that requires some explanation and detail",
            source="notion"
        )
        duration = self.matcher._estimate_duration(medium_activity)
        assert duration == 30
    
    def test_estimate_duration_long_content(self):
        """Test duration estimation for long content."""
        long_content = " ".join(["word"] * 120)  # 120 words
        long_activity = RawActivity(
            date="2024-08-30",
            details=long_content,
            source="notion"
        )
        duration = self.matcher._estimate_duration(long_activity)
        assert duration == 90
    
    def test_dates_within_window(self):
        """Test date window checking."""
        assert self.matcher._dates_within_window("2024-08-30", "2024-08-30", days=1) == True
        assert self.matcher._dates_within_window("2024-08-30", "2024-08-31", days=1) == True
        assert self.matcher._dates_within_window("2024-08-30", "2024-09-01", days=1) == False
        assert self.matcher._dates_within_window("invalid", "2024-08-30", days=1) == False
    
    def test_get_matching_statistics(self):
        """Test matching statistics generation."""
        activities = [
            RawActivity(date="2024-08-30", details="test1", source="notion"),
            RawActivity(date="2024-08-30", details="test2", source="google_calendar"),
            RawActivity(date="2024-08-30", details="test3", source="merged"),
            RawActivity(date="2024-08-30", details="test4", source="merged")
        ]
        
        stats = self.matcher.get_matching_statistics(activities)
        
        assert stats['total_activities'] == 4
        assert stats['merged_activities'] == 2
        assert stats['notion_only'] == 1
        assert stats['calendar_only'] == 1
        assert stats['merge_rate'] == 50.0
    
    def test_process_unmatched_notion_activities(self):
        """Test processing of unmatched Notion activities."""
        notion_activities = [
            RawActivity(date="2024-08-30", details="Task 1", source="notion"),
            RawActivity(date="2024-08-30", details="Task 2 with more detailed content", source="notion")
        ]
        
        processed = self.matcher._process_unmatched_notion_activities(notion_activities)
        
        assert len(processed) == 2
        for activity in processed:
            assert activity.duration_minutes > 0
            assert activity.raw_data['duration_estimated'] == True
            assert activity.raw_data['estimation_method'] == 'content_analysis'
    
    def test_find_best_calendar_match_no_candidates(self):
        """Test finding match when no candidates exist."""
        notion_activity = RawActivity(
            date="2024-08-30",
            details="Test task",
            source="notion"
        )
        
        # Calendar activity on different date
        calendar_activities = [RawActivity(
            date="2024-09-05",
            time="10:00", 
            details="Different task",
            source="google_calendar"
        )]
        
        match = self.matcher._find_best_calendar_match(notion_activity, calendar_activities)
        assert match is None
    
    def test_find_best_calendar_match_with_candidates(self):
        """Test finding best match among multiple candidates."""
        notion_activity = RawActivity(
            date="2024-08-30",
            details="Working on project alpha",
            source="notion"
        )
        
        calendar_activities = [
            RawActivity(
                date="2024-08-30",
                time="10:00",
                details="Meeting about project beta",
                source="google_calendar"
            ),
            RawActivity(
                date="2024-08-30", 
                time="14:00",
                details="Development work on project alpha",
                source="google_calendar"
            )
        ]
        
        match_result = self.matcher._find_best_calendar_match(notion_activity, calendar_activities)
        assert match_result is not None
        
        matched_activity, confidence = match_result
        assert "project alpha" in matched_activity.details
        assert confidence > 0.3
    
    def test_time_window_configuration(self):
        """Test that time window configuration affects matching."""
        # Create matcher with very small time window
        strict_matcher = ActivityMatcher(time_window_minutes=30)
        
        notion_with_time = RawActivity(
            date="2024-08-30",
            time="12:00",
            details="Test task",
            source="notion"
        )
        
        # Calendar event 1 hour later
        late_calendar = RawActivity(
            date="2024-08-30",
            time="13:00", 
            details="Test task",
            source="google_calendar"
        )
        
        # Should have lower confidence with strict matcher
        confidence = strict_matcher._calculate_time_confidence(notion_with_time, late_calendar)
        assert confidence <= 0.8  # 1 hour difference should get 0.8
        
        # Default matcher should be more lenient
        default_confidence = self.matcher._calculate_time_confidence(notion_with_time, late_calendar)
        assert default_confidence >= 0.6  # Within 120-minute window

@pytest.fixture
def sample_mixed_activities():
    """Fixture providing a realistic mix of activities for integration tests."""
    return [
        # Notion activities
        RawActivity(
            date="2024-08-30",
            time=None,
            duration_minutes=0,
            details="[Project Planning] Reviewed requirements for user authentication",
            source="notion",
            raw_data={'block_id': 'auth-planning-123'}
        ),
        RawActivity(
            date="2024-08-30", 
            time=None,
            duration_minutes=0,
            details="[Development] Fixed bug in login validation",
            source="notion",
            raw_data={'block_id': 'bug-fix-456'}
        ),
        # Calendar activities
        RawActivity(
            date="2024-08-30",
            time="09:00",
            duration_minutes=120,
            details="Sprint Planning - Authentication Features",
            source="google_calendar",
            raw_data={'event_id': 'sprint-planning-789'}
        ),
        RawActivity(
            date="2024-08-30",
            time="14:00", 
            duration_minutes=90,
            details="Development Time - Bug Fixes",
            source="google_calendar",
            raw_data={'event_id': 'dev-time-012'}
        ),
        RawActivity(
            date="2024-08-30",
            time="16:30",
            duration_minutes=30, 
            details="1:1 with Team Lead",
            source="google_calendar",
            raw_data={'event_id': 'one-on-one-345'}
        )
    ]

class TestActivityMatcherIntegration:
    """Integration tests with realistic data scenarios."""
    
    def test_realistic_matching_scenario(self, sample_mixed_activities):
        """Test matching with realistic mixed activity data."""
        matcher = ActivityMatcher()
        result = matcher.match_activities(sample_mixed_activities)
        
        # Should have some merged activities
        merged_activities = [a for a in result if a.source == "merged"]
        assert len(merged_activities) >= 1
        
        # Should have some unmatched activities
        unmatched = [a for a in result if a.source != "merged"]
        assert len(unmatched) >= 1
        
        # All activities should have durations
        for activity in result:
            assert activity.duration_minutes > 0
    
    def test_matching_statistics_realistic(self, sample_mixed_activities):
        """Test statistics generation with realistic data."""
        matcher = ActivityMatcher()
        result = matcher.match_activities(sample_mixed_activities)
        stats = matcher.get_matching_statistics(result)
        
        assert stats['total_activities'] == len(result)
        assert stats['merge_rate'] >= 0  # Should be reasonable percentage
        assert stats['merged_activities'] + stats['notion_only'] + stats['calendar_only'] == len(result)
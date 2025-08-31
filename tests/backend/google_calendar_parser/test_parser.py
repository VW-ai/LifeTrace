import unittest
import json
import tempfile
import os
from datetime import datetime, timezone, timedelta
from src.backend.parsers.google_calendar.parser import parse_calendar_events, calculate_duration

class TestGoogleCalendarParser(unittest.TestCase):
    
    def setUp(self):
        """Set up test data."""
        self.sample_event = {
            "id": "test_event_1",
            "summary": "Test Meeting",
            "description": "This is a test meeting",
            "start": {
                "dateTime": "2025-08-29T10:00:00+08:00",
                "timeZone": "Asia/Shanghai"
            },
            "end": {
                "dateTime": "2025-08-29T11:00:00+08:00", 
                "timeZone": "Asia/Shanghai"
            },
            "updated": "2025-08-29T08:00:00.000Z",
            "htmlLink": "https://example.com/event"
        }
        
        self.old_event = {
            "id": "old_event",
            "summary": "Old Meeting",
            "start": {
                "dateTime": "2025-07-01T10:00:00+08:00"
            },
            "end": {
                "dateTime": "2025-07-01T11:00:00+08:00"
            },
            "updated": "2025-07-01T08:00:00.000Z"
        }
    
    def test_calculate_duration(self):
        """Test duration calculation."""
        # Test normal duration
        start = "2025-08-29T10:00:00+08:00"
        end = "2025-08-29T11:30:00+08:00"
        duration = calculate_duration(start, end)
        self.assertEqual(duration, 90)  # 1.5 hours = 90 minutes
        
        # Test same time
        duration = calculate_duration(start, start)
        self.assertEqual(duration, 0)
        
        # Test invalid input
        duration = calculate_duration("invalid", "invalid")
        self.assertEqual(duration, 0)
    
    def test_parse_calendar_events_filtering(self):
        """Test event filtering by update time."""
        now = datetime(2025, 8, 29, 12, 0, 0, tzinfo=timezone.utc)
        
        # Should include recent event (updated 4 hours ago)
        events = [self.sample_event]
        parsed = parse_calendar_events(events, hours_since_last_update=8, now=now)
        self.assertEqual(len(parsed), 1)
        
        # Should exclude old event (updated more than 8 hours ago)
        events = [self.old_event]
        parsed = parse_calendar_events(events, hours_since_last_update=8, now=now)
        self.assertEqual(len(parsed), 0)
    
    def test_parse_calendar_events_structure(self):
        """Test parsed event structure."""
        events = [self.sample_event]
        parsed = parse_calendar_events(events, hours_since_last_update=24*30)
        
        self.assertEqual(len(parsed), 1)
        event = parsed[0]
        
        # Check required fields
        self.assertEqual(event["source"], "google_calendar")
        self.assertEqual(event["event_id"], "test_event_1")
        self.assertEqual(event["event_type"], "calendar_event")
        self.assertEqual(event["text"], "Test Meeting - This is a test meeting")
        self.assertEqual(event["summary"], "Test Meeting")
        self.assertEqual(event["description"], "This is a test meeting")
        self.assertEqual(event["duration_minutes"], 60)
        self.assertEqual(event["hierarchy"], [])
        self.assertIn("start_time", event)
        self.assertIn("end_time", event)
    
    def test_event_without_description(self):
        """Test event without description."""
        event_no_desc = {
            "id": "no_desc",
            "summary": "Simple Event",
            "start": {"dateTime": "2025-08-29T10:00:00+08:00"},
            "end": {"dateTime": "2025-08-29T11:00:00+08:00"},
            "updated": "2025-08-29T08:00:00.000Z"
        }
        
        # Set 'now' to be within the time window of the event
        now = datetime(2025, 8, 29, 12, 0, 0, tzinfo=timezone.utc)
        parsed = parse_calendar_events([event_no_desc], hours_since_last_update=24, now=now)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["text"], "Simple Event")
        self.assertEqual(parsed[0]["description"], "")

if __name__ == '__main__':
    unittest.main()
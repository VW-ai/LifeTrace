import pytest
import json
import tempfile
import os
from src.backend.agent import ActivityProcessor

class TestActivityProcessorIntegration:
    """Integration tests for the complete ActivityProcessor pipeline."""
    
    def setup_method(self):
        """Set up test files with sample data."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Sample Notion data
        self.notion_data = [
            {
                "block_id": "notion-123",
                "block_type": "paragraph",
                "text": "Working on user authentication implementation",
                "hierarchy": ["Projects", "SmartHistory", "Development"]
            },
            {
                "block_id": "notion-456", 
                "block_type": "to_do",
                "text": "Review pull request for bug fixes",
                "hierarchy": ["Tasks", "Code Review"]
            }
        ]
        
        # Sample Calendar data
        self.calendar_data = [
            {
                "event_id": "cal-789",
                "summary": "Development Block - Authentication",
                "description": "Working on auth system implementation",
                "start_time": "2024-08-30T14:00:00Z",
                "end_time": "2024-08-30T16:00:00Z",
                "duration_minutes": 120,
                "text": "Development Block - Authentication: Working on auth system implementation",
                "html_link": "https://calendar.google.com/event/789"
            },
            {
                "event_id": "cal-012",
                "summary": "Code Review Session",
                "description": "Review outstanding PRs",
                "start_time": "2024-08-30T10:00:00Z", 
                "end_time": "2024-08-30T10:30:00Z",
                "duration_minutes": 30,
                "text": "Code Review Session: Review outstanding PRs",
                "html_link": "https://calendar.google.com/event/012"
            }
        ]
        
        # Create temp files
        self.notion_file = os.path.join(self.temp_dir, "test_notion.json")
        self.calendar_file = os.path.join(self.temp_dir, "test_calendar.json")
        
        with open(self.notion_file, 'w') as f:
            json.dump(self.notion_data, f)
        
        with open(self.calendar_file, 'w') as f:
            json.dump(self.calendar_data, f)
    
    def teardown_method(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_processing_pipeline(self):
        """Test the complete processing pipeline with sample data."""
        # Initialize processor without OpenAI (to test fallback functionality)
        processor = ActivityProcessor(openai_api_key=None)
        
        # Set up output files
        raw_output = os.path.join(self.temp_dir, "raw_activities.json")
        processed_output = os.path.join(self.temp_dir, "processed_activities.json")
        
        # Run processing
        report = processor.process_daily_activities(
            notion_file=self.notion_file,
            calendar_file=self.calendar_file,
            output_raw_file=raw_output,
            output_processed_file=processed_output,
            use_database=False  # Use test files instead of database
        )
        
        # Verify report structure
        assert report['status'] == 'success'
        assert 'processing_timestamp' in report
        assert 'processed_counts' in report
        assert 'tag_analysis' in report
        assert 'duration_analysis' in report
        assert 'matching_analysis' in report
        
        # Verify processing results
        processed_counts = report['processed_counts']
        assert processed_counts['raw_activities'] > 0
        assert processed_counts['processed_activities'] > 0
        
        # Verify files were created
        assert os.path.exists(raw_output)
        assert os.path.exists(processed_output)
        
        # Verify file contents
        with open(raw_output, 'r') as f:
            raw_activities = json.load(f)
            assert len(raw_activities) > 0
            
            # Check that activities have required fields
            for activity in raw_activities:
                assert 'date' in activity
                assert 'source' in activity
                assert 'details' in activity
                assert 'duration_minutes' in activity
                assert activity['duration_minutes'] > 0  # Should have estimated duration
        
        with open(processed_output, 'r') as f:
            processed_activities = json.load(f)
            assert len(processed_activities) > 0
            
            # Check that processed activities have tags
            for activity in processed_activities:
                assert 'tags' in activity
                assert len(activity['tags']) > 0
    
    def test_insights_generation(self):
        """Test insights generation from processed activities."""
        processor = ActivityProcessor()
        
        # Create sample processed activities directly
        sample_activities = []
        from src.backend.agent import ProcessedActivity
        
        sample_activities = [
            ProcessedActivity(
                date="2024-08-30",
                time="14:00",
                tags=["programming", "development"],
                total_duration_minutes=120,
                combined_details="Working on authentication system",
                sources=["merged"]
            ),
            ProcessedActivity(
                date="2024-08-30", 
                time="10:00",
                tags=["code_review", "collaboration"],
                total_duration_minutes=30,
                combined_details="Code review session",
                sources=["google_calendar"]
            )
        ]
        
        insights = processor.get_activity_insights(sample_activities)
        
        # Verify insights structure
        assert 'total_tracked_hours' in insights
        assert 'activity_count' in insights
        assert 'tag_time_distribution' in insights
        assert 'tag_percentages' in insights
        assert 'top_5_activities' in insights
        assert 'unique_tags' in insights
        
        # Verify calculations
        assert insights['total_tracked_hours'] == 2.5  # 150 minutes / 60
        assert insights['activity_count'] == 2
        assert insights['unique_tags'] > 0
    
    def test_empty_data_handling(self):
        """Test handling of empty input data."""
        # Create empty files
        empty_notion = os.path.join(self.temp_dir, "empty_notion.json")
        empty_calendar = os.path.join(self.temp_dir, "empty_calendar.json")
        
        with open(empty_notion, 'w') as f:
            json.dump([], f)
        
        with open(empty_calendar, 'w') as f:
            json.dump([], f)
        
        processor = ActivityProcessor(openai_api_key=None)
        
        raw_output = os.path.join(self.temp_dir, "empty_raw.json")
        processed_output = os.path.join(self.temp_dir, "empty_processed.json")
        
        report = processor.process_daily_activities(
            notion_file=empty_notion,
            calendar_file=empty_calendar,
            output_raw_file=raw_output,
            output_processed_file=processed_output,
            use_database=False  # Use file-based processing for this test
        )
        
        # Should handle empty data gracefully
        assert report['status'] == 'no_data'
        assert report['processed_count'] == 0
    
    def test_missing_files_handling(self):
        """Test handling of missing input files."""
        processor = ActivityProcessor(openai_api_key=None)
        
        nonexistent_notion = os.path.join(self.temp_dir, "nonexistent_notion.json")
        nonexistent_calendar = os.path.join(self.temp_dir, "nonexistent_calendar.json")
        
        raw_output = os.path.join(self.temp_dir, "missing_raw.json")
        processed_output = os.path.join(self.temp_dir, "missing_processed.json")
        
        # Should handle missing files without crashing
        report = processor.process_daily_activities(
            notion_file=nonexistent_notion,
            calendar_file=nonexistent_calendar,
            output_raw_file=raw_output,
            output_processed_file=processed_output,
            use_database=False  # Use file-based processing for this test
        )
        
        assert report['status'] == 'no_data'
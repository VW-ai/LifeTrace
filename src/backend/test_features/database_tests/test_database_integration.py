#!/usr/bin/env python3
"""
Database Integration Tests for SmartHistory

Comprehensive tests for database functionality including:
- Connection management and pooling
- CRUD operations for all entities
- Data validation and constraints
- Migration system
- Performance and indexes
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
import sys
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.database import (
    DatabaseConnection, ConnectionConfig,
    RawActivityDB, ProcessedActivityDB, TagDB, ActivityTagDB, UserSessionDB,
    RawActivityDAO, ProcessedActivityDAO, TagDAO, ActivityTagDAO, UserSessionDAO,
    SessionStatus, get_db_manager, initialize_database
)
from src.backend.database.migrations import MigrationManager, Migration

class TestDatabaseIntegration(unittest.TestCase):
    """Integration tests for database functionality."""
    
    def setUp(self):
        """Set up test database."""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Initialize database with test configuration
        self.config = ConnectionConfig(db_path=self.temp_db.name)
        self.db = initialize_database(self.temp_db.name)
        
    def tearDown(self):
        """Clean up test database."""
        # Close all connections
        self.db.close_all_connections()
        
        # Clear the database connection instances for proper test isolation
        DatabaseConnection._instances.clear()
        
        # Remove temporary file
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def test_database_initialization(self):
        """Test database initialization and schema creation."""
        # Check that all required tables exist
        required_tables = [
            'schema_versions', 'raw_activities', 'processed_activities',
            'tags', 'activity_tags', 'user_sessions', 'tag_generations'
        ]
        
        for table in required_tables:
            self.assertTrue(self.db.table_exists(table), f"Table {table} should exist")
        
        # Check schema version is recorded
        result = self.db.execute_query("SELECT MAX(version) as version FROM schema_versions")
        self.assertIsNotNone(result[0]['version'], "Schema version should be recorded")
    
    def test_raw_activity_crud(self):
        """Test Raw Activity CRUD operations."""
        # Create activity
        activity = RawActivityDB(
            date='2025-08-31',
            time='14:30',
            duration_minutes=60,
            details='Working on database implementation',
            source='notion',
            orig_link='https://notion.so/page/123',
            raw_data={'type': 'development', 'priority': 'high'}
        )
        
        activity_id = RawActivityDAO.create(activity)
        self.assertIsNotNone(activity_id, "Activity ID should be returned")
        
        # Read activity
        retrieved = RawActivityDAO.get_by_id(activity_id)
        self.assertIsNotNone(retrieved, "Activity should be retrievable")
        self.assertEqual(retrieved.date, '2025-08-31')
        self.assertEqual(retrieved.source, 'notion')
        self.assertEqual(retrieved.duration_minutes, 60)
        self.assertEqual(retrieved.raw_data['type'], 'development')
        
        # Update activity
        retrieved.details = 'Updated database implementation details'
        retrieved.duration_minutes = 90
        success = RawActivityDAO.update(retrieved)
        self.assertTrue(success, "Update should succeed")
        
        # Verify update
        updated = RawActivityDAO.get_by_id(activity_id)
        self.assertEqual(updated.details, 'Updated database implementation details')
        self.assertEqual(updated.duration_minutes, 90)
        
        # Delete activity
        success = RawActivityDAO.delete(activity_id)
        self.assertTrue(success, "Delete should succeed")
        
        # Verify deletion
        deleted = RawActivityDAO.get_by_id(activity_id)
        self.assertIsNone(deleted, "Activity should be deleted")
    
    def test_tag_management(self):
        """Test tag creation and management."""
        # Create tags
        tag1 = TagDB(name='work', description='Work related activities', color='#FF0000')
        tag2 = TagDB(name='development', description='Software development', color='#00FF00')
        
        tag1_id = TagDAO.create(tag1)
        tag2_id = TagDAO.create(tag2)
        
        self.assertIsNotNone(tag1_id)
        self.assertIsNotNone(tag2_id)
        
        # Test unique constraint
        with self.assertRaises(ValueError):
            TagDAO.create(TagDB(name='work', description='Duplicate'))
        
        # Get all tags
        all_tags = TagDAO.get_all()
        self.assertEqual(len(all_tags), 2)
        self.assertEqual(all_tags[0].name, 'work')  # Should be ordered by usage_count desc
        
        # Get by name
        work_tag = TagDAO.get_by_name('work')
        self.assertIsNotNone(work_tag)
        self.assertEqual(work_tag.description, 'Work related activities')
    
    def test_processed_activity_with_tags(self):
        """Test processed activities with tag relationships."""
        # Create raw activities
        raw1 = RawActivityDB(
            date='2025-08-31',
            details='Morning standup meeting',
            source='google_calendar',
            duration_minutes=30
        )
        raw2 = RawActivityDB(
            date='2025-08-31', 
            details='Code review session',
            source='notion',
            duration_minutes=45
        )
        
        raw1_id = RawActivityDAO.create(raw1)
        raw2_id = RawActivityDAO.create(raw2)
        
        # Create tags
        work_tag = TagDB(name='work', description='Work activities')
        meeting_tag = TagDB(name='meeting', description='Meetings')
        
        work_tag_id = TagDAO.create(work_tag)
        meeting_tag_id = TagDAO.create(meeting_tag)
        
        # Create processed activity
        processed = ProcessedActivityDB(
            date='2025-08-31',
            time='09:00',
            total_duration_minutes=75,
            combined_details='Morning standup meeting and code review session',
            raw_activity_ids=[raw1_id, raw2_id],
            sources=['google_calendar', 'notion']
        )
        
        processed_id = ProcessedActivityDAO.create(processed)
        
        # Create tag relationships
        ActivityTagDAO.create(ActivityTagDB(
            processed_activity_id=processed_id,
            tag_id=work_tag_id,
            confidence_score=0.9
        ))
        
        ActivityTagDAO.create(ActivityTagDB(
            processed_activity_id=processed_id,
            tag_id=meeting_tag_id,
            confidence_score=0.8
        ))
        
        # Get activity with tags
        activity_with_tags = ProcessedActivityDAO.get_with_tags(processed_id)
        self.assertIsNotNone(activity_with_tags)
        
        activity, tags = activity_with_tags
        self.assertEqual(len(tags), 2)
        self.assertEqual(activity.total_duration_minutes, 75)
        
        # Verify tag usage counts were updated
        work_tag_updated = TagDAO.get_by_id(work_tag_id)
        meeting_tag_updated = TagDAO.get_by_id(meeting_tag_id)
        self.assertEqual(work_tag_updated.usage_count, 1)
        self.assertEqual(meeting_tag_updated.usage_count, 1)
        
        # Test tag queries
        tags_for_activity = ActivityTagDAO.get_tags_for_activity(processed_id)
        self.assertEqual(len(tags_for_activity), 2)
        
        # Should be ordered by confidence score
        self.assertEqual(tags_for_activity[0][1], 0.9)  # work tag confidence
        self.assertEqual(tags_for_activity[1][1], 0.8)  # meeting tag confidence
    
    def test_date_range_queries(self):
        """Test date range queries for activities."""
        # Create activities across multiple dates
        dates = ['2025-08-29', '2025-08-30', '2025-08-31', '2025-09-01']
        activity_ids = []
        
        for date in dates:
            activity = RawActivityDB(
                date=date,
                details=f'Activity on {date}',
                source='test',
                duration_minutes=60
            )
            activity_ids.append(RawActivityDAO.create(activity))
        
        # Query specific date range
        activities = RawActivityDAO.get_by_date_range('2025-08-30', '2025-08-31')
        self.assertEqual(len(activities), 2)
        self.assertEqual(activities[0].date, '2025-08-30')
        self.assertEqual(activities[1].date, '2025-08-31')
        
        # Query with source filter
        activities_filtered = RawActivityDAO.get_by_date_range(
            '2025-08-29', '2025-09-01', source='test'
        )
        self.assertEqual(len(activities_filtered), 4)
    
    def test_user_session_tracking(self):
        """Test user session tracking functionality."""
        # Create session
        session = UserSessionDB(
            session_type='daily_processing',
            status=SessionStatus.STARTED,
            metadata={'version': '1.0', 'mode': 'test'},
            processed_raw_count=0,
            processed_activity_count=0,
            tags_generated=0
        )
        
        session_id = UserSessionDAO.create(session)
        self.assertIsNotNone(session_id)
        
        # Update session status
        success = UserSessionDAO.update_status(
            session_id, 
            SessionStatus.COMPLETED
        )
        self.assertTrue(success)
        
        # Get recent sessions
        recent_sessions = UserSessionDAO.get_recent_sessions(limit=5)
        self.assertEqual(len(recent_sessions), 1)
        self.assertEqual(recent_sessions[0].status, SessionStatus.COMPLETED)
        self.assertIsNotNone(recent_sessions[0].end_time)
    
    def test_data_validation(self):
        """Test data validation and constraints."""
        # Test invalid date format
        with self.assertRaises(ValueError):
            invalid_activity = RawActivityDB(
                date='2025/08/31',  # Invalid format
                source='test'
            )
            invalid_activity.validate()
        
        # Test invalid time format
        with self.assertRaises(ValueError):
            invalid_activity = RawActivityDB(
                date='2025-08-31',
                time='25:00',  # Invalid time
                source='test'
            )
            invalid_activity.validate()
        
        # Test negative duration
        with self.assertRaises(ValueError):
            invalid_activity = RawActivityDB(
                date='2025-08-31',
                source='test',
                duration_minutes=-10
            )
            invalid_activity.validate()
        
        # Test missing required fields
        with self.assertRaises(ValueError):
            invalid_activity = RawActivityDB(date='', source='test')
            invalid_activity.validate()
        
        with self.assertRaises(ValueError):
            invalid_activity = RawActivityDB(date='2025-08-31', source='')
            invalid_activity.validate()
    
    def test_transaction_rollback(self):
        """Test transaction rollback on errors."""
        # Create initial data
        tag = TagDB(name='test_tag')
        tag_id = TagDAO.create(tag)
        
        initial_count = len(TagDAO.get_all())
        
        # Test transaction rollback
        try:
            with self.db.transaction() as conn:
                # Insert valid tag
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO tags (name, description) VALUES (?, ?)",
                    ('temp_tag', 'Temporary tag')
                )
                
                # This should cause a constraint violation and rollback
                cursor.execute(
                    "INSERT INTO tags (name, description) VALUES (?, ?)",
                    ('test_tag', 'Duplicate tag')  # Violates unique constraint
                )
        except:
            pass  # Expected to fail
        
        # Verify rollback - count should be unchanged
        final_count = len(TagDAO.get_all())
        self.assertEqual(initial_count, final_count, "Transaction should have been rolled back")
    
    def test_migration_system(self):
        """Test migration system functionality."""
        manager = MigrationManager()
        
        # Test current version
        current_version = manager.get_current_version()
        self.assertGreaterEqual(current_version, 1, "Should have at least version 1")
        
        # Test migration history
        history = manager.get_migration_history()
        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0, "Should have migration history")
        
        # Test schema validation
        validation_result = manager.validate_schema()
        self.assertTrue(validation_result, "Schema validation should pass")
    
    def test_performance_indexes(self):
        """Test that performance indexes are created and working."""
        # Get index information
        indexes = self.db.execute_query("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND sql IS NOT NULL
            ORDER BY name
        """)
        
        index_names = [row['name'] for row in indexes]
        
        # Check for key performance indexes
        expected_indexes = [
            'idx_raw_activities_date',
            'idx_raw_activities_source',
            'idx_processed_activities_date',
            'idx_tags_name',
            'idx_activity_tags_processed_activity',
            'idx_activity_tags_tag'
        ]
        
        for expected_index in expected_indexes:
            self.assertIn(expected_index, index_names, f"Index {expected_index} should exist")
        
        # Test query performance with large dataset
        # Create test data
        test_activities = []
        for i in range(100):
            date = datetime(2025, 8, 1) + timedelta(days=i % 30)
            activity = RawActivityDB(
                date=date.strftime('%Y-%m-%d'),
                source='performance_test',
                details=f'Performance test activity {i}',
                duration_minutes=30 + (i % 60)
            )
            test_activities.append(activity)
        
        # Batch insert
        activity_ids = []
        for activity in test_activities:
            activity_ids.append(RawActivityDAO.create(activity))
        
        # Test indexed queries (should be fast even with more data)
        start_time = datetime.now()
        
        # Date range query (uses idx_raw_activities_date)
        results = RawActivityDAO.get_by_date_range('2025-08-01', '2025-08-31')
        
        query_time = datetime.now() - start_time
        
        self.assertGreater(len(results), 0, "Should find activities in date range")
        self.assertLess(query_time.total_seconds(), 1.0, "Query should be fast with indexes")

class TestDatabaseCLI(unittest.TestCase):
    """Test database CLI functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Set test database path
        os.environ['TEST_DATABASE_PATH'] = self.temp_db.name
        
        # Initialize database
        initialize_database(self.temp_db.name)
    
    def tearDown(self):
        """Clean up."""
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def test_cli_import(self):
        """Test that CLI module can be imported."""
        try:
            from src.backend.database import cli
            self.assertTrue(True, "CLI module should import successfully")
        except ImportError as e:
            self.fail(f"CLI module import failed: {e}")

def run_all_tests():
    """Run all database tests."""
    print("Running SmartHistory Database Tests")
    print("=" * 50)
    
    # Create test suite
    test_classes = [TestDatabaseIntegration, TestDatabaseCLI]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for test_class in test_classes:
        print(f"\n🧪 Running {test_class.__name__}")
        print("-" * 30)
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
    
    print(f"\n📊 Test Summary")
    print("=" * 50)
    print(f"Total Tests: {total_tests}")
    print(f"Failures: {total_failures}")
    print(f"Errors: {total_errors}")
    
    if total_failures == 0 and total_errors == 0:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
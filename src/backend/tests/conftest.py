"""
Pytest Configuration and Fixtures

Shared fixtures and configuration for SmartHistory backend tests.
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="function")
def test_database():
    """Create a temporary database for testing."""
    # Create temporary database file
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db_path = tmp_file.name
    
    # Set environment variable for test database
    original_db_path = os.environ.get('SMARTHISTORY_DB_PATH')
    os.environ['SMARTHISTORY_DB_PATH'] = test_db_path
    
    # Initialize test database
    try:
        from src.backend.database import get_db_manager
        db = get_db_manager()
        
        # Create some test data
        _setup_test_data(db)
        
        yield db
        
    finally:
        # Cleanup
        if original_db_path:
            os.environ['SMARTHISTORY_DB_PATH'] = original_db_path
        else:
            os.environ.pop('SMARTHISTORY_DB_PATH', None)
        
        # Clear database manager instances for proper test isolation
        from src.backend.database.core.database_manager import DatabaseManager
        DatabaseManager._instances.clear()
        
        # Remove test database file
        try:
            os.unlink(test_db_path)
        except OSError:
            pass


@pytest.fixture
def api_client(test_database):
    """Create a test client for the FastAPI app."""
    from fastapi.testclient import TestClient
    from src.backend.api import get_api_app
    
    # Set development environment to disable auth
    os.environ['SMARTHISTORY_ENV'] = 'development'
    
    app = get_api_app()
    client = TestClient(app)
    
    yield client
    
    # Cleanup
    os.environ.pop('SMARTHISTORY_ENV', None)


def _setup_test_data(db):
    """Set up test data in the database."""
    from src.backend.database import RawActivityDAO, ProcessedActivityDAO, TagDAO, ActivityTagDAO
    from src.backend.database import RawActivityDB, ProcessedActivityDB, TagDB, ActivityTagDB
    from datetime import datetime
    
    # Create test raw activities
    test_activities = [
        RawActivityDB(
            date="2025-08-31",
            time="09:00",
            duration_minutes=60,
            details="Team standup meeting",
            source="google_calendar",
            orig_link="https://calendar.google.com/test1",
            raw_data={"event_id": "test1", "summary": "Standup"}
        ),
        RawActivityDB(
            date="2025-08-31",
            time="10:30",
            duration_minutes=90,
            details="Code review session",
            source="notion",
            orig_link="",
            raw_data={"block_id": "test2", "hierarchy": ["Work", "Development"]}
        ),
        RawActivityDB(
            date="2025-08-30",
            time="14:00",
            duration_minutes=120,
            details="Client presentation",
            source="google_calendar",
            orig_link="https://calendar.google.com/test2",
            raw_data={"event_id": "test3", "summary": "Presentation"}
        )
    ]
    
    # Insert raw activities (use unique details to avoid conflicts)
    raw_activity_ids = []
    for i, activity in enumerate(test_activities):
        try:
            # Make details unique by adding timestamp
            import time
            activity.details = f"{activity.details} - Test {int(time.time() * 1000)}_{i}"
            activity_id = RawActivityDAO.create(activity)
            raw_activity_ids.append(activity_id)
        except Exception as e:
            # Skip if creation fails
            pass
    
    # Create test tags
    test_tags = [
        TagDB(name="meetings", description="Team meetings and standups", color="#4285f4"),
        TagDB(name="development", description="Software development work", color="#34a853"),
        TagDB(name="presentations", description="Client presentations", color="#ea4335")
    ]
    
    tag_ids = []
    for tag in test_tags:
        # Check if tag already exists first
        existing_tag = TagDAO.get_by_name(tag.name)
        if existing_tag:
            tag_ids.append(existing_tag.id)
        else:
            try:
                tag_id = TagDAO.create(tag)
                tag_ids.append(tag_id)
            except Exception as e:
                # If it fails, try to get existing tag again
                existing_tag = TagDAO.get_by_name(tag.name)
                if existing_tag:
                    tag_ids.append(existing_tag.id)
    
    # Create test processed activities
    if raw_activity_ids and tag_ids:
        try:
            processed_activity = ProcessedActivityDB(
                date="2025-08-31",
                time="09:00",
                total_duration_minutes=150,
                combined_details="Team standup meeting and code review session",
                raw_activity_ids=[raw_activity_ids[0], raw_activity_ids[1]],
                sources=["google_calendar", "notion"]
            )
            
            processed_id = ProcessedActivityDAO.create(processed_activity)
            
            # Add tags to processed activity
            if len(tag_ids) >= 2:
                for i, tag_id in enumerate(tag_ids[:2]):
                    activity_tag = ActivityTagDB(
                        processed_activity_id=processed_id,
                        tag_id=tag_id,
                        confidence_score=0.9 - (i * 0.1)
                    )
                    ActivityTagDAO.create(activity_tag)
                    
        except Exception as e:
            # Processed activity setup failed - non-critical for basic tests
            pass
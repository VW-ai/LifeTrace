"""
API Dependencies

Dependency injection for API services, providing singleton instances
and database connections for the FastAPI endpoints.
"""

import sys
from pathlib import Path
from functools import lru_cache

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.database import get_db_manager
from .services import ActivityService, TagService, InsightsService, ProcessingService, SystemService


@lru_cache()
def get_database_manager():
    """Get the database manager instance (cached)."""
    return get_db_manager()


@lru_cache()
def get_activity_service() -> ActivityService:
    """Get the activity service instance (cached)."""
    db_manager = get_database_manager()
    return ActivityService(db_manager)


@lru_cache()
def get_tag_service() -> TagService:
    """Get the tag service instance (cached)."""
    db_manager = get_database_manager()
    return TagService(db_manager)


@lru_cache()
def get_insights_service() -> InsightsService:
    """Get the insights service instance (cached)."""
    db_manager = get_database_manager()
    return InsightsService(db_manager)


@lru_cache()
def get_processing_service() -> ProcessingService:
    """Get the processing service instance (cached)."""
    db_manager = get_database_manager()
    return ProcessingService(db_manager)


@lru_cache()
def get_system_service() -> SystemService:
    """Get the system service instance (cached)."""
    db_manager = get_database_manager()
    return SystemService(db_manager)
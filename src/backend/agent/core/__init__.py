"""Core agent functionality."""

from .models import RawActivity, ProcessedActivity, TagGenerationContext
from .models import serialize_activities, serialize_processed_activities
from .models import deserialize_activities, deserialize_processed_activities
from .data_consumer import DataConsumer
from .activity_matcher import ActivityMatcher
from .activity_processor import ActivityProcessor
from .agent import load_api_key, run_daily_processing, run_insights_generation

__all__ = [
    'RawActivity', 'ProcessedActivity', 'TagGenerationContext',
    'serialize_activities', 'serialize_processed_activities',
    'deserialize_activities', 'deserialize_processed_activities',
    'DataConsumer', 'ActivityMatcher', 'ActivityProcessor',
    'load_api_key', 'run_daily_processing', 'run_insights_generation'
]
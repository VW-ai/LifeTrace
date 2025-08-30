"""
SmartHistory AI Agent - Intelligent Activity Processing

This module provides AI-powered activity processing capabilities including:
- Cross-source activity matching and correlation
- LLM-powered intelligent tagging
- Duration estimation and time tracking
- Data consolidation and analysis
"""

# Core functionality
from .core import (
    RawActivity, ProcessedActivity, TagGenerationContext,
    serialize_activities, serialize_processed_activities,
    deserialize_activities, deserialize_processed_activities,
    DataConsumer, ActivityMatcher, ActivityProcessor,
    load_api_key, run_daily_processing, run_insights_generation
)

# Tools
from .tools import TagGenerator

# Prompts
from .prompts import TagPrompts

__version__ = "1.0.0"

__all__ = [
    # Core models and data structures
    'RawActivity', 'ProcessedActivity', 'TagGenerationContext',
    
    # Serialization utilities
    'serialize_activities', 'serialize_processed_activities',
    'deserialize_activities', 'deserialize_processed_activities',
    
    # Core processing components
    'DataConsumer', 'ActivityMatcher', 'ActivityProcessor',
    
    # Tools and utilities
    'TagGenerator',
    
    # Prompts
    'TagPrompts',
    
    # Main entry points
    'load_api_key', 'run_daily_processing', 'run_insights_generation'
]
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import json

@dataclass
class RawActivity:
    """Raw activity data structure matching database schema."""
    date: str  # Date in YYYY-MM-DD format
    time: Optional[str] = None  # Time in HH:MM format or None
    duration_minutes: int = 0  # Duration in minutes
    details: str = ""  # Thorough summary of raw information
    source: str = ""  # e.g., "notion", "google_calendar"
    orig_link: str = ""  # Link pointing to original information
    
    # Additional metadata for processing
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'date': self.date,
            'time': self.time,
            'duration_minutes': self.duration_minutes,
            'details': self.details,
            'source': self.source,
            'orig_link': self.orig_link,
            'raw_data': self.raw_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RawActivity':
        """Create RawActivity from dictionary."""
        return cls(
            date=data['date'],
            time=data.get('time'),
            duration_minutes=data.get('duration_minutes', 0),
            details=data.get('details', ''),
            source=data.get('source', ''),
            orig_link=data.get('orig_link', ''),
            raw_data=data.get('raw_data', {})
        )

@dataclass 
class ProcessedActivity:
    """Processed activity data structure matching database schema."""
    date: str  # Date in YYYY-MM-DD format
    time: Optional[str] = None  # Time in HH:MM format or None
    raw_activity_ids: List[str] = field(default_factory=list)  # IDs of raw activities
    tags: List[str] = field(default_factory=list)  # Generated tags
    
    # Aggregated information
    total_duration_minutes: int = 0
    combined_details: str = ""
    sources: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'date': self.date,
            'time': self.time,
            'raw_activity_ids': self.raw_activity_ids,
            'tags': self.tags,
            'total_duration_minutes': self.total_duration_minutes,
            'combined_details': self.combined_details,
            'sources': self.sources
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessedActivity':
        """Create ProcessedActivity from dictionary."""
        return cls(
            date=data['date'],
            time=data.get('time'),
            raw_activity_ids=data.get('raw_activity_ids', []),
            tags=data.get('tags', []),
            total_duration_minutes=data.get('total_duration_minutes', 0),
            combined_details=data.get('combined_details', ''),
            sources=data.get('sources', [])
        )

@dataclass
class TagGenerationContext:
    """Context information for tag generation."""
    existing_tags: List[str] = field(default_factory=list)
    activity_text: str = ""
    source: str = ""
    duration_minutes: int = 0
    time_context: Optional[str] = None  # Time of day context
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'existing_tags': self.existing_tags,
            'activity_text': self.activity_text,
            'source': self.source,
            'duration_minutes': self.duration_minutes,
            'time_context': self.time_context
        }

def serialize_activities(activities: List[RawActivity], filepath: str) -> None:
    """Serialize list of activities to JSON file."""
    data = [activity.to_dict() for activity in activities]
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def deserialize_activities(filepath: str) -> List[RawActivity]:
    """Deserialize list of activities from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [RawActivity.from_dict(item) for item in data]

def serialize_processed_activities(activities: List[ProcessedActivity], filepath: str) -> None:
    """Serialize list of processed activities to JSON file."""
    data = [activity.to_dict() for activity in activities]
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def deserialize_processed_activities(filepath: str) -> List[ProcessedActivity]:
    """Deserialize list of processed activities from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [ProcessedActivity.from_dict(item) for item in data]
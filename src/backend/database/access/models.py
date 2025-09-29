#!/usr/bin/env python3
"""
Database Models and CRUD Operations for SmartHistory

Provides high-level database operations for all entities with validation,
error handling, and type safety.
"""

import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

from ..core.transaction_manager import DatabaseOperationError

def get_db_manager():
    """Get the default database manager instance."""
    from ..core.database_manager import DatabaseManager
    return DatabaseManager.get_instance()

logger = logging.getLogger(__name__)

class SessionStatus(Enum):
    """User session status enumeration."""
    STARTED = "started"
    COMPLETED = "completed" 
    FAILED = "failed"

class GenerationType(Enum):
    """Tag generation type enumeration."""
    SYSTEM_WIDE = "system_wide"
    INCREMENTAL = "incremental"
    MANUAL = "manual"

@dataclass
class RawActivityDB:
    """Raw activity database model with comprehensive validation.
    
    Represents an individual activity record from a data source before AI processing.
    Each raw activity corresponds to a single event or note from sources like Notion
    or Google Calendar, maintaining the original data for traceability.
    
    Attributes:
        id: Database-generated unique identifier (None for new records).
        date: Activity date in YYYY-MM-DD format (required).
        time: Activity time in HH:MM format (optional for all-day activities).
        duration_minutes: Activity duration in minutes (0 for unknown duration).
        details: Detailed description or content from the original source.
        source: Data source identifier (e.g., 'notion', 'google_calendar').
        orig_link: URL or identifier linking back to the original source.
        raw_data: Additional metadata stored as JSON (flexible schema).
        created_at: Timestamp when record was created (auto-populated).
        updated_at: Timestamp when record was last modified (auto-populated).
    """
    id: Optional[int] = None
    date: str = ""
    time: Optional[str] = None
    duration_minutes: int = 0
    details: str = ""
    source: str = ""
    orig_link: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def validate(self) -> bool:
        """Validate the raw activity data according to business rules.
        
        Ensures data integrity and consistency for database storage. Date and source
        are mandatory as they identify when and where the activity occurred.
        
        Returns:
            True if validation passes.
            
        Raises:
            ValueError: If any validation rule fails with specific error message.
        """
        # Core required fields for activity identification
        if not self.date:
            raise ValueError("Date is required")
        if not self.source:
            raise ValueError("Source is required")
            
        # Business logic: duration cannot be negative (unknown duration = 0)
        if self.duration_minutes < 0:
            raise ValueError("Duration cannot be negative")
        
        # Validate date format for database consistency (ISO 8601 date)
        try:
            datetime.strptime(self.date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        
        # Validate time format if provided (24-hour format for consistency)
        if self.time:
            try:
                datetime.strptime(self.time, '%H:%M')
            except ValueError:
                raise ValueError("Time must be in HH:MM format")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = asdict(self)
        data['raw_data'] = json.dumps(self.raw_data)
        return data

@dataclass  
class ProcessedActivityDB:
    """Processed activity database model with validation."""
    id: Optional[int] = None
    date: str = ""
    time: Optional[str] = None
    total_duration_minutes: int = 0
    combined_details: str = ""
    raw_activity_ids: List[int] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def validate(self) -> bool:
        """Validate the processed activity data."""
        if not self.date:
            raise ValueError("Date is required")
        if self.total_duration_minutes < 0:
            raise ValueError("Duration cannot be negative")
        if not self.raw_activity_ids:
            raise ValueError("At least one raw activity ID is required")
        
        # Validate date format
        try:
            datetime.strptime(self.date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        
        # Validate time format if provided
        if self.time:
            try:
                datetime.strptime(self.time, '%H:%M')
            except ValueError:
                raise ValueError("Time must be in HH:MM format")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = asdict(self)
        data['raw_activity_ids'] = json.dumps(self.raw_activity_ids)
        data['sources'] = json.dumps(self.sources)
        return data

@dataclass
class TagDB:
    """Tag database model with validation."""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    color: Optional[str] = None
    usage_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def validate(self) -> bool:
        """Validate the tag data."""
        if not self.name:
            raise ValueError("Tag name is required")
        if len(self.name) > 100:
            raise ValueError("Tag name cannot exceed 100 characters")
        if self.usage_count < 0:
            raise ValueError("Usage count cannot be negative")
        
        # Validate color format if provided (hex color)
        if self.color:
            if not (self.color.startswith('#') and len(self.color) in [4, 7]):
                raise ValueError("Color must be a valid hex color code")
        
        return True

@dataclass
class ActivityTagDB:
    """Activity-Tag relationship model."""
    id: Optional[int] = None
    processed_activity_id: int = 0
    tag_id: int = 0
    confidence_score: float = 1.0
    created_at: Optional[datetime] = None
    
    def validate(self) -> bool:
        """Validate the activity-tag relationship."""
        if not self.processed_activity_id:
            raise ValueError("Processed activity ID is required")
        if not self.tag_id:
            raise ValueError("Tag ID is required")
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("Confidence score must be between 0 and 1")
        return True

@dataclass
class UserSessionDB:
    """User session database model."""
    id: Optional[int] = None
    session_type: str = ""
    status: SessionStatus = SessionStatus.STARTED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    processed_raw_count: int = 0
    processed_activity_count: int = 0
    tags_generated: int = 0
    
    def validate(self) -> bool:
        """Validate the user session data."""
        if not self.session_type:
            raise ValueError("Session type is required")
        if self.processed_raw_count < 0:
            raise ValueError("Processed raw count cannot be negative")
        if self.processed_activity_count < 0:
            raise ValueError("Processed activity count cannot be negative")
        if self.tags_generated < 0:
            raise ValueError("Tags generated cannot be negative")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = asdict(self)
        data['status'] = self.status.value
        data['metadata'] = json.dumps(self.metadata)
        return data

@dataclass
class TagGenerationDB:
    """Tag generation history model."""
    id: Optional[int] = None
    generation_type: GenerationType = GenerationType.INCREMENTAL
    trigger_reason: Optional[str] = None
    total_activities: int = 0
    tags_created: int = 0
    tags_updated: int = 0
    tag_event_ratio: Optional[float] = None
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate the tag generation data."""
        if self.total_activities < 0:
            raise ValueError("Total activities cannot be negative")
        if self.tags_created < 0:
            raise ValueError("Tags created cannot be negative") 
        if self.tags_updated < 0:
            raise ValueError("Tags updated cannot be negative")
        if self.tag_event_ratio is not None and self.tag_event_ratio < 0:
            raise ValueError("Tag event ratio cannot be negative")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = asdict(self)
        data['generation_type'] = self.generation_type.value
        data['metadata'] = json.dumps(self.metadata)
        return data

class RawActivityDAO:
    """Data Access Object for raw activities following Google Python Style.
    
    Provides CRUD operations for raw activity records with comprehensive validation,
    error handling, and type safety. Raw activities represent individual activity
    records from different data sources (Notion, Google Calendar, etc.) before
    AI processing and aggregation.
    
    All methods are static to follow the DAO pattern and avoid state management.
    """
    
    @staticmethod
    def create(activity: RawActivityDB) -> int:
        """Create a new raw activity record in the database.
        
        Validates the activity data before insertion and ensures all required
        fields are present. The activity source and date are mandatory fields
        that identify where and when the activity occurred.
        
        Args:
            activity: Raw activity model with all required data fields.
            
        Returns:
            The database-generated unique ID for the created activity.
            
        Raises:
            ValueError: If activity validation fails (missing required fields, 
                       invalid date/time format, negative duration, etc.).
            DatabaseOperationError: If database insertion fails.
        """
        activity.validate()
        
        query = """
        INSERT INTO raw_activities 
        (date, time, duration_minutes, details, source, orig_link, raw_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            activity.date,
            activity.time,
            activity.duration_minutes,
            activity.details,
            activity.source,
            activity.orig_link,
            json.dumps(activity.raw_data)
        )
        
        db = get_db_manager()
        return db.execute_insert(query, params)
    
    @staticmethod
    def get_by_id(activity_id: int) -> Optional[RawActivityDB]:
        """Get raw activity by ID."""
        query = "SELECT * FROM raw_activities WHERE id = ?"
        
        db = get_db_manager()
        results = db.execute_query(query, (activity_id,))
        
        if not results:
            return None
        
        row = results[0]
        return RawActivityDAO._row_to_model(row)
    
    @staticmethod
    def get_by_date_range(start_date: str, end_date: str, 
                         source: Optional[str] = None) -> List[RawActivityDB]:
        """Get raw activities within a date range."""
        query = "SELECT * FROM raw_activities WHERE date >= ? AND date <= ?"
        params = [start_date, end_date]
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        query += " ORDER BY date, time"
        
        db = get_db_manager()
        results = db.execute_query(query, tuple(params))
        
        return [RawActivityDAO._row_to_model(row) for row in results]
    
    @staticmethod
    def update(activity: RawActivityDB) -> bool:
        """Update an existing raw activity."""
        if not activity.id:
            raise ValueError("Activity ID is required for update")
        
        activity.validate()
        
        query = """
        UPDATE raw_activities 
        SET date=?, time=?, duration_minutes=?, details=?, 
            source=?, orig_link=?, raw_data=?
        WHERE id=?
        """
        
        params = (
            activity.date,
            activity.time,
            activity.duration_minutes,
            activity.details,
            activity.source,
            activity.orig_link,
            json.dumps(activity.raw_data),
            activity.id
        )
        
        db = get_db_manager()
        affected = db.execute_update(query, params)
        return affected > 0
    
    @staticmethod
    def delete(activity_id: int) -> bool:
        """Delete a raw activity."""
        query = "DELETE FROM raw_activities WHERE id = ?"
        
        db = get_db_manager()
        affected = db.execute_update(query, (activity_id,))
        return affected > 0
    
    @staticmethod
    def get_all(limit: Optional[int] = None, offset: int = 0) -> List[RawActivityDB]:
        """Get all raw activities with optional pagination."""
        query = "SELECT * FROM raw_activities ORDER BY date DESC, created_at DESC"
        
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        db = get_db_manager()
        results = db.execute_query(query)
        
        return [RawActivityDAO._row_to_model(row) for row in results]
    
    @staticmethod
    def _row_to_model(row) -> RawActivityDB:
        """Convert database row to RawActivityDB model."""
        return RawActivityDB(
            id=row['id'],
            date=row['date'],
            time=row['time'],
            duration_minutes=row['duration_minutes'],
            details=row['details'],
            source=row['source'],
            orig_link=row['orig_link'],
            raw_data=json.loads(row['raw_data']) if row['raw_data'] else {},
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

class ProcessedActivityDAO:
    """Data Access Object for processed activities."""
    
    @staticmethod
    def create(activity: ProcessedActivityDB) -> int:
        """Create a new processed activity."""
        activity.validate()
        
        query = """
        INSERT INTO processed_activities 
        (date, time, total_duration_minutes, combined_details, raw_activity_ids, sources)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        params = (
            activity.date,
            activity.time,
            activity.total_duration_minutes,
            activity.combined_details,
            json.dumps(activity.raw_activity_ids),
            json.dumps(activity.sources)
        )
        
        db = get_db_manager()
        return db.execute_insert(query, params)
    
    @staticmethod
    def get_by_id(activity_id: int) -> Optional[ProcessedActivityDB]:
        """Get processed activity by ID."""
        query = "SELECT * FROM processed_activities WHERE id = ?"
        
        db = get_db_manager()
        results = db.execute_query(query, (activity_id,))
        
        if not results:
            return None
        
        return ProcessedActivityDAO._row_to_model(results[0])
    
    @staticmethod
    def get_with_tags(activity_id: int) -> Optional[Tuple[ProcessedActivityDB, List[TagDB]]]:
        """Get processed activity with its tags."""
        query = """
        SELECT pa.*, t.id as tag_id, t.name as tag_name, t.description as tag_description,
               t.color as tag_color, t.usage_count as tag_usage_count,
               at.confidence_score
        FROM processed_activities pa
        LEFT JOIN activity_tags at ON pa.id = at.processed_activity_id
        LEFT JOIN tags t ON at.tag_id = t.id
        WHERE pa.id = ?
        """
        
        db = get_db_manager()
        results = db.execute_query(query, (activity_id,))
        
        if not results:
            return None
        
        # Build activity and tags from joined results
        activity = None
        tags = []
        
        for row in results:
            if activity is None:
                activity = ProcessedActivityDAO._row_to_model(row)
            
            if row['tag_id']:
                tag = TagDB(
                    id=row['tag_id'],
                    name=row['tag_name'],
                    description=row['tag_description'],
                    color=row['tag_color'],
                    usage_count=row['tag_usage_count']
                )
                tags.append(tag)
        
        return activity, tags
    
    @staticmethod
    def update(activity: ProcessedActivityDB) -> bool:
        """Update an existing processed activity."""
        if not activity.id:
            raise ValueError("Activity ID is required for update")
        
        activity.validate()
        
        query = """
        UPDATE processed_activities 
        SET date=?, time=?, total_duration_minutes=?, combined_details=?,
            raw_activity_ids=?, sources=?
        WHERE id=?
        """
        
        params = (
            activity.date,
            activity.time,
            activity.total_duration_minutes,
            activity.combined_details,
            json.dumps(activity.raw_activity_ids),
            json.dumps(activity.sources),
            activity.id
        )
        
        db = get_db_manager()
        affected = db.execute_update(query, params)
        return affected > 0
    
    @staticmethod
    def delete(activity_id: int) -> bool:
        """Delete a processed activity and its tags."""
        # Note: activity_tags will be deleted automatically due to CASCADE
        query = "DELETE FROM processed_activities WHERE id = ?"
        
        db = get_db_manager()
        affected = db.execute_update(query, (activity_id,))
        return affected > 0
    
    @staticmethod
    def _row_to_model(row) -> ProcessedActivityDB:
        """Convert database row to ProcessedActivityDB model."""
        return ProcessedActivityDB(
            id=row['id'],
            date=row['date'],
            time=row['time'],
            total_duration_minutes=row['total_duration_minutes'],
            combined_details=row['combined_details'],
            raw_activity_ids=json.loads(row['raw_activity_ids']) if row['raw_activity_ids'] else [],
            sources=json.loads(row['sources']) if row['sources'] else [],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

class TagDAO:
    """Data Access Object for tags."""
    
    @staticmethod
    def create(tag: TagDB) -> int:
        """Create a new tag."""
        tag.validate()
        
        query = """
        INSERT INTO tags (name, description, color, usage_count)
        VALUES (?, ?, ?, ?)
        """
        
        params = (tag.name, tag.description, tag.color, tag.usage_count)
        
        db = get_db_manager()
        try:
            return db.execute_insert(query, params)
        except DatabaseOperationError as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError(f"Tag '{tag.name}' already exists")
            raise
    
    @staticmethod
    def get_by_id(tag_id: int) -> Optional[TagDB]:
        """Get tag by ID."""
        query = "SELECT * FROM tags WHERE id = ?"
        
        db = get_db_manager()
        results = db.execute_query(query, (tag_id,))
        
        if not results:
            return None
        
        return TagDAO._row_to_model(results[0])
    
    @staticmethod
    def get_by_name(name: str) -> Optional[TagDB]:
        """Get tag by name."""
        query = "SELECT * FROM tags WHERE name = ?"
        
        db = get_db_manager()
        results = db.execute_query(query, (name,))
        
        if not results:
            return None
        
        return TagDAO._row_to_model(results[0])
    
    @staticmethod
    def get_all() -> List[TagDB]:
        """Get all tags ordered by usage count."""
        query = "SELECT * FROM tags ORDER BY usage_count DESC, name"
        
        db = get_db_manager()
        results = db.execute_query(query)
        
        return [TagDAO._row_to_model(row) for row in results]
    
    @staticmethod
    def update(tag: TagDB) -> bool:
        """Update an existing tag."""
        if not tag.id:
            raise ValueError("Tag ID is required for update")
        
        tag.validate()
        
        query = """
        UPDATE tags 
        SET name=?, description=?, color=?, usage_count=?
        WHERE id=?
        """
        
        params = (tag.name, tag.description, tag.color, tag.usage_count, tag.id)
        
        db = get_db_manager()
        try:
            affected = db.execute_update(query, params)
            return affected > 0
        except DatabaseOperationError as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError(f"Tag '{tag.name}' already exists")
            raise
    
    @staticmethod
    def delete(tag_id: int) -> bool:
        """Delete a tag and its activity relationships."""
        # Note: activity_tags will be deleted automatically due to CASCADE
        query = "DELETE FROM tags WHERE id = ?"
        
        db = get_db_manager()
        affected = db.execute_update(query, (tag_id,))
        return affected > 0
    
    @staticmethod
    def _row_to_model(row) -> TagDB:
        """Convert database row to TagDB model."""
        return TagDB(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            color=row['color'],
            usage_count=row['usage_count'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

class ActivityTagDAO:
    """Data Access Object for activity-tag relationships."""
    
    @staticmethod
    def create(activity_tag: ActivityTagDB) -> int:
        """Create a new activity-tag relationship."""
        activity_tag.validate()
        
        query = """
        INSERT INTO activity_tags (processed_activity_id, tag_id, confidence_score)
        VALUES (?, ?, ?)
        """
        
        params = (
            activity_tag.processed_activity_id,
            activity_tag.tag_id,
            activity_tag.confidence_score
        )
        
        db = get_db_manager()
        try:
            return db.execute_insert(query, params)
        except DatabaseOperationError as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("Activity-tag relationship already exists")
            raise
    
    @staticmethod
    def get_tags_for_activity(activity_id: int) -> List[Tuple[TagDB, float]]:
        """Get all tags for a processed activity with confidence scores."""
        query = """
        SELECT t.*, at.confidence_score
        FROM tags t
        JOIN activity_tags at ON t.id = at.tag_id
        WHERE at.processed_activity_id = ?
        ORDER BY at.confidence_score DESC
        """
        
        db = get_db_manager()
        results = db.execute_query(query, (activity_id,))
        
        return [(TagDAO._row_to_model(row), row['confidence_score']) for row in results]
    
    @staticmethod
    def get_activities_for_tag(tag_id: int) -> List[Tuple[ProcessedActivityDB, float]]:
        """Get all activities for a tag with confidence scores."""
        query = """
        SELECT pa.*, at.confidence_score
        FROM processed_activities pa
        JOIN activity_tags at ON pa.id = at.processed_activity_id
        WHERE at.tag_id = ?
        ORDER BY pa.date DESC
        """
        
        db = get_db_manager()
        results = db.execute_query(query, (tag_id,))
        
        return [(ProcessedActivityDAO._row_to_model(row), row['confidence_score']) 
                for row in results]
    
    @staticmethod
    def update_confidence(activity_id: int, tag_id: int, confidence: float) -> bool:
        """Update confidence score for an activity-tag relationship."""
        if not (0.0 <= confidence <= 1.0):
            raise ValueError("Confidence score must be between 0 and 1")
        
        query = """
        UPDATE activity_tags 
        SET confidence_score = ?
        WHERE processed_activity_id = ? AND tag_id = ?
        """
        
        db = get_db_manager()
        affected = db.execute_update(query, (confidence, activity_id, tag_id))
        return affected > 0
    
    @staticmethod
    def delete(activity_id: int, tag_id: int) -> bool:
        """Delete an activity-tag relationship."""
        query = """
        DELETE FROM activity_tags 
        WHERE processed_activity_id = ? AND tag_id = ?
        """
        
        db = get_db_manager()
        affected = db.execute_update(query, (activity_id, tag_id))
        return affected > 0
    
    @staticmethod
    def delete_by_tag_id(tag_id: int) -> int:
        """Delete all activity-tag relationships for a specific tag."""
        query = "DELETE FROM activity_tags WHERE tag_id = ?"
        
        db = get_db_manager()
        affected = db.execute_update(query, (tag_id,))
        return affected
    
    @staticmethod
    def get_by_processed_activity_id(processed_activity_id: int) -> List['ActivityTagDB']:
        """Get all activity-tag relationships for a processed activity."""
        query = """
        SELECT * FROM activity_tags 
        WHERE processed_activity_id = ?
        ORDER BY confidence_score DESC
        """
        
        db = get_db_manager()
        results = db.execute_query(query, (processed_activity_id,))
        return [ActivityTagDAO._row_to_model(row) for row in results]
    
    @staticmethod
    def _row_to_model(row) -> 'ActivityTagDB':
        """Convert database row to ActivityTagDB model."""
        return ActivityTagDB(
            id=row.get('id'),
            processed_activity_id=row['processed_activity_id'],
            tag_id=row['tag_id'],
            confidence_score=row['confidence_score'],
            created_at=datetime.fromisoformat(row['created_at']) if row.get('created_at') else datetime.now()
        )

class UserSessionDAO:
    """Data Access Object for user sessions."""
    
    @staticmethod
    def create(session: UserSessionDB) -> int:
        """Create a new user session."""
        session.validate()
        
        query = """
        INSERT INTO user_sessions 
        (session_type, status, metadata, processed_raw_count, 
         processed_activity_count, tags_generated)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        params = (
            session.session_type,
            session.status.value,
            json.dumps(session.metadata),
            session.processed_raw_count,
            session.processed_activity_count,
            session.tags_generated
        )
        
        db = get_db_manager()
        return db.execute_insert(query, params)
    
    @staticmethod
    def update_status(session_id: int, status: SessionStatus, 
                     error_message: Optional[str] = None) -> bool:
        """Update session status and end time."""
        query = """
        UPDATE user_sessions 
        SET status = ?, end_time = CURRENT_TIMESTAMP, error_message = ?
        WHERE id = ?
        """
        
        db = get_db_manager()
        affected = db.execute_update(query, (status.value, error_message, session_id))
        return affected > 0
    
    @staticmethod
    def get_recent_sessions(limit: int = 10) -> List[UserSessionDB]:
        """Get recent user sessions."""
        query = """
        SELECT * FROM user_sessions 
        ORDER BY start_time DESC 
        LIMIT ?
        """
        
        db = get_db_manager()
        results = db.execute_query(query, (limit,))
        
        return [UserSessionDAO._row_to_model(row) for row in results]
    
    @staticmethod
    def _row_to_model(row) -> UserSessionDB:
        """Convert database row to UserSessionDB model."""
        return UserSessionDB(
            id=row['id'],
            session_type=row['session_type'],
            status=SessionStatus(row['status']),
            start_time=row['start_time'],
            end_time=row['end_time'],
            metadata=json.loads(row['metadata']) if row['metadata'] else {},
            error_message=row['error_message'],
            processed_raw_count=row['processed_raw_count'],
            processed_activity_count=row['processed_activity_count'],
            tags_generated=row['tags_generated']
        )

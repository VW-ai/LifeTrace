"""
API Services

Business logic layer for the SmartHistory API, handling database operations
and data transformation between internal models and API responses.
"""

import os
import sys
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.database import (
    RawActivityDAO, ProcessedActivityDAO, TagDAO, ActivityTagDAO,
    RawActivityDB, ProcessedActivityDB, TagDB, ActivityTagDB
)
from src.backend.agent.core.activity_processor import ActivityProcessor
from .models import *


class ActivityService:
    """Service for activity-related operations."""
    
    def __init__(self, db_manager):
        self.db = db_manager
        
    async def get_raw_activities(self, source: Optional[str] = None, 
                               date_start: Optional[str] = None,
                               date_end: Optional[str] = None,
                               limit: int = 100, offset: int = 0) -> PaginatedActivitiesResponse:
        """Get raw activities with filtering and pagination."""
        
        # Build query conditions
        conditions = []
        params = []
        
        if source:
            conditions.append("source = ?")
            params.append(source)
            
        if date_start:
            conditions.append("date >= ?")
            params.append(date_start)
            
        if date_end:
            conditions.append("date <= ?")
            params.append(date_end)
        
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        
        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM raw_activities {where_clause}"
        count_result = self.db.execute_query(count_query, params)
        total_count = count_result[0]['count'] if count_result else 0
        
        # Get activities
        query = f"""
            SELECT * FROM raw_activities {where_clause}
            ORDER BY date DESC, time DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        results = self.db.execute_query(query, params)
        
        # Convert to response models
        activities = []
        for row in results:
            # Parse raw_data if it's a JSON string
            raw_data = row['raw_data'] or {}
            if isinstance(raw_data, str):
                try:
                    import json
                    raw_data = json.loads(raw_data)
                except (json.JSONDecodeError, TypeError):
                    raw_data = {}
            
            activity = RawActivityResponse(
                id=row['id'],
                date=row['date'],
                time=row['time'],
                duration_minutes=row['duration_minutes'],
                details=row['details'],
                source=row['source'],
                orig_link=row['orig_link'],
                raw_data=raw_data,
                created_at=datetime.fromisoformat(row['created_at'])
            )
            activities.append(activity)
        
        return PaginatedActivitiesResponse(
            activities=activities,
            total_count=total_count,
            page_info=PageInfo(
                limit=limit,
                offset=offset,
                has_more=(offset + limit) < total_count
            )
        )
    
    async def get_processed_activities(self, date_start: Optional[str] = None,
                                     date_end: Optional[str] = None,
                                     tags: Optional[List[str]] = None,
                                     limit: int = 100, offset: int = 0) -> PaginatedProcessedActivitiesResponse:
        """Get processed activities with filtering and pagination."""
        
        conditions = []
        params = []
        
        if date_start:
            conditions.append("pa.date >= ?")
            params.append(date_start)
            
        if date_end:
            conditions.append("pa.date <= ?")
            params.append(date_end)
        
        # Handle tag filtering
        tag_join = ""
        if tags:
            tag_placeholders = ",".join(["?" for _ in tags])
            tag_join = f"""
                INNER JOIN activity_tags at ON pa.id = at.processed_activity_id
                INNER JOIN tags t ON at.tag_id = t.id
                WHERE t.name IN ({tag_placeholders})
            """
            params.extend(tags)
            
            if conditions:
                tag_join = tag_join.replace("WHERE", "AND")
        
        base_conditions = ""
        if conditions and not tag_join:
            base_conditions = "WHERE " + " AND ".join(conditions)
        elif conditions and tag_join:
            base_conditions = " AND " + " AND ".join(conditions)
        
        # Get total count
        count_query = f"""
            SELECT COUNT(DISTINCT pa.id) as count 
            FROM processed_activities pa {tag_join} {base_conditions}
        """
        count_result = self.db.execute_query(count_query, params)
        total_count = count_result[0]['count'] if count_result else 0
        
        # Get activities
        query = f"""
            SELECT DISTINCT pa.* FROM processed_activities pa 
            {tag_join} {base_conditions}
            ORDER BY pa.date DESC, pa.time DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        results = self.db.execute_query(query, params)
        
        # Convert to response models with tags
        activities = []
        for row in results:
            # Get tags for this activity
            tag_query = """
                SELECT t.*, at.confidence_score
                FROM tags t
                INNER JOIN activity_tags at ON t.id = at.tag_id
                WHERE at.processed_activity_id = ?
                ORDER BY at.confidence_score DESC
            """
            tag_results = self.db.execute_query(tag_query, [row['id']])
            
            activity_tags = []
            for tag_row in tag_results:
                tag = TagResponse(
                    id=tag_row['id'],
                    name=tag_row['name'],
                    description=tag_row['description'],
                    color=tag_row['color'],
                    usage_count=tag_row['usage_count'],
                    confidence=tag_row['confidence_score'],
                    created_at=datetime.fromisoformat(tag_row['created_at']),
                    updated_at=datetime.fromisoformat(tag_row['updated_at'])
                )
                activity_tags.append(tag)
            
            # Parse JSON fields that are stored as strings
            sources = row['sources'] or []
            if isinstance(sources, str):
                try:
                    import json
                    sources = json.loads(sources)
                except (json.JSONDecodeError, TypeError):
                    sources = []
            
            raw_activity_ids = row['raw_activity_ids'] or []
            if isinstance(raw_activity_ids, str):
                try:
                    import json
                    raw_activity_ids = json.loads(raw_activity_ids)
                except (json.JSONDecodeError, TypeError):
                    raw_activity_ids = []
            
            activity = ProcessedActivityResponse(
                id=row['id'],
                date=row['date'],
                time=row['time'],
                total_duration_minutes=row['total_duration_minutes'],
                combined_details=row['combined_details'],
                sources=sources,
                tags=activity_tags,
                raw_activity_ids=raw_activity_ids,
                created_at=datetime.fromisoformat(row['created_at'])
            )
            activities.append(activity)
        
        return PaginatedProcessedActivitiesResponse(
            activities=activities,
            total_count=total_count,
            page_info=PageInfo(
                limit=limit,
                offset=offset,
                has_more=(offset + limit) < total_count
            )
        )


class TagService:
    """Service for tag-related operations."""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    async def get_tags(self, sort_by: str = 'usage_count', 
                      limit: int = 100, offset: int = 0) -> PaginatedTagsResponse:
        """Get tags with sorting and pagination."""
        
        # Validate sort field
        sort_field = {
            'name': 'name',
            'usage_count': 'usage_count DESC',
            'created_at': 'created_at DESC'
        }.get(sort_by, 'usage_count DESC')
        
        # Get total count
        count_query = "SELECT COUNT(*) as count FROM tags"
        count_result = self.db.execute_query(count_query)
        total_count = count_result[0]['count'] if count_result else 0
        
        # Get tags
        query = f"""
            SELECT * FROM tags 
            ORDER BY {sort_field}
            LIMIT ? OFFSET ?
        """
        results = self.db.execute_query(query, [limit, offset])
        
        # Convert to response models
        tags = []
        for row in results:
            tag = TagResponse(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                color=row['color'],
                usage_count=row['usage_count'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )
            tags.append(tag)
        
        return PaginatedTagsResponse(
            tags=tags,
            total_count=total_count,
            page_info=PageInfo(
                limit=limit,
                offset=offset,
                has_more=(offset + limit) < total_count
            )
        )
    
    async def get_tag_by_id(self, tag_id: int) -> Optional[TagResponse]:
        """Get a specific tag by ID."""
        tag_db = TagDAO.get_by_id(tag_id)
        if not tag_db:
            return None
        
        return TagResponse(
            id=tag_db.id,
            name=tag_db.name,
            description=tag_db.description,
            color=tag_db.color,
            usage_count=tag_db.usage_count,
            created_at=tag_db.created_at,
            updated_at=tag_db.updated_at
        )
    
    async def create_tag(self, tag_data: TagCreateRequest) -> TagResponse:
        """Create a new tag."""
        # Check if tag already exists
        existing = TagDAO.get_by_name(tag_data.name)
        if existing:
            from fastapi import HTTPException
            raise HTTPException(status_code=409, detail=f"Tag '{tag_data.name}' already exists")
        
        # Create new tag
        tag_db = TagDB(
            name=tag_data.name,
            description=tag_data.description,
            color=tag_data.color,
            usage_count=0
        )
        
        tag_id = TagDAO.create(tag_db)
        created_tag = TagDAO.get_by_id(tag_id)
        
        return TagResponse(
            id=created_tag.id,
            name=created_tag.name,
            description=created_tag.description,
            color=created_tag.color,
            usage_count=created_tag.usage_count,
            created_at=created_tag.created_at,
            updated_at=created_tag.updated_at
        )
    
    async def update_tag(self, tag_id: int, tag_data: TagUpdateRequest) -> Optional[TagResponse]:
        """Update an existing tag."""
        existing = TagDAO.get_by_id(tag_id)
        if not existing:
            return None
        
        # Check name collision
        name_check = TagDAO.get_by_name(tag_data.name)
        if name_check and name_check.id != tag_id:
            raise ValueError(f"Tag '{tag_data.name}' already exists")
        
        # Update tag
        existing.name = tag_data.name
        existing.description = tag_data.description
        existing.color = tag_data.color
        existing.updated_at = datetime.now()
        
        TagDAO.update(existing)
        updated_tag = TagDAO.get_by_id(tag_id)
        
        return TagResponse(
            id=updated_tag.id,
            name=updated_tag.name,
            description=updated_tag.description,
            color=updated_tag.color,
            usage_count=updated_tag.usage_count,
            created_at=updated_tag.created_at,
            updated_at=updated_tag.updated_at
        )
    
    async def delete_tag(self, tag_id: int) -> bool:
        """Delete a tag."""
        existing = TagDAO.get_by_id(tag_id)
        if not existing:
            return False
        
        # Delete associated activity_tags first
        ActivityTagDAO.delete_by_tag_id(tag_id)
        
        # Delete the tag
        TagDAO.delete(tag_id)
        return True


class InsightsService:
    """Service for insights and analytics operations."""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.processor = ActivityProcessor()
    
    async def get_overview(self, date_start: Optional[str] = None, 
                          date_end: Optional[str] = None) -> InsightsOverviewResponse:
        """Get activity insights overview."""
        
        # Get processed activities for the date range
        activities = await self._get_processed_activities_for_insights(date_start, date_end)
        
        if not activities:
            # Return empty insights
            today = datetime.now().strftime('%Y-%m-%d')
            return InsightsOverviewResponse(
                total_tracked_hours=0.0,
                activity_count=0,
                unique_tags=0,
                tag_time_distribution={},
                tag_percentages={},
                top_5_activities=[],
                date_range=DateRange(start=today, end=today)
            )
        
        # Use the existing insights logic from ActivityProcessor
        insights_data = self.processor.get_activity_insights(activities)
        
        # Determine date range
        dates = [a.date for a in activities if a.date]
        dates.sort()
        date_range = DateRange(
            start=dates[0] if dates else date_start or datetime.now().strftime('%Y-%m-%d'),
            end=dates[-1] if dates else date_end or datetime.now().strftime('%Y-%m-%d')
        )
        
        return InsightsOverviewResponse(
            total_tracked_hours=insights_data['total_tracked_hours'],
            activity_count=insights_data['activity_count'],
            unique_tags=insights_data['unique_tags'],
            tag_time_distribution=insights_data['tag_time_distribution'],
            tag_percentages=insights_data['tag_percentages'],
            top_5_activities=[
                TopActivity(tag=item['tag'], hours=item['hours']) 
                for item in insights_data['top_5_activities']
            ],
            date_range=date_range
        )
    
    async def get_time_distribution(self, date_start: Optional[str] = None,
                                   date_end: Optional[str] = None,
                                   group_by: str = 'day') -> TimeDistributionResponse:
        """Get time distribution analysis."""
        
        # Get processed activities for the date range
        activities = await self._get_processed_activities_for_insights(date_start, date_end)
        
        if not activities:
            return TimeDistributionResponse(
                time_series=[],
                summary=TimeDistributionSummary(
                    total_period_hours=0.0,
                    average_daily_hours=0.0,
                    most_productive_day=datetime.now().strftime('%Y-%m-%d')
                )
            )
        
        # Group activities by time period
        time_groups = {}
        total_minutes = 0
        
        for activity in activities:
            # Group key based on group_by parameter
            if group_by == 'day':
                key = activity.date
            elif group_by == 'week':
                date_obj = datetime.strptime(activity.date, '%Y-%m-%d')
                week_start = date_obj - timedelta(days=date_obj.weekday())
                key = week_start.strftime('%Y-%m-%d')
            elif group_by == 'month':
                key = activity.date[:7] + '-01'  # First day of month
            else:
                key = activity.date
            
            if key not in time_groups:
                time_groups[key] = {'total': 0, 'tags': {}}
            
            time_groups[key]['total'] += activity.total_duration_minutes
            total_minutes += activity.total_duration_minutes
            
            # Track by tags
            for tag in activity.tags:
                if tag not in time_groups[key]['tags']:
                    time_groups[key]['tags'][tag] = 0
                time_groups[key]['tags'][tag] += activity.total_duration_minutes
        
        # Create time series
        time_series = []
        daily_totals = []
        
        for date, data in sorted(time_groups.items()):
            time_series.append(TimeSeriesPoint(
                date=date,
                total_minutes=data['total'],
                tag_breakdown=data['tags']
            ))
            daily_totals.append(data['total'])
        
        # Calculate summary
        avg_daily_minutes = sum(daily_totals) / len(daily_totals) if daily_totals else 0
        most_productive_day = max(time_groups.keys(), key=lambda k: time_groups[k]['total']) if time_groups else datetime.now().strftime('%Y-%m-%d')
        
        return TimeDistributionResponse(
            time_series=time_series,
            summary=TimeDistributionSummary(
                total_period_hours=round(total_minutes / 60, 2),
                average_daily_hours=round(avg_daily_minutes / 60, 2),
                most_productive_day=most_productive_day
            )
        )
    
    async def _get_processed_activities_for_insights(self, date_start: Optional[str], 
                                                   date_end: Optional[str]):
        """Helper to get processed activities for insights."""
        from src.backend.agent.core.models import ProcessedActivity
        
        # Get processed activities from database
        conditions = []
        params = []
        
        if date_start:
            conditions.append("date >= ?")
            params.append(date_start)
        
        if date_end:
            conditions.append("date <= ?")
            params.append(date_end)
        
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        
        query = f"SELECT * FROM processed_activities {where_clause}"
        results = self.db.execute_query(query, params)
        
        # Convert to agent models
        activities = []
        for row in results:
            # Get tags for this activity
            tag_query = """
                SELECT t.name FROM tags t
                INNER JOIN activity_tags at ON t.id = at.tag_id
                WHERE at.processed_activity_id = ?
            """
            tag_results = self.db.execute_query(tag_query, [row['id']])
            tags = [tag_row['name'] for tag_row in tag_results]
            
            activity = ProcessedActivity(
                date=row['date'],
                time=row['time'],
                raw_activity_ids=row['raw_activity_ids'],
                tags=tags,
                total_duration_minutes=row['total_duration_minutes'],
                combined_details=row['combined_details'],
                sources=row['sources']
            )
            activities.append(activity)
        
        return activities


class ProcessingService:
    """Service for processing and import operations."""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._processing_jobs = {}  # In-memory job tracking (TODO: move to database)
    
    async def trigger_daily_processing(self, request: ProcessingRequest) -> ProcessingResponse:
        """Trigger daily activity processing."""
        job_id = f"proc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        # Create processing job status
        job_status = ProcessingStatus(
            job_id=job_id,
            status="running",
            started_at=datetime.now()
        )
        self._processing_jobs[job_id] = job_status
        
        try:
            # Run the processing
            processor = ActivityProcessor()
            report = processor.process_daily_activities(use_database=request.use_database)
            
            # Update job status
            job_status.status = "completed"
            job_status.completed_at = datetime.now()
            job_status.progress = 1.0
            
            return ProcessingResponse(
                status="success",
                job_id=job_id,
                processed_counts=ProcessingCounts(
                    raw_activities=report['processed_counts']['raw_activities'],
                    processed_activities=report['processed_counts']['processed_activities']
                ),
                tag_analysis=TagAnalysis(
                    total_unique_tags=report['tag_analysis']['total_unique_tags'],
                    average_tags_per_activity=report['tag_analysis']['average_tags_per_activity']
                )
            )
            
        except Exception as e:
            # Update job status on error
            job_status.status = "failed"
            job_status.completed_at = datetime.now()
            job_status.error_message = str(e)
            
            raise
    
    async def get_processing_status(self, job_id: str) -> Optional[ProcessingStatus]:
        """Get status of a processing job."""
        return self._processing_jobs.get(job_id)
    
    async def get_processing_history(self, limit: int = 50) -> List[ProcessingStatus]:
        """Get processing job history."""
        # Sort by started_at descending
        jobs = sorted(self._processing_jobs.values(), 
                     key=lambda x: x.started_at, reverse=True)
        return jobs[:limit]
    
    async def import_calendar_data(self, request: ImportRequest) -> Dict[str, Any]:
        """Import data from Google Calendar parser."""
        try:
            from src.backend.parsers.google_calendar.parser import parse_to_database
            count = parse_to_database('google_calendar_events.json', 
                                    hours_since_last_update=request.hours_since_last_update)
            
            return {
                "status": "success",
                "imported_count": count,
                "source": "google_calendar"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "source": "google_calendar"
            }
    
    async def import_notion_data(self, request: ImportRequest) -> Dict[str, Any]:
        """Import data from Notion parser."""
        try:
            from src.backend.parsers.notion.parser import parse_to_database
            count = parse_to_database('notion_content.json', 
                                    hours_since_last_edit=request.hours_since_last_update)
            
            return {
                "status": "success", 
                "imported_count": count,
                "source": "notion"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "source": "notion"
            }
    
    async def get_import_status(self) -> Dict[str, Any]:
        """Get status of data imports."""
        try:
            # Check database for recent imports
            calendar_query = "SELECT COUNT(*) as count, MAX(created_at) as last_import FROM raw_activities WHERE source = 'google_calendar'"
            notion_query = "SELECT COUNT(*) as count, MAX(created_at) as last_import FROM raw_activities WHERE source = 'notion'"
            
            calendar_result = self.db.execute_query(calendar_query)[0]
            notion_result = self.db.execute_query(notion_query)[0]
            
            return {
                "google_calendar": {
                    "total_activities": calendar_result['count'],
                    "last_import": calendar_result['last_import']
                },
                "notion": {
                    "total_activities": notion_result['count'], 
                    "last_import": notion_result['last_import']
                }
            }
        except Exception as e:
            return {"error": str(e)}


class SystemService:
    """Service for system health and statistics."""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.start_time = datetime.now()
    
    async def get_system_health(self) -> SystemHealthResponse:
        """Get system health status."""
        try:
            # Test database connection
            test_query = "SELECT COUNT(*) as count FROM raw_activities"
            result = self.db.execute_query(test_query)
            total_activities = result[0]['count'] if result else 0
            
            # Get last update time
            last_update_query = "SELECT MAX(created_at) as last_update FROM raw_activities"
            update_result = self.db.execute_query(last_update_query)
            last_updated = update_result[0]['last_update'] if update_result and update_result[0]['last_update'] else datetime.now()
            
            database_health = DatabaseHealth(
                connected=True,
                total_activities=total_activities,
                last_updated=datetime.fromisoformat(last_updated) if isinstance(last_updated, str) else last_updated
            )
            
            services_health = ServiceHealth(
                tag_generator="operational",
                activity_matcher="operational"
            )
            
            return SystemHealthResponse(
                status="healthy",
                database=database_health,
                services=services_health
            )
            
        except Exception as e:
            return SystemHealthResponse(
                status="down",
                database=DatabaseHealth(
                    connected=False,
                    total_activities=0,
                    last_updated=datetime.now()
                ),
                services=ServiceHealth(
                    tag_generator="down",
                    activity_matcher="down"
                )
            )
    
    async def get_system_stats(self) -> SystemStatsResponse:
        """Get system statistics."""
        try:
            # Get counts for each table
            raw_count = self.db.execute_query("SELECT COUNT(*) as count FROM raw_activities")[0]['count']
            processed_count = self.db.execute_query("SELECT COUNT(*) as count FROM processed_activities")[0]['count']
            tags_count = self.db.execute_query("SELECT COUNT(*) as count FROM tags")[0]['count']
            sessions_count = self.db.execute_query("SELECT COUNT(*) as count FROM user_sessions")[0]['count']
            
            # Get database file size
            db_path = self.db.config.db_path
            db_size_bytes = os.path.getsize(db_path) if os.path.exists(db_path) else 0
            db_size_mb = round(db_size_bytes / (1024 * 1024), 2)
            
            # Get last processing run
            last_processing_query = "SELECT MAX(start_time) as last_run FROM user_sessions WHERE session_type = 'processing'"
            processing_result = self.db.execute_query(last_processing_query)
            last_processing = processing_result[0]['last_run'] if processing_result and processing_result[0]['last_run'] else None
            
            # Calculate uptime
            uptime_seconds = int((datetime.now() - self.start_time).total_seconds())
            
            return SystemStatsResponse(
                total_raw_activities=raw_count,
                total_processed_activities=processed_count,
                total_tags=tags_count,
                total_sessions=sessions_count,
                database_size_mb=db_size_mb,
                last_processing_run=datetime.fromisoformat(last_processing) if last_processing else None,
                uptime_seconds=uptime_seconds
            )
            
        except Exception as e:
            # Return error stats
            return SystemStatsResponse(
                total_raw_activities=0,
                total_processed_activities=0,
                total_tags=0,
                total_sessions=0,
                database_size_mb=0.0,
                last_processing_run=None,
                uptime_seconds=0
            )
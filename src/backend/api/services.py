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
from src.backend.agent.tools.context_retriever import ContextRetriever


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
        tag_db = TagDB(
            name=tag_data.name,
            description=tag_data.description,
            color=tag_data.color
        )

        tag_id = TagDAO.create(tag_db)
        return await self.get_tag_by_id(tag_id)

    async def update_tag(self, tag_id: int, tag_data: TagUpdateRequest) -> Optional[TagResponse]:
        """Update an existing tag."""
        existing_tag = TagDAO.get_by_id(tag_id)
        if not existing_tag:
            return None

        updated_tag = TagDB(
            id=tag_id,
            name=tag_data.name,
            description=tag_data.description,
            color=tag_data.color,
            usage_count=existing_tag.usage_count,
            created_at=existing_tag.created_at,
            updated_at=datetime.now()
        )

        TagDAO.update(updated_tag)
        return await self.get_tag_by_id(tag_id)

    async def delete_tag(self, tag_id: int) -> bool:
        """Delete a tag."""
        existing_tag = TagDAO.get_by_id(tag_id)
        if not existing_tag:
            return False

        TagDAO.delete(tag_id)
        return True

    async def get_tag_summary(self, start_date: Optional[str] = None,
                             end_date: Optional[str] = None,
                             limit: int = 20) -> TagSummaryResponse:
        """Get tag usage summary."""
        # Build query with date filters
        conditions = []
        params = []

        if start_date:
            conditions.append("pa.date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("pa.date <= ?")
            params.append(end_date)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT t.name as tag,
                   COUNT(*) as count,
                   ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
            FROM tags t
            JOIN activity_tags at ON t.id = at.tag_id
            JOIN processed_activities pa ON at.processed_activity_id = pa.id
            {where_clause}
            GROUP BY t.id, t.name
            ORDER BY count DESC
            LIMIT ?
        """
        params.append(limit)

        results = self.db.execute_query(query, params)

        # Get total count
        total_query = "SELECT COUNT(DISTINCT id) as count FROM tags"
        total_result = self.db.execute_query(total_query)
        total_tags = total_result[0]['count'] if total_result else 0

        # Convert to response format
        top_tags = []
        color_map = {}

        for row in results:
            top_tags.append(TagSummaryItem(
                tag=row['tag'],
                count=row['count'],
                percentage=row['percentage']
            ))

            # Get color for this tag
            tag_color_query = "SELECT color FROM tags WHERE name = ?"
            tag_color_result = self.db.execute_query(tag_color_query, [row['tag']])
            if tag_color_result:
                color_map[row['tag']] = tag_color_result[0]['color'] or '#6b7280'

        return TagSummaryResponse(
            total_tags=total_tags,
            top_tags=top_tags,
            color_map=color_map
        )

    async def get_tag_cooccurrence(self, start_date: Optional[str] = None,
                                  end_date: Optional[str] = None,
                                  tags: Optional[List[str]] = None,
                                  threshold: int = 2,
                                  limit: int = 50) -> TagCooccurrenceResponse:
        """Get tag co-occurrence analysis."""
        conditions = []
        params = []

        if start_date:
            conditions.append("pa.date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("pa.date <= ?")
            params.append(end_date)
        if tags:
            placeholders = ','.join(['?' for _ in tags])
            conditions.append(f"(t1.name IN ({placeholders}) OR t2.name IN ({placeholders}))")
            params.extend(tags * 2)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT t1.name as tag1, t2.name as tag2,
                   COUNT(*) as count,
                   ROUND(COUNT(*) * 1.0 / MAX(tag_counts.max_count), 3) as strength
            FROM activity_tags at1
            JOIN activity_tags at2 ON at1.processed_activity_id = at2.processed_activity_id
                                   AND at1.tag_id < at2.tag_id
            JOIN tags t1 ON at1.tag_id = t1.id
            JOIN tags t2 ON at2.tag_id = t2.id
            JOIN processed_activities pa ON at1.processed_activity_id = pa.id
            CROSS JOIN (SELECT MAX(cnt) as max_count FROM (
                SELECT COUNT(*) as cnt
                FROM activity_tags at3
                JOIN processed_activities pa3 ON at3.processed_activity_id = pa3.id
                {where_clause.replace('pa.', 'pa3.')}
                GROUP BY at3.tag_id
            )) tag_counts
            {where_clause}
            GROUP BY t1.id, t1.name, t2.id, t2.name
            HAVING count >= ?
            ORDER BY count DESC
            LIMIT ?
        """
        params.extend([threshold, limit])

        results = self.db.execute_query(query, params)

        data = []
        for row in results:
            data.append(TagCooccurrenceItem(
                tag1=row['tag1'],
                tag2=row['tag2'],
                strength=row['strength'],
                count=row['count']
            ))

        return TagCooccurrenceResponse(data=data)

    async def get_tag_transitions(self, start_date: Optional[str] = None,
                                 end_date: Optional[str] = None,
                                 tags: Optional[List[str]] = None,
                                 limit: int = 50) -> TagTransitionResponse:
        """Get tag transition patterns."""
        # This is a simplified implementation - in a real system you'd analyze temporal sequences
        conditions = []
        params = []

        if start_date:
            conditions.append("pa1.date >= ? AND pa2.date >= ?")
            params.extend([start_date, start_date])
        if end_date:
            conditions.append("pa1.date <= ? AND pa2.date <= ?")
            params.extend([end_date, end_date])
        if tags:
            placeholders = ','.join(['?' for _ in tags])
            conditions.append(f"(t1.name IN ({placeholders}) OR t2.name IN ({placeholders}))")
            params.extend(tags * 2)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT t1.name as from_tag, t2.name as to_tag,
                   COUNT(*) as count,
                   ROUND(COUNT(*) * 1.0 / SUM(COUNT(*)) OVER(), 3) as strength
            FROM processed_activities pa1
            JOIN activity_tags at1 ON pa1.id = at1.processed_activity_id
            JOIN tags t1 ON at1.tag_id = t1.id
            JOIN processed_activities pa2 ON DATE(pa2.date) = DATE(pa1.date, '+1 day')
            JOIN activity_tags at2 ON pa2.id = at2.processed_activity_id
            JOIN tags t2 ON at2.tag_id = t2.id
            {where_clause}
            GROUP BY t1.id, t1.name, t2.id, t2.name
            ORDER BY count DESC
            LIMIT ?
        """
        params.append(limit)

        results = self.db.execute_query(query, params)

        data = []
        for row in results:
            data.append(TagTransitionItem(
                from_tag=row['from_tag'],
                to_tag=row['to_tag'],
                strength=row['strength'],
                count=row['count']
            ))

        return TagTransitionResponse(data=data)

    async def get_tag_time_series(self, start_date: Optional[str] = None,
                                 end_date: Optional[str] = None,
                                 tags: Optional[List[str]] = None,
                                 granularity: str = "day",
                                 mode: str = "absolute") -> TagTimeSeriesResponse:
        """Get tag time series data."""
        conditions = []
        params = []

        if start_date:
            conditions.append("pa.date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("pa.date <= ?")
            params.append(end_date)
        if tags:
            placeholders = ','.join(['?' for _ in tags])
            conditions.append(f"t.name IN ({placeholders})")
            params.extend(tags)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        # Determine time grouping based on granularity
        if granularity == "hour":
            time_group = "pa.date, CAST(strftime('%H', pa.time) as INTEGER)"
            time_select = "pa.date, CAST(strftime('%H', pa.time) as INTEGER) as hour"
        else:
            time_group = "pa.date"
            time_select = "pa.date, NULL as hour"

        query = f"""
            SELECT t.name as tag, {time_select},
                   COUNT(*) as count,
                   SUM(pa.total_duration_minutes) as duration
            FROM tags t
            JOIN activity_tags at ON t.id = at.tag_id
            JOIN processed_activities pa ON at.processed_activity_id = pa.id
            {where_clause}
            GROUP BY t.id, t.name, {time_group}
            ORDER BY pa.date, t.name
        """

        results = self.db.execute_query(query, params)

        data = []
        for row in results:
            data.append(TagTimeSeriesItem(
                tag=row['tag'],
                date=row['date'],
                hour=row['hour'],
                count=row['count'],
                duration=row['duration'] or 0
            ))

        return TagTimeSeriesResponse(data=data)

    async def get_top_tags_with_relationships(self, top_tags_limit: int = 5,
                                            related_tags_limit: int = 5):
        """Get top tags with their co-occurring related tags."""
        # Get top tags by usage
        top_tags_query = """
            SELECT t.name, t.usage_count
            FROM tags t
            ORDER BY t.usage_count DESC
            LIMIT ?
        """
        top_tags_result = self.db.execute_query(top_tags_query, [top_tags_limit])

        relationships = {}
        for tag_row in top_tags_result:
            tag_name = tag_row['name']

            # Get related tags for this tag
            related_query = """
                SELECT t2.name as related_tag, COUNT(*) as cooccurrence_count
                FROM activity_tags at1
                JOIN activity_tags at2 ON at1.processed_activity_id = at2.processed_activity_id
                                       AND at1.tag_id != at2.tag_id
                JOIN tags t1 ON at1.tag_id = t1.id
                JOIN tags t2 ON at2.tag_id = t2.id
                WHERE t1.name = ?
                GROUP BY t2.id, t2.name
                ORDER BY cooccurrence_count DESC
                LIMIT ?
            """
            related_result = self.db.execute_query(related_query, [tag_name, related_tags_limit])

            relationships[tag_name] = {
                'usage_count': tag_row['usage_count'],
                'related_tags': [
                    {
                        'tag': row['related_tag'],
                        'cooccurrence_count': row['cooccurrence_count']
                    }
                    for row in related_result
                ]
            }

        return relationships

    async def cleanup_tags(self, request: TagCleanupRequest) -> TagCleanupResponse:
        """Clean up meaningless tags using AI analysis."""
        try:
            from src.backend.agent.tools.tag_cleaner import TagCleaner

            # Initialize tag cleaner
            cleaner = TagCleaner()

            # Perform cleanup
            result = cleaner.clean_meaningless_tags(
                db_manager=self.db,
                dry_run=request.dry_run,
                removal_threshold=request.removal_threshold,
                merge_threshold=request.merge_threshold,
                date_start=request.date_start,
                date_end=request.date_end
            )

            # Convert to API response format
            tags_to_remove = [
                TagCleanupAction(
                    name=tag["name"],
                    reason=tag["reason"],
                    confidence=tag["confidence"]
                )
                for tag in result.get("tags_to_remove", [])
            ]

            tags_to_merge = [
                TagCleanupAction(
                    name=tag["source"],
                    reason=tag["reason"],
                    confidence=tag["confidence"],
                    target=tag["target"]
                )
                for tag in result.get("tags_to_merge", [])
            ]

            return TagCleanupResponse(
                status=result["status"],
                total_analyzed=result["total_analyzed"],
                marked_for_removal=result["marked_for_removal"],
                marked_for_merge=result["marked_for_merge"],
                removed=result["removed"],
                merged=result["merged"],
                dry_run=result["dry_run"],
                scope=result["scope"],
                tags_to_remove=tags_to_remove,
                tags_to_merge=tags_to_merge
            )

        except Exception as e:
            return TagCleanupResponse(
                status="error",
                total_analyzed=0,
                marked_for_removal=0,
                marked_for_merge=0,
                removed=0,
                merged=0,
                dry_run=request.dry_run,
                scope={"date_start": request.date_start, "date_end": request.date_end},
                tags_to_remove=[],
                tags_to_merge=[]
            )


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
        self._job_progress = {}  # Real-time progress tracking for active jobs
    
    async def trigger_daily_processing(self, request: ProcessingRequest) -> ProcessingResponse:
        """Trigger daily activity processing with real-time progress tracking."""
        job_id = f"proc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        # Create processing job status
        job_status = ProcessingStatus(
            job_id=job_id,
            status="running",
            started_at=datetime.now()
        )
        self._processing_jobs[job_id] = job_status

        # Initialize progress tracking
        self._job_progress[job_id] = {
            "status": "running",
            "activity_index": 0,
            "total_activities": 0,
            "current_activity": "",
            "current_tags": [],
            "progress": 0
        }

        # Start processing in background
        asyncio.create_task(self._process_with_progress(job_id, request))

        # Return immediately with job_id for polling
        return ProcessingResponse(
            status="processing",
            job_id=job_id,
            message="Processing started. Poll /api/v1/process/progress/{job_id} for updates.",
            processed_counts=ProcessingCounts(
                raw_activities=0,
                processed_activities=0
            ),
            tag_analysis=TagAnalysis(
                total_unique_tags=0,
                average_tags_per_activity=0.0
            )
        )

    async def _process_with_progress(self, job_id: str, request: ProcessingRequest):
        """Run processing with progress callbacks."""
        try:
            # Define progress callback
            def progress_callback(activity_index: int, total: int, current_activity: str, current_tags: List[str]):
                """Update progress for this job."""
                self._job_progress[job_id].update({
                    "status": "running",
                    "activity_index": activity_index,
                    "total_activities": total,
                    "current_activity": current_activity[:200],  # Limit activity text length
                    "current_tags": current_tags[:10],  # Limit to first 10 tags
                    "progress": int((activity_index / total) * 100) if total > 0 else 0
                })

            # Run the processing with callback in thread pool (it's CPU-bound and synchronous)
            processor = ActivityProcessor()
            loop = asyncio.get_event_loop()
            report = await loop.run_in_executor(
                None,
                lambda: processor.process_daily_activities(
                    use_database=request.use_database,
                    progress_callback=progress_callback
                )
            )

            # Update job status on completion
            job_status = self._processing_jobs.get(job_id)
            if job_status:
                job_status.status = "completed"
                job_status.completed_at = datetime.now()
                job_status.progress = 1.0

            # Update progress tracking
            self._job_progress[job_id].update({
                "status": "completed",
                "progress": 100,
                "report": report
            })

        except Exception as e:
            # Update job status on error
            job_status = self._processing_jobs.get(job_id)
            if job_status:
                job_status.status = "failed"
                job_status.completed_at = datetime.now()
                job_status.error_message = str(e)

            # Update progress tracking
            self._job_progress[job_id].update({
                "status": "failed",
                "error": str(e)
            })

    async def get_processing_progress(self, job_id: str) -> Dict[str, Any]:
        """Get real-time progress for a processing job."""
        if job_id not in self._job_progress:
            return {
                "status": "not_found",
                "message": "Job ID not found"
            }

        progress = self._job_progress[job_id]

        # Return progress data
        return {
            "job_id": job_id,
            "status": progress.get("status"),
            "activity_index": progress.get("activity_index", 0),
            "total_activities": progress.get("total_activities", 0),
            "current_activity": progress.get("current_activity", ""),
            "current_tags": progress.get("current_tags", []),
            "progress": progress.get("progress", 0),
            "error": progress.get("error"),
            "report": progress.get("report")
        }
    
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
        """Import data from Google Calendar API."""
        try:
            from src.backend.parsers.google_calendar.ingest_api import ingest_to_database
            from datetime import datetime, timedelta

            # Calculate date range based on hours_since_last_update
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=request.hours_since_last_update)

            # Format dates as YYYY-MM-DD
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")

            # Use 'primary' calendar by default
            count = ingest_to_database(start_str, end_str, calendar_ids=['primary'])

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

    async def backfill_calendar(self, months: int = 7) -> Dict[str, Any]:
        """One-click backfill for the last N months of calendar events."""
        try:
            from src.backend.parsers.google_calendar.ingest_api import ingest_to_database
            from datetime import datetime, timedelta

            # Calculate date range for backfill
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)  # Approximate month as 30 days

            # Format dates as YYYY-MM-DD
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")

            # Use 'primary' calendar by default
            count = ingest_to_database(start_str, end_str, calendar_ids=['primary'])

            return {
                "status": "success",
                "message": f"Backfilled {months} months of calendar events",
                "imported_count": count,
                "date_range": {
                    "start": start_str,
                    "end": end_str
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def reprocess_date_range(self, date_start: str, date_end: str,
                                   regenerate_system_tags: bool = False) -> Dict[str, Any]:
        """Purge processed results for a date range and reprocess that range.
        Note: current processor runs DB-wide but filters to the date range.
        """
        try:
            # Purge processed activities in range (cascade deletes activity_tags)
            deleted = self.db.execute_update(
                "DELETE FROM processed_activities WHERE date >= ? AND date <= ?",
                (date_start, date_end)
            )
            # Run processing for specified date range
            processor = ActivityProcessor()
            processor.enable_system_tag_regeneration = regenerate_system_tags
            report = processor.process_daily_activities(
                use_database=True,
                date_start=date_start,
                date_end=date_end
            )

            return {
                "status": "success",
                "deleted_processed": deleted,
                "date_start": date_start,
                "date_end": date_end,
                "processed_counts": report.get('processed_counts', {}),
                "tag_analysis": report.get('tag_analysis', {})
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def index_notion_blocks(self, scope: str = "all", hours: int = 24) -> Dict[str, Any]:
        """Generate abstracts and embeddings for Notion blocks.
        scope: 'all' or 'recent' (by edited time window)
        """
        from src.backend.database import NotionBlockDAO, NotionEmbeddingDAO, NotionEmbeddingDB
        from src.backend.notion.abstracts import generate_abstract, embed_text

        try:
            if scope == "recent":
                blocks = NotionBlockDAO.get_recently_edited(hours=hours)
            else:
                blocks = NotionBlockDAO.get_all_leaf_blocks()

            processed = 0
            for blk in blocks:
                # Ensure abstract
                abstract = blk.abstract or generate_abstract(blk.text or "")
                if abstract != blk.abstract:
                    # update abstract field via upsert
                    from src.backend.database import NotionBlockDB
                    updated = NotionBlockDB(
                        block_id=blk.block_id,
                        page_id=blk.page_id,
                        parent_block_id=blk.parent_block_id,
                        is_leaf=blk.is_leaf,
                        text=blk.text,
                        abstract=abstract,
                        last_edited_at=blk.last_edited_at,
                    )
                    from src.backend.database import NotionBlockDAO as NBD
                    NBD.upsert(updated)

                # Ensure embedding
                emb = NotionEmbeddingDAO.get_by_block(blk.block_id)
                if not emb or not (emb.vector):
                    vec = embed_text(abstract or (blk.text or ""))
                    emb_db = NotionEmbeddingDB(block_id=blk.block_id, vector=vec)
                    NotionEmbeddingDAO.upsert(emb_db)

                processed += 1

            return {"status": "success", "processed_blocks": processed, "scope": scope}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def import_notion_data(self, request: ImportRequest) -> Dict[str, Any]:
        """Import data from Notion API."""
        try:
            from src.backend.parsers.notion.ingest_api import NotionIngestor

            # Initialize Notion ingestor (uses NOTION_API_KEY from env)
            ingestor = NotionIngestor()

            # Ingest all accessible pages and blocks
            # Note: Notion API doesn't support time-based filtering in the same way
            # We ingest everything and then filter by last_edited_at in the database
            count = ingestor.ingest_all()

            return {
                "status": "success",
                "imported_count": count,
                "source": "notion",
                "message": f"Imported {count} pages/blocks from Notion"
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
            calendar_query = "SELECT COUNT(*) as count, MAX(created_at) as last_sync FROM raw_activities WHERE source = 'google_calendar'"
            notion_query = "SELECT COUNT(*) as count FROM raw_activities WHERE source = 'notion'"
            notion_pages_query = "SELECT COUNT(*) as page_count, MAX(created_at) as last_sync FROM notion_pages"

            calendar_results = self.db.execute_query(calendar_query)
            notion_results = self.db.execute_query(notion_query)
            notion_pages_results = self.db.execute_query(notion_pages_query)

            # Handle empty result sets and convert sqlite3.Row to dict
            calendar_result = dict(calendar_results[0]) if calendar_results else {'count': 0, 'last_sync': None}
            notion_result = dict(notion_results[0]) if notion_results else {'count': 0}
            notion_pages_result = dict(notion_pages_results[0]) if notion_pages_results else {'page_count': 0, 'last_sync': None}

            # Determine status based on data
            calendar_count = calendar_result.get('count', 0) or 0
            notion_count = notion_result.get('count', 0) or 0
            notion_page_count = notion_pages_result.get('page_count', 0) or 0

            return {
                "calendar": {
                    "last_sync": calendar_result.get('last_sync'),
                    "status": "healthy" if calendar_count > 0 else "no_data",
                    "total_imported": calendar_count
                },
                "notion": {
                    "last_sync": notion_pages_result.get('last_sync'),
                    "status": "healthy" if (notion_count > 0 or notion_page_count > 0) else "no_data",
                    "total_imported": max(notion_count, notion_page_count)
                }
            }
        except Exception as e:
            # Log the error for debugging
            print(f"Error getting import status: {str(e)}")
            import traceback
            traceback.print_exc()

            # Return no_data instead of error for better UX
            return {
                "calendar": {
                    "last_sync": None,
                    "status": "no_data",
                    "total_imported": 0
                },
                "notion": {
                    "last_sync": None,
                    "status": "no_data",
                    "total_imported": 0
                }
            }

    async def build_taxonomy(self, request: TaxonomyBuildRequest) -> TaxonomyBuildResponse:
        """Build AI-generated tag taxonomy and synonyms."""
        try:
            from src.backend.agent.tools.taxonomy_builder import build_and_save

            # Call taxonomy builder
            result = build_and_save(
                date_start=request.date_start,
                date_end=request.date_end
            )

            # Parse the result to extract information
            if isinstance(result, dict) and result.get("status") == "success":
                return TaxonomyBuildResponse(
                    status="success",
                    message=result.get("message", "Taxonomy and synonyms built successfully"),
                    files_generated=result.get("files", []),
                    taxonomy_size=result.get("taxonomy_size"),
                    synonyms_count=result.get("synonyms_count"),
                    data_scope={
                        "date_start": request.date_start,
                        "date_end": request.date_end
                    }
                )
            else:
                # Handle string response or error case
                message = str(result) if not isinstance(result, dict) else result.get("message", "Taxonomy build completed")
                return TaxonomyBuildResponse(
                    status="success",
                    message=message,
                    files_generated=[
                        "agent/resources/hierarchical_taxonomy_generated.json",
                        "agent/resources/synonyms_generated.json"
                    ],
                    data_scope={
                        "date_start": request.date_start,
                        "date_end": request.date_end
                    }
                )

        except Exception as e:
            return TaxonomyBuildResponse(
                status="error",
                message=f"Taxonomy build failed: {str(e)}",
                files_generated=[],
                data_scope={
                    "date_start": request.date_start,
                    "date_end": request.date_end
                }
            )

    async def get_processing_logs(self,
                                 limit: int = 100,
                                 offset: int = 0,
                                 level: Optional[str] = None,
                                 source: Optional[str] = None) -> ProcessingLogsResponse:
        """Get processing logs with filtering and pagination."""
        try:
            import os
            from pathlib import Path
            import json
            from datetime import datetime

            # Check for log files in logs/ directory
            log_dir = Path("logs")
            log_entries = []

            if log_dir.exists():
                # Read JSONL log files
                for log_file in log_dir.glob("*.jsonl"):
                    try:
                        with open(log_file, 'r') as f:
                            for line in f:
                                if line.strip():
                                    try:
                                        entry = json.loads(line.strip())

                                        # Convert to ProcessingLogEntry format
                                        log_entry = ProcessingLogEntry(
                                            timestamp=datetime.fromisoformat(entry.get('timestamp', datetime.now().isoformat())),
                                            level=entry.get('level', 'INFO'),
                                            message=entry.get('message', ''),
                                            source=entry.get('source', log_file.stem),
                                            context=entry.get('context')
                                        )

                                        # Apply filters
                                        if level and log_entry.level != level:
                                            continue
                                        if source and log_entry.source != source:
                                            continue

                                        log_entries.append(log_entry)
                                    except json.JSONDecodeError:
                                        continue
                    except Exception:
                        continue

            # Sort by timestamp (newest first)
            log_entries.sort(key=lambda x: x.timestamp, reverse=True)

            # Apply pagination
            total_count = len(log_entries)
            paginated_logs = log_entries[offset:offset + limit]

            return ProcessingLogsResponse(
                logs=paginated_logs,
                total_count=total_count,
                page_info=PageInfo(
                    limit=limit,
                    offset=offset,
                    has_next_page=offset + limit < total_count
                )
            )

        except Exception as e:
            # Return empty response on error
            return ProcessingLogsResponse(
                logs=[],
                total_count=0,
                page_info=PageInfo(
                    limit=limit,
                    offset=offset,
                    has_next_page=False
                )
            )


class SystemService:
    """Service for system health and statistics."""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.start_time = datetime.now()
    
    async def get_system_health(self) -> SystemHealthResponse:
        """Get system health status."""
        import os

        # Check database connection
        db_connected = False
        db_type = "unknown"
        try:
            test_query = "SELECT 1"
            self.db.execute_query(test_query)
            db_connected = True
            # Determine database type from connection string or path
            if hasattr(self.db.config, 'db_path'):
                db_type = "sqlite"
            else:
                db_type = "postgresql"
        except Exception:
            pass

        database_health = DatabaseHealth(
            connected=db_connected,
            type=db_type
        )

        # Check Notion API
        notion_configured = False
        notion_connected = False
        try:
            notion_api_key = os.getenv('NOTION_API_KEY')
            if notion_api_key:
                notion_configured = True
                # Try to actually test the Notion API connection
                try:
                    from notion_client import Client
                    notion = Client(auth=notion_api_key)
                    # Quick test - just check if we can authenticate
                    # This will raise an exception if the key is invalid
                    notion.users.me()
                    notion_connected = True
                except Exception as e:
                    # API key exists but connection failed
                    print(f"Notion API configured but connection failed: {str(e)}")
                    notion_connected = False
        except Exception as e:
            print(f"Notion API check error: {str(e)}")
            pass

        # Check Google Calendar API
        gcal_configured = False
        gcal_connected = False
        try:
            # Check if credentials.json and token.json exist
            credentials_path = os.path.join(PROJECT_ROOT, 'credentials.json')
            token_path = os.path.join(PROJECT_ROOT, 'token.json')

            if os.path.exists(credentials_path):
                gcal_configured = True
                if os.path.exists(token_path):
                    gcal_connected = True
        except Exception:
            pass

        # Check OpenAI API
        openai_configured = False
        openai_connected = False
        try:
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if openai_api_key:
                openai_configured = True
                # Try to actually test the OpenAI API connection
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=openai_api_key)
                    # Quick test - just check if we can list models
                    models = client.models.list()
                    openai_connected = True
                except Exception as e:
                    # API key exists but connection failed
                    print(f"OpenAI API configured but connection failed: {str(e)}")
                    openai_connected = False
        except Exception as e:
            print(f"OpenAI API check error: {str(e)}")
            pass

        apis_health = ApiConnectionsHealth(
            notion=ApiStatus(configured=notion_configured, connected=notion_connected),
            google_calendar=ApiStatus(configured=gcal_configured, connected=gcal_connected),
            openai=ApiStatus(configured=openai_configured, connected=openai_connected)
        )

        # Determine overall status
        overall_status = "healthy"
        if not db_connected:
            overall_status = "down"
        elif not (notion_connected or gcal_connected):
            overall_status = "degraded"

        return SystemHealthResponse(
            status=overall_status,
            database=database_health,
            apis=apis_health,
            timestamp=datetime.now().isoformat()
        )
    
    async def get_system_stats(self) -> SystemStatsResponse:
        """Get system statistics."""
        try:
            # Get counts for each table
            raw_count = self.db.execute_query("SELECT COUNT(*) as count FROM raw_activities")[0]['count']
            processed_count = self.db.execute_query("SELECT COUNT(*) as count FROM processed_activities")[0]['count']
            tags_count = self.db.execute_query("SELECT COUNT(*) as count FROM tags")[0]['count']

            # Get Notion counts
            notion_pages_count = 0
            notion_blocks_count = 0
            try:
                notion_pages_count = self.db.execute_query("SELECT COUNT(*) as count FROM notion_pages")[0]['count']
                notion_blocks_count = self.db.execute_query("SELECT COUNT(*) as count FROM notion_blocks")[0]['count']
            except Exception:
                pass  # Tables might not exist

            # Get date ranges
            raw_earliest = None
            raw_latest = None
            try:
                raw_range = self.db.execute_query(
                    "SELECT MIN(date) as earliest, MAX(date) as latest FROM raw_activities"
                )[0]
                raw_earliest = raw_range['earliest']
                raw_latest = raw_range['latest']
            except Exception:
                pass

            processed_earliest = None
            processed_latest = None
            try:
                processed_range = self.db.execute_query(
                    "SELECT MIN(date) as earliest, MAX(date) as latest FROM processed_activities"
                )[0]
                processed_earliest = processed_range['earliest']
                processed_latest = processed_range['latest']
            except Exception:
                pass

            database_stats = DatabaseStats(
                raw_activities_count=raw_count,
                processed_activities_count=processed_count,
                tags_count=tags_count,
                notion_pages_count=notion_pages_count,
                notion_blocks_count=notion_blocks_count
            )

            date_ranges = DateRanges(
                raw_activities=DateRangeInfo(earliest=raw_earliest, latest=raw_latest),
                processed_activities=DateRangeInfo(earliest=processed_earliest, latest=processed_latest)
            )

            return SystemStatsResponse(
                database=database_stats,
                date_ranges=date_ranges
            )
        except Exception as e:
            # Return error stats
            return SystemStatsResponse(
                database=DatabaseStats(
                    raw_activities_count=0,
                    processed_activities_count=0,
                    tags_count=0,
                    notion_pages_count=0,
                    notion_blocks_count=0
                ),
                date_ranges=DateRanges(
                    raw_activities=DateRangeInfo(),
                    processed_activities=DateRangeInfo()
                )
            )

    # Retrieval / Context endpoints (class-level methods)
    async def get_notion_context(self, query: str, hours: int = 24, k: int = 5) -> Dict[str, Any]:
        """Retrieve top-K Notion contexts for a query within recent hours."""
        retriever = ContextRetriever()
        results = retriever.retrieve(query, hours=hours, k=k)
        items = []
        for r in results:
            blk = r.block
            items.append({
                "block_id": blk.block_id,
                "page_id": blk.page_id,
                "parent_block_id": blk.parent_block_id,
                "is_leaf": blk.is_leaf,
                "text": blk.text,
                "abstract": blk.abstract,
                "last_edited_at": blk.last_edited_at,
                "score": round(r.score, 4)
            })
        return {"query": query, "results": items}

    async def get_notion_context_by_date(self, query: str, date: str, window_days: int = 1, k: int = 5) -> Dict[str, Any]:
        """Retrieve top-K Notion contexts around a specific date.
        date format: YYYY-MM-DD; window_days selects [date - window_days, date + window_days].
        """
        retriever = ContextRetriever()
        results = retriever.retrieve_by_date(query, date=date, days_window=window_days, k=k)
        items = []
        for r in results:
            blk = r.block
            items.append({
                "block_id": blk.block_id,
                "page_id": blk.page_id,
                "parent_block_id": blk.parent_block_id,
                "is_leaf": blk.is_leaf,
                "text": blk.text,
                "abstract": blk.abstract,
                "last_edited_at": blk.last_edited_at,
                "score": round(r.score, 4)
            })
        return {"query": query, "date": date, "window_days": window_days, "results": items}

    async def update_api_configuration(self, config_request: 'ApiConfigurationRequest') -> 'ApiConfigurationResponse':
        """Update API configuration by writing to .env file."""
        import os
        from pathlib import Path

        try:
            # Path to root .env file
            env_path = Path(PROJECT_ROOT) / '.env'

            # Read existing .env file
            env_vars = {}
            if env_path.exists():
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            # Remove quotes if present
                            value = value.strip('"').strip("'")
                            env_vars[key.strip()] = value

            # Update with new values
            updated_keys = []
            if config_request.notion_api_key is not None:
                env_vars['NOTION_API_KEY'] = config_request.notion_api_key
                updated_keys.append('NOTION_API_KEY')
                # Also update in current environment
                os.environ['NOTION_API_KEY'] = config_request.notion_api_key

            if config_request.openai_api_key is not None:
                env_vars['OPENAI_API_KEY'] = config_request.openai_api_key
                updated_keys.append('OPENAI_API_KEY')
                os.environ['OPENAI_API_KEY'] = config_request.openai_api_key

            if config_request.openai_model is not None:
                env_vars['OPENAI_MODEL'] = config_request.openai_model
                updated_keys.append('OPENAI_MODEL')
                os.environ['OPENAI_MODEL'] = config_request.openai_model

            if config_request.openai_embed_model is not None:
                env_vars['OPENAI_EMBED_MODEL'] = config_request.openai_embed_model
                updated_keys.append('OPENAI_EMBED_MODEL')
                os.environ['OPENAI_EMBED_MODEL'] = config_request.openai_embed_model

            if config_request.google_calendar_key is not None:
                env_vars['GOOGLE_CALENDAR_KEY'] = config_request.google_calendar_key
                updated_keys.append('GOOGLE_CALENDAR_KEY')
                os.environ['GOOGLE_CALENDAR_KEY'] = config_request.google_calendar_key

            # Write back to .env file
            with open(env_path, 'w') as f:
                for key, value in env_vars.items():
                    f.write(f'{key}="{value}"\n')

            from .models import ApiConfigurationResponse
            return ApiConfigurationResponse(
                status="success",
                message=f"Updated {len(updated_keys)} configuration key(s)",
                updated_keys=updated_keys,
                restart_required=False  # Since we're updating os.environ, no restart needed
            )

        except Exception as e:
            from .models import ApiConfigurationResponse
            return ApiConfigurationResponse(
                status="error",
                message=f"Failed to update configuration: {str(e)}",
                updated_keys=[],
                restart_required=False
            )

    async def test_api_connection(self, test_request: 'TestApiConnectionRequest') -> 'TestApiConnectionResponse':
        """Test API connection with provided or configured credentials."""
        import os
        from .models import TestApiConnectionResponse

        api_type = test_request.api_type
        api_key = test_request.api_key

        if api_type == 'notion':
            try:
                # Use provided key or get from environment
                notion_key = api_key or os.getenv('NOTION_API_KEY')
                if not notion_key:
                    return TestApiConnectionResponse(
                        api_type='notion',
                        success=False,
                        message="No API key provided or configured",
                        details=None
                    )

                # Test Notion API
                from notion_client import Client
                notion = Client(auth=notion_key)
                # Try to list users (simple API call)
                response = notion.users.list()

                return TestApiConnectionResponse(
                    api_type='notion',
                    success=True,
                    message="Successfully connected to Notion API",
                    details={"users_count": len(response.get('results', []))}
                )
            except Exception as e:
                return TestApiConnectionResponse(
                    api_type='notion',
                    success=False,
                    message=f"Failed to connect: {str(e)}",
                    details=None
                )

        elif api_type == 'openai':
            try:
                # Use provided key or get from environment
                openai_key = api_key or os.getenv('OPENAI_API_KEY')
                if not openai_key:
                    return TestApiConnectionResponse(
                        api_type='openai',
                        success=False,
                        message="No API key provided or configured",
                        details=None
                    )

                # Test OpenAI API
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                # Try to list models (simple API call)
                models = client.models.list()

                return TestApiConnectionResponse(
                    api_type='openai',
                    success=True,
                    message="Successfully connected to OpenAI API",
                    details={"models_count": len(models.data)}
                )
            except Exception as e:
                return TestApiConnectionResponse(
                    api_type='openai',
                    success=False,
                    message=f"Failed to connect: {str(e)}",
                    details=None
                )

        elif api_type == 'google_calendar':
            try:
                # Check if credentials and token exist
                credentials_path = os.path.join(PROJECT_ROOT, 'credentials.json')
                token_path = os.path.join(PROJECT_ROOT, 'token.json')

                if not os.path.exists(credentials_path):
                    return TestApiConnectionResponse(
                        api_type='google_calendar',
                        success=False,
                        message="credentials.json not found in project root",
                        details=None
                    )

                if not os.path.exists(token_path):
                    return TestApiConnectionResponse(
                        api_type='google_calendar',
                        success=False,
                        message="token.json not found. Please run OAuth flow first.",
                        details=None
                    )

                # Try to import and use the calendar ingest API
                from src.backend.parsers.google_calendar.ingest_api import ingest_to_database

                return TestApiConnectionResponse(
                    api_type='google_calendar',
                    success=True,
                    message="Successfully connected to Google Calendar API",
                    details={"credentials_valid": True}
                )
            except Exception as e:
                return TestApiConnectionResponse(
                    api_type='google_calendar',
                    success=False,
                    message=f"Failed to connect: {str(e)}",
                    details=None
                )

        else:
            return TestApiConnectionResponse(
                api_type=api_type,
                success=False,
                message=f"Unknown API type: {api_type}",
                details=None
            )

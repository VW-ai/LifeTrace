import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from .models import RawActivity

class DataConsumer:
    """Handles loading and processing data from database (updated for database-first architecture)."""
    
    def __init__(self, notion_file: str = None, calendar_file: str = None):
        # Keep file parameters for backwards compatibility, but prefer database
        self.notion_file = notion_file
        self.calendar_file = calendar_file
        self._db_manager = None
    
    def _get_db_manager(self):
        """Get database manager instance."""
        if self._db_manager is None:
            try:
                import sys
                from pathlib import Path
                
                # Add project root to path if needed
                current_file = Path(__file__).resolve()
                project_root = current_file.parent.parent.parent.parent
                if str(project_root) not in sys.path:
                    sys.path.insert(0, str(project_root))
                
                from src.backend.database import get_db_manager, RawActivityDAO
                self._db_manager = get_db_manager()
                self._raw_activity_dao = RawActivityDAO
            except ImportError as e:
                print(f"Warning: Database not available, falling back to JSON files: {e}")
                self._db_manager = None
        
        return self._db_manager
    
    def load_raw_activities_from_database(self, hours_filter: int = 24*7) -> List[RawActivity]:
        """Load raw activities directly from database (preferred method)."""
        db_manager = self._get_db_manager()
        
        if db_manager is None:
            print("Database not available, falling back to JSON file loading")
            return self.load_all_raw_activities()  # Fallback to old method
        
        try:
            # Get raw activities from database
            raw_activities_db = self._raw_activity_dao.get_all()
            
            # Convert database models to agent models
            raw_activities = []
            for activity_db in raw_activities_db:
                # Convert database model to agent model
                raw_activity = RawActivity(
                    date=activity_db.date,
                    time=activity_db.time,
                    duration_minutes=activity_db.duration_minutes,
                    details=activity_db.details,
                    source=activity_db.source,
                    orig_link=activity_db.orig_link or "",
                    raw_data=activity_db.raw_data or {}
                )
                raw_activities.append(raw_activity)
            
            print(f"Loaded {len(raw_activities)} raw activities from database")
            return raw_activities
            
        except Exception as e:
            print(f"Error loading from database: {e}")
            print("Falling back to JSON file loading")
            return self.load_all_raw_activities()  # Fallback to old method
    
    def load_notion_data(self) -> List[Dict[str, Any]]:
        """Load parsed Notion data from JSON file."""
        try:
            with open(self.notion_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Notion file {self.notion_file} not found")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {self.notion_file}")
            return []
    
    def load_calendar_data(self) -> List[Dict[str, Any]]:
        """Load parsed Google Calendar data from JSON file."""
        try:
            with open(self.calendar_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Calendar file {self.calendar_file} not found")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {self.calendar_file}")
            return []
    
    def convert_notion_to_raw_activity(self, notion_item: Dict[str, Any]) -> RawActivity:
        """Convert a Notion parser item to RawActivity format."""
        # Extract hierarchy path for better context
        hierarchy_text = " > ".join(notion_item.get('hierarchy', []))
        
        # Combine text content with hierarchy for better details
        details = notion_item.get('text', '')
        if hierarchy_text:
            details = f"[{hierarchy_text}] {details}"
        
        # Extract date from block metadata if available (placeholder for now)
        # In real implementation, this would need to extract date from Notion metadata
        date = datetime.now().strftime('%Y-%m-%d')
        
        return RawActivity(
            date=date,
            time=None,  # Notion doesn't have precise time data
            duration_minutes=0,  # Will be estimated later
            details=details.strip(),
            source="notion",
            orig_link="",  # Could be constructed from block_id
            raw_data={
                'block_id': notion_item.get('block_id'),
                'block_type': notion_item.get('block_type'),
                'hierarchy': notion_item.get('hierarchy', [])
            }
        )
    
    def convert_calendar_to_raw_activity(self, calendar_item: Dict[str, Any]) -> RawActivity:
        """Convert a Calendar parser item to RawActivity format."""
        # Parse start time to extract date and time
        start_time = calendar_item.get('start_time', '')
        date = ""
        time = None
        
        if start_time:
            try:
                dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                date = dt.strftime('%Y-%m-%d')
                time = dt.strftime('%H:%M')
            except (ValueError, AttributeError):
                date = datetime.now().strftime('%Y-%m-%d')
        
        return RawActivity(
            date=date,
            time=time,
            duration_minutes=calendar_item.get('duration_minutes', 0),
            details=calendar_item.get('text', ''),
            source="google_calendar",
            orig_link=calendar_item.get('html_link', ''),
            raw_data={
                'event_id': calendar_item.get('event_id'),
                'summary': calendar_item.get('summary'),
                'description': calendar_item.get('description'),
                'start_time': calendar_item.get('start_time'),
                'end_time': calendar_item.get('end_time'),
                'updated': calendar_item.get('updated')
            }
        )
    
    def load_all_raw_activities(self) -> List[RawActivity]:
        """Load and convert all data from both sources into RawActivity format."""
        raw_activities = []
        
        # Load Notion data
        notion_data = self.load_notion_data()
        for item in notion_data:
            try:
                activity = self.convert_notion_to_raw_activity(item)
                raw_activities.append(activity)
            except Exception as e:
                print(f"Error processing Notion item: {e}")
                continue
        
        # Load Calendar data  
        calendar_data = self.load_calendar_data()
        for item in calendar_data:
            try:
                activity = self.convert_calendar_to_raw_activity(item)
                raw_activities.append(activity)
            except Exception as e:
                print(f"Error processing Calendar item: {e}")
                continue
        
        print(f"Loaded {len(raw_activities)} raw activities:")
        print(f"  - Notion items: {len(notion_data)}")
        print(f"  - Calendar items: {len(calendar_data)}")
        
        return raw_activities
    
    def filter_activities_by_date_range(self, activities: List[RawActivity], 
                                      start_date: Optional[str] = None,
                                      end_date: Optional[str] = None) -> List[RawActivity]:
        """Filter activities by date range (YYYY-MM-DD format)."""
        if not start_date and not end_date:
            return activities
        
        filtered = []
        for activity in activities:
            if start_date and activity.date < start_date:
                continue
            if end_date and activity.date > end_date:
                continue
            filtered.append(activity)
        
        return filtered
    
    def get_activities_summary(self, activities: List[RawActivity]) -> Dict[str, Any]:
        """Get summary statistics for loaded activities."""
        if not activities:
            return {'total': 0, 'by_source': {}, 'date_range': None}
        
        by_source = {}
        dates = []
        total_duration = 0
        
        for activity in activities:
            # Count by source
            source = activity.source
            by_source[source] = by_source.get(source, 0) + 1
            
            # Collect dates
            if activity.date:
                dates.append(activity.date)
            
            # Sum duration
            total_duration += activity.duration_minutes
        
        date_range = None
        if dates:
            dates.sort()
            date_range = {'start': dates[0], 'end': dates[-1]}
        
        return {
            'total': len(activities),
            'by_source': by_source,
            'date_range': date_range,
            'total_duration_minutes': total_duration,
            'total_duration_hours': round(total_duration / 60, 2)
        }
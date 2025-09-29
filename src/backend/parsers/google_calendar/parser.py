"""
DEPRECATED: Legacy Google Calendar Parser

⚠️  WARNING: This file is deprecated and will be removed in a future version.
⚠️  MIGRATION: Use `src/backend/parsers/google_calendar/ingest_api.py` instead.
⚠️  REASON: File-based JSON parsing superseded by direct database ingestion.

Legacy file-based parser functionality for Google Calendar events.
"""

import json
from datetime import datetime, timedelta, timezone

def calculate_duration(start_time, end_time):
    """Calculate duration between start and end times in minutes."""
    try:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        duration = end - start
        return int(duration.total_seconds() / 60)  # Return duration in minutes
    except (ValueError, AttributeError):
        return 0

def parse_calendar_events(events, hours_since_last_update, now=None):
    """Parse Google Calendar events into standardized format."""
    if now is None:
        now = datetime.now(timezone.utc)
    time_threshold = now - timedelta(hours=hours_since_last_update)
    
    parsed_data = []
    
    for event in events:
        # Check if event was updated within the time threshold
        updated_str = event.get('updated')
        if updated_str:
            updated_time = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
            if updated_time < time_threshold:
                continue
        
        # Extract event details
        event_id = event.get('id', '')
        summary = event.get('summary', 'Untitled Event')
        description = event.get('description', '')
        
        # Extract time information
        start_info = event.get('start', {})
        end_info = event.get('end', {})
        
        # Handle both dateTime and date formats
        start_time = start_info.get('dateTime') or start_info.get('date')
        end_time = end_info.get('dateTime') or end_info.get('date')
        
        # Calculate duration
        duration = 0
        if start_time and end_time:
            duration = calculate_duration(start_time, end_time)
        
        # Build text content combining summary and description
        text_content = summary
        if description:
            text_content += f" - {description}"
        
        # Create standardized event object matching notion parser format
        event_obj = {
            "source": "google_calendar",
            "event_id": event_id,
            "event_type": "calendar_event",
            "text": text_content,
            "summary": summary,
            "description": description,
            "start_time": start_time,
            "end_time": end_time,
            "duration_minutes": duration,
            "updated": updated_str,
            "html_link": event.get('htmlLink', ''),
            "hierarchy": []  # Calendar events don't have hierarchy like Notion blocks
        }
        
        parsed_data.append(event_obj)
    
    return parsed_data

def parse_to_database(input_file='google_calendar_events.json', hours_since_last_update=24):
    """Parse Google Calendar events and save directly to database."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            events = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
        return 0
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {input_file}")
        return 0
    
    # Ensure events is a list
    if not isinstance(events, list):
        print(f"Error: Expected a list of events in {input_file}")
        return 0
    
    parsed_data = parse_calendar_events(events, hours_since_last_update)
    
    # Save directly to database
    try:
        import sys
        from pathlib import Path
        
        # Add project root to path for database imports
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        from src.backend.database import RawActivityDAO, RawActivityDB
        
        activities_saved = 0
        for event in parsed_data:
            try:
                raw_activity = RawActivityDB(
                    date=event.get('date', '2025-08-31'),
                    time=event.get('time'),
                    duration_minutes=event.get('duration_minutes', 0),
                    details=event.get('summary', ''),
                    source='google_calendar',
                    orig_link=event.get('link', ''),
                    raw_data=event
                )
                
                RawActivityDAO.create(raw_activity)
                activities_saved += 1
                
            except Exception as e:
                print(f"Warning: Failed to save activity: {e}")
        
        print(f"Successfully parsed and saved {activities_saved} calendar activities to database")
        return activities_saved
        
    except Exception as e:
        print(f"Error saving to database: {e}")
        return 0

def main(input_file='google_calendar_events.json', output_file='parsed_google_calendar_events.json', hours_since_last_update=24):
    """Main function - backwards compatible but now database-first."""
    print("Note: Parser now saves directly to database. JSON output is deprecated.")
    return parse_to_database(input_file, hours_since_last_update)

if __name__ == '__main__':
    main()
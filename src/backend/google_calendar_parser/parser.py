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

def main(input_file='google_calendar_events.json', output_file='parsed_google_calendar_events.json', hours_since_last_update=24):
    """Main function to parse Google Calendar events."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            events = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {input_file}")
        return
    
    # Ensure events is a list
    if not isinstance(events, list):
        print(f"Error: Expected a list of events in {input_file}")
        return
    
    parsed_data = parse_calendar_events(events, hours_since_last_update)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=4)
        
        print(f"Successfully parsed {len(parsed_data)} calendar events and saved to {output_file}")
    except IOError as e:
        print(f"Error writing to {output_file}: {e}")

if __name__ == '__main__':
    main()
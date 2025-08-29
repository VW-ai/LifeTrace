# Google Calendar Parser

## Purpose
This module parses Google Calendar events from JSON format into a standardized document format compatible with the smartHistory system. It filters events based on their `updated` timestamp and extracts relevant information for activity tracking.

## Core Logic

### Input
- **File**: `google_calendar_events.json` - Raw Google Calendar API response containing event data
- **Filter**: `hours_since_last_update` (default: 24 hours) - Only processes events updated within this timeframe

### Processing
1. **Time Filtering**: Events are filtered based on their `updated` timestamp
2. **Duration Calculation**: Calculates event duration in minutes from start/end times
3. **Text Extraction**: Combines event summary and description into readable text
4. **Standardization**: Converts to consistent format matching Notion parser output

### Output Format
Each event is converted to:
```json
{
    "source": "google_calendar",
    "event_id": "unique_event_id",
    "event_type": "calendar_event", 
    "text": "summary - description",
    "summary": "event title",
    "description": "event description",
    "start_time": "2025-07-29T15:45:00+08:00",
    "end_time": "2025-07-29T17:00:00+08:00", 
    "duration_minutes": 75,
    "updated": "2025-07-29T09:31:51.577Z",
    "html_link": "google_calendar_link",
    "hierarchy": []
}
```

## Integration
- **Input**: Consumes output from `test_google_calendar.py` API calls
- **Output**: Feeds into the AI agent for activity categorization and tagging
- **Consistency**: Maintains same document structure as `notion_parser` for unified processing

## Key Features
- Handles both `dateTime` and `date` event formats
- Robust error handling for malformed data
- Time zone aware processing
- Consistent with existing parser architecture
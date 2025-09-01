#!/usr/bin/env python3
"""
Database-First Parser Runner for SmartHistory

Runs parsers to directly populate the database with raw activities.
No more JSON intermediate files!
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.parsers.google_calendar.parser import parse_to_database as parse_calendar
from src.backend.parsers.notion.parser import parse_to_database as parse_notion

def main():
    """Run all parsers and save directly to database."""
    print("🚀 SmartHistory Database-First Parsers")
    print("=" * 50)
    
    total_activities = 0
    
    # Parse Google Calendar
    print("📅 Parsing Google Calendar events...")
    try:
        calendar_count = parse_calendar('google_calendar_events.json', hours_since_last_update=24*7)
        total_activities += calendar_count
        print(f"✅ Google Calendar: {calendar_count} activities")
    except Exception as e:
        print(f"❌ Google Calendar failed: {e}")
    
    # Parse Notion
    print("📝 Parsing Notion content...")
    try:
        notion_count = parse_notion('notion_content.json', hours_since_last_edit=24*7)
        total_activities += notion_count
        print(f"✅ Notion: {notion_count} activities")
    except Exception as e:
        print(f"❌ Notion failed: {e}")
    
    print("=" * 50)
    print(f"🎉 Total: {total_activities} activities parsed directly to database!")
    print("💾 No JSON files needed - everything is in the database!")
    
    # Show database status
    try:
        from src.backend.database import RawActivityDAO
        all_activities = RawActivityDAO.get_all()
        sources = {}
        for activity in all_activities:
            sources[activity.source] = sources.get(activity.source, 0) + 1
        
        print("\n📊 Database Summary:")
        for source, count in sources.items():
            print(f"   {source}: {count} activities")
    except Exception as e:
        print(f"Could not get database summary: {e}")

if __name__ == '__main__':
    main()
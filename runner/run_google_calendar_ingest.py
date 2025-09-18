#!/usr/bin/env python3
"""
Google Calendar Ingest Script

Simple script to ingest Google Calendar events into the database.
Based on existing ingest_api.py and run_ingest.py patterns.

Usage:
  python runner/run_google_calendar_ingest.py --start 2025-01-01 --end 2025-09-18 [--cal-ids primary,other@gmail.com]
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None  # type: ignore

from src.backend.database.schema.migrations import MigrationManager


def ensure_schema_columns():
    """Ensure required columns exist in raw_activities table."""
    from src.backend.database import get_db_manager
    db = get_db_manager()
    with db.get_connection() as conn:
        cur = conn.cursor()
        # Check if raw_activities table has required columns
        cur.execute("PRAGMA table_info(raw_activities)")
        columns = [row[1] for row in cur.fetchall()]
        
        required_columns = {
            'date': 'TEXT NOT NULL',
            'time': 'TEXT',
            'duration_minutes': 'INTEGER DEFAULT 0',
            'details': 'TEXT DEFAULT ""',
            'source': 'TEXT NOT NULL DEFAULT ""',
            'orig_link': 'TEXT DEFAULT ""',
            'raw_data': 'TEXT DEFAULT "{}"'
        }
        
        for col, col_def in required_columns.items():
            if col not in columns:
                print(f"Adding missing column: {col}")
                cur.execute(f"ALTER TABLE raw_activities ADD COLUMN {col} {col_def}")
        
        conn.commit()


def main():
    parser = argparse.ArgumentParser(description="Ingest Google Calendar events into database")
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    parser.add_argument("--cal-ids", default="primary", help="Comma-separated Google Calendar IDs (default: primary)")
    args = parser.parse_args()

    start_date = args.start
    end_date = args.end
    cal_ids = [c.strip() for c in args.cal_ids.split(",") if c.strip()]

    # Validate dates
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        print("Error: Dates must be in YYYY-MM-DD format")
        sys.exit(1)

    # Load env
    if load_dotenv is not None:
        env_path = PROJECT_ROOT / '.env'
        if env_path.exists():
            load_dotenv(env_path)

    print("Setting up database schema...")
    # Run migrations
    mm = MigrationManager()
    mm.migrate_up()
    ensure_schema_columns()

    # Calendar API ingest
    print(f"Ingesting Google Calendar events from {start_date} to {end_date}")
    print(f"Calendar IDs: {cal_ids}")
    
    try:
        from src.backend.parsers.google_calendar.ingest_api import ingest_to_database as gcal_ingest
        count = gcal_ingest(start_date, end_date, calendar_ids=cal_ids)
        print(f"✅ Successfully ingested {count} Google Calendar events")
        return count
    except Exception as e:
        print(f"❌ Error ingesting Google Calendar events: {str(e)}")
        return 0


if __name__ == '__main__':
    main()
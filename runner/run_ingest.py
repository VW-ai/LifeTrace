#!/usr/bin/env python3
"""
SmartHistory Ingest Runner (DB-only)

Runs ingestion ONLY so you can debug backfill without tagging:
  1) Ensure schema (migrations + column repair)
  2) Ingest Google Calendar events for a date range
  3) Ingest Notion workspace pages/blocks
  4) Index Notion abstracts + embeddings (all leaf blocks)

Usage:
  python runner/run_ingest.py --start 2025-02-01 --end 2025-09-10 [--cal-ids primary,foo@bar]
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
import asyncio

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None  # type: ignore

from src.backend.api.dependencies import get_processing_service
from src.backend.database.schema.migrations import MigrationManager


def hours_since(date_str: str) -> int:
    d = datetime.strptime(date_str, "%Y-%m-%d")
    now = datetime.now()
    return max(1, int((now - d).total_seconds() // 3600))


def ensure_schema_columns():
    from src.backend.database import get_db_manager
    db = get_db_manager()
    with db.get_connection() as conn:
        cur = conn.cursor()
        def has_col(table, col):
            cur.execute(f"PRAGMA table_info({table})")
            return col in [row[1] for row in cur.fetchall()]
        # notion_pages
        if not has_col('notion_pages', 'last_edited_at'):
            cur.execute("ALTER TABLE notion_pages ADD COLUMN last_edited_at DATETIME")
        # notion_blocks
        if not has_col('notion_blocks', 'is_leaf'):
            cur.execute("ALTER TABLE notion_blocks ADD COLUMN is_leaf INTEGER DEFAULT 0")
        if not has_col('notion_blocks', 'abstract'):
            cur.execute("ALTER TABLE notion_blocks ADD COLUMN abstract TEXT")
        if not has_col('notion_blocks', 'last_edited_at'):
            cur.execute("ALTER TABLE notion_blocks ADD COLUMN last_edited_at DATETIME")
        if not has_col('notion_blocks', 'text'):
            cur.execute("ALTER TABLE notion_blocks ADD COLUMN text TEXT")
        if not has_col('notion_blocks', 'block_type'):
            cur.execute("ALTER TABLE notion_blocks ADD COLUMN block_type TEXT DEFAULT ''")
        conn.commit()


def main():
    parser = argparse.ArgumentParser(description="Ingest calendar + notion into DB (no tagging)")
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    parser.add_argument("--cal-ids", default="primary", help="Comma-separated Google Calendar IDs (default: primary)")
    args = parser.parse_args()

    start_date = args.start
    end_date = args.end
    cal_ids = [c.strip() for c in args.cal_ids.split(",") if c.strip()]

    # Load env
    if load_dotenv is not None:
        env_path = PROJECT_ROOT / '.env'
        if env_path.exists():
            load_dotenv(env_path)

    # Run migrations
    mm = MigrationManager()
    mm.migrate_up()
    ensure_schema_columns()

    async def run_ingest():
        # Calendar API ingest
        print(f"[1/3] Ingesting Google Calendar {start_date}..{end_date} (cal_ids={cal_ids})")
        try:
            from src.backend.parsers.google_calendar.ingest_api import ingest_to_database as gcal_ingest
            count = gcal_ingest(start_date, end_date, calendar_ids=cal_ids)
            print({"status": "success", "google_calendar_ingested": count})
        except Exception as e:
            print({"status": "error", "source": "google_calendar", "message": str(e)})

        # Notion API ingest (to notion_* tables only)
        print(f"[2/3] Ingesting Notion workspace → DB")
        try:
            from src.backend.parsers.notion.incremental_ingest import IncrementalNotionIngestor
            
            def progress_callback(msg):
                print(f"  {msg}")
            
            n_ing = IncrementalNotionIngestor(batch_size=5)  # Small batches to avoid timeouts
            result = n_ing.ingest_with_progress(
                max_pages=200,  # Limit pages for testing
                progress_callback=progress_callback
            )
            print(result)
        except Exception as e:
            print({"status": "error", "source": "notion", "message": str(e)})

        # Index Notion (abstracts + embeddings)
        processing = get_processing_service()
        print(f"[3/3] Indexing Notion abstracts + embeddings (all leaf blocks)")
        print(await processing.index_notion_blocks(scope="all"))

    asyncio.run(run_ingest())


if __name__ == '__main__':
    main()

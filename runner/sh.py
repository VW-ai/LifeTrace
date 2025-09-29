#!/usr/bin/env python3
"""
SmartHistory Unified Runner (one-point access)

Subcommands:
  - ingest: calendar, notion, or both (date-ranged for calendar)
  - index:  generate abstracts + embeddings for Notion blocks
  - process: run tagging for a date range, optional taxonomy pre-step
  - cleanup: remove/merge meaningless tags (supports date range scope)
  - api:     start FastAPI server
  - agent:   run agent modes (daily|insights|test)

Examples:
  python runner/sh.py ingest --calendar --start 2025-02-01 --end 2025-09-10
  python runner/sh.py process --start 2025-09-01 --end 2025-09-10 --taxonomy
  python runner/sh.py cleanup --start 2025-09-01 --end 2025-09-10 --dry-run
  python runner/sh.py index --scope recent --hours 48
  python runner/sh.py api --reload --host 0.0.0.0 --port 8080
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None  # type: ignore


def _load_env():
    if load_dotenv is not None:
        env_path = PROJECT_ROOT / '.env'
        if env_path.exists():
            load_dotenv(env_path)


def cmd_ingest(args: argparse.Namespace) -> int:
    from src.backend.database.schema.migrations import MigrationManager
    _load_env()
    mm = MigrationManager()
    mm.migrate_up()

    total = 0
    if args.calendar or (not args.calendar and not args.notion):
        from src.backend.parsers.google_calendar.ingest_api import ingest_to_database
        cal_ids = [c.strip() for c in (args.cal_ids or "primary").split(",") if c.strip()]
        print(f"[ingest:calendar] {args.start}..{args.end} cal_ids={cal_ids}")
        total += ingest_to_database(args.start, args.end, calendar_ids=cal_ids)

    if args.notion or (not args.calendar and not args.notion):
        # Default to incremental Notion ingestor (stores in notion_* tables only)
        try:
            from src.backend.parsers.notion.incremental_ingest import IncrementalNotionIngestor
            def progress(msg: str):
                print(f"  [notion] {msg}")
            ing = IncrementalNotionIngestor(batch_size=5)
            stats = ing.ingest_with_progress(progress_callback=progress)
            print({"status": "success", "notion": stats})
        except Exception as e:
            print({"status": "error", "source": "notion", "message": str(e)})
    return total


def cmd_index(args: argparse.Namespace) -> None:
    from src.backend.api.dependencies import get_processing_service
    _load_env()
    processing = get_processing_service()
    import asyncio
    print(asyncio.run(processing.index_notion_blocks(scope=args.scope, hours=args.hours)))


def _compute_only_new_date_range():
    """Compute [start, end] covering raw activities created after last processed_activities.created_at.
    Returns (start_date, end_date) or (None, None) if no delta.
    """
    from src.backend.database import get_db_manager
    db = get_db_manager()
    last_proc = db.execute_query("SELECT MAX(created_at) as ts FROM processed_activities")[0]['ts']
    if not last_proc:
        # Nothing processed yet; fallback to all available dates
        row = db.execute_query("SELECT MIN(date) as d, MAX(date) as m FROM raw_activities")[0]
        return row['d'], row['m']
    # Find min date of raw activities created after last_proc
    row = db.execute_query(
        "SELECT MIN(date) as d, MAX(date) as m FROM raw_activities WHERE datetime(created_at) > datetime(?)",
        [last_proc],
    )[0]
    if not row['d']:
        return None, None
    return row['d'], row['m']


def cmd_process(args: argparse.Namespace) -> None:
    from src.backend.api.dependencies import get_processing_service
    _load_env()

    date_start = args.start
    date_end = args.end
    if args.only_new and not (date_start or date_end):
        s, e = _compute_only_new_date_range()
        if not s:
            print("No new raw activities since last processing.")
            return
        date_start, date_end = s, e
        print(f"[process:only-new] computed range {date_start}..{date_end}")

    if args.taxonomy:
        try:
            from src.backend.agent.tools.taxonomy_builder import build_and_save
            print(build_and_save(date_start, date_end))
        except Exception as e:
            print({"status": "warn", "message": f"taxonomy build skipped: {e}"})

    processing = get_processing_service()
    import asyncio
    print(
        asyncio.run(
            processing.reprocess_date_range(
                date_start=date_start or "0001-01-01",
                date_end=date_end or "9999-12-31",
                regenerate_system_tags=bool(args.regenerate_system_tags),
            )
        )
    )


def cmd_cleanup(args: argparse.Namespace) -> None:
    from src.backend.database import get_db_manager
    from src.backend.agent.tools.tag_cleaner import TagCleaner
    _load_env()

    db = get_db_manager()
    cleaner = TagCleaner()
    result = cleaner.clean_meaningless_tags(
        db_manager=db,
        dry_run=args.dry_run,
        removal_threshold=args.removal_threshold,
        merge_threshold=args.merge_threshold,
        date_start=args.start,
        date_end=args.end,
    )
    print(result)


def cmd_api(args: argparse.Namespace) -> None:
    # Delegate to existing runner
    os.execvp(sys.executable, [sys.executable, str(PROJECT_ROOT / 'runner' / 'run_api.py')] + sys.argv[2:])


def cmd_agent(args: argparse.Namespace) -> None:
    os.execvp(sys.executable, [sys.executable, str(PROJECT_ROOT / 'runner' / 'run_agent.py')] + sys.argv[2:])


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="SmartHistory Unified Runner")
    sub = p.add_subparsers(dest="cmd", required=True)

    # ingest
    pi = sub.add_parser("ingest", help="Ingest sources into DB")
    pi.add_argument("--start", required=True, help="Start date YYYY-MM-DD (calendar)")
    pi.add_argument("--end", required=True, help="End date YYYY-MM-DD (calendar)")
    pi.add_argument("--calendar", action="store_true", help="Ingest Google Calendar only")
    pi.add_argument("--notion", action="store_true", help="Ingest Notion only")
    pi.add_argument("--cal-ids", default="primary", help="Comma-separated calendar IDs")
    pi.set_defaults(func=cmd_ingest)

    # index
    px = sub.add_parser("index", help="Index Notion abstracts + embeddings")
    px.add_argument("--scope", choices=["all", "recent"], default="all")
    px.add_argument("--hours", type=int, default=24, help="Recent window size if scope=recent")
    px.set_defaults(func=cmd_index)

    # process
    pp = sub.add_parser("process", help="Process + tag a date range")
    pp.add_argument("--start", help="Start date YYYY-MM-DD (optional)")
    pp.add_argument("--end", help="End date YYYY-MM-DD (optional)")
    pp.add_argument("--only-new", action="store_true", help="Compute range from last processed to newest raw")
    pp.add_argument("--taxonomy", action="store_true", help="Run taxonomy build before processing")
    pp.add_argument("--regenerate-system-tags", action="store_true")
    pp.set_defaults(func=cmd_process)

    # cleanup
    pc = sub.add_parser("cleanup", help="Clean meaningless tags (global or date-scoped)")
    pc.add_argument("--start", help="Start date YYYY-MM-DD (optional)")
    pc.add_argument("--end", help="End date YYYY-MM-DD (optional)")
    mode = pc.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--clean", action="store_true")
    pc.add_argument("--removal-threshold", type=float, default=0.8)
    pc.add_argument("--merge-threshold", type=float, default=0.6)
    pc.set_defaults(func=cmd_cleanup)

    # api
    pa = sub.add_parser("api", help="Start API server (delegates to run_api.py)")
    pa.add_argument("--host", default="127.0.0.1")
    pa.add_argument("--port", type=int, default=8000)
    pa.add_argument("--reload", action="store_true")
    pa.add_argument("--log-level", default="info")
    pa.set_defaults(func=cmd_api)

    # agent
    pg = sub.add_parser("agent", help="Run agent modes (delegates to run_agent.py)")
    pg.add_argument("--mode", choices=["daily", "insights"], help="Agent mode")
    pg.add_argument("--test", action="store_true")
    pg.add_argument("--output-dir")
    pg.set_defaults(func=cmd_agent)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

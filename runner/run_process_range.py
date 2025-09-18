#!/usr/bin/env python3
"""
SmartHistory Process Runner (Tagging only)

Runs ONLY the processing/tagging stage for a date range, so ingestion can be
debugged separately.

Usage:
  python runner/run_process_range.py --start 2025-02-01 --end 2025-09-10 [--regenerate-system-tags]
"""

import argparse
import os
import sys
from pathlib import Path
import asyncio

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None  # type: ignore

from src.backend.api.dependencies import get_processing_service
from src.backend.database.schema.migrations import MigrationManager


def main():
    parser = argparse.ArgumentParser(description="Process + tag a date range (no ingestion)")
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    parser.add_argument("--regenerate-system-tags", action="store_true", help="Allow system-wide tag regeneration")
    args = parser.parse_args()

    # Load env
    if load_dotenv is not None:
        env_path = PROJECT_ROOT / '.env'
        if env_path.exists():
            load_dotenv(env_path)

    # Prepare structured tagging log file (for observability)
    from datetime import datetime as _dt
    logs_dir = PROJECT_ROOT / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / f"tagging_run_{args.start}_to_{args.end}_{_dt.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    os.environ['TAGGING_LOG_FILE'] = str(log_file)
    print(f"Tagging log: {log_file}")

    # Migrations (ensure schema)
    mm = MigrationManager()
    mm.migrate_up()

    processing = get_processing_service()

    async def run_process():
        print(f"Reprocessing range {args.start}..{args.end} regenerate={args.regenerate_system_tags}")
        res = await processing.reprocess_date_range(
            date_start=args.start,
            date_end=args.end,
            regenerate_system_tags=bool(args.regenerate_system_tags)
        )
        print(res)

    asyncio.run(run_process())


if __name__ == '__main__':
    main()

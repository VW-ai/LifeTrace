#!/usr/bin/env python3
"""
SmartHistory Backfill Runner

Runs a two-layer backfill for a specified date range:
1) Backfill raw events (calendar, notion) and index Notion (abstracts + embeddings)
2) Purge + reprocess processed events for the same date range

Defaults: 2025-02-01 to 2025-09-10

Usage:
  python runner/run_backfill.py --start 2025-02-01 --end 2025-09-10

Notes:
- This script invokes service-layer methods directly (no HTTP server required).
"""

import argparse
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.api.dependencies import get_processing_service


def hours_since(date_str: str) -> int:
    d = datetime.strptime(date_str, "%Y-%m-%d")
    now = datetime.now()
    delta = now - d
    return max(1, int(delta.total_seconds() // 3600))


def months_between(start: str, end: str) -> int:
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    months = (e.year - s.year) * 12 + (e.month - s.month)
    if e.day >= s.day:
        months += 0
    return max(1, months)


def evaluate_metrics(db_path: str = "smarthistory.db") -> dict:
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT COUNT(*) AS n FROM processed_activities")
    pa = c.fetchone()["n"]
    c.execute(
        """
        SELECT COUNT(DISTINCT pa.id) AS n
        FROM processed_activities pa
        JOIN activity_tags at ON pa.id = at.processed_activity_id
        """
    )
    tagged = c.fetchone()["n"] if pa else 0
    c.execute(
        """
        SELECT AVG(tag_cnt) AS avg_tags,
               SUM(CASE WHEN tag_cnt > 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS multi_ratio
        FROM (
          SELECT pa.id, COUNT(at.id) AS tag_cnt
          FROM processed_activities pa
          LEFT JOIN activity_tags at ON pa.id = at.processed_activity_id
          GROUP BY pa.id
        )
        """
    )
    row = c.fetchone()
    avg_tags = row["avg_tags"] or 0.0
    multi_ratio = row["multi_ratio"] or 0.0
    return {
        "processed_activities": pa,
        "tagged_activities": tagged,
        "coverage_pct": round((tagged / pa * 100.0), 2) if pa else 0.0,
        "avg_tags_per_activity": round(avg_tags, 3),
        "multi_tag_ratio": round(multi_ratio, 3),
    }


def main():
    parser = argparse.ArgumentParser(description="Backfill 7 months (or specified range)")
    parser.add_argument("--start", default="2025-02-01", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default="2025-09-10", help="End date YYYY-MM-DD")
    args = parser.parse_args()

    start_date = args.start
    end_date = args.end

    print("=== SmartHistory Backfill Runner ===")
    print(f"Date range: {start_date} -> {end_date}")

    processing = get_processing_service()

    # Layer 1: backfill raw
    # Calendar backfill (approximate months between start and end)
    months = months_between(start_date, end_date)
    print(f"\n[1/5] Backfilling calendar for ~{months} months...")
    print(processing.backfill_calendar(months=months).result())  # type: ignore

    # Notion import for the range (hours since start)
    hours = hours_since(start_date)
    print(f"\n[2/5] Importing Notion edits for last {hours} hours...")
    print(processing.import_notion_data(type("Req", (), {"hours_since_last_update": hours})()).result())  # type: ignore

    # Index Notion (all)
    print("\n[3/5] Indexing Notion abstracts + embeddings (all leaf blocks)...")
    print(processing.index_notion_blocks(scope="all").result())  # type: ignore

    # Layer 2: purge + reprocess date range
    print(f"\n[4/5] Purge + reprocess processed activities in range {start_date}..{end_date}...")
    print(processing.reprocess_date_range(date_start=start_date, date_end=end_date).result())  # type: ignore

    # Metrics
    print("\n[5/5] Tagging metrics after backfill:")
    metrics = evaluate_metrics()
    for k, v in metrics.items():
        print(f"  - {k}: {v}")


if __name__ == "__main__":
    main()


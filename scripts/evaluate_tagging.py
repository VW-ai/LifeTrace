#!/usr/bin/env python3
"""
Evaluate Tagging Quality against the current SQLite database.

Metrics:
- processed_activities, tagged_activities, coverage_pct
- avg_tags_per_activity, multi_tag_ratio
- top tags by usage
- confidence histogram (0.0–1.0 buckets)

Usage:
  python scripts/evaluate_tagging.py [--db smarthistory.db]
"""

import argparse
import os
import sqlite3
from typing import List, Tuple


def query_db(db_path: str):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Processed count
    cur.execute("SELECT COUNT(*) AS n FROM processed_activities")
    processed = cur.fetchone()["n"]

    # Tagged activities
    cur.execute(
        """
        SELECT COUNT(DISTINCT pa.id) AS n
        FROM processed_activities pa
        JOIN activity_tags at ON pa.id = at.processed_activity_id
        """
    )
    tagged = cur.fetchone()["n"] if processed else 0

    # Avg tags per activity and multi-tag ratio
    cur.execute(
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
    row = cur.fetchone()
    avg_tags = row["avg_tags"] or 0.0
    multi_ratio = row["multi_ratio"] or 0.0

    # Top tags
    cur.execute(
        """
        SELECT t.name, COUNT(*) AS usage
        FROM activity_tags at
        JOIN tags t ON t.id = at.tag_id
        GROUP BY t.id
        ORDER BY usage DESC
        LIMIT 20
        """
    )
    top = [(r["name"], r["usage"]) for r in cur.fetchall()]

    # Confidence buckets
    cur.execute(
        """
        SELECT ROUND(confidence_score, 1) AS bucket, COUNT(*) AS cnt
        FROM activity_tags
        GROUP BY ROUND(confidence_score, 1)
        ORDER BY bucket
        """
    )
    conf = [(r["bucket"], r["cnt"]) for r in cur.fetchall()]

    return {
        "processed_activities": processed,
        "tagged_activities": tagged,
        "coverage_pct": round((tagged / processed * 100.0), 2) if processed else 0.0,
        "avg_tags_per_activity": round(avg_tags, 3),
        "multi_tag_ratio": round(multi_ratio, 3),
        "top_tags": top,
        "confidence_buckets": conf,
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate tagging metrics")
    parser.add_argument("--db", default="smarthistory.db", help="Path to SQLite database")
    args = parser.parse_args()

    metrics = query_db(args.db)
    print("=== Tagging Evaluation ===")
    print(f"Database: {os.path.abspath(args.db)}")
    for k in [
        "processed_activities",
        "tagged_activities",
        "coverage_pct",
        "avg_tags_per_activity",
        "multi_tag_ratio",
    ]:
        print(f"{k}: {metrics[k]}")
    print("top_tags:")
    for name, cnt in metrics["top_tags"]:
        print(f"  - {name}: {cnt}")
    print("confidence_buckets:")
    for bucket, cnt in metrics["confidence_buckets"]:
        print(f"  - {bucket}: {cnt}")


if __name__ == "__main__":
    main()


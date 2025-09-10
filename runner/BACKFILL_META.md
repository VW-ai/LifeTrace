# Backfill Runner

Purpose
- Run a complete two-layer backfill for a date range:
  1) Backfill raw events (calendar, notion) and index Notion (abstracts + embeddings)
  2) Purge + reprocess processed activities for that date range

Script
- `runner/run_backfill.py`

Usage
```
python runner/run_backfill.py --start 2025-02-01 --end 2025-09-10
```

Details
- Calendar backfill uses an approximate month count between start and end dates.
- Notion import uses hours since `start` to include the full range.
- Indexing runs on all leaf blocks to ensure retrieval is effective.
- Reprocessing purges processed_activities in range (cascading activity_tags) and re-runs processing for the window.
- Prints tagging metrics at the end.

Notes
- Ensure API dependencies and DB are configured. Server not required; script calls service layer directly.
- `HISTORY_PAGE_ID` can be set via env to guide Notion scoping (future step).


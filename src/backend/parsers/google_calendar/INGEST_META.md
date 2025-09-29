# Google Calendar API Ingestion (DB-only)

Purpose
- Fetch events by date range and write to `raw_activities` without any JSON files.

Usage
- `ingest_to_database(start_date: 'YYYY-MM-DD', end_date: 'YYYY-MM-DD', calendar_ids?: string[])`
- Reads OAuth creds from `credentials.json` and `token.json` at repo root.

Notes
- Requires `google-api-python-client` and `google-auth` libraries.
- Uses timezone-aware RFC3339 times and computes duration from start/end.
- Stores full event JSON in `raw_data` for traceability.


# Runner Folder META

Purpose
- Operational entrypoints for SmartHistory: ingestion, indexing, processing, API/agent startup, utilities, and deployment wrappers. Scripts are thin orchestrators; business logic lives under `src/backend/**` per atomicity.

Prerequisites
- Python environment active, dependencies installed, `.env` present with required keys (e.g., `OPENAI_API_KEY`, Notion/Google creds). Database file `smarthistory.db` accessible. Use `runner` from project root.

Scripts
- `sh.py` — Unified CLI (one-point access).
  - Ingest: `python runner/sh.py ingest --start YYYY-MM-DD --end YYYY-MM-DD [--calendar|--notion] [--cal-ids primary,team@org]`
  - Index: `python runner/sh.py index [--scope all|recent] [--hours 24]`
  - Process: `python runner/sh.py process [--start ...] [--end ...] [--only-new] [--taxonomy] [--regenerate-system-tags]`
  - Cleanup: `python runner/sh.py cleanup [--start ...] [--end ...] (--dry-run | --clean) [--removal-threshold 0.8] [--merge-threshold 0.6]`
  - API: `python runner/sh.py api [--host ...] [--port ...] [--reload]`
  - Agent: `python runner/sh.py agent --mode daily|insights | --test`
  - Notes: Calendar ingest deduplicates by event id/link+time; Notion upserts by page/block id into notion tables (no Notion entries in raw_activities). Cleanup supports date-scoped operations without global tag deletion.

- `run_backfill.py` — End‑to‑end backfill for a date window.
  - Usage: `python runner/run_backfill.py --start YYYY-MM-DD --end YYYY-MM-DD`
  - Steps: migrations → GCal ingest → Notion ingest → index abstracts+embeddings → purge+reprocess range → metrics.

- `run_ingest.py` — Ingest only (no tagging) and index Notion.
  - Usage: `python runner/run_ingest.py --start YYYY-MM-DD --end YYYY-MM-DD [--cal-ids primary,team@org]`
  - Ensures schema/columns; ingests Google Calendar; ingests Notion (incremental); indexes Notion leaf blocks.

- `run_process_range.py` — Processing/tagging only for a date window.
  - Usage: `python runner/run_process_range.py --start YYYY-MM-DD --end YYYY-MM-DD [--regenerate-system-tags]`
  - Writes structured log to `logs/tagging_run_*.jsonl`.

- `run_google_calendar_ingest.py` — Focused Google Calendar DB ingest.
  - Usage: `python runner/run_google_calendar_ingest.py --start YYYY-MM-DD --end YYYY-MM-DD [--cal-ids primary,other@gmail.com]`
  - Runs migrations and ensures raw activity columns, then ingests events.

- `run_build_taxonomy.py` — Build AI‑driven tag taxonomy and synonyms.
  - Usage: `python runner/run_build_taxonomy.py [--start YYYY-MM-DD] [--end YYYY-MM-DD]`
  - Outputs under `src/backend/agent/resources/`.

- `run_tag_cleanup.py` — Analyze/clean meaningless tags; merge similar tags.
  - Usage: `python runner/run_tag_cleanup.py --dry-run` or `--clean` with thresholds `--removal-threshold` and `--merge-threshold`.

- `run_parsers.py` — Database‑first parsers (no JSON intermediates).
  - Usage: `python runner/run_parsers.py`
  - Populates DB from Google Calendar and Notion via parser modules.
  - Status: legacy; prefer `sh.py ingest`.

- `run_api.py` — Start FastAPI backend.
  - Usage: `python runner/run_api.py [--host 0.0.0.0] [--port 8080] [--reload]`
  - Serves `src.backend.api:get_api_app`; checks DB connectivity on start.

- `run_agent.py` — Convenience wrapper (DB-first processing).
  - Usage: `python runner/run_agent.py [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--regenerate-system-tags]` or `--test`
  - Delegates to processing service. Insights generation here is deprecated.

- `deploy.sh` — Deployment helper (local, docker, production, aws).
  - Usage: `bash runner/deploy.sh [local|docker|production|aws]`
  - Requires platform CLIs; see script output for endpoints.

Interactions
- Most scripts import `get_processing_service()` and/or parser/ingestor modules under `src/backend/**`. Schema migrations run via `MigrationManager`. Notion indexing targets leaf blocks for abstracts and embeddings.

Notes
- Keep scripts minimal and single‑purpose; place substantive logic in `src/` and update this META when adding/modifying scripts. Prefer flags over hard‑coding to maintain testability and reuse.

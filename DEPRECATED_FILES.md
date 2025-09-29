# Deprecated Files (Tracking)

Purpose
- Track files no longer needed in the current DB‑first backend design so we can remove them safely after a short migration window. This list is curated using the runner scripts as the canonical entry points.

Fully deprecated (remove after docs/tests adjust)
- `runner/run_parsers.py`
  - Reason: Legacy parser runner. Superseded by `runner/sh.py ingest` and `runner/run_ingest.py` (API‑based ingests). Docs still reference it and should be updated.
- `src/backend/parsers/google_calendar/parser.py`
  - Reason: File‑based JSON parser. Superseded by `src/backend/parsers/google_calendar/ingest_api.py`.
- `src/backend/parsers/notion/parser.py`
  - Reason: File‑based JSON parser. Superseded by `src/backend/parsers/notion/incremental_ingest.py` that writes to notion tables used for context retrieval.
- `src/backend/agent/core/agent.py`
  - Reason: Implements file‑based daily/insights flows no longer used. The DB‑first flow runs via `processing.reprocess_date_range` (see `runner/sh.py process` and `runner/run_agent.py`). Keep `ActivityProcessor` and other core classes in `agent/core`.

Candidates (partial deprecations / function‑level)
- `src/backend/agent/__init__.py`
  - Deprecate re‑exports: `run_daily_processing`, `run_insights_generation` (file‑based). Keep models, `ActivityProcessor`, `TagGenerator`, prompts re‑exports.
- `runner/run_backfill.py`
  - Consider deprecating in favor of `runner/sh.py ingest` + `runner/sh.py process` (same steps with more control). Keep temporarily if needed for muscle memory; mark as deprecated in file header.

Not deprecated, but must be refactored away from legacy parsers
- `src/backend/api/services.py`
  - Methods using file parsers must switch to API‑based ingests:
    - Calendar: `parsers.google_calendar.ingest_api.ingest_to_database(start, end, calendar_ids=...)`
    - Notion: `parsers.notion.incremental_ingest.IncrementalNotionIngestor(...).ingest_with_progress(...)`
  - Keep `index_notion_blocks` and `reprocess_date_range` as they are.

Documentation updates required
- References to `runner/run_parsers.py` in:
  - `README.md`
  - `src/backend/README.md`
  - `src/backend/API_QUICKSTART.md`
  - `META/PROGRESS.md`

Notes
- Runners that represent the canonical flow: `runner/sh.py`, `runner/run_ingest.py`, `runner/run_process_range.py`, `runner/run_build_taxonomy.py`, `runner/run_tag_cleanup.py`, `runner/run_api.py`.
- Deployment: `runner/deploy.sh` starts backend via a non‑existent `start.py`; update to use `python runner/run_api.py --reload` instead of deprecating the script.


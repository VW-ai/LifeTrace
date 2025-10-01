# API/Frontend Data Mismatch Diagnosis

Author: Codex CLI assistant
Date: 2025-09-01

## Summary
- The frontend dashboard shows “No activity data” despite having data in SQLite.
- Root causes are twofold:
  1) Backend reads from an empty DB file (`src/backend/smarthistory.db`) while the populated DB appears to be at project root (`smarthistory.db`).
  2) Frontend↔API contract mismatches (query param names and response shapes) cause the dashboard to drop/ignore valid data.

## Symptoms
- Frontend at `http://localhost:5174/` renders without activities; charts show empty states.
- Backend running at `http://localhost:8000` returns 200 for endpoints but with empty `activities` arrays.

## Findings

### 1) Database path mismatch
- Backend DB manager default path: `src/backend/database/core/config.py`
  - `ConnectionConfig.db_path` defaults to `"smarthistory.db"` (relative to backend working dir), resulting in an on-disk DB at `src/backend/smarthistory.db` when run via backend scripts.
- Observed counts (via local inspection):
  - `src/backend/smarthistory.db`: `raw_activities = 0`, `processed_activities = 0`.
  - Root `smarthistory.db`: likely contains your populated data (frontend expectation), but the API is not pointing at it.
- Effect: API queries empty tables → frontend sees no activities.

### 2) Frontend/API contract mismatches
- Endpoint base and params
  - Frontend client (`src/frontend/src/api/client.ts`) uses `/activities/processed` etc., but sends `start_date`/`end_date` query params.
  - Backend (`src/backend/api/server.py`) expects `date_start`/`date_end` for both raw and processed activities.
  - Result: date filters are ignored. Not strictly breaking, but misleading and inconsistent.

- Response shape differences (Processed Activities):
  - Backend model (`ProcessedActivityResponse` in `src/backend/api/models.py`):
    - `total_duration_minutes` (number)
    - `combined_details` (string)
    - `tags` is `TagResponse[]` (objects with `name`, `color`, etc.)
  - Frontend `ProcessedActivity` interface (`src/frontend/src/api/client.ts`) expects:
    - `duration_minutes` (not `total_duration_minutes`)
    - `description` (not `combined_details`)
    - `tags?: string[]` (not objects)
  - Dashboard (`src/frontend/src/components/dashboard/Dashboard/Dashboard.tsx`) then reads:
    - `activity.duration_minutes` (undefined → 0 during math)
    - Treats `activity.tags` as an array of strings when aggregating.
  - Result: even if activities exist, computations reduce to empty/NaN and charts stay empty.

- Pagination envelope differences (Tags):
  - Backend returns `{ tags, total_count, page_info }`.
  - Frontend `getTags()` currently returns entire response, and the consumer expects a flat `Tag[]`.

## Verification Steps
1) Verify backend DB file currently in use:
   - If started via `src/backend/start.py`, the path resolves to `src/backend/smarthistory.db`.
   - Check counts:
     - `sqlite3 -line src/backend/smarthistory.db "SELECT COUNT(*) AS c FROM processed_activities;"`
     - `sqlite3 -line src/backend/smarthistory.db "SELECT COUNT(*) AS c FROM raw_activities;"`
2) Check API payload shape (confirm field names):
   - `curl http://localhost:8000/api/v1/activities/processed`
   - Note keys: `total_duration_minutes`, `combined_details`, `tags: [{ name, ...}]`.
3) Check frontend client requests:
   - `src/frontend/src/api/client.ts` uses `start_date`/`end_date` and returns raw response without mapping.

## Fix Plan

### A) Align the API to the populated database
Pick one option:
- Option A1 (simple): Copy the populated root DB over the backend DB path.
  - `cp smarthistory.db src/backend/smarthistory.db`
  - Pros: No code change. Cons: Forgets the “single source of truth” if both files diverge.

- Option A2 (recommended): Make DB path configurable and point to the root DB.
  - Add env var support, e.g., `SMARTHISTORY_DB_PATH` read by the DB layer.
  - Where: `src/backend/database/core/config.py` or `src/backend/database/__init__.py:get_db_manager()`.
  - Example change: If `os.getenv('SMARTHISTORY_DB_PATH')` is set, use that path in `ConnectionConfig`.
  - Then set `SMARTHISTORY_DB_PATH=../smarthistory.db` when running API from backend dir.

### B) Normalize frontend client to backend contracts
In `src/frontend/src/api/client.ts`:
- Use backend param names:
  - Replace `start_date` → `date_start`, `end_date` → `date_end` in both raw and processed activity requests.
- Map backend responses to the frontend’s expected shape:
  - Processed activities mapping:
    - `duration_minutes = total_duration_minutes`
    - `description = combined_details`
    - `tags = (tags || []).map(t => t.name)`
  - Return only the `tags` array from `/tags` response (`data.tags`) to callers expecting `Tag[]`.
- Alternatively, update the frontend types and Dashboard to use backend names directly. Mapping in the client keeps the rest of the app unchanged.

### C) Optional: Update Dashboard calculations
If you prefer not to map on the client:
- Update `Dashboard.tsx` to use:
  - `activity.total_duration_minutes` instead of `activity.duration_minutes`
  - `Array.isArray(activity.tags) ? activity.tags.map(t => t.name) : activity.tags` when aggregating.

## Risks & Notes
- Copying DB (A1) risks divergence if both files are used; prefer config (A2).
- Ensure CORS origins include `http://localhost:5174` (they do by default via `config.CORS_ORIGINS`).
- Frontend `environment.ts` already detects API base as `http://localhost:8000/api/v1` locally.

## Concrete Changes (proposed)
1) Backend DB path env support:
   - Read `SMARTHISTORY_DB_PATH` in DB config and pass into `ConnectionConfig`.
2) Frontend API client mapping:
   - Fix query param names to `date_start`/`date_end`.
   - Transform processed activity objects to expected shape.
   - Return `data.tags` from `getTags()`.

## Quick Test After Fix
1) Start API and frontend.
2) Hit `http://localhost:8000/api/v1/activities/processed` and confirm non-empty `activities`.
3) Refresh `http://localhost:5174/` and confirm:
   - Metrics show non-zero counts/hours.
   - Area and Pie charts render with data.


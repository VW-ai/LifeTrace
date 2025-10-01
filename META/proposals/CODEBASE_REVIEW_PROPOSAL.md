# SmartHistory Codebase Review Proposal

Scope: end-to-end review of backend (API, database, agent), frontend, runner scripts, and repo organization. This proposal highlights discrepancies vs. design, redundancies, consistency gaps, and coding-practice issues, with prioritized recommendations.

## Summary of Top Priorities
- Enforce API auth and rate limiting per design; wire dependencies on routes (P1).
- Fix DB last-insert ID retrieval to avoid race/mismatch (P1).
- Correct schema mismatch in joins (`activity_tags.processed_activity_id`) (P1).
- Remove blocking subprocess calls from API; run imports/processing as background jobs (P1).
- Standardize environment flags and config usage (`ENVIRONMENT` vs `SMARTHISTORY_ENV`) (P1).

- Unify DAO usage vs raw SQL; avoid brittle SQL string assembly (P2).
- Normalize error handling (raise HTTPException consistently; map service errors) (P2).
- Replace mutable Pydantic defaults with default_factory (P2).
- Consolidate tests and retire legacy scripts/paths (P2).

- Remove sys.path hacks; use proper package imports (P3).
- Tighten production security (TrustedHost, CORS, rate limiter storage) (P3).

---

## 1) Discrepancies (Design vs Implementation)

- API authentication and rate limiting not enforced on endpoints
  - Design: API_DESIGN.md and api_META.md specify API key auth and per-endpoint-type rate limits.
  - Implementation: `auth.get_api_key` and `check_rate_limit` exist but are not applied to routes in `api/server.py`.
  - Impact: Production endpoints are unauthenticated and unthrottled.
  - Recommendation: Add `Depends(get_api_key)` on all routes; apply `Depends(lambda: check_rate_limit('<type>'))` on processing/import routes. Gate behavior using `config.ENVIRONMENT`.

- Environment flag mismatch
  - Design/Config: `config.py` uses `ENVIRONMENT`.
  - Implementation: `auth.py` uses `SMARTHISTORY_ENV` to bypass auth; tests set `SMARTHISTORY_ENV`.
  - Impact: Confusing behavior between modules; auth bypass may persist unexpectedly.
  - Recommendation: Standardize on `ENVIRONMENT` (via `get_config()`), deprecate `SMARTHISTORY_ENV`.

- Schema mismatch in service query
  - Design/Schema: `activity_tags` has `processed_activity_id`.
  - Implementation: `TagService.get_tag_coverage_stats` joins on `at.activity_id`.
  - Impact: Incorrect / empty join results; coverage stats become wrong.
  - Recommendation: Replace with `at.processed_activity_id`.

- Import endpoints ignore request semantics and use wrong path
  - Design: `/import/calendar` and `/import/notion` accept parameters and reflect status.
  - Implementation: `ProcessingService.import_calendar_activities` calls a subprocess with a miscomputed path (`src/import_calendar_data.py` vs repo-root `import_calendar_data.py`), and ignores request body params.
  - Impact: Fails to run in deployed API; request options unused.
  - Recommendation: Use `PROJECT_ROOT / 'import_calendar_data.py'`; plumb `hours_since_last_update` from `ImportRequest`. Prefer background task manager.

- Trusted hosts and CORS in production
  - Design: “Industry-ready with dynamic configuration”.
  - Implementation: `TrustedHostMiddleware` allows `['*']` in production; permissive CORS defaults.
  - Impact: Weaker security posture.
  - Recommendation: Parameterize allowed hosts and CORS from `APIConfig`; default-secure in production.

- Async endpoints with sync DB access
  - Design: FastAPI async endpoints.
  - Implementation: DB access uses synchronous sqlite3 in async handlers.
  - Impact: Event loop blocking under load.
  - Recommendation: Use threadpool (`anyio.to_thread.run_sync`) wrappers or adopt async DB access layer for production.

- Legacy JSON path retained despite DB-first design
  - Design: “Database-first, no JSON intermediate files”.
  - Implementation: `ActivityProcessor.process_daily_activities` still supports JSON I/O path.
  - Impact: Extra surface area and confusion.
  - Recommendation: Keep behind an explicit, documented legacy flag or remove.

## 2) Redundancies and Simplifications

- Duplicate test trees and feature tests
  - Observed: `src/backend/tests/...`, `tests/backend/...`, `test_features/...`, and `src/backend/test_features/...` coexist.
  - Impact: Fragmented coverage, slower CI, confusion.
  - Recommendation: Consolidate under a single `tests/` tree; migrate/merge and deprecate others. Align pytest config.

- Mixed DAO and raw SQL usage in `api/services.py`
  - Observed: Tag operations use DAOs; activity endpoints handcraft SQL.
  - Impact: Inconsistent abstraction; more code paths to maintain.
  - Recommendation: Introduce DAOs for read paths or central query helpers; favor DAOs for consistency.

- Multiple runner scripts and root scripts overlapping API capability
  - Observed: `regenerate_tags*.py`, `import_calendar_data.py`, and API management endpoints overlap.
  - Impact: Duplication and divergent behavior.
  - Recommendation: Move scripts into `scripts/` and have API call shared library functions; document single source of truth.

- Frontend `templateLook/` directory
  - Observed: Large set of template components not wired to `src/frontend/src`.
  - Impact: Repo weight and cognitive load.
  - Recommendation: Archive to a separate branch or move under `examples/` with a clear note.

- sys.path manipulation in multiple modules
  - Observed: Several modules push project root into `sys.path`.
  - Impact: Hidden import coupling; harder packaging.
  - Recommendation: Use proper package-relative imports; ensure runner sets PYTHONPATH or install as editable package.

## 3) Consistency Gaps (Iteration Drift)

- Error handling strategy
  - Observed: Some service methods raise `HTTPException` (create_tag), others raise `ValueError` (update_tag), others return dicts-on-error. Global 500 handler masks details.
  - Impact: Inconsistent API error responses and codes.
  - Recommendation: Services raise domain exceptions; API layer maps to consistent `ErrorResponse`. Use 4xx vs 5xx appropriately.

- Pydantic model defaults
  - Observed: Mutable defaults like `tags: List[...] = []`, `raw_data: Dict[...] = {}` in `models.py`.
  - Impact: Shared state bugs.
  - Recommendation: Use `Field(default_factory=list/dict)`.

- Parameter validation vs SQL construction
  - Observed: Building WHERE/AND fragments via string replacement for `get_processed_activities`.
  - Impact: Brittle queries, hard-to-extend filters.
  - Recommendation: Structured clause assembly; or hand it to DAO with explicit parameters.

- Table/column naming consistency in queries
  - Observed: `activity_id` vs `processed_activity_id` mismatch.
  - Impact: Runtime bugs.
  - Recommendation: Centralize constants or use an ORM/Query builder to avoid typos.

- Environment and config usage
  - Observed: `ENVIRONMENT` vs `SMARTHISTORY_ENV` split; mixed use of `config` and raw env reads.
  - Impact: Non-deterministic behavior.
  - Recommendation: Read all env via `APIConfig`; pass into modules as needed.

## 4) Coding Practices

- Last inserted ID retrieval is unsafe across pooled connections
  - Observed: DAOs fetch `SELECT last_insert_rowid()` on a separate pooled connection.
  - Impact: Wrong IDs possible; race conditions.
  - Recommendation: Modify `TransactionManager.execute_update` to return `cursor.lastrowid`; have DAO `create()` use that return value. Alternatively expose a `execute_insert` method returning lastrowid.

- Blocking subprocess calls in API thread
  - Observed: `import_calendar_activities` uses `subprocess.run(..., timeout=300)`.
  - Impact: Blocks event loop worker; timeouts under load.
  - Recommendation: Offload to background tasks (FastAPI `BackgroundTasks`, Celery/RQ, or asyncio.create_task with proper lifecycle).

- Rate limiter is in-memory and not thread/process safe
  - Observed: `_rate_limiter` stores counters in a plain dict without locks; per-process only.
  - Impact: Race conditions and porous enforcement with multiple workers.
  - Recommendation: Use a shared store (Redis) or a library like `fastapi-limiter`. At minimum, add a lock and document single-worker limitation.

- SQL composition and potential injection
  - Observed: Manual string assembly for clauses; parameters are mostly bound, but clause assembly is brittle.
  - Impact: Maintenance risk; security footgun if future filters are not bound.
  - Recommendation: Centralize query building with parameter binding; or adopt SQLAlchemy Core/ORM.

- Inconsistent time parsing/serialization
  - Observed: Conversions via `datetime.fromisoformat` on strings coming from SQLite; some models pass datetimes directly.
  - Impact: Surprises on timezone/format; mixed types.
  - Recommendation: Normalize to ISO 8601 strings in API models; ensure DB adapters use consistent format.

- Trusted hosts and CORS defaults
  - Observed: `allowed_hosts=['*']` in production; `CORS_HEADERS/METHODS=['*']`.
  - Impact: Weaker production security.
  - Recommendation: Configure from env and default to restrictive in prod.

- sys.path modification
  - Observed: Multiple files manipulate `sys.path`.
  - Impact: Fragile imports.
  - Recommendation: Use package-relative imports and a single entry-point configuration.

---

## Concrete Fix Plan (Phased)

Phase 1 (Correctness & Security)
- Wire API auth and rate limiting
  - Add `Depends(get_api_key)` to all routes; add `check_rate_limit('processing'|'import')` to relevant endpoints.
  - Replace `SMARTHISTORY_ENV` checks with `config.ENVIRONMENT`.

- Fix DB lastrowid pattern
  - Update `TransactionManager.execute_update` to return `(affected_rows, lastrowid)` or expose `execute_insert`.
  - Update all DAO `create()` methods to rely on returned lastrowid (remove separate `SELECT last_insert_rowid()`).

- Fix schema mismatch
  - Replace `at.activity_id` with `at.processed_activity_id` in `TagService.get_tag_coverage_stats`.

- Correct import script path and offload processing
  - Resolve script path via `PROJECT_ROOT`.
  - Switch to background tasks; surface job IDs via `/process/status`.

Phase 2 (Consistency & Cleanup)
- Standardize service/DAO usage and SQL building
  - Add DAO methods for activity reads with filters; remove brittle WHERE/AND string hacks.

- Normalize error handling and responses
  - Create exception classes (ValidationError, ConflictError); map to consistent `ErrorResponse`.

- Pydantic models: default_factory and stricter types
  - Replace mutable defaults; ensure model_config and validators reflect intended contract.

- Consolidate tests and scripts
  - Move all tests under `tests/`; deprecate duplicate trees. Move root scripts to `scripts/` and consume shared lib code.

Phase 3 (Hardening & DX)
- Imports/package hygiene
  - Remove `sys.path` hacks; rely on relative imports and an editable install (`pip install -e .`) or `PYTHONPATH` from runners.

- Production security posture
  - Restrict `TrustedHostMiddleware` and CORS; document env vars; set safe defaults.

- Async DB or threadpool execution
  - Wrap sync DB calls with `run_in_threadpool` or adopt an async driver for production.

---

## Quick Wins (Low-Risk PRs)
- Replace `at.activity_id` in `get_tag_coverage_stats`.
- Switch Pydantic mutable defaults to `default_factory`.
- Align `auth.py` to use `config.ENVIRONMENT` and deprecate `SMARTHISTORY_ENV`.
- Fix import script path using `PROJECT_ROOT` and add basic background task.
- Add `Depends(get_api_key)` to routes when `ENVIRONMENT == 'production'`.

## Follow-ups
- Evaluate moving to SQLAlchemy Core/ORM with async support.
- Add API integration tests that cover auth and rate limiting.
- Add CI to run consolidated tests and linting.

---

## Noted Files/Lines (for implementers)
- `src/backend/api/services.py`
  - Tag coverage join: uses `at.activity_id` (should be `processed_activity_id`).
  - Subprocess import path resolves to `src/import_calendar_data.py` but script lives at repo root.
  - Mixed DAO and raw SQL; brittle WHERE/AND building in activities queries.

- `src/backend/api/server.py`
  - Endpoints do not include auth/rate limit dependencies.
  - Production `TrustedHostMiddleware` allows `['*']`.

- `src/backend/api/models.py`
  - Mutable defaults (`{}`, `[]`) on Pydantic models.

- `src/backend/api/auth.py`
  - Uses `SMARTHISTORY_ENV`; standardize on `ENVIRONMENT` via `get_config()`.
  - In-memory rate limiter without locks/shared store.

- `src/backend/database/access/models.py` and DAOs
  - Use of `SELECT last_insert_rowid()` on a different pooled connection; should return `cursor.lastrowid` from the same operation.

- Test layout: multiple roots (`src/backend/tests`, `tests/backend`, `test_features`, `src/backend/test_features`).

- Multiple modules modify `sys.path` to import from project root.

---

Prepared by: Codebase review (backend, frontend, repo) with emphasis on security, correctness, and maintainability.


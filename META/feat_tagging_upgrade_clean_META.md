# Tagging Upgrade (Clean) - Plan

Branch: `feat/tagging_upgrade_clean` (from `main`)

Objective
- Deliver equivalent or improved tagging functionality with a cleaner codebase.
- Prioritize code sanity and development ergonomics; follow REGULATION.md.

Scope (Phase 1 - Implemented)
- Safe DB inserts: use same-cursor `lastrowid` via `execute_insert`; update DAOs.
- Pydantic model defaults: replace mutable defaults with `default_factory`.
- Correctness review of joins and paths. (No `activity_id` mismatch in main.)
- Add evaluation script `scripts/evaluate_tagging.py` to baseline tagging metrics.

Metrics Baseline
- Coverage: ~100%
- Avg tags/activity: ~1.05
- Multi-tag ratio: ~0.046
- Dominant tag: `work`
- Confidence mostly at ~0.5, with many low buckets (0.1–0.2)

Next (Phase 2)
- Improve TagGenerator scoring:
  - Thresholding (>0.5), top-N (1–3) tags
  - Synonym/taxonomy weighting; reduce `work` over-assignment
  - Source-aware heuristics (calendar title vs notion body)
  - Configurable calibration JSON
- Evaluate again, target:
  - Avg tags/activity ≥ 1.3
  - Multi-tag ratio ≥ 0.2
  - Confidence distribution centered ≥ 0.5

Next (Phase 3)
- Unify service queries behind DAOs; remove brittle SQL clause stitching.
- Background tasks for heavy work (processing/import), avoid blocking in API.
- Remove `sys.path` hacks gradually; rely on package-relative imports and runners.

Testing
- Consolidate under `tests/` in future PR; add tagging metrics tests and DAO insert tests.


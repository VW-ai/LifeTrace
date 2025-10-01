# Milestone 2 — Agent Intelligence & Production Readiness

This document defines the scope, deliverables, and plan for Milestone 2. It operationalizes the next-stage improvements called out in PRODUCT.md, DESIGN.md, and PROGRESS.md, focusing on AI agent quality, data enrichment, tagging, review workflows, and light production readiness.

## Objectives
- Increase match accuracy between Notion edits and Calendar events.
- Produce meaningful, reusable tags using a controlled taxonomy with confidences.
- Enrich weak events with context to improve processing quality.
- Add confidence-driven review workflows for human oversight.
- Instrument quality metrics and surface them in the dashboard/API.
- Prepare for limited external demo deployment with privacy controls.

## Scope
1) AI Agent Enhancements (matching, tagging, inference)
2) Data Enrichment (parsers and priors)
3) Tag Taxonomy + Synonyms (governed vocabulary)
4) Review UI + Rules (human-in-the-loop)
5) Metrics & Monitoring (quality signals)
6) Minimal Production Readiness (auth, privacy toggles, reprocessing)

## Deliverables
- Enriched parsers for Notion/Calendar (additional context in `RawActivity.raw_data`).
- Upgraded `ActivityMatcher` with TF‑IDF cosine similarity and configurable time window.
- Tagging pipeline using a taxonomy-first prompt + rule-based fallback + confidence scoring.
- New data artifacts: `tag_taxonomy.json`, `synonyms.json` (versioned config).
- Confidence and review flags persisted; API filters and minimal UI to manage them.
- Metrics endpoints and dashboard cards for merge rate, coverage, and entropy.

## Technical Plan

### 1) Data Enrichment
- Notion: capture parent page titles, database properties, relations, breadcrumbs, inline tags/mentions; store in `raw_data`.
- Calendar: capture description, attendees, location, recurrence metadata; store in `raw_data`.
- Project memory: maintain “project dictionary” (top keywords, typical tags, time-of-day patterns) used as priors during tagging.

### 2) Activity Matching Improvements
- Content similarity: switch from Jaccard to TF‑IDF cosine (fallback to current if unavailable).
- Synonyms map (e.g., oauth~authentication, gym~workout) applied during normalization.
- Temporal tolerance: widen date window (±1 → ±2–3 days), normalize timezones; parameterize in matcher.
- Session clustering: group raw events by proximity (≤45 min gaps), match at session level when beneficial.
- Confidence model: weighted sum of time proximity, cosine similarity, keyword overlap, and project prior; persist `raw_data.match_confidence`.

### 3) Tagging Enhancements
- Taxonomy-first: define 12–20 top-level tags (work, meetings, coding, study, exercise, social, admin, errands, health, reading, planning, commute, hobby), optional sub-tags.
- Prompt updates: inject taxonomy and examples into `TagPrompts`; request tags with confidences and short reasons.
- Fallback heuristics: rule-based keyword/synonym mapping to taxonomy for offline or low-confidence cases.
- Post-processing: fuzzy map freeform tags to taxonomy; collapse near-duplicates.

### 4) Confidence-Driven Review
- Mark `ProcessedActivity.is_review_needed` for low-confidence matches/tags or taxonomy violations.
- API: filter by `review_needed=true` to power a simple “Review Inbox”.
- UI: accept/adjust suggestions; bulk merge/rename tags; map freeform → taxonomy.

### 5) Metrics & Monitoring
- Track and expose: `merge_rate`, `avg_match_confidence`, `top_tag_coverage`, `tag_entropy`, `review_queue_size`.
- API: surface in `/api/v1/system/stats` (and a dedicated insights endpoint if needed).
- Frontend: add metric cards to dashboard; show trend over time.

### 6) Minimal Production Readiness
- Auth for protected endpoints (API key already supported; extend where needed).
- Privacy: local processing toggle, PII scrubbing of emails/URLs in stored details.
- Reprocessing: allow batch reprocessing for selected time ranges; show progress and a summary diff.

## Data & API Changes (Design)
- Database (proposed):
  - `tags`: optional `parent_tag_id` or `category` field to support hierarchy.
  - `activity_tags`: add `confidence` (float 0–1).
  - `processed_activities`: add `is_review_needed` (boolean).
- API:
  - `GET /api/v1/activities/processed?review_needed=true` (filter).
  - `GET/PUT /api/v1/taxonomy` (read/update taxonomy and synonyms; behind auth).
  - Extend `/api/v1/system/stats` with metrics above.

## Files to Add
- `src/backend/agent/resources/tag_taxonomy.json` — canonical tags (+ optional hierarchy).
- `src/backend/agent/resources/synonyms.json` — normalization and equivalence mapping.
- Tests covering parser enrichment, matcher similarity, and tagging fallback.

## Phased Execution
- Phase 1 (high impact, 1–2 sessions):
  - Implement taxonomy + synonyms; integrate into prompts and fallback mapper.
  - Upgrade `ActivityMatcher` with TF‑IDF cosine + configurable date window; add synonyms normalization.
  - Enrich Notion/Calendar parsers with parent/context fields in `raw_data`.
  - Instrument basic metrics (merge rate, tag coverage) and log to console/API.

- Phase 2:
  - Add `confidence` to `activity_tags` and `is_review_needed` to `processed_activities`; wire API filters.
  - Minimal Review Inbox in frontend; bulk tag merge/rename.
  - Dashboard cards for quality metrics; surface low-confidence counts.

- Phase 3:
  - Session clustering, project priors, duration estimation improvements.
  - Rules editor (user-defined mapping) and backfill UI.
  - Optional connectors spike (VS Code/Git, fitness, screen time) behind feature flags.

## Risks & Mitigations
- Overfitting taxonomy: start small (12–20 tags), measure entropy/coverage, iterate.
- LLM drift: enforce taxonomy in prompts, apply strict post-mapping to allowed vocabulary.
- Sparse data quality: rely on enrichment + priors + sessionization; add review workflow for edge cases.
- Performance: use TF‑IDF caching and batch processing; maintain fallbacks.

## Success Criteria
- ≥40% match rate across Notion↔Calendar with average confidence ≥0.6 on development dataset.
- ≥80% of activities mapped to top 12–20 tags; tag entropy stabilized across weeks.
- ≤10% of processed activities flagged for review after Phase 2.
- Dashboard displays quality metrics; Review Inbox operational for corrections.

## META Updates
- Update `DESIGN.md` and `PRODUCT.md` where agent design, data schema, or UI flows evolve.
- Log progress and decisions in `PROGRESS.md` and track actionable items in `TODO.md`.


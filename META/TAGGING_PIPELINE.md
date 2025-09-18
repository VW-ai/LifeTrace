# Tagging Pipeline: Calendar-as-Query → Notion-as-Context

Purpose
- Explain how Notion context powers tagging: ingest → index → retrieve → tag → persist → evaluate.

Overview
1) Ingest Notion workspace into DB
   - Tables: `notion_pages` (page_id, title, url, last_edited_at), `notion_blocks` (block_id, page_id, parent_block_id, block_type, text, is_leaf, last_edited_at), `notion_block_edits`
   - Code: `src/backend/parsers/notion/ingest_api.py` or `parsers/notion/incremental_ingest.py`
   - Runner: `python runner/run_ingest.py --start YYYY-MM-DD --end YYYY-MM-DD`

2) Index leaf blocks (abstracts + embeddings)
   - Abstracts (30–100 words) and embeddings for `is_leaf=1` blocks
   - Code: `src/backend/notion/abstracts.py`
   - Invoked by: `ProcessingService.index_notion_blocks(scope='all'|'recent')`
   - Runner step: `run_ingest.py` step [3/3]

3) Retrieve context during tagging
   - For each calendar event, build a query from title/details
   - Date-based retrieval: get blocks edited around the event date (±windowDays), compute cosine similarity to block embeddings, return top‑K
   - Code: `src/backend/agent/tools/context_retriever.py`
   - Debug endpoint: `/api/v1/retrieval/notion-context-by-date` (query, date, windowDays, k)

4) Enrich and score tags
   - TagGenerator merges event details + top abstracts into a single text basis
   - Scoring uses calibration (`agent/resources/tagging_calibration.json`): thresholds, max_tags (10), synonyms, taxonomy, weights, biases
   - Normalizes to [0,1], keeps tags ≥ threshold, returns top‑N (≤10)
   - Code: `src/backend/agent/tools/tag_generator.py`

5) Persist results
   - `processed_activities` rows and `activity_tags` with confidence
   - DAOs: `src/backend/database/access/models.py`
   - Runner: `python runner/run_process_range.py --start ... --end ...`

6) Evaluate
   - Script: `python scripts/evaluate_tagging.py --db smarthistory.db`
   - Metrics: coverage, avg_tags_per_activity, multi_tag_ratio, top tags, confidence histogram

How to run (two-phase)
1. Ingest only (DB)
```
python runner/run_ingest.py --start 2025-02-01 --end 2025-09-10
```
2. Tag only (processing)
```
python runner/run_process_range.py --start 2025-02-01 --end 2025-09-10
```

Taxonomy Builder (Agentic)
- Generate a practical, data-driven taxonomy and synonyms from your Calendar + Notion corpus.
- Outputs are auto-merged into TagGenerator at runtime if present.
```
python runner/run_build_taxonomy.py --start 2025-02-01 --end 2025-09-10
```
- Files written:
  - `src/backend/agent/resources/hierarchical_taxonomy_generated.json`
  - `src/backend/agent/resources/synonyms_generated.json`

Tagging Logs
- `runner/run_process_range.py` enables structured JSONL logging by default.
- Path printed on start: `logs/tagging_run_{start}_to_{end}_{timestamp}.jsonl`
- Each line includes: calendar summary/details, retrieved Notion abstracts (block ids, scores, abstract/text), normalized tag scores, and selected tags.

System‑wide re‑tag (date range)
- Use `--regenerate-system-tags` to enable heavier regeneration when debugging tag quality.
```
python runner/run_process_range.py --start 2025-02-01 --end 2025-09-10 --regenerate-system-tags
```

Notes
- JSON ingestion is deprecated; we use APIs and DB only.
- Runners ensure schema (migrations + column repair) for legacy DBs.
- OpenAI usage is optional; set `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_EMBED_MODEL` in `.env` for best results.

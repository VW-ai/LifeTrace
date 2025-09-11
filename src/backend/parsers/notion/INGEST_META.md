# Notion API Ingestion (DB-only)

Purpose
- Traverse Notion pages/blocks and populate:
  - `notion_pages` (page_id, title, url, last_edited_at)
  - `notion_blocks` (block_id, parent_block_id, text, is_leaf, last_edited_at)
  - `notion_block_edits` (edited history)

Usage
- `NotionIngestor().ingest_all()`
  - Searches workspace and ingests discovered pages.
- `NotionIngestor().ingest_all(start_page_ids=[...])`
  - Starts from the provided page IDs and ingests their trees.

Notes
- Requires `notion_client`.
- Text extracted from rich_text for text-capable blocks.
- `is_leaf` marks text blocks without children; abstracts/embeddings are filled by the indexing job.

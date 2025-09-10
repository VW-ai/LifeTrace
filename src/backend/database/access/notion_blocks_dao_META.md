# Notion Blocks DAO

Purpose
- Store Notion pages and blocks with parent/child relationships.
- Track edited blocks over time for quick daily edited-tree construction.
- Store embeddings for leaf abstracts to support retrieval.

Models
- NotionPageDB: `page_id`, `title`, `url`, `last_edited_at`
- NotionBlockDB: `block_id`, `page_id`, `parent_block_id`, `is_leaf`, `text`, `abstract`, `last_edited_at`
- NotionBlockEditDB: `block_id`, `edited_at`
- NotionEmbeddingDB: `block_id`, `model`, `vector(JSON)`, `dim`

DAOs
- NotionPageDAO: `upsert`, `get_by_page_id`
- NotionBlockDAO: `upsert`, `get_recently_edited`
- NotionBlockEditDAO: `record_edit`, `get_recent_edited_tree`
- NotionEmbeddingDAO: `upsert`, `get_by_block`

Notes
- Embeddings stored as JSON arrays; migrate to vector extension later.
- Keep files atomic; do not mix unrelated responsibilities.


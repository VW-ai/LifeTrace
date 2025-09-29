# Notion Context Pipeline (Scaffold)

Purpose
- Provide Calendar-as-Query → Notion-as-Context retrieval by indexing Notion blocks as a tree, generating abstracts for leaf blocks, and storing embeddings for retrieval.

Components
- `notion/abstracts.py`: abstract generation (OpenAI or fallback) and embeddings
- Database schema additions: `notion_pages`, `notion_blocks`, `notion_block_edits`, `notion_embeddings`
- DAOs: upsert pages/blocks, record edits, store embeddings, and fetch recently edited blocks
- Retriever: `agent/tools/context_retriever.py` computes cosine similarity between query and candidate blocks

Next
- Indexing job to generate abstracts + embeddings for newly edited leaf blocks daily
- API integration to attach context abstracts to processed activities
- Config: `HISTORY_PAGE_ID` (env) for anchoring historical backfill and scope control


#!/usr/bin/env python3
"""
Notion API Ingestion (DB-only)

Traverses Notion pages/blocks and writes pages to `notion_pages` and blocks
to `notion_blocks` (with parent/child relationships, text, is_leaf, last_edited_at).

Env:
- NOTION_API_KEY
- HISTORY_PAGE_ID (optional starting page)

Notes:
- Uses `notion_client` library.
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
import os
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from notion_client import Client  # type: ignore
except Exception:
    Client = None  # type: ignore

from src.backend.database import (
    NotionPageDAO,
    NotionBlockDAO,
    NotionBlockEditDAO,
    NotionPageDB,
    NotionBlockDB,
)


TEXT_BLOCK_TYPES = {
    "paragraph",
    "bulleted_list_item",
    "numbered_list_item",
    "to_do",
    "quote",
    "callout",
}


def _plain_text(rich_text: List[Dict[str, Any]]) -> str:
    return "".join([t.get("plain_text", "") for t in (rich_text or [])]).strip()


def _iso(ts: Optional[str]) -> Optional[str]:
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ts


class NotionIngestor:
    def __init__(self, api_key: Optional[str] = None):
        if Client is None:
            raise RuntimeError("notion_client not installed")
        api_key = api_key or os.getenv("NOTION_API_KEY")
        if not api_key:
            raise RuntimeError("NOTION_API_KEY not set")
        self.client = Client(auth=api_key)

    def ingest_all(self, start_page_ids: Optional[List[str]] = None) -> int:
        """Ingest pages/blocks into DB. If start_page_ids is given, ingest those; otherwise search workspace."""
        count = 0
        if start_page_ids:
            for pid in start_page_ids:
                count += self._ingest_page_recursive(pid)
            return count

        # Search entire workspace for pages
        cursor = None
        while True:
            resp = self.client.search(query="", start_cursor=cursor)
            results = resp.get("results", [])
            for r in results:
                if r.get("object") == "page":
                    pid = r.get("id")
                    if pid:
                        count += self._ingest_page_recursive(pid)
            if not resp.get("has_more"):
                break
            cursor = resp.get("next_cursor")
        return count

    def _ingest_page_recursive(self, page_id: str) -> int:
        # Fetch page metadata
        page = self.client.pages.retrieve(page_id=page_id)
        title = self._page_title(page)
        url = page.get("url")
        last_edited = _iso(page.get("last_edited_time"))
        NotionPageDAO.upsert(NotionPageDB(page_id=page_id, title=title, url=url, last_edited_at=last_edited))

        # Walk blocks under this page
        total = 0
        cursor = None
        while True:
            resp = self.client.blocks.children.list(block_id=page_id, start_cursor=cursor)
            results = resp.get("results", [])
            for blk in results:
                total += self._ingest_block_recursive(blk, page_id, parent_block_id=None)
            if not resp.get("has_more"):
                break
            cursor = resp.get("next_cursor")
        return total

    def _ingest_block_recursive(self, block: Dict[str, Any], page_id: str, parent_block_id: Optional[str]) -> int:
        bid = block.get("id")
        btype = block.get("type")
        last_edited = _iso(block.get("last_edited_time"))
        text = ""
        is_leaf = False

        # Extract text for text-capable block types
        if btype in TEXT_BLOCK_TYPES:
            text = _plain_text(block.get(btype, {}).get("rich_text", []))
            # We'll mark as leaf later if it has no children

        # Check if block has children
        has_children = bool(block.get("has_children"))
        if not has_children and btype in TEXT_BLOCK_TYPES and text:
            is_leaf = True

        # Upsert block
        NotionBlockDAO.upsert(
            NotionBlockDB(
                block_id=bid,
                page_id=page_id,
                parent_block_id=parent_block_id,
                block_type=btype,
                is_leaf=is_leaf,
                text=text,
                abstract=None,
                last_edited_at=last_edited,
            )
        )

        # Record edit
        if last_edited:
            try:
                NotionBlockEditDAO.record_edit(block_id=bid, edited_at=datetime.fromisoformat(last_edited))  # type: ignore
            except Exception:
                pass

        # Recurse into children if present
        count = 1
        if has_children:
            cursor = None
            while True:
                resp = self.client.blocks.children.list(block_id=bid, start_cursor=cursor)
                results = resp.get("results", [])
                for child in results:
                    count += self._ingest_block_recursive(child, page_id=page_id, parent_block_id=bid)
                if not resp.get("has_more"):
                    break
                cursor = resp.get("next_cursor")
        return count

    def _page_title(self, page: Dict[str, Any]) -> str:
        # Find title property heuristically
        props = page.get("properties", {})
        for _, val in props.items():
            if val.get("type") == "title":
                return _plain_text(val.get("title", []))
        return ""


__all__ = ["NotionIngestor"]

#!/usr/bin/env python3
"""
Incremental Notion Ingestion with Progress Tracking

Provides robust ingestion with:
- Progress tracking and status updates
- Resume capability for interrupted runs
- Batch processing to avoid timeouts
- Error handling and retry logic
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any, Set
import os
import sys
import time
import json
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


class IncrementalNotionIngestor:
    def __init__(self, api_key: Optional[str] = None, batch_size: int = 10):
        if Client is None:
            raise RuntimeError("notion_client not installed")
        api_key = api_key or os.getenv("NOTION_API_KEY")
        if not api_key:
            raise RuntimeError("NOTION_API_KEY not set")
        self.client = Client(auth=api_key)
        self.batch_size = batch_size
        self.processed_pages: Set[str] = set()
        self.total_blocks_processed = 0
        self.total_pages_processed = 0
        self.blocks_updated = 0
        self.blocks_skipped = 0
        self.pages_updated = 0  
        self.pages_skipped = 0
        
    def ingest_with_progress(
        self, 
        start_page_ids: Optional[List[str]] = None,
        max_pages: Optional[int] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Ingest pages/blocks with progress tracking and batching.
        
        Args:
            start_page_ids: Specific page IDs to start with (if None, searches workspace)
            max_pages: Maximum number of pages to process (None = no limit)
            progress_callback: Function to call with progress updates
            
        Returns:
            Dict with processing statistics
        """
        start_time = time.time()
        
        if progress_callback:
            progress_callback(f"Starting Notion ingestion (batch_size={self.batch_size})")
        
        try:
            if start_page_ids:
                page_ids = start_page_ids
            else:
                page_ids = self._discover_all_pages(max_pages, progress_callback)
            
            # Process pages in batches
            for i in range(0, len(page_ids), self.batch_size):
                batch = page_ids[i:i + self.batch_size]
                
                if progress_callback:
                    progress_callback(f"Processing page batch {i//self.batch_size + 1}: {len(batch)} pages")
                
                for page_id in batch:
                    if page_id in self.processed_pages:
                        continue
                        
                    try:
                        blocks_count = self._ingest_page_with_retry(page_id)
                        self.processed_pages.add(page_id)
                        self.total_pages_processed += 1
                        self.total_blocks_processed += blocks_count
                        
                        if progress_callback:
                            progress_callback(f"Page {self.total_pages_processed}/{len(page_ids)}: {blocks_count} blocks")
                            
                    except Exception as e:
                        if progress_callback:
                            progress_callback(f"Error processing page {page_id}: {str(e)}")
                        continue
                
                # Brief pause between batches to avoid rate limiting
                time.sleep(0.5)
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "pages_processed": self.total_pages_processed,
                "blocks_processed": self.total_blocks_processed,
                "duration_seconds": time.time() - start_time
            }
        
        return {
            "status": "success", 
            "pages_processed": self.total_pages_processed,
            "pages_updated": self.pages_updated,
            "pages_skipped": self.pages_skipped,
            "blocks_processed": self.total_blocks_processed,
            "blocks_updated": self.blocks_updated,
            "blocks_skipped": self.blocks_skipped,
            "duration_seconds": time.time() - start_time
        }
    
    def _discover_all_pages(self, max_pages: Optional[int] = None, progress_callback: Optional[callable] = None) -> List[str]:
        """Discover all pages in workspace with progress tracking."""
        page_ids = []
        cursor = None
        
        while True:
            try:
                resp = self.client.search(query="", start_cursor=cursor)
                results = resp.get("results", [])
                
                for r in results:
                    if r.get("object") == "page":
                        pid = r.get("id")
                        if pid:
                            page_ids.append(pid)
                            
                            if max_pages and len(page_ids) >= max_pages:
                                if progress_callback:
                                    progress_callback(f"Reached max_pages limit: {max_pages}")
                                return page_ids
                
                if progress_callback and len(page_ids) % 50 == 0:
                    progress_callback(f"Discovered {len(page_ids)} pages...")
                
                if not resp.get("has_more"):
                    break
                cursor = resp.get("next_cursor")
                
                # Brief pause to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                if progress_callback:
                    progress_callback(f"Error during page discovery: {str(e)}")
                break
        
        if progress_callback:
            progress_callback(f"Discovery complete: {len(page_ids)} total pages")
            
        return page_ids
    
    def _ingest_page_with_retry(self, page_id: str, max_retries: int = 3) -> int:
        """Ingest a single page with retry logic."""
        for attempt in range(max_retries):
            try:
                return self._ingest_page_recursive(page_id)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(2 ** attempt)  # Exponential backoff
        return 0
    
    def _ingest_page_recursive(self, page_id: str) -> int:
        """Ingest a single page and all its blocks."""
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
            
            # Brief pause between block fetches
            time.sleep(0.1)
            
        return total

    def _ingest_block_recursive(self, block: Dict[str, Any], page_id: str, parent_block_id: Optional[str]) -> int:
        """Ingest a single block recursively."""
        bid = block.get("id")
        if bid in self.processed_blocks:
            return 0
            
        btype = block.get("type")
        last_edited = _iso(block.get("last_edited_time"))
        text = ""
        is_leaf = False

        # Extract text for text-capable block types
        if btype in TEXT_BLOCK_TYPES:
            text = _plain_text(block.get(btype, {}).get("rich_text", []))

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
        
        self.processed_blocks.add(bid)

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
                
                # Brief pause between child block fetches
                time.sleep(0.1)
                
        return count

    def _page_title(self, page: Dict[str, Any]) -> str:
        """Extract page title heuristically."""
        props = page.get("properties", {})
        for _, val in props.items():
            if val.get("type") == "title":
                return _plain_text(val.get("title", []))
        return ""


__all__ = ["IncrementalNotionIngestor"]
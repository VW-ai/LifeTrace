#!/usr/bin/env python3
"""
Notion Pages/Blocks DAO

Atomic DAOs and models to store Notion pages, blocks (with parent/child links),
edited tracking, and embeddings for leaf abstracts.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import json

from ..core.database_manager import DatabaseManager


def get_db_manager():
    return DatabaseManager.get_instance()


@dataclass
class NotionPageDB:
    id: Optional[int] = None
    page_id: str = ""
    title: str = ""
    url: Optional[str] = None
    created_at: Optional[datetime] = None
    last_edited_at: Optional[datetime] = None

    def validate(self) -> bool:
        if not self.page_id:
            raise ValueError("page_id is required")
        return True


@dataclass
class NotionBlockDB:
    id: Optional[int] = None
    block_id: str = ""
    page_id: str = ""
    parent_block_id: Optional[str] = None
    is_leaf: bool = False
    text: str = ""
    abstract: Optional[str] = None
    created_at: Optional[datetime] = None
    last_edited_at: Optional[datetime] = None

    def validate(self) -> bool:
        if not self.block_id:
            raise ValueError("block_id is required")
        if not self.page_id:
            raise ValueError("page_id is required")
        return True


@dataclass
class NotionBlockEditDB:
    id: Optional[int] = None
    block_id: str = ""
    edited_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> bool:
        if not self.block_id:
            raise ValueError("block_id is required")
        return True


@dataclass
class NotionEmbeddingDB:
    id: Optional[int] = None
    block_id: str = ""
    model: str = "text-embedding-3-small"
    vector: List[float] = field(default_factory=list)
    dim: Optional[int] = None
    created_at: Optional[datetime] = None

    def validate(self) -> bool:
        if not self.block_id:
            raise ValueError("block_id is required")
        if not self.vector:
            raise ValueError("vector is required")
        return True


class NotionPageDAO:
    @staticmethod
    def upsert(page: NotionPageDB) -> int:
        page.validate()
        db = get_db_manager()
        # Try update
        affected = db.execute_update(
            """
            UPDATE notion_pages SET title=?, url=?, last_edited_at=?
            WHERE page_id=?
            """,
            (page.title, page.url, page.last_edited_at, page.page_id),
        )
        if affected == 0:
            return db.execute_insert(
                """
                INSERT INTO notion_pages (page_id, title, url, last_edited_at)
                VALUES (?, ?, ?, ?)
                """,
                (page.page_id, page.title, page.url, page.last_edited_at),
            )
        # fetch id
        row = db.execute_query(
            "SELECT id FROM notion_pages WHERE page_id=?", (page.page_id,)
        )
        return row[0]["id"] if row else 0

    @staticmethod
    def get_by_page_id(page_id: str) -> Optional[NotionPageDB]:
        db = get_db_manager()
        rows = db.execute_query("SELECT * FROM notion_pages WHERE page_id=?", (page_id,))
        if not rows:
            return None
        r = rows[0]
        return NotionPageDB(
            id=r["id"],
            page_id=r["page_id"],
            title=r["title"],
            url=r["url"],
            created_at=r["created_at"],
            last_edited_at=r["last_edited_at"],
        )


class NotionBlockDAO:
    @staticmethod
    def upsert(block: NotionBlockDB) -> int:
        block.validate()
        db = get_db_manager()
        affected = db.execute_update(
            """
            UPDATE notion_blocks
            SET page_id=?, parent_block_id=?, is_leaf=?, text=?, abstract=?, last_edited_at=?
            WHERE block_id=?
            """,
            (
                block.page_id,
                block.parent_block_id,
                1 if block.is_leaf else 0,
                block.text,
                block.abstract,
                block.last_edited_at,
                block.block_id,
            ),
        )
        if affected == 0:
            return db.execute_insert(
                """
                INSERT INTO notion_blocks (block_id, page_id, parent_block_id, is_leaf, text, abstract, last_edited_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    block.block_id,
                    block.page_id,
                    block.parent_block_id,
                    1 if block.is_leaf else 0,
                    block.text,
                    block.abstract,
                    block.last_edited_at,
                ),
            )
        # fetch id
        row = db.execute_query(
            "SELECT id FROM notion_blocks WHERE block_id=?", (block.block_id,)
        )
        return row[0]["id"] if row else 0

    @staticmethod
    def get_recently_edited(hours: int = 24) -> List[NotionBlockDB]:
        db = get_db_manager()
        threshold = (datetime.now() - timedelta(hours=hours)).isoformat(sep=" ")
        rows = db.execute_query(
            """
            SELECT * FROM notion_blocks
            WHERE last_edited_at >= ?
            ORDER BY last_edited_at DESC
            """,
            (threshold,),
        )
        return [NotionBlockDAO._row_to_model(r) for r in rows]

    @staticmethod
    def get_all_leaf_blocks() -> List[NotionBlockDB]:
        """Return all leaf blocks (for full indexing)."""
        db = get_db_manager()
        rows = db.execute_query(
            "SELECT * FROM notion_blocks WHERE is_leaf = 1 ORDER BY last_edited_at DESC"
        )
        return [NotionBlockDAO._row_to_model(r) for r in rows]

    @staticmethod
    def get_by_edited_range(start_iso: str, end_iso: str) -> List[NotionBlockDB]:
        """Return blocks edited between start_iso and end_iso (inclusive)."""
        db = get_db_manager()
        rows = db.execute_query(
            """
            SELECT * FROM notion_blocks
            WHERE last_edited_at >= ? AND last_edited_at <= ?
            ORDER BY last_edited_at DESC
            """,
            (start_iso, end_iso),
        )
        return [NotionBlockDAO._row_to_model(r) for r in rows]

    @staticmethod
    def _row_to_model(r) -> NotionBlockDB:
        return NotionBlockDB(
            id=r["id"],
            block_id=r["block_id"],
            page_id=r["page_id"],
            parent_block_id=r["parent_block_id"],
            is_leaf=bool(r["is_leaf"]),
            text=r["text"],
            abstract=r["abstract"],
            created_at=r["created_at"],
            last_edited_at=r["last_edited_at"],
        )


class NotionBlockEditDAO:
    @staticmethod
    def record_edit(block_id: str, edited_at: Optional[datetime] = None) -> int:
        edited_at = edited_at or datetime.now()
        db = get_db_manager()
        return db.execute_insert(
            "INSERT INTO notion_block_edits (block_id, edited_at) VALUES (?, ?)",
            (block_id, edited_at),
        )

    @staticmethod
    def get_recent_edited_tree(hours: int = 24) -> List[Tuple[str, datetime]]:
        db = get_db_manager()
        threshold = (datetime.now() - timedelta(hours=hours)).isoformat(sep=" ")
        rows = db.execute_query(
            "SELECT block_id, edited_at FROM notion_block_edits WHERE edited_at >= ? ORDER BY edited_at DESC",
            (threshold,),
        )
        return [(r["block_id"], r["edited_at"]) for r in rows]


class NotionEmbeddingDAO:
    @staticmethod
    def upsert(emb: NotionEmbeddingDB) -> int:
        emb.validate()
        db = get_db_manager()
        vec_json = json.dumps(emb.vector)
        affected = db.execute_update(
            """
            UPDATE notion_embeddings SET model=?, vector=?, dim=?
            WHERE block_id=? AND model=?
            """,
            (emb.model, vec_json, emb.dim or len(emb.vector), emb.block_id, emb.model),
        )
        if affected == 0:
            return db.execute_insert(
                """
                INSERT INTO notion_embeddings (block_id, model, vector, dim)
                VALUES (?, ?, ?, ?)
                """,
                (emb.block_id, emb.model, vec_json, emb.dim or len(emb.vector)),
            )
        row = db.execute_query(
            "SELECT id FROM notion_embeddings WHERE block_id=? AND model=?",
            (emb.block_id, emb.model),
        )
        return row[0]["id"] if row else 0

    @staticmethod
    def get_by_block(block_id: str) -> Optional[NotionEmbeddingDB]:
        db = get_db_manager()
        rows = db.execute_query(
            "SELECT * FROM notion_embeddings WHERE block_id=? ORDER BY created_at DESC LIMIT 1",
            (block_id,),
        )
        if not rows:
            return None
        r = rows[0]
        return NotionEmbeddingDB(
            id=r["id"],
            block_id=r["block_id"],
            model=r["model"],
            vector=json.loads(r["vector"]) if r["vector"] else [],
            dim=r["dim"],
            created_at=r["created_at"],
        )

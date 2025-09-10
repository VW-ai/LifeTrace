#!/usr/bin/env python3
"""
Context Retriever

Calendar-as-Query → Notion-as-Context: retrieve top-K Notion leaf blocks
for a query (event title/details) within a recent edited time window.
"""

from typing import List, Dict, Any, Tuple
from math import sqrt
from dataclasses import dataclass

from src.backend.database import (
    NotionBlockDAO,
    NotionEmbeddingDAO,
    NotionBlockDB,
)
from src.backend.notion.abstracts import embed_text


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sqrt(sum(x * x for x in a)) or 1.0
    nb = sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


@dataclass
class RetrievedContext:
    block: NotionBlockDB
    score: float


class ContextRetriever:
    def __init__(self, embed_model: str = "text-embedding-3-small"):
        self.embed_model = embed_model

    def retrieve(self, query_text: str, hours: int = 24, k: int = 5) -> List[RetrievedContext]:
        """Return top-K edited leaf blocks by cosine similarity to query_text."""
        q_vec = embed_text(query_text)
        candidates = NotionBlockDAO.get_recently_edited(hours=hours)
        results: List[RetrievedContext] = []
        for blk in candidates:
            emb = NotionEmbeddingDAO.get_by_block(blk.block_id)
            if not emb or not emb.vector:
                # Skip if no embedding yet (will be filled by indexing job)
                continue
            score = _cosine(q_vec, emb.vector)
            results.append(RetrievedContext(block=blk, score=score))
        # sort and take top-K
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:k]

    def retrieve_by_date(self, query_text: str, date: str, days_window: int = 1, k: int = 5) -> List[RetrievedContext]:
        """Return top-K leaf blocks edited around a specific date.
        date: 'YYYY-MM-DD'; window selects [date - days_window, date + days_window].
        """
        from datetime import datetime, timedelta
        q_vec = embed_text(query_text)
        d = datetime.strptime(date, "%Y-%m-%d")
        start = (d - timedelta(days=days_window)).strftime("%Y-%m-%d 00:00:00")
        end = (d + timedelta(days=days_window)).strftime("%Y-%m-%d 23:59:59")
        candidates = NotionBlockDAO.get_by_edited_range(start, end)
        results: List[RetrievedContext] = []
        for blk in candidates:
            emb = NotionEmbeddingDAO.get_by_block(blk.block_id)
            if not emb or not emb.vector:
                continue
            score = _cosine(q_vec, emb.vector)
            results.append(RetrievedContext(block=blk, score=score))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:k]

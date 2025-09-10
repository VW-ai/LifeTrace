#!/usr/bin/env python3
"""
Notion Abstracts & Embeddings

Generates short abstracts (30–100 words) for Notion leaf blocks and
produces embeddings for retrieval. Uses OpenAI when available, with
fallbacks for local development.
"""

from typing import Optional, List
import os
import re
import json

try:
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def generate_abstract(text: str, target_words: int = 60) -> str:
    """Generate a 30–100 word abstract.
    Fallback: heuristic truncation of sentences to ~target_words.
    """
    text = _clean_text(text)
    if not text:
        return ""

    api_key = os.getenv("OPENAI_API_KEY")
    if OpenAI and api_key:
        try:
            client = OpenAI(api_key=api_key)
            prompt = (
                "Summarize the following content into 30–100 words, focusing on the key activity context.\n\n" + text
            )
            resp = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=120,
            )
            summary = resp.choices[0].message.content.strip()
            return summary
        except Exception:
            pass

    # Heuristic fallback
    words = text.split()
    if len(words) <= 100:
        return " ".join(words[:100])
    return " ".join(words[:target_words])


def embed_text(text: str) -> List[float]:
    """Produce an embedding for text.
    Fallback: simple hashing-based embedding to avoid extra deps in dev.
    """
    text = _clean_text(text)
    api_key = os.getenv("OPENAI_API_KEY")
    if OpenAI and api_key:
        try:
            client = OpenAI(api_key=api_key)
            model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
            resp = client.embeddings.create(model=model, input=text)
            vec = resp.data[0].embedding
            return vec
        except Exception:
            pass

    # Fallback: 256-dim hashing-based embedding
    dim = 256
    vec = [0.0] * dim
    for i, ch in enumerate(text[:2048]):
        idx = (ord(ch) + i) % dim
        vec[idx] += 1.0
    # L2 normalize
    norm = sum(v * v for v in vec) ** 0.5 or 1.0
    return [v / norm for v in vec]


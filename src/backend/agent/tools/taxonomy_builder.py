#!/usr/bin/env python3
"""
Agentic Taxonomy & Synonyms Builder

Generates practical, non‑over‑abstract tag taxonomy and synonyms from your
Calendar (raw_activities) and Notion context (notion_blocks abstracts).

Outputs JSON files under agent/resources/:
- hierarchical_taxonomy_generated.json
- synonyms_generated.json

Uses OpenAI when available; otherwise falls back to a frequency‑based sketch.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore

from src.backend.database import get_db_manager
from ..prompts.tag_prompts import TagPrompts


def _fetch_corpus(date_start: Optional[str], date_end: Optional[str], limit: int = 2000) -> List[Dict[str, str]]:
    db = get_db_manager()
    corpus: List[Dict[str, str]] = []
    # Calendar events (raw_activities)
    where = ["source='google_calendar'"]
    params: List[Any] = []
    if date_start:
        where.append("date >= ?")
        params.append(date_start)
    if date_end:
        where.append("date <= ?")
        params.append(date_end)
    where_sql = " AND ".join(where)
    rows = db.execute_query(
        f"SELECT date, time, details, json_extract(raw_data,'$.summary') AS summary FROM raw_activities WHERE {where_sql} ORDER BY date DESC, time DESC LIMIT {limit}",
        tuple(params) if params else None,
    )
    for r in rows:
        title = r["summary"] or ""
        corpus.append({"type": "calendar", "title": title, "text": r["details"] or ""})

    # Notion abstracts (leaf blocks)
    rows2 = db.execute_query(
        """
        SELECT nb.page_id, nb.block_id, nb.abstract, nb.text, nb.last_edited_at
        FROM notion_blocks nb
        WHERE nb.is_leaf = 1 AND (nb.abstract IS NOT NULL OR nb.text IS NOT NULL)
        ORDER BY nb.last_edited_at DESC
        LIMIT ?
        """,
        (limit,),
    )
    for r in rows2:
        corpus.append({"type": "notion", "title": "", "text": (r["abstract"] or r["text"] or "")})
    return corpus




def _build_with_openai(corpus: List[Dict[str, str]], model: str) -> Dict[str, Any]:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # Sample/pack corpus to stay within token limits
    sampled = corpus[:100] if len(corpus) > 100 else corpus
    
    # Format examples using the centralized function
    examples = []
    for item in sampled:
        title = item.get("title") or ""
        text = item.get("text") or ""
        example = TagPrompts.format_activity_example(item['type'], title, text)
        examples.append(example)
    
    # Use centralized prompts
    system_prompt = TagPrompts.get_taxonomy_builder_system_prompt()
    user_prompt = TagPrompts.get_taxonomy_builder_user_prompt(examples)
    
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        temperature=0.3,
        max_tokens=1200,
    )
    content = resp.choices[0].message.content.strip()
    print(f"[DEBUG] OpenAI response: {content[:200]}...")
    
    # Handle markdown code blocks
    if content.startswith("```json"):
        content = content[7:]  # Remove ```json
    if content.startswith("```"):
        content = content[3:]   # Remove ```
    if content.endswith("```"):
        content = content[:-3]  # Remove trailing ```
    
    content = content.strip()
    data = json.loads(content)
    return data


def _build_fallback(corpus: List[Dict[str, str]]) -> Dict[str, Any]:
    # Improved fallback with distinct taxonomy vs synonyms
    from collections import Counter
    import re
    text = " ".join((c.get("title") or "") + " " + (c.get("text") or "") for c in corpus)
    words = [w.lower() for w in re.findall(r"[a-zA-Z][a-zA-Z\-]{2,}", text)]
    stop = {"the", "and", "with", "from", "into", "that", "this", "have", "will", "been"}
    word_counts = Counter(words)
    top = [w for w, _ in word_counts.most_common(200) if w not in stop and len(w) > 2]
    
    # TAXONOMY: organize by activity domains
    taxonomy = {
        "work": [w for w in top if any(k in w for k in ("meeting", "project", "code", "review", "planning", "standup", "sync"))][:6],
        "health": [w for w in top if any(k in w for k in ("gym", "exercise", "run", "walk", "meal", "lunch", "dinner", "breakfast"))][:6],
        "personal": [w for w in top if any(k in w for k in ("write", "read", "learn", "study", "practice"))][:6],
        "social": [w for w in top if any(k in w for k in ("call", "chat", "visit", "party", "event"))][:6],
        "maintenance": [w for w in top if any(k in w for k in ("clean", "shop", "cook", "laundry", "grocery"))][:6],
    }
    
    # SYNONYMS: alternative terms for specific activities  
    synonyms = {
        "meetings": [w for w in top if any(k in w for k in ("call", "standup", "sync", "conference", "1-1", "retro"))][:8],
        "coding": [w for w in top if any(k in w for k in ("develop", "program", "debug", "commit", "deploy", "code"))][:8], 
        "exercise": [w for w in top if any(k in w for k in ("gym", "workout", "training", "fitness", "run", "jog"))][:8],
        "eating": [w for w in top if any(k in w for k in ("meal", "lunch", "dinner", "breakfast", "snack", "food"))][:8],
        "writing": [w for w in top if any(k in w for k in ("document", "note", "journal", "blog", "draft", "edit"))][:8],
    }
    
    # Remove empty categories
    taxonomy = {k: v for k, v in taxonomy.items() if v}
    synonyms = {k: v for k, v in synonyms.items() if v}
    
    return {"taxonomy": taxonomy, "synonyms": synonyms}


def build_and_save(date_start: Optional[str], date_end: Optional[str]) -> Dict[str, str]:
    corpus = _fetch_corpus(date_start, date_end, limit=2000)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if OpenAI and os.getenv("OPENAI_API_KEY"):
        try:
            data = _build_with_openai(corpus, model)
        except Exception as e:
            print(f"[WARN] OpenAI error: {e}. Falling back to frequency sketch.")
            print(f"[DEBUG] OpenAI model: {model}, API key present: {bool(os.getenv('OPENAI_API_KEY'))}")
            data = _build_fallback(corpus)
    else:
        data = _build_fallback(corpus)

    # Validate structure
    taxonomy = data.get("taxonomy") or {}
    synonyms = data.get("synonyms") or {}

    res_dir = Path(__file__).resolve().parents[1] / "resources"
    res_dir.mkdir(parents=True, exist_ok=True)
    tax_path = res_dir / "hierarchical_taxonomy_generated.json"
    syn_path = res_dir / "synonyms_generated.json"
    with open(tax_path, "w", encoding="utf-8") as f:
        json.dump(taxonomy, f, ensure_ascii=False, indent=2)
    with open(syn_path, "w", encoding="utf-8") as f:
        json.dump(synonyms, f, ensure_ascii=False, indent=2)
    return {"taxonomy": str(tax_path), "synonyms": str(syn_path)}


#!/usr/bin/env python3
"""
Tagging Run Logger

Lightweight JSONL logger for tagging runs. Each line is a JSON object with
the activity info, retrieved Notion contexts, and selected tags.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class TaggingRunLogger:
    def __init__(self, path: str) -> None:
        self.path = path
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Create/append file with a small header entry
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "_type": "tagging_log_start",
                    "timestamp": datetime.now().isoformat(),
                }) + "\n")
        except Exception:
            pass

    def log(self, record: Dict[str, Any]) -> None:
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            # Avoid crashing tagging due to logging issues
            pass


_singleton: Optional[TaggingRunLogger] = None


def get_logger() -> Optional[TaggingRunLogger]:
    global _singleton
    if _singleton is not None:
        return _singleton
    path = os.getenv("TAGGING_LOG_FILE")
    if not path:
        return None
    _singleton = TaggingRunLogger(path)
    return _singleton


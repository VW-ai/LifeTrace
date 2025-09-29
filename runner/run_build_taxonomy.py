#!/usr/bin/env python3
"""
Build tag taxonomy and synonyms from your Calendar + Notion data using AI.

Outputs under agent/resources/:
- hierarchical_taxonomy_generated.json
- synonyms_generated.json

Usage:
  python runner/run_build_taxonomy.py --start 2025-02-01 --end 2025-09-10
"""

import argparse
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None  # type: ignore

from src.backend.agent.tools.taxonomy_builder import build_and_save


def main():
    p = argparse.ArgumentParser(description="Build AI-driven tag taxonomy + synonyms")
    p.add_argument("--start", default=None, help="Start date YYYY-MM-DD (optional)")
    p.add_argument("--end", default=None, help="End date YYYY-MM-DD (optional)")
    args = p.parse_args()

    if load_dotenv is not None:
        env_path = PROJECT_ROOT / '.env'
        if env_path.exists():
            load_dotenv(env_path)

    out = build_and_save(args.start, args.end)
    print({"status": "success", "outputs": out})


if __name__ == '__main__':
    main()


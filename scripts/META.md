# Scripts

Utility scripts for development and evaluation. Follow REGULATION.md principles:

- Atomic files: each script does one thing (no mixed concerns).
- Co-located docs: this META explains script purposes and usage.

Included:
- `evaluate_tagging.py`: prints tagging coverage, avg tags per activity, top tags, and confidence histogram against the SQLite DB.

Usage examples:
```
python scripts/evaluate_tagging.py --db smarthistory.db
```

Notes:
- Scripts should import shared code where applicable; avoid subprocess calls from API paths.
- Keep scripts idempotent and read-only unless explicitly designed to write.


# Tagging Calibration

Purpose
- Provide configurable thresholds, weights, synonyms, taxonomy relations, and source biases for TagGenerator to reduce generic tagging and improve multi-tag relevance.

File
- `tagging_calibration.json`

Key Fields
- `threshold`: normalized score threshold [0,1] to accept a tag
- `max_tags`: maximum number of tags to return per activity
- `weights`: weights for scoring components (synonyms, taxonomy, duration, title bonus)
- `downweight`: per-tag multiplicative factors (e.g., downweight `work`)
- `synonyms`: map of tag -> keyword list
- `taxonomy`: parent -> [children] for hierarchical credit
- `source_bias`: source -> { tag -> additive bias }

Notes
- Keep the file small and readable; iterate with data.
- Changes are picked up on TagGenerator init (loaded once per process).


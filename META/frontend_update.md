**Overview**
- Goal: deliver an artistic, modern, tag‑driven analytics UI with cross‑filtered views powered by your generated tags.
- Scope: reuse best of current frontend, add shared types/helpers, integrate views into the Dashboard, and enable simple global tag filtering as a foundation.

**Objectives**
- Artistic: cinematic hero and tasteful visuals; animated, responsive components.
- Interaction: cross‑filtering by time/tags, hover tooltips, zoom/pan, clean keyboardable UI.
- Tag utilization: co‑occurrence exploration, time rhythms, densities, and transitions.

**Data Model**
- Source event fields (from logs and API): `date`, `time`, `summary/details`, `selected_tags/tags[]`, `source`, `duration_minutes`.
- Shared frontend type: `types/activity.ts` defines a single `Activity` shape used across features.
- Adapter: map backend `ProcessedActivity` → `Activity` in Dashboard.

**What We Will Reuse**
- Tag Galaxy: `InteractiveTagMap` (force graph, zoom/pan, search, tooltips).
- Timeline: `TimelineView` (grouped per-day, tags, durations, source badges, expand/collapse).
- Calendar Heatmap: `ActivityHeatmap` (GitHub‑style intensity with tooltip + stats).
- Charts: `AreaChart`, `PieChart` for tag trends and composition.
- Dashboard shell: `components/dashboard/Dashboard` + `styles/professional-theme`.
- Tag insights: `TopTagsList` using `/tags/relationships`.

**Gaps To Fill**
- Cross‑filters: global selected tags and time range shared by all views; start simple in state, graduate to store + URL sync.
- Data adapter: unify activity shape across API and features.
- Color system: single stable tag color hashing util used by all components.
- New visualizations (later phases): Streamgraph (Tag River), Chord transitions, Radial day clock.

**Plan (Phases)**
- Phase 1 (done in part):
  - Add shared `Activity` type and tag utilities.
  - Integrate TagMap, Heatmap, Timeline into Dashboard with simple tag cross‑filtering.
  - Map backend `ProcessedActivity` to shared `Activity`.
- Phase 2:
  - Introduce a tiny global store (e.g., Zustand) for filters and URL state.
  - Add filter chips with clear/reset; unify color usage across all views.
  - Hook charts (Area/Pie) to the same filtered dataset.
- Phase 3:
  - Add Streamgraph (Tag River) and Radial day clock.
  - Performance passes: memoization, workerizing heavy layouts.
- Phase 4:
  - Add Chord diagram for tag‑to‑tag transitions and “Stories” (saved filter states).
- Phase 5:
  - Polish: motion tuning, accessibility review, export to PNG/SVG.

**Code Updates Just Made**
- New: `src/frontend/src/types/activity.ts` — shared `Activity` interface.
- New: `src/frontend/src/utils/tags.ts` — `stableTagColor(tag)` and `formatDuration()`.
- Updated: `InteractiveTagMap.tsx` — emits `onSelectTag(tag)` on node click.
- Updated: `Dashboard/Dashboard.tsx` —
  - Maps `ProcessedActivity` → shared `Activity`.
  - Maintains `selectedTags` state and filters activities across views.
  - Renders Tag Galaxy, Calendar Heatmap, and Timeline with filtered data.

**Next Steps**
- Add filter chips UI in Dashboard header with clear/reset; display selected tags.
- Centralize tag color usage in Timeline/TagMap/Heatmap using `stableTagColor()`.
- Optional: add Zustand `useFilters` + URL query sync for shareable views.
- Extend charts to respect `selectedTags` (currently based on all activities in range).

**Risks & Mitigations**
- Data shape mismatch: handled via adapter; keep adapter near Dashboard until stabilized.
- Performance with many tags: consider WebGL (Pixi/regl) for TagMap in Phase 3 and layout in a Web Worker.
- Accessibility: add keyboard focus states and reduced‑motion guards in polish phase.

**Estimates (T‑shirt)**
- Phase 2: M (3–5 days)
- Phase 3: M (3–5 days)
- Phase 4: M (3–5 days)
- Phase 5: S (1–2 days)

**References**
- Logs for tagging context: `logs/tagging_run_*.jsonl`.
- Primary files: Dashboard shell, features (TagMap/Timeline/Heatmap), charts.


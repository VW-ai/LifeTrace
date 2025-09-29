# Frontend Update Plan — Tag‑Driven Visualization (UX‑Focused)

This plan consumes our live database strictly through the existing FastAPI backend (database-first, no local file ingestion). If a needed aggregate isn’t available, we will add a new backend API following existing patterns and META/REGULATION.md. It adds a senior UI/UX lens across principles, IA, design system, interaction patterns, states, accessibility, and validation.

## Goals
- Expressive visuals: cinematic hero canvas, purposeful motion, minimal chrome.
- Modern interaction: cross‑filters, brush/zoom, keyboard nav, save/shareable stories.
- Insight density: co‑occurrence, rhythms over time, transitions, clusters.
- Inclusive and fast: accessible color/contrast, reduced‑motion support, 60fps where it matters.

## Audience & Use Cases
- Personal reflection: skim patterns over weeks/months, drill into notable days.
- Research/exploration: compare tag sets, surface relationships and transitions.
- Sharing: capture a “story” (named filter state) and share a URL/snapshot.

## Information Architecture
- Global layout: hero canvas (Tag Field) as ambient context; right panel is the Event Drawer.
- Primary nav (top): Timeline, Galaxy, River, Calendar, Chords, Stories.
- Secondary controls (left rail): filter summary, active tag chips, search, compare mode toggle.
- Global status strip (bottom): time window, selection count, performance hints (e.g., “Large data mode”).

## Design System (Tokens & Primitives)
- Color tokens: background, surface[1–3], text[primary|secondary|muted], stroke[soft|strong], accent, success, warning, danger.
- Tag hues: stable HSL hash per tag; ensure min ΔE for adjacent hues; colorblind‑safe set for top N tags.
- Density ramps: perceptual sequential (e.g., CIELAB‑tuned) for heat/volume; diverging for compare.
- Type ramp: Inter or IBM Plex; 12/14/16/20/24/28/36; 1.4–1.6 line heights; tabular nums for timelines.
- Spacing & grid: 8px base; container 1200–1440px with responsive breakpoints (sm 640, md 768, lg 1024, xl 1280).
- Radius & elevation: 8/12 radius; 3 elevation levels with soft shadows and backdrop blur for glass panels.
- Motion: 120–240ms defaults, cubic‑bezier(0.2, 0.8, 0.2, 1); physics for canvas; respect `prefers-reduced-motion`.

## Data Model
- Event (from backend): `date`, `time`, `source`, `summary`, `details`, `selected_tags[]`.
- Derived (via backend services): per‑day/per‑hour tag counts, co‑occurrence matrix, tag transitions (adjacent events), tag clusters via community detection.

## Key Views (UX Specs)
- Tag Field (Hero): ambient Voronoi/particle field keyed to active tags; subtle pulses on selection; pauses on user input; not essential for comprehension.
- Timeline: zoomable time band with tag pills; brush to filter; grouping by `source`; clear handles, live preview while brushing.
- Tag Galaxy: force graph of tags sized by frequency; edges by co‑occurrence; lasso and click selection; focus+context zoom; declutter via edge bundling/threshold.
- Tag River: stacked streamgraph of tag volumes over time; absolute/normalized/share‑of‑day; legend with pin/compare affordances.
- Calendar: month heatmap for density; radial day clock for hourly rhythms; click a day opens Drawer with that window.
- Chords: tag‑to‑tag transitions across adjacent events; hover shows directional flows; edge thickness encodes strength.
- Event Drawer: virtualized list; sticky header summarizing filters; inline tag chips; keyboard navigable; split view on wide screens.

## Interaction Patterns
- Cross‑filtering: click any tag/view element to filter; multi‑select via lasso/cmd‑click; filters represented as chips with quick remove; “Clear all” and step‑back (undo).
- Brushing & zooming: drag with explicit handles; double‑click to reset; wheel+ctrl for zoom; transitions preserve relative positions (object constancy).
- Hover & scrub: tooltips use 300ms delay; scrubbing timeline previews counts and top tags; escape dismisses focus/hover.
- Compare mode: two palettes A/B; pinned sets shown in legend; metrics show absolute and delta; togglable normalization.
- Keyboard map: `/` search; `f` toggle filters; `.` play/pause scrub; `←/→` step time; `Shift` modifies step size; `Esc` clear selection.

## States & Feedback
- Loading: skeleton timelines/legends; optimistic layout placeholders.
- Empty: friendly guidance with example tags; CTA to load logs.
- Sparse data: degrade visuals (e.g., show dots instead of streams) and annotate.
- Errors: non‑blocking toasts with retry; details in a collapsible panel.
- Performance: show “Large data mode” banner when thresholds trigger simplification; allow opt‑out.

## Accessibility
- Color contrast: target AA for all text and essential marks; non‑essential ambient visuals may fall below but must not encode essential information alone.
- Reduced motion: disable particle/physics effects; replace with fades/steps; maintain focus outlines.
- Screen reader: landmarks for nav/main/aside; aria‑labels for charts; textual summary region reflecting current filters and highlights.
- Keyboard: all controls reachable and operable; visible focus states; lasso has keyboard alternative via list selection.

## Tech Stack
- React + TypeScript + Vite; Tailwind (recommended for custom visuals). Chakra acceptable if component density increases.
- D3 + visx for charts; Pixi.js or regl for Galaxy/Chords when WebGL is beneficial.
- State: Zustand for global state; URL sync via `useSearchParams` for shareable views.
- Data: Fetch via FastAPI endpoints (see API section); no JSONL ingestion in frontend.
- Performance: Server‑side aggregation where possible; Web Workers only for client‑side interaction transforms; `react-virtual` for lists; IndexedDB for client‑side caching of API responses.

## Data Access & Caching (Backend‑First)
- Prefer backend aggregates; avoid heavy client computation.
- Primary endpoints (existing; see `src/backend/api/API_DESIGN.md` and `api_META.md`):
  - `GET /api/v1/activities/raw`
  - `GET /api/v1/activities/processed`
  - `GET /api/v1/insights/overview`
  - `GET /api/v1/insights/time-distribution`
  - `GET /api/v1/tags`
- Aggregate endpoints to use/add (if missing, implement in backend services):
  - `GET /api/v1/tags/summary` — total usage, top tags, color map
  - `GET /api/v1/tags/cooccurrence` — matrix or sparse edges; supports thresholds and tag filters
  - `GET /api/v1/tags/transitions` — directional transitions across adjacent events within window
  - `GET /api/v1/tags/clusters` — community detection results over co‑occurrence graph
  - `GET /api/v1/tags/time-series` — per‑day and per‑hour tag histograms (modes: abs/normalized/share)
- Client caching: IndexedDB cache of API responses keyed by endpoint + params + data version; stale‑while‑revalidate strategy.
- Live updates: Optionally `GET /api/v1/system/health` polling or WebSocket in future for incremental refresh.

## Implementation Phases (Design + Build)
1) Foundation (P1)
   - UX: define tokens (color/type/spacing), component inventory, low‑fi wireframes for Timeline, Filter Bar, Event Drawer.
   - Build: API client + schema guards; global state; Timeline (brushable) + tag frequency cards; filter bar; URL sync. No local file ingestion.
2) Galaxy + Cross‑Filters (P2)
   - UX: interaction spec for lasso, selection chips, performance thresholds; micro‑interaction timings.
   - Build: WebGL force graph; click/lasso; bi‑directional filters with Timeline; initial perf baseline. Data from `/tags/cooccurrence` and `/tags/clusters`.
3) River + Calendar + Radial Clock (P3)
   - UX: streamgraph modes, heatmap legend, radial clock ticks/labels; compare mode MVP visuals.
   - Build: Streamgraph; month heatmap; radial clock; compare mode with dual palettes and delta readouts. Data from `/tags/time-series` and `/insights/time-distribution`.
4) Chords + Stories (P4)
   - UX: chord hover/selection patterns; story save/share flows; snapshot export framing.
   - Build: Chord diagram from `/tags/transitions`; “Save Story” (named filter states) with URL encoding; PNG/SVG export.
5) Polish & Accessibility (P5)
   - UX: color audit, reduced‑motion review, keyboard help overlay, empty/loading/error states QA.
   - Build: motion tuning, theming, export refinement, performance guardrails.

## Acceptance Criteria (by phase)
- P1: Timeline brush filters Drawer; tag chips filter globally; URL reflects filters; base tokens applied consistently; AA contrast on core UI; all data via backend API.
- P2: Galaxy >1k nodes at ~60fps on modern laptop; selection round‑trips across views; lasso discoverable and documented.
- P3: Stream/heatmap/clock animate smoothly on filter changes; compare mode conveys absolute and delta without ambiguity.
- P4: Chords reflect transitions within active window; stories save/load/share reliably; snapshot export produces crisp, branded output.
- P5: Keyboard map fully operable; reduced‑motion honored; visual QA checklist passes; no major jank during brush/zoom.

## Backend Additions (If Needed)
- Follow `src/backend/api` structure (routers in `server.py`, Pydantic in `models.py`, logic in `services.py`, DI in `dependencies.py`).
- Add endpoints listed under Data Access when absent; keep pagination/filters consistent with `API_DESIGN.md` (date ranges, tags, sources, limit/offset).
- Ensure REGULATION.md compliance: atomic files, META docs, and tests in `src/backend/api/test_api.py`.

## Visual QA Checklist
- Labels never overlap critically; truncation with middle ellipsis; full label in tooltip.
- Legends: clear, clickable, show active/inactive states; maintain color stability across sessions.
- Axis & ticks: consistent formatting; local time handling explicit; gridlines subtle.
- Tooltips: 300ms delay, 24px min target, anchored, never off‑screen; escape to dismiss.

## Metrics & Evaluation
- Engagement: time on page, interactions per session, story saves.
- Performance: first interaction < 2s after load; brush → response < 100ms visual feedback, < 300ms full redraw.
- Accessibility: contrast audit (AA), keyboard coverage, reduced‑motion compliance.
- Comprehension: task success in usability tests (find co‑occurrence partner; compare rhythms).

## Risks & Mitigations
- WebGL complexity: start with SVG for small sets; feature‑flag Pixi/regl; document fallback.
- Large data: pre‑aggregate in worker; simplify visuals beyond thresholds; virtualize and memoize aggressively.
- Color stability: HSL hashing with reserved palette for top tags; lock palette early; colorblind audit.

## Next Steps
- Decide Tailwind vs. Chakra (recommend Tailwind); finalize palette and type.
- Approve P1 scope; produce wireframes and token sheet; scaffold app and implement Timeline + Tag cards.

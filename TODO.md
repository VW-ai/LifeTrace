# Development2Development
This TODO is Designed to be update everytime we finished our current development. 
This TODO serves as a guideline on what we should work on the next time we come back to this project's development.
And every time we resume to development, we should read TODO first to know where to start
We follow an append-only strategy in the writing of thie file.

---
### Next Steps (as of 2025-08-28)

-   **[High Priority] Implement `notion_parser.py`:**
    -   Read `notion_content.json`.
    -   Implement recursive parsing of blocks.
    -   Implement filtering based on `last_edited_time` (with a default of 24 hours).
    -   Output a structured list of "document" objects as designed.

-   **[High Priority] Implement `google_calendar_parser.py`:**
    -   Read `google_calendar_events.json`.
    -   Implement parsing of events.
    -   Implement filtering based on the `updated` timestamp (with a default of 24 hours).
    -   Output a structured list of "document" objects consistent with the Notion parser's output.

-   **[Medium Priority] Implement the initial version of the AI agent:**
    -   The agent should be able to consume the output of both parsers.
    -   Implement a basic activity identification mechanism using an LLM.
    -   The agent should save the processed activities to a CSV/JSON file.

---
### Next Steps (as of 2025-08-29)

-   **[COMPLETED] ✅ Implement `google_calendar_parser.py`:**
    -   ✅ Read `google_calendar_events.json`.
    -   ✅ Implement parsing of events with time filtering.
    -   ✅ Implement filtering based on the `updated` timestamp.
    -   ✅ Output structured document objects consistent with Notion parser.
    -   ✅ Add comprehensive testing and documentation.

-   **[High Priority] Implement the AI Agent (`src/backend/agent/`):**
    -   Create agent directory structure with proper documentation.
    -   Implement data consumption from both notion and google calendar parsers.
    -   Design tag generation system with existing tag reuse logic.
    -   Implement LLM integration for activity categorization and tagging.
    -   Create raw activity table data structure (Date, Duration, Details, Source, Tags).
    -   Implement processed activity table with tag consolidation.
    -   Add agent testing framework.

-   **[High Priority] Database Schema Implementation:**
    -   Design and implement SQL database schema for raw and processed activity tables.
    -   Create database connection and CRUD operations.
    -   Implement data persistence for agent output.
    -   Add database migration scripts.

-   **[Medium Priority] Agent Intelligence Features:**
    -   Implement event matching between Notion edits and Calendar events.
    -   Add time estimation for unscheduled Notion activities.
    -   Create system-wide tag regeneration when tag:event ratio is too high.
    -   Implement decision logic for new/merged/abandoned Notion updates.

-   **[Low Priority] Integration & API Layer:**
    -   Create internal API endpoints for frontend data consumption.
    -   Implement data aggregation for charts (line, pie, breakdown list).
    -   Add time range filtering and query optimization.
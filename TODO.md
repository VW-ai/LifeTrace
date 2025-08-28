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

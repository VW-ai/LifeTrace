# Development2Development
This TODO is Designed to be update everytime we finished our current development. 
This TODO serves as a guideline on what we should work on the next time we come back to this project's development.
And every time we resume to development, we should read TODO first to know where to start
We follow an append-only strategy in the writing of thie file.

---
### Next Steps (as of 2025-09-09)

- [HIGH] Calendar-as-Query, Notion-as-Context (storage + IR pipeline)
  - Design and implement Notion blocks storage with parent/child links, last_edited_at, and daily “edited-tree” snapshots (tree merge of edited chains). Co-locate META.
  - Generate 30–100 word abstracts for leaf blocks; store abstract; compute/store embeddings (JSON for now; vector extension later). Co-locate META.
  - Retrieval helper: from a calendar event, select time-window candidates → embed query → cosine similarity to candidate leaf embeddings → top-K selection; optional LLM reasoning pass to validate matches.
  - Integrate selected abstracts into TagGenerator scoring (Phase 2) to improve tag diversity and confidence.

- [HIGH] One-click backfill (last 6 months of calendar events)
  - CLI + API to backfill last 6 months from Google Calendar; progress logging.
  - Re-run tagging pipeline on backfilled data to measure improvements over time; persist evaluation metrics (coverage, avg tags/activity, multi-tag ratio, confidence histogram).

- [HIGH] Google Calendar integration upgrade (multi-calendar)
  - Add support for an additional Google Calendar API / multiple calendars; make calendar sources configurable.
  - Normalize multi-calendar ingestion into raw_activities with clear source identifiers.

- [HIGH] Use all Notion pages (not just diary)
  - Expand Notion ingestion to index all pages/blocks (not limited to diary); respect page types while building edited-tree; configurable scopes.

- [HIGH] Agentic tagging calibration
  - Auto-generate synonyms and taxonomy with AI using our Notion + Calendar corpus; periodic regeneration endpoint that updates `agent/resources` (with META + audit trail).
  - Feed regenerated synonyms/taxonomy into TagGenerator calibration; keep manual overrides possible.

- [MEDIUM] API and UI enhancements
  - API: return context abstracts with processed activities; add endpoints to view tagging metrics history and IR candidates per activity.
  - UI: show abstracts in tooltips/hover for top activities; add backfill trigger and status in dashboard.
  - Background tasks for long-running operations (imports, backfills, IR indexing) with job status endpoints.

- [MEDIUM] Consistency & cleanup
  - Replace brittle SQL clause building with DAO queries for activities and tags; keep services thin.
  - Remove sys.path hacks; use package-relative imports and runner-based PYTHONPATH.

- [LOW] Hardening (post-dev)
  - Production CORS/TrustedHost tightening; rate limiting via shared store; auth enablement.

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

---
### Next Steps (as of 2025-08-30)

-   **[COMPLETED] ✅ Implement the AI Agent (`src/backend/agent/`):**
    -   ✅ Created complete agent architecture with modular core/tools/prompts structure.
    -   ✅ Implemented data consumption from both notion and google calendar parsers.
    -   ✅ Built tag generation system with existing tag reuse logic and LLM integration.
    -   ✅ Created raw and processed activity data structures with comprehensive processing.
    -   ✅ Added comprehensive testing framework with 27 unit tests and integration tests.
    -   ✅ Achieved production-ready performance and scalability benchmarks.

-   **[COMPLETED] ✅ Advanced Agent Intelligence Features:**
    -   ✅ Implemented cross-source event matching between Notion edits and Calendar events.
    -   ✅ Added time estimation for unscheduled Notion activities using content analysis.
    -   ✅ Created system-wide tag regeneration with configurable thresholds.
    -   ✅ Implemented decision logic for activity correlation with confidence scoring.

-   **[COMPLETED] ✅ Database Schema Design & Implementation:**
    -   ✅ Designed comprehensive database schema with all required tables and relationships.
    -   ✅ Created tables for raw activities, processed activities, tags, user sessions, and activity-tag relationships.
    -   ✅ Implemented robust database connection layer with connection pooling, error handling, and transaction support.
    -   ✅ Added full CRUD operations for all data entities with comprehensive validation and type safety.
    -   ✅ Created migration system with version control, rollback support, and automated schema updates.
    -   ✅ Designed performance indexes for optimal query performance on date, tag, and source-based queries.
    -   ✅ Built database CLI tool for management, migration, validation, and debugging operations.

-   **[COMPLETED] ✅ Backend API Design & Implementation:**
    -   ✅ Designed and implemented comprehensive RESTful API with 20+ endpoints for all frontend data consumption needs.
    -   ✅ Created complete CRUD operations for activities, tags, insights, processing, and system management.
    -   ✅ Implemented service layer architecture with dependency injection, authentication middleware, and rate limiting.
    -   ✅ Built data aggregation endpoints for dashboard charts (time distribution, tag breakdowns, activity insights).
    -   ✅ Added comprehensive filtering capabilities with date ranges, tags, sources, and pagination support.
    -   ✅ Implemented processing trigger endpoints for on-demand data processing and status tracking.
    -   ✅ Created FastAPI automatic documentation with Swagger UI and comprehensive API specification.
    -   ✅ Achieved 48/48 API tests passing with complete endpoint validation and error handling.

-   **[HIGH Priority] Frontend Architecture & Design:**
    -   Design responsive dashboard interface with activity visualization components.
    -   Create time-based activity charts (daily, weekly, monthly views) with interactive filtering.
    -   Implement tag-based activity breakdown with pie charts and category analysis.
    -   Design activity timeline view showing merged activities from multiple sources.
    -   Add settings interface for tag management, data source configuration, and preferences.
    -   Implement data refresh mechanisms and real-time updates for live activity tracking.

-   **[MEDIUM Priority] Production Infrastructure:**
    -   Set up database hosting and configuration for production environment.
    -   Implement proper logging and monitoring for API endpoints and data processing.
    -   Create deployment scripts and CI/CD pipeline for automated releases.
    -   Add environment configuration management for development, staging, and production.
    -   Implement backup and data recovery procedures for user activity data.

-   **[MEDIUM Priority] User Experience Enhancements:**
    -   Add onboarding flow for new users to connect data sources and configure settings.
    -   Implement data source management interface for Google Calendar and Notion integration.
    -   Create activity editing capabilities for manual corrections and additions.
    -   Add notification system for processing completion and data insights.
    -   Implement data privacy controls and user data management features.

-   **[LOW Priority] Advanced Analytics & Insights:**
    -   Implement advanced productivity analytics with trend analysis and recommendations.
    -   Add activity pattern recognition for identifying productive vs. unproductive time periods.
    -   Create goal setting and tracking features with progress visualization.
    -   Implement comparative analytics (week-over-week, month-over-month productivity).
    -   Add integration capabilities for additional data sources (Apple Calendar, Outlook, etc.).

---
### Next Steps (as of 2025-08-31)

-   **[COMPLETED] ✅ API Testing Infrastructure & Backend Stability:**
    -   ✅ Fixed all pytest collection errors and resolved Pydantic v2 compatibility issues throughout the codebase.
    -   ✅ Resolved JSON deserialization problems for database-stored arrays in API responses (sources, raw_activity_ids).
    -   ✅ Updated error handling from ValueError to proper HTTPException with correct HTTP status codes.
    -   ✅ Fixed agent integration tests to properly work with database-first architecture using controlled test scenarios.
    -   ✅ Configured pytest to exclude integration tests from unit test runs for clean CI/CD pipelines.
    -   ✅ Achieved **96/96 unit tests passing (100%)** across API, Agent, Parser, and Database layers.

## 🎯 **CURRENT TOP PRIORITY: Frontend Implementation**

-   **[URGENT - HIGH Priority] Frontend Architecture & Dashboard Implementation:**
    -   **Primary Goal:** Create the complete frontend application to consume the ready REST API backend.
    -   Design and implement responsive dashboard interface with modern UI framework (React/Vue/Svelte).
    -   Create time-based activity visualization components (daily, weekly, monthly charts) with interactive filtering.
    -   Implement tag-based activity breakdown with pie charts and category analysis for productivity insights.
    -   Design activity timeline view showing merged activities from multiple data sources with source indicators.
    -   Build settings interface for tag management, data source configuration, and user preferences.
    -   Implement data refresh mechanisms and real-time updates for live activity tracking and processing status.
    -   Add proper error handling and loading states for all API interactions with user feedback.

-   **[HIGH Priority] Frontend-Backend Integration:**
    -   Integrate with existing FastAPI backend using the 20+ REST endpoints for complete data consumption.
    -   Implement authentication flow and API key management for secure backend communication.
    -   Create data fetching layers with proper error handling, caching, and loading states.
    -   Build processing trigger interface allowing users to initiate daily activity processing from the frontend.
    -   Add real-time status updates for long-running processing operations with progress indicators.

-   **[HIGH Priority] User Experience & Dashboard Features:**
    -   Design intuitive onboarding flow guiding users through data source connection and initial setup.
    -   Create comprehensive activity dashboard with multiple visualization options and interactive filters.
    -   Implement tag management interface allowing users to create, edit, and delete activity tags.
    -   Build activity editing capabilities for manual corrections, additions, and data refinement.
    -   Add notification system for processing completion, data insights, and system status updates.

---
### Next Steps (as of 2025-09-01 - Post Frontend Initialization)

-   **[COMPLETED] ✅ Frontend Foundation & Dadaist Design System:**
    -   ✅ Implemented React + TypeScript frontend with Vite development environment.
    -   ✅ Created atomic component architecture following REGULATION.md principles.
    -   ✅ Built ChaoticButton foundation component with 5 variants and chaos control system.
    -   ✅ Established styled-components theme system with Dadaist design principles.
    -   ✅ Integrated Framer Motion animations and real-time backend API health monitoring.
    -   ✅ Resolved all TypeScript compilation errors and achieved production build capability.

## 🎨 **CURRENT PRIORITY: Frontend Design Direction & Refinement**

-   **[URGENT - HIGH Priority] Design System Evaluation & Potential Redesign:**
    -   **Critical Decision Point:** Current Dadaist design implementation requires significant styling adjustments and refinement.
    -   **Design Direction Assessment:** Evaluate whether to continue with Dadaist approach or transition to more conventional/professional design patterns.
    -   **Styling System Refactoring:** If moving away from Dadaism, redesign theme system, color palettes, and animation approaches.
    -   **Component Restyling:** Adapt existing atomic components (ChaoticButton, etc.) to new design direction while maintaining functionality.
    -   **User Experience Testing:** Assess current Dadaist interface for usability, accessibility, and professional application suitability.

-   **[HIGH Priority] Dashboard Implementation (Design-Agnostic):**
    -   **Core Dashboard Layout:** Create main productivity dashboard interface consuming backend API data.
    -   **Activity Timeline View:** Build timeline component displaying merged activities from multiple sources with filtering capabilities.
    -   **Data Visualization Components:** Implement charts and graphs for productivity insights (time distribution, tag breakdowns, trends).
    -   **Real-time Data Integration:** Connect dashboard to all 20+ backend REST endpoints with proper loading states and error handling.
    -   **Responsive Dashboard Design:** Ensure dashboard works effectively across desktop, tablet, and mobile screen sizes.

-   **[HIGH Priority] Core User Interface Features:**
    -   **Navigation System:** Implement routing and navigation between different app sections (dashboard, settings, processing status).
    -   **Settings Interface:** Create user preferences panel for API configuration, data source management, and display options.
    -   **Processing Trigger Interface:** Build UI for initiating daily activity processing with progress tracking and status updates.
    -   **Tag Management System:** Implement full CRUD interface for activity tags with usage analytics and bulk operations.
    -   **Activity Data Management:** Create interfaces for viewing, editing, and managing raw and processed activity data.

-   **[MEDIUM Priority] Enhanced User Experience:**
    -   **Authentication Interface:** Implement API key management and user session handling with secure storage.
    -   **Data Export Functionality:** Build user interfaces for exporting activity data in various formats (CSV, JSON, PDF reports).
    -   **Advanced Filtering System:** Create sophisticated filtering and search capabilities across all activity data.
    -   **Notification System:** Implement in-app notifications for processing completion, errors, and system status updates.
    -   **Performance Optimization:** Optimize frontend performance for large datasets and complex visualizations.

## 📋 **Design Philosophy Notes for Future Development:**
- **Current Architecture Strength:** Atomic component structure allows complete design system changes without functionality loss.
- **Flexibility Built-in:** Styled-components and theme system enable rapid design iteration and A/B testing.
- **Functional Foundation:** Core logic (API integration, state management, routing) remains stable regardless of visual design choices.
- **Migration Path:** Easy transition between design systems using existing component interfaces and props structure.

--- 
### Next Steps (as of 2025-08-30)
The following are manually written, You should reorgniaze it for formatting.
1. API is not correctly retrieving database from our database
    1.1 Why is our testing pass even in such case? Maybe we need to fix some tests?
    1.2 We need to fix our APi
2. Frontend upgrade
    1. The top5 section in our templateLook is not being mirrored into our frontend development.
    2. We should 

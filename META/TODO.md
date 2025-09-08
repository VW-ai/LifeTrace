# Development TODO
This TODO serves as a guideline for what we should work on next. It tracks both high-level goals and detailed implementation tasks. Updated after each development session to reflect current priorities.

---

## 🎯 **CURRENT MILESTONE: MILESTONE 2 - AI AGENT INTELLIGENCE & PRODUCTION READINESS**

### **Phase 1: AI-Native Tagging System** ✅ **COMPLETED (2025-09-07)**
- ✅ Taxonomy-first tagging architecture with controlled vocabulary
- ✅ AI-driven personalized taxonomy and synonym generation  
- ✅ Confidence-based tag assignment with review workflow foundation
- ✅ Bilingual support and personal context awareness

---

## 📋 **ACTIVE DEVELOPMENT PRIORITIES**

### **🚀 URGENT PRIORITY: Real Data Integration & Testing Infrastructure**

**Data Import & Processing:**
- **[URGENT] Import 3-Month Recent Calendar Events as Raw Activities**
  - Create calendar API data collection script or fix existing parsers
  - Import recent 3 months of actual calendar events into `raw_activities` table
  - Verify data structure and content quality for enhanced tagging testing
  - Document data collection workflow for future use

- **[URGENT] Generate Processed Activities from Real Calendar Data** 
  - Run enhanced AI-native tagging system on imported real calendar events
  - Test personalized taxonomy generation with actual user language patterns
  - Validate confidence scoring and synonym matching on real data
  - Demonstrate improved tagging quality vs old hardcoded system

**Development Workflow Enhancement:**
- **[MEDIUM URGENT] Expose Testing & Management APIs**
  - Add API endpoints for data import/export operations
  - Create endpoints for triggering tag regeneration and processing
  - Build database management APIs (clear data, reset, inspect stats)
  - Add development helper APIs to reduce need for custom scripts every update
  - Include debugging endpoints for system state inspection

### **🧠 HIGH PRIORITY: Milestone 2 Phase 2 - Integration & Intelligence**

**Activity Matching Engine Upgrades:**
- **[URGENT] Upgrade ActivityMatcher with TF-IDF cosine similarity** 
  - Replace current Jaccard similarity with TF-IDF for better semantic matching
  - Implement configurable time window (currently fixed at ±1 day, expand to ±2-3 days)
  - Add synonym normalization before similarity calculation
  - Session clustering: group raw events by proximity (≤45 min gaps)

- **[HIGH] Enhanced Cross-Source Correlation**
  - Current merge rate is 0.0% - needs significant improvement
  - Implement content similarity analysis beyond time-window matching
  - Add contextual understanding for recurring activities (meetings, work blocks)
  - Calendar-as-Query + Notion-as-Context retrieval system (from Tagging_Enhance_Proposal)

**Data Enrichment & Context:**
- **[HIGH] Enrich Parser Output with Additional Context**
  - Notion: capture parent page titles, database properties, relations, breadcrumbs
  - Calendar: capture description, attendees, location, recurrence metadata
  - Store enriched data in `RawActivity.raw_data` JSON field
  - Implement tree-structure preservation for Notion blocks

- **[MEDIUM] Project Memory & Priors**
  - Build "project dictionary" with top keywords, typical tags, time patterns
  - Use priors during tagging for better context-aware categorization
  - Implement duration estimation for unscheduled Notion activities

### **🔧 MEDIUM PRIORITY: System Integration & Quality**

**Confidence-Driven Review Workflow:**
- **[HIGH] Integrate Confidence Scores with Database**
  - Update ActivityProcessor to use `generate_tags_with_confidence_for_activity()`
  - Store confidence scores in `activity_tags.confidence_score` field
  - Mark `ProcessedActivity.is_review_needed` for confidence < 0.5

- **[MEDIUM] Review UI Implementation**
  - API filter: `GET /api/v1/activities/processed?review_needed=true`
  - Frontend review inbox for low-confidence activities
  - Bulk tag merge/rename capabilities
  - User feedback integration for improving confidence models

**Metrics & Quality Monitoring:**
- **[MEDIUM] Quality Metrics Implementation**
  - Track: merge_rate, avg_match_confidence, top_tag_coverage, tag_entropy
  - API endpoint: `GET /api/v1/system/stats` enhancement
  - Dashboard cards showing quality trends over time
  - Review queue size monitoring

### **🚀 LOW PRIORITY: Production Readiness**

**Personalized Taxonomy Deployment:**
- **[MEDIUM] AI-Generated Taxonomy Integration**
  - Run `update_taxonomy_from_data()` on user's full dataset
  - Generate personalized `tag_taxonomy_personalized.json` and `synonyms_personalized.json`
  - A/B test personalized vs generic taxonomy performance
  - User interface for taxonomy customization and management

**Advanced Features:**
- **[LOW] Embedding-Based Context Retrieval**
  - Implement Calendar → Notion context retrieval using embeddings
  - Generate abstracts (30-100 words) for matched activities
  - Semantic proximity graph for related activities
  - R@100 retrieval system for global context finding

---

## 🔄 **TECHNICAL DEBT & MAINTENANCE**

**Current System Limitations:**
- **[MEDIUM] Remove 3-day Processing Limitation**
  - Currently limited to 3-day subsets for development speed
  - Scale to full dataset (2,258+ raw activities) processing
  - Performance optimization for large-scale processing

- **[LOW] Database Schema Extensions** (Future consideration)
  - Add `parent_tag_id` to tags table for hierarchy support
  - Extend `processed_activities` with `is_review_needed` boolean field
  - Consider separate Calendar vs Notion storage schemas (per Tagging_Enhance_Proposal)

**Frontend Enhancement Needs:**
- **[MEDIUM] Tag Management Interface**
  - CRUD interface for taxonomy and tag management
  - Confidence score visualization and editing
  - Tag usage analytics and bulk operations

- ✅ **[COMPLETED] Responsive Design Optimization (2025-09-08)**
  - Fixed dashboard layout issues at 100% screen proportion
  - Resolved root container constraints and layout conflicts
  - Implemented responsive grid systems and breakpoints
  - Added cross-viewport compatibility with proper scaling

- **[LOW] Advanced Dashboard Features**
  - Navigation system between dashboard sections
  - Advanced filtering with confidence score ranges
  - Export functionality for tagged activity data

---

## 📊 **MILESTONE PROGRESS TRACKING**

### **Milestone 2 Scope Coverage:**
- ✅ **AI Agent Enhancements**: Tagging pipeline complete (Phase 1)
- 🔄 **Data Enrichment**: Parser upgrades pending
- 🔄 **Tag Taxonomy + Synonyms**: Base implementation complete, integration pending  
- ⏳ **Review UI + Rules**: Foundation ready, UI implementation needed
- ⏳ **Metrics & Monitoring**: API structure ready, implementation needed
- ⏳ **Production Readiness**: Basic auth exists, privacy controls needed

### **Success Metrics (Milestone 2 Targets):**
- **Match Rate Goal**: ≥40% (currently 0.0%) 
- **Tag Coverage Goal**: ≥80% activities mapped to top 12-20 tags
- **Review Efficiency Goal**: ≤10% activities flagged for review
- **Confidence Goal**: Average confidence ≥0.6 on processed activities

---

## 📝 **SESSION PLANNING NOTES**

**Immediate Next Session Priorities:**
1. **Data Import & Processing** - Get real calendar data into system to test enhanced tagging
2. **Enhanced API Tooling** - Reduce development friction with management APIs
3. **Activity Matching Upgrades** - Critical for improving 0.0% merge rate
4. **Confidence Score Integration** - Leverage completed tagging intelligence

**Dependencies & Considerations:**
- TF-IDF implementation may require additional libraries (sklearn, numpy)
- Large dataset processing may need chunking and progress tracking
- Personalized taxonomy generation requires sufficient activity history
- Review UI depends on frontend architectural decisions

---

*Last Updated: 2025-09-07 (Post AI-Native Tagging Implementation)*
*Next Update: After Milestone 2 Phase 2 completion*
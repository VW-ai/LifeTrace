# Agent Core Components

## Purpose
The core directory contains the fundamental data structures, processing logic, and orchestration components that drive the SmartHistory AI agent. These components implement the core business logic for activity processing, matching, and intelligent categorization.

## Contents

### agent.py
**Purpose**: Main agent orchestrator and entry point for activity processing workflows.
**Core Logic**: 
- Coordinates the complete processing pipeline from raw data to structured activities
- Manages session tracking and error handling
- Integrates with database layer for persistence
- Implements processing mode selection (daily, insights, etc.)

**Key Methods**:
- `process_activities()`: Main processing workflow orchestration
- `generate_insights()`: Analytics and insights generation
- Session management and progress tracking

### activity_processor.py
**Purpose**: Core activity processing engine that transforms raw activities into processed, tagged activities.
**Core Logic**:
- Manages the activity aggregation and merging pipeline
- Coordinates tag generation with enhanced AI-native system
- Implements confidence-based quality control
- Handles database integration for processed activities

**Processing Steps**:
1. Raw activity ingestion and validation
2. Activity matching and correlation
3. AI-native tag generation with confidence scoring
4. Quality assessment and review flagging
5. Database persistence with metadata

### activity_matcher.py
**Purpose**: Intelligent activity matching system for correlating activities across different sources.
**Core Logic**:
- Implements time-based correlation algorithms
- Future: TF-IDF cosine similarity for semantic matching
- Handles Notion-Calendar cross-source correlation
- Manages session clustering and proximity detection

**Matching Strategies**:
- Time window correlation (±1 day, expandable)
- Content similarity analysis (planned upgrade)
- Calendar-as-Query + Notion-as-Context retrieval (planned)

### data_consumer.py
**Purpose**: Data ingestion and validation layer for consuming parsed activity data.
**Core Logic**:
- Loads and validates data from parsers
- Implements data cleaning and normalization
- Handles multiple data source integration
- Provides unified data interface to processing components

**Data Sources**:
- Notion parser output
- Google Calendar parser output  
- Direct API integrations
- Database raw activity records

### models.py
**Purpose**: Core data models and structures used throughout the agent system.
**Core Logic**:
- Defines RawActivity and ProcessedActivity data models
- Implements TagGenerationContext for AI processing
- Provides validation and serialization logic
- Maintains compatibility with database schemas

**Key Models**:
- `RawActivity`: Individual activity records from data sources
- `ProcessedActivity`: Aggregated and tagged activity records
- `TagGenerationContext`: Context for AI tag generation
- Helper classes for data transformation and validation

## System Interactions

### Integration Flow
```
Parser Output → data_consumer → activity_processor → activity_matcher
                                       ↓
Database ← Processed Activities ← Enhanced Tag Generator
```

### Dependency Chain
- `agent.py` orchestrates all core components
- `activity_processor.py` uses `activity_matcher.py` and enhanced tag generation
- `data_consumer.py` provides data to processing pipeline
- `models.py` provides data structures to all components

## Enhanced Capabilities (Milestone 2)

### AI-Native Integration
- **Taxonomy-First Processing**: Core components now use controlled vocabulary
- **Confidence-Based Quality**: Processing includes confidence assessment and review workflows
- **Personalized Intelligence**: Core logic adapts to user-specific language patterns
- **Bilingual Support**: Native handling of mixed language content throughout pipeline

### Future Enhancements (Planned)
- **TF-IDF Matching**: Upgrade activity_matcher with semantic similarity
- **Session Clustering**: Group related activities by proximity and content
- **Calendar-Context Retrieval**: Implement Calendar-as-Query system from Tagging_Enhance_Proposal
- **Dynamic Processing**: Adaptive processing based on data patterns and quality metrics

## Performance Considerations
- **Batch Processing**: Optimized for processing large activity datasets
- **Memory Management**: Efficient handling of activity data structures
- **Database Integration**: Streamlined persistence with minimal overhead
- **Error Resilience**: Robust error handling throughout processing pipeline
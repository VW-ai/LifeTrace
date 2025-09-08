# AI Agent for Activity Processing

## Purpose
This module implements the enhanced AI agent responsible for processing and categorizing activities from both Notion and Google Calendar data sources. The agent uses a taxonomy-first approach with AI-native tagging to generate consistent, personalized activity categorization with confidence scoring.

## Core Architecture

### Single Agent Structure
Following the DESIGN.md specification, we use a single agent that accomplishes all processing tasks using specialized tools and workflows. Enhanced in Milestone 2 with AI-native intelligence.

### Enhanced Data Flow (Milestone 2)
1. **Input**: Consumes parsed data from:
   - `notion_parser` - Notion blocks with hierarchy and text content
   - `google_calendar_parser` - Calendar events with time and duration data
   - **New**: Direct Google Calendar API integration for real-time data import

2. **AI-Native Processing**: 
   - **Taxonomy-First Tagging**: Uses controlled vocabulary with 14+ categories
   - **Personalized Intelligence**: AI generates custom taxonomies from user data patterns
   - **Bilingual Support**: Handles mixed Chinese-English personal language patterns
   - **Confidence Scoring**: Multi-factor confidence assessment for quality control
   - **Synonym Mapping**: Intelligent mapping of personal shortcuts to categories
   - **Event Matching**: Correlates activities based on semantic similarity and time proximity

3. **Output**: Generates structured activity records with confidence-scored tags for database storage

## Key Components

### 1. Data Consumption (`data_consumer.py`)
- Loads and validates parsed data from both sources
- Implements time-based filtering and data cleaning
- Handles data format consistency

### 2. Activity Matcher (`activity_matcher.py`) 
- Matches Notion edits with Calendar events using time correlation
- Implements decision logic for new/merged/abandoned updates
- Handles unmatched activities appropriately

### 3. Enhanced Tag Generator (`tag_generator.py`) - **Milestone 2 Upgrade**
- **Taxonomy-First Approach**: Uses controlled vocabulary from `resources/tag_taxonomy.json`
- **AI-Powered Personalization**: Generates custom taxonomies from user data patterns
- **Bilingual Intelligence**: Handles Chinese-English mixed content via `resources/synonyms.json`
- **Multi-Method Tagging**: Combines synonym matching, keyword analysis, and LLM generation
- **Confidence Assessment**: Multi-factor scoring for tag assignment quality
- **Fuzzy Mapping**: Intelligent fallback system with taxonomy validation
- **Review Workflow**: Flags low-confidence activities for human review

### 4. Activity Processor (`activity_processor.py`)
- Main orchestrator that coordinates all processing steps
- Manages the workflow from raw data to structured activities
- Implements error handling and logging

### 5. Data Structures (`models.py`)
- Defines RawActivity and ProcessedActivity data models
- Implements validation and serialization logic
- Maintains consistency with database schema

## Integration Points
- **Input**: Consumes from `notion_parser` and `google_calendar_parser` outputs
- **Output**: Feeds into database layer for persistence
- **LLM**: Integrates with OpenAI API for intelligent categorization
- **Database**: Writes to raw and processed activity tables

### 6. AI Prompt Management (`prompts/`)
- **Taxonomy Generation**: Prompts for creating personalized taxonomies from user data
- **Synonym Extraction**: Prompts for learning personal language patterns and shortcuts
- **Enhanced Tag Prompts**: Taxonomy-injected prompts with structured JSON responses
- **Bilingual Context**: Prompts optimized for mixed Chinese-English content

### 7. Resource Management (`resources/`)
- **Canonical Taxonomy**: `tag_taxonomy.json` with 14+ categories and bilingual keywords
- **Synonym Mappings**: `synonyms.json` with personal shortcuts and technical terms
- **Personalized Resources**: Auto-generated user-specific taxonomies and synonyms
- **Version Control**: Timestamped resources for schema evolution

## Key Features (Enhanced Milestone 2)
- **AI-Native Intelligence**: Personalized taxonomy generation from actual user data
- **Bilingual Processing**: Native support for Chinese-English mixed content
- **Confidence-Based Quality**: Multi-factor confidence scoring with review workflows
- **Taxonomy-First Consistency**: Controlled vocabulary prevents tag proliferation
- **Fallback Resilience**: Intelligent heuristics work without LLM API access
- **Personal Context Awareness**: Learns project names, shortcuts, and user patterns
- **Real-Time Data Integration**: Direct API connections for live calendar import
- **Comprehensive Testing**: 25+ test cases covering all functionality
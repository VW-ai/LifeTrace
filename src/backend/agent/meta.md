# AI Agent for Activity Processing

## Purpose
This module implements the core AI agent responsible for processing and categorizing activities from both Notion and Google Calendar data sources. The agent uses LLM capabilities to generate consistent tags and organize time-tracking data into structured activity records.

## Core Architecture

### Single Agent Structure
Following the DESIGN.md specification, we use a single agent that accomplishes all processing tasks using specialized tools and workflows.

### Data Flow
1. **Input**: Consumes parsed data from:
   - `notion_parser` - Notion blocks with hierarchy and text content
   - `google_calendar_parser` - Calendar events with time and duration data

2. **Processing**: 
   - **Event Matching**: Correlates Notion edits with Calendar events based on time proximity
   - **Tag Generation**: Uses LLM to generate consistent activity tags
   - **Tag Reuse**: Queries existing tags to maintain consistency
   - **Duration Estimation**: Estimates time for unscheduled Notion activities

3. **Output**: Generates structured activity records for database storage

## Key Components

### 1. Data Consumption (`data_consumer.py`)
- Loads and validates parsed data from both sources
- Implements time-based filtering and data cleaning
- Handles data format consistency

### 2. Activity Matcher (`activity_matcher.py`) 
- Matches Notion edits with Calendar events using time correlation
- Implements decision logic for new/merged/abandoned updates
- Handles unmatched activities appropriately

### 3. Tag Generator (`tag_generator.py`)
- Uses LLM integration for intelligent tag generation
- Implements existing tag reuse logic to maintain consistency
- Handles system-wide tag regeneration when tag:event ratio exceeds threshold

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

## Key Features
- Time-based correlation between different data sources
- Intelligent tag generation with consistency enforcement
- Robust error handling for malformed or missing data
- Configurable processing parameters
- Comprehensive logging for debugging and monitoring
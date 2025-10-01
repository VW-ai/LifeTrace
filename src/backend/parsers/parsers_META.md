# Data Parsers Module

## Purpose
This module contains data parsers responsible for extracting and normalizing activity data from external sources. Each parser handles source-specific data formats and converts them into standardized internal formats for the agent processing pipeline.

## Architecture

### Parser Structure
Each parser follows a consistent interface pattern:
- **Input**: Raw data from external APIs or exports
- **Processing**: Data normalization, validation, and enrichment
- **Output**: Standardized data structures for agent consumption

### Supported Data Sources

#### 1. Google Calendar Parser (`google_calendar/`)
- **Purpose**: Extracts calendar events and time-based activities
- **Input**: Google Calendar API data
- **Output**: Normalized event data with timestamps and metadata
- **Key Features**:
  - Time zone handling
  - Recurring event expansion
  - Attendee information processing
  - Event categorization

#### 2. Notion Parser (`notion/`)
- **Purpose**: Extracts content blocks and page hierarchies from Notion
- **Input**: Notion API data (blocks, pages, databases)
- **Output**: Structured content with hierarchy and relationships
- **Key Features**:
  - Block hierarchy preservation
  - Content type handling (text, code, tables, etc.)
  - Page relationship mapping
  - Database record processing

## Data Flow

```
External APIs → Parsers → Standardized Data → Agent Processing → Database
    ↓              ↓           ↓                  ↓              ↓
Calendar API → gcal_parser → Event Objects → Activity Matcher → Activities
Notion API  → notion_parser → Content Blocks → Tag Generator → Tagged Activities
```

## Integration Points

### Input Sources
- **Google Calendar API**: OAuth2-authenticated calendar access
- **Notion API**: Integration token-based workspace access

### Output Consumers
- **Agent Module**: Primary consumer for activity processing
- **Database Layer**: Direct storage for raw parsed data
- **API Module**: Serves parsed data to frontend

## Key Features

### Data Validation
- Schema validation for all parsed data
- Error handling for malformed source data
- Data completeness verification

### Performance Optimization
- Incremental parsing for large datasets
- Caching of frequently accessed data
- Efficient API rate limit handling

### Extensibility
- Pluggable parser interface for new data sources
- Configurable data transformation pipelines
- Modular parser component design

## Configuration

### Google Calendar Parser
- API credentials and OAuth2 configuration
- Calendar selection and filtering rules
- Time range and sync frequency settings

### Notion Parser
- Integration token configuration
- Workspace and database selection
- Content filtering and parsing depth

## Testing

### Unit Tests
- Individual parser component testing
- Data transformation verification
- Error handling validation

### Integration Tests
- End-to-end parsing workflows
- API connectivity testing
- Data consistency verification

## Future Enhancements

### Additional Sources
- Slack workspace integration
- GitHub activity parsing
- Email client integration (Outlook, Gmail)
- Time tracking app integration (Toggl, RescueTime)

### Performance Improvements
- Streaming parser implementation
- Parallel processing for multiple sources
- Advanced caching strategies

### Data Enrichment
- Automatic content categorization
- Location and context extraction
- Sentiment analysis for text content
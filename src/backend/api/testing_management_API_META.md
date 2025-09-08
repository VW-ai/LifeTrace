# Testing and Management API Endpoints

## Purpose
This document describes the testing and management API endpoints that provide developers with easy access to enhanced tagging system functionality, hierarchical tagging capabilities, and system management operations without requiring custom scripts.

## Core Logic

### Testing Endpoints
**Path Prefix**: `/api/v1/test/`

#### POST /api/v1/test/hierarchical-tagging
**Purpose**: Test three-layer hierarchical tagging system on recent activities.
**Parameters**:
- `limit` (query): Number of recent activities to test (default: 10, max: 100)

**Response Structure**:
```json
{
  "status": "success",
  "test_results": [...],  // First 5 results for brevity
  "summary": {
    "total_activities": 10,
    "coverage_stats": {...},
    "confidence_stats": {...}
  },
  "hierarchical_system_available": true
}
```

#### POST /api/v1/test/enhanced-tagging  
**Purpose**: Test enhanced taxonomy-first tagging on recent activities.
**Parameters**:
- `limit` (query): Number of recent activities to test (default: 10, max: 100)

**Response**: Test results with confidence scores and taxonomy matching details.

### Management Endpoints
**Path Prefix**: `/api/v1/management/`

#### GET /api/v1/management/taxonomy
**Purpose**: Get current taxonomy and hierarchical structure information.
**Response**: Complete taxonomy structure, synonyms, and statistics.

#### POST /api/v1/management/update-taxonomy
**Purpose**: Update taxonomy and synonyms from user activity data.
**Parameters**:
- `max_categories` (query): Maximum categories to generate (default: 20, range: 10-50)

#### POST /api/v1/management/regenerate-tags
**Purpose**: Regenerate tags for all activities using enhanced system.
**Parameters**:
- `force` (query): Force regeneration even if activities already tagged (default: false)
- `batch_size` (query): Batch processing size (default: 100, range: 10-1000)

#### GET /api/v1/management/tag-coverage
**Purpose**: Get tag coverage statistics for recent activities.
**Parameters**:
- `days_back` (query): Number of days to analyze (default: 30, max: 365)

#### POST /api/v1/management/import-calendar
**Purpose**: Import calendar activities from specified months back.
**Parameters**:
- `months_back` (query): Number of months to import (default: 3, max: 12)

#### GET /api/v1/management/activity-summary
**Purpose**: Get comprehensive activity summary with hierarchical tagging.
**Parameters**:
- `days_back` (query): Days to analyze (default: 7, max: 365)
- `include_hierarchical` (query): Include hierarchical analysis (default: true)

## System Interactions

### Service Layer Integration
- **TagService**: Handles testing and taxonomy management operations
- **ProcessingService**: Manages bulk operations and imports
- **SystemService**: Provides comprehensive summaries and statistics

### Enhanced Tagging Integration
- **TagGenerator**: Core enhanced tagging with confidence scoring
- **Hierarchical System**: Three-layer nature/subject/project classification
- **Fallback Support**: Graceful degradation when OpenAI API unavailable

### Database Operations
- **Atomic Operations**: Each endpoint performs focused, single-purpose tasks
- **Batch Processing**: Large operations handled in configurable batches
- **Error Resilience**: Comprehensive error handling and status reporting

## Implementation Benefits

### Developer Experience
- **No Custom Scripts**: All functionality accessible via REST API
- **Immediate Testing**: Quick validation of tagging improvements
- **Real Data**: Tests run on actual user activities, not synthetic data
- **Progress Tracking**: Detailed status and progress reporting

### System Management
- **Easy Maintenance**: Bulk operations available via API calls
- **Performance Monitoring**: Coverage and confidence statistics
- **Taxonomy Evolution**: AI-driven taxonomy updates from user data
- **Import Automation**: Programmatic data import capabilities

### REGULATION.md Compliance
- **Atomic Functionality**: Each endpoint serves single, well-defined purpose
- **Comprehensive Documentation**: Complete API specifications and usage
- **Error Handling**: Robust error responses with helpful messages
- **Resource Management**: Configurable limits and batch processing

## Usage Examples

### Test Hierarchical Tagging
```bash
curl -X POST "http://localhost:8000/api/v1/test/hierarchical-tagging?limit=5"
```

### Get Taxonomy Information
```bash
curl "http://localhost:8000/api/v1/management/taxonomy"
```

### Check Tag Coverage
```bash
curl "http://localhost:8000/api/v1/management/tag-coverage?days_back=14"
```

### Regenerate All Tags
```bash
curl -X POST "http://localhost:8000/api/v1/management/regenerate-tags?batch_size=50&force=true"
```

## Security Considerations
- **Rate Limiting**: Implemented via existing auth middleware
- **Timeout Protection**: Long operations include timeout handling
- **Resource Limits**: Configurable limits prevent resource exhaustion
- **Error Isolation**: Failures don't affect other system components

## Future Enhancements
- **WebSocket Support**: Real-time progress updates for long operations
- **Scheduled Operations**: Background task scheduling for maintenance
- **Export Capabilities**: Data export in various formats
- **Advanced Analytics**: Enhanced insights and visualization support
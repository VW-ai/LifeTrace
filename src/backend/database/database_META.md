# Database Package Documentation

## Purpose
The database package provides comprehensive data persistence capabilities for SmartHistory, implementing a robust SQLite-based storage system with connection management, migration support, and type-safe data operations.

## Core Components

### Directory Structure (Following REGULATION.md 2.5)
```
database/
├── __init__.py                 - Package initialization and public API
├── database_META.md            - This documentation file
├── core/                       - Core infrastructure components
│   ├── config.py              - Configuration management
│   ├── connection_pool.py     - Connection pooling and lifecycle
│   ├── transaction_manager.py - Query execution and transactions
│   ├── database_manager.py    - Component coordination
│   └── core_META.md           - Core components documentation
├── access/                     - Data access layer
│   ├── models.py              - Data models and DAOs
│   └── access_META.md         - Data access documentation
├── schema/                     - Schema management
│   ├── schema_manager.py      - Schema initialization and validation
│   ├── migrations.py          - Migration system
│   ├── schema.sql             - Database schema definition
│   ├── migrations/            - Migration files
│   └── schema_META.md         - Schema management documentation
├── tools/                      - Tools and utilities
│   ├── cli.py                 - Command-line interface
│   └── tools_META.md          - Tools documentation
└── ../test_features/database_tests/ - Comprehensive test suite
```

### Atomic Organization Benefits
- **Core**: Infrastructure components with single responsibilities
- **Access**: Data layer completely separated from infrastructure
- **Schema**: All schema-related functionality in one place
- **Tools**: Operational utilities isolated from core logic

## Architecture Overview

### Data Flow
```
Application Layer
       ↓
   DAO Classes (models.py)
       ↓
Connection Manager (connection.py)
       ↓
   SQLite Database
```

### Core Logic

**Connection Management:**
- Singleton pattern per database path for efficient resource usage
- Thread-safe connection pooling with configurable pool size
- Automatic retry mechanisms and graceful error handling
- Transaction support with automatic rollback on failures

**Data Layer:**
- Type-safe data models with comprehensive validation
- Atomic CRUD operations through Data Access Objects
- Support for complex queries with proper indexing
- JSON metadata storage for flexible data structures

**Schema Evolution:**
- Version-controlled database migrations with rollback support
- Automatic schema validation and integrity checking
- SQL file-based migrations with Python function support

## Database Schema

### Core Tables
1. **raw_activities** - Individual activity records from data sources
2. **processed_activities** - Aggregated and tagged activity groups
3. **tags** - Tag vocabulary with usage tracking
4. **activity_tags** - Many-to-many relationships with confidence scores
5. **user_sessions** - System processing session tracking
6. **tag_generations** - Tag generation history and analytics
7. **schema_versions** - Migration version control

### Key Relationships
- Processed activities aggregate multiple raw activities
- Tags have many-to-many relationships with processed activities
- Confidence scoring tracks AI tag assignment accuracy
- Automatic usage count maintenance via database triggers

## Integration Points

### With AI Agent System
```python
# Agent creates raw activities from parsed data
raw_activity = RawActivityDB(date='2025-08-31', source='notion', ...)
activity_id = RawActivityDAO.create(raw_activity)

# Agent processes and tags activities
processed = ProcessedActivityDB(raw_activity_ids=[activity_id], ...)
processed_id = ProcessedActivityDAO.create(processed)

# Agent assigns tags with confidence scores
ActivityTagDAO.create(ActivityTagDB(
    processed_activity_id=processed_id,
    tag_id=tag_id,
    confidence_score=0.85
))
```

### With API Layer (Future)
- DAOs provide clean data access interface for API endpoints
- Connection manager handles concurrent API requests efficiently
- Migration system supports schema evolution without downtime

## Performance Characteristics

### Optimizations
- Comprehensive indexing strategy for common query patterns
- Connection pooling reduces connection overhead
- WAL mode for better concurrent access
- Optimized SQLite configuration for performance

### Scalability
- Designed to handle thousands of activities efficiently
- Batch operations for bulk data processing
- Memory-efficient query patterns with proper pagination

## Error Handling

### Exception Hierarchy
- `DatabaseConnectionError` - Connection-related issues
- `DatabaseOperationError` - Query execution failures
- Validation errors at model level prevent invalid data persistence

### Recovery Mechanisms
- Automatic connection retry with exponential backoff
- Transaction rollback on any operation failure
- Connection pool cleanup and recreation on persistent errors

## Usage Examples

### Basic Operations
```python
from src.backend.database import RawActivityDAO, RawActivityDB

# Create activity
activity = RawActivityDB(date='2025-08-31', source='notion', details='Work')
activity_id = RawActivityDAO.create(activity)

# Query activities
activities = RawActivityDAO.get_by_date_range('2025-08-01', '2025-08-31')
```

### Migration Management
```bash
# Check database status
python -m src.backend.database.cli status

# Run migrations
python -m src.backend.database.cli migrate

# Validate integrity
python -m src.backend.database.cli validate
```

## Future Enhancements

### Planned Features
- Database connection monitoring and metrics
- Advanced query optimization and caching
- Support for distributed database configurations
- Enhanced CLI tools for data analysis and debugging

### Extensibility Points
- Custom migration functions for complex schema changes
- Pluggable connection backends beyond SQLite
- Configurable indexing strategies based on usage patterns
# Database Schema Components

## Purpose
Schema management system providing database initialization, validation, and evolution capabilities through version-controlled migrations.

## Components

### schema_manager.py
- **Purpose**: Database schema initialization and validation
- **Core Logic**:
  - Loads and executes schema.sql for initial database setup
  - Validates that all required tables exist with correct structure
  - Provides table introspection capabilities
- **Integration**: Used by DatabaseManager during initialization

### migrations.py
- **Purpose**: Database migration system with version control
- **Core Logic**:
  - **Migration Discovery**: Loads migration files from migrations/ directory
  - **Version Tracking**: Maintains schema_versions table for state management
  - **Forward/Rollback**: Supports both up and down migrations
  - **Validation**: Ensures database consistency before and after migrations
- **Integration**: Used by CLI tools and can be invoked programmatically

### schema.sql
- **Purpose**: Initial database schema definition
- **Core Logic**:
  - Defines all tables with proper relationships and constraints
  - Creates performance indexes for common query patterns
  - Sets up database triggers for automatic timestamp and count maintenance
- **Integration**: Executed by SchemaManager during first-time setup

### migrations/ (directory)
- **Purpose**: Version-controlled schema evolution files
- **Core Logic**: SQL files with numbered prefixes for ordered execution
- **Integration**: Discovered and executed by MigrationManager

## Migration System Architecture

### Version Control Flow
```
Current DB State → Migration Discovery → Version Comparison → Execute Migrations → Update Version
```

### Migration File Format
- **Naming**: `001_description.sql`, `002_add_indexes.sql`, etc.
- **Structure**: UP section followed by optional DOWN section
- **Discovery**: Automatic loading from migrations/ directory

### Safety Features
- **Transaction Wrapping**: All migrations execute in transactions with rollback on failure
- **Validation**: Schema validation before and after migration execution
- **Version Tracking**: Prevents duplicate execution and enables rollback

## Database Schema Design

### Table Relationships
- **raw_activities**: Source data from Notion/Calendar
- **processed_activities**: Aggregated activities with AI processing
- **tags**: Vocabulary management with usage tracking
- **activity_tags**: Many-to-many with confidence scoring
- **user_sessions**: Processing history and system state
- **schema_versions**: Migration version control

### Performance Features
- **Indexes**: Comprehensive indexing for date, tag, and source queries
- **Triggers**: Automatic timestamp updates and usage count maintenance
- **WAL Mode**: Optimized for concurrent access patterns

## Integration Points

### With Core Components
- SchemaManager ensures proper database initialization
- Migration system enables zero-downtime schema updates

### With CLI Tools
- Migration commands for operational database management
- Validation tools for integrity checking and debugging
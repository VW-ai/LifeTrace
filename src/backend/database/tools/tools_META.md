# Database Tools and Utilities

## Purpose
Command-line tools and utilities for database management, operations, and debugging. Provides operational capabilities for database administration and maintenance.

## Components

### cli.py
- **Purpose**: Command-line interface for database operations
- **Core Logic**:
  - **status**: Database health check and statistics
  - **migrate**: Schema migration management with safety checks
  - **validate**: Data integrity checking with automated fixes
  - **backup**: Database backup creation
  - **info**: Detailed database structure information
- **Integration**: Uses core database components through public APIs

## CLI Commands

### Database Status (`status`)
- **Purpose**: System health and statistics overview
- **Information Provided**:
  - Database connection status and file location
  - Current schema version and pending migrations
  - Table row counts and recent session information
- **Usage**: `python -m src.backend.database.tools.cli status`

### Migration Management (`migrate`)
- **Purpose**: Execute database schema migrations
- **Features**:
  - Version targeting (migrate to specific version)
  - Safety confirmations for production use
  - Automatic rollback on failure
- **Usage**: `python -m src.backend.database.tools.cli migrate [--version N] [--force]`

### Data Validation (`validate`)
- **Purpose**: Check data integrity and schema consistency
- **Checks Performed**:
  - Schema validation against expected structure
  - Foreign key relationship integrity
  - Tag usage count accuracy
  - Orphaned record detection
- **Usage**: `python -m src.backend.database.tools.cli validate [--fix]`

### Backup Creation (`backup`)
- **Purpose**: Create database backups for disaster recovery
- **Features**:
  - SQLite-optimized backup process
  - Timestamped backup file naming
  - Verification of backup integrity
- **Usage**: `python -m src.backend.database.tools.cli backup [--output path]`

### Database Information (`info`)
- **Purpose**: Detailed database structure and metadata
- **Information Provided**:
  - Complete table structure with columns and types
  - Row counts for all tables
  - Migration history with timestamps
  - Index information and query optimization data
- **Usage**: `python -m src.backend.database.tools.cli info`

## Operational Integration

### Development Workflow
- Use `status` to check database state during development
- Use `migrate` to apply schema changes safely
- Use `validate` to catch data integrity issues early

### Production Deployment
- Use `backup` before major operations
- Use `migrate` with safety confirmations for schema updates
- Use `validate` for health checks and monitoring

## Error Handling
- Comprehensive error messages with actionable suggestions
- Graceful handling of database connection failures
- Safe defaults to prevent accidental data loss
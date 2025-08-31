# Database Core Components

## Purpose
Core infrastructure components that provide the foundation for all database operations in SmartHistory. These components handle connection management, transaction processing, and system coordination following atomic design principles.

## Components

### config.py
- **Purpose**: Database connection configuration with validation
- **Core Logic**: Validates configuration parameters and ensures database directory exists
- **Integration**: Used by ConnectionPool and DatabaseManager for initialization

### connection_pool.py  
- **Purpose**: Thread-safe connection pooling and lifecycle management
- **Core Logic**: 
  - Maintains pool of reusable SQLite connections
  - Validates connections before reuse
  - Handles connection creation with optimal SQLite settings
- **Integration**: Used by TransactionManager for all database operations

### transaction_manager.py
- **Purpose**: Database transaction management and query execution
- **Core Logic**:
  - Provides transaction context managers with automatic rollback
  - Handles query execution with proper error handling
  - Supports batch operations for performance
- **Integration**: Used by DatabaseManager and all DAO classes

### database_manager.py
- **Purpose**: Main coordinator that orchestrates all core components
- **Core Logic**:
  - Implements singleton pattern per database path
  - Coordinates between connection pool, schema manager, and transaction manager
  - Provides unified public API surface
- **Integration**: Primary interface used by application layer and DAO classes

## Architecture Flow
```
Application → DatabaseManager → TransactionManager → ConnectionPool → SQLite
                    ↓
               SchemaManager (initialization)
```

## Thread Safety
All components are designed to be thread-safe:
- ConnectionPool uses locks for pool access
- TransactionManager ensures atomic operations
- DatabaseManager coordinates safe component interaction
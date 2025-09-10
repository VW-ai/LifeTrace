#!/usr/bin/env python3
"""
SmartHistory Database Package

Provides database connection, models, and operations for the SmartHistory application.
This package follows atomic design principles with separate components for:

- Connection pooling and management
- Schema initialization and validation
- Transaction management and query execution
- Data models and access objects
- Migration system with version control

Usage:
    from src.backend.database import get_db_manager, RawActivityDAO, TagDAO
    
    # Initialize database
    db = get_db_manager()
    
    # Create a new activity
    activity = RawActivityDB(date='2025-08-31', source='notion', details='Working on code')
    activity_id = RawActivityDAO.create(activity)
"""

# Import atomic components from organized subdirectories
from typing import Optional
from .core.config import ConnectionConfig
from .core.connection_pool import DatabaseConnectionError
from .core.transaction_manager import DatabaseOperationError  
from .core.database_manager import DatabaseManager

# Maintain backward compatibility
def get_db_manager(config: Optional[ConnectionConfig] = None) -> DatabaseManager:
    """Get the database manager instance for the given config."""
    return DatabaseManager.get_instance(config)

def initialize_database(db_path: str = None) -> DatabaseManager:
    """Initialize database with custom path."""
    if db_path:
        config = ConnectionConfig(db_path=db_path)
    else:
        config = ConnectionConfig()
    return get_db_manager(config)

# Convenience functions for backward compatibility
def execute_query(query: str, params=None):
    """Execute a SELECT query using the default database manager."""
    return get_db_manager().execute_query(query, params)

def execute_update(query: str, params=None) -> int:
    """Execute an UPDATE/INSERT/DELETE query using the default database manager."""
    return get_db_manager().execute_update(query, params)

def transaction():
    """Get a transaction context manager from the default database manager."""
    return get_db_manager().transaction()

from .access.models import (
    # Enums
    SessionStatus,
    GenerationType,
    
    # Database Models
    RawActivityDB,
    ProcessedActivityDB,
    TagDB,
    ActivityTagDB,
    UserSessionDB,
    TagGenerationDB,
    
    # Data Access Objects
    RawActivityDAO,
    ProcessedActivityDAO,
    TagDAO,
    ActivityTagDAO,
    UserSessionDAO
)

# Notion storage exports
from .access.notion_blocks_dao import (
    NotionPageDB,
    NotionBlockDB,
    NotionBlockEditDB,
    NotionEmbeddingDB,
    NotionPageDAO,
    NotionBlockDAO,
    NotionBlockEditDAO,
    NotionEmbeddingDAO,
)

__all__ = [
    # Atomic components
    'DatabaseManager',
    'ConnectionConfig',
    'DatabaseConnectionError', 
    'DatabaseOperationError',
    
    # Public interface
    'get_db_manager',
    'initialize_database',
    'execute_query',
    'execute_update',
    'transaction',
    
    # Enums
    'SessionStatus',
    'GenerationType',
    
    # Models
    'RawActivityDB',
    'ProcessedActivityDB',
    'TagDB',
    'ActivityTagDB', 
    'UserSessionDB',
    'TagGenerationDB',
    
    # DAOs
    'RawActivityDAO',
    'ProcessedActivityDAO',
    'TagDAO',
    'ActivityTagDAO',
    'UserSessionDAO'
    ,
    # Notion
    'NotionPageDB',
    'NotionBlockDB',
    'NotionBlockEditDB',
    'NotionEmbeddingDB',
    'NotionPageDAO',
    'NotionBlockDAO',
    'NotionBlockEditDAO',
    'NotionEmbeddingDAO'
]

# Package version
__version__ = '1.0.0'

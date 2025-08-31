#!/usr/bin/env python3
"""
Database Schema Manager for SmartHistory

Handles database schema initialization and validation
following the atomic responsibility principle.
"""

import logging
from pathlib import Path
from typing import Optional
from ..core.connection_pool import ConnectionPool

logger = logging.getLogger(__name__)

class DatabaseSchemaError(Exception):
    """Custom exception for database schema errors."""
    pass

class SchemaManager:
    """
    Database schema initialization and management.
    
    Responsible for:
    - Schema file loading and execution
    - Schema validation
    - Table existence checking
    """
    
    def __init__(self, connection_pool: ConnectionPool):
        """Initialize schema manager with connection pool."""
        self.pool = connection_pool
        self.schema_path = Path(__file__).parent / "schema.sql"
    
    def initialize_schema(self) -> None:
        """Initialize database schema from SQL file."""
        try:
            if not self.schema_path.exists():
                logger.warning(f"Schema file not found: {self.schema_path}")
                return
                
            with self.pool.get_connection() as conn:
                schema_sql = self._load_schema_file()
                conn.executescript(schema_sql)
                conn.commit()
                logger.info("Database schema initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise DatabaseSchemaError(f"Schema initialization failed: {e}")
    
    def _load_schema_file(self) -> str:
        """Load schema SQL from file."""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            raise DatabaseSchemaError(f"Failed to read schema file: {e}")
    
    def validate_schema(self) -> bool:
        """Validate that required tables exist."""
        required_tables = [
            'schema_versions',
            'raw_activities',
            'processed_activities', 
            'tags',
            'activity_tags',
            'user_sessions',
            'tag_generations'
        ]
        
        try:
            with self.pool.get_connection() as conn:
                for table in required_tables:
                    if not self._table_exists(conn, table):
                        logger.error(f"Required table '{table}' is missing")
                        return False
                        
            logger.debug("Schema validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False
    
    def _table_exists(self, conn, table_name: str) -> bool:
        """Check if a table exists in the database."""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        return cursor.fetchone() is not None
    
    def get_table_info(self, table_name: str) -> list:
        """Get column information for a table."""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name})")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get table info for {table_name}: {e}")
            raise DatabaseSchemaError(f"Table info retrieval failed: {e}")
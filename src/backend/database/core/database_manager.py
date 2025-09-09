#!/usr/bin/env python3
"""
Database Manager for SmartHistory

Main database interface that coordinates atomic components
following the atomic responsibility principle.
"""

import logging
from typing import Optional, Union, Tuple, Dict, List
import sqlite3
from .config import ConnectionConfig
from .connection_pool import ConnectionPool
from ..schema.schema_manager import SchemaManager
from .transaction_manager import TransactionManager

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Main database interface coordinating atomic components.
    
    Responsible for:
    - Component coordination
    - Public API surface
    - Instance management per database path
    """
    
    _instances = {}  # Support multiple instances for testing
    _lock = None
    
    def __init__(self, config: Optional[ConnectionConfig] = None):
        """Initialize database manager with atomic components."""
        self.config = config or ConnectionConfig()
        
        # Initialize atomic components
        self.pool = ConnectionPool(self.config)
        self.schema = SchemaManager(self.pool)
        self.transactions = TransactionManager(self.pool)
        
        # Initialize database schema
        self.schema.initialize_schema()
        
        logger.debug(f"DatabaseManager initialized for {self.config.db_path}")
    
    @classmethod
    def get_instance(cls, config: Optional[ConnectionConfig] = None):
        """Get database manager instance for configuration."""
        import threading
        if cls._lock is None:
            cls._lock = threading.Lock()
            
        config = config or ConnectionConfig()
        db_path = config.db_path
        
        if db_path not in cls._instances:
            with cls._lock:
                if db_path not in cls._instances:
                    cls._instances[db_path] = cls(config)
        
        return cls._instances[db_path]
    
    # Query execution methods (delegate to transaction manager)
    def execute_query(self, query: str, 
                     params: Optional[Union[Tuple, Dict]] = None) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results."""
        return self.transactions.execute_query(query, params)
    
    def execute_update(self, query: str, 
                      params: Optional[Union[Tuple, Dict]] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query."""
        return self.transactions.execute_update(query, params)
    
    def execute_insert(self, query: str,
                       params: Optional[Union[Tuple, Dict]] = None) -> int:
        """Execute an INSERT and return last inserted row id."""
        return self.transactions.execute_insert(query, params)
    
    def execute_batch(self, query: str, 
                     params_list: List[Union[Tuple, Dict]]) -> int:
        """Execute a batch of queries with different parameters."""
        return self.transactions.execute_batch(query, params_list)
    
    def transaction(self):
        """Get a transaction context manager."""
        return self.transactions.transaction()
    
    def get_last_insert_id(self) -> Optional[int]:
        """Get the ID of the last inserted row."""
        return self.transactions.get_last_insert_id()
    
    # Schema management methods (delegate to schema manager)
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        try:
            with self.pool.get_connection() as conn:
                return self.schema._table_exists(conn, table_name)
        except Exception:
            return False
    
    def get_table_info(self, table_name: str) -> List[Dict]:
        """Get column information for a table."""
        return self.schema.get_table_info(table_name)
    
    def validate_schema(self) -> bool:
        """Validate that required tables exist."""
        return self.schema.validate_schema()
    
    # Connection management (delegate to pool)
    def get_connection(self):
        """Get a database connection context manager."""
        return self.pool.get_connection()
    
    def close_all_connections(self) -> None:
        """Close all connections in the pool."""
        self.pool.close_all_connections()
    
    def get_pool_stats(self) -> dict:
        """Get current pool statistics."""
        return self.pool.get_pool_stats()
    
    @classmethod
    def clear_instances(cls) -> None:
        """Clear all cached instances (useful for testing)."""
        for instance in cls._instances.values():
            try:
                instance.close_all_connections()
            except:
                pass
        cls._instances.clear()

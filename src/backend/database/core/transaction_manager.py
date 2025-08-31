#!/usr/bin/env python3
"""
Database Transaction Manager for SmartHistory

Handles database transactions and query execution
following the atomic responsibility principle.
"""

import logging
from typing import Optional, Union, Tuple, Dict, List
from contextlib import contextmanager
import sqlite3
from .connection_pool import ConnectionPool

logger = logging.getLogger(__name__)

class DatabaseOperationError(Exception):
    """Custom exception for database operation errors."""
    pass

class TransactionManager:
    """
    Database transaction and query execution manager.
    
    Responsible for:
    - Transaction context management
    - Query execution with error handling
    - Batch operations
    """
    
    def __init__(self, connection_pool: ConnectionPool):
        """Initialize transaction manager with connection pool."""
        self.pool = connection_pool
    
    @contextmanager
    def transaction(self):
        """
        Database transaction context manager with automatic rollback.
        
        Usage:
            with transaction_manager.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO ...")
                cursor.execute("UPDATE ...")
                # Auto-commits on success, auto-rollbacks on error
        """
        with self.pool.get_connection() as conn:
            try:
                conn.execute("BEGIN")
                yield conn
                conn.commit()
                logger.debug("Transaction committed successfully")
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction rolled back due to error: {e}")
                raise
    
    def execute_query(self, query: str, 
                     params: Optional[Union[Tuple, Dict]] = None) -> List[sqlite3.Row]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL SELECT query
            params: Query parameters (tuple or dict)
            
        Returns:
            List of rows as sqlite3.Row objects
            
        Raises:
            DatabaseOperationError: If query execution fails
        """
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                    
                results = cursor.fetchall()
                logger.debug(f"Query executed successfully, returned {len(results)} rows")
                return results
                
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {e}")
            raise DatabaseOperationError(f"Query failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during query: {e}")
            raise DatabaseOperationError(f"Query failed: {e}")
    
    def execute_update(self, query: str, 
                      params: Optional[Union[Tuple, Dict]] = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query
            params: Query parameters (tuple or dict)
            
        Returns:
            Number of affected rows
            
        Raises:
            DatabaseOperationError: If query execution fails
        """
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                    
                conn.commit()
                affected_rows = cursor.rowcount
                logger.debug(f"Update executed successfully, affected {affected_rows} rows")
                return affected_rows
                
        except sqlite3.Error as e:
            logger.error(f"Update execution failed: {e}")
            raise DatabaseOperationError(f"Update failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during update: {e}")
            raise DatabaseOperationError(f"Update failed: {e}")
    
    def execute_batch(self, query: str, 
                     params_list: List[Union[Tuple, Dict]]) -> int:
        """
        Execute a batch of queries with different parameters.
        
        Args:
            query: SQL query template
            params_list: List of parameter sets
            
        Returns:
            Total number of affected rows
            
        Raises:
            DatabaseOperationError: If batch execution fails
        """
        if not params_list:
            return 0
            
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()
                total_affected = 0
                
                for params in params_list:
                    cursor.execute(query, params)
                    total_affected += cursor.rowcount
                    
                logger.debug(f"Batch execution completed, total affected rows: {total_affected}")
                return total_affected
                
        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            raise DatabaseOperationError(f"Batch execution failed: {e}")
    
    def get_last_insert_id(self) -> Optional[int]:
        """
        Get the ID of the last inserted row.
        
        Returns:
            Last inserted row ID or None if no insert occurred
        """
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT last_insert_rowid()")
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            logger.error(f"Failed to get last insert ID: {e}")
            return None
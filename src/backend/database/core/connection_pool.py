#!/usr/bin/env python3
"""
Database Connection Pool Manager for SmartHistory

Handles connection pooling, thread safety, and connection lifecycle management
following the atomic responsibility principle.
"""

import sqlite3
import threading
import logging
from typing import Optional, List
from contextlib import contextmanager
from .config import ConnectionConfig

logger = logging.getLogger(__name__)

class DatabaseConnectionError(Exception):
    """Custom exception for database connection errors."""
    pass

class ConnectionPool:
    """Thread-safe connection pool manager following atomic responsibility principle.
    
    This class manages a pool of SQLite connections to improve performance by reusing
    connections instead of creating new ones for each operation. It ensures thread safety
    and handles connection lifecycle management including validation and cleanup.
    
    Attributes:
        config: Database connection configuration
        _pool: List of available database connections
        _pool_lock: Thread lock for pool access synchronization
        _created_connections: Counter for total connections created (debugging)
    """
    
    def __init__(self, config: ConnectionConfig) -> None:
        """Initialize connection pool with the provided configuration.
        
        Args:
            config: Database connection configuration containing pool size,
                   timeout, and other connection parameters.
        """
        self.config = config
        self._pool: List[sqlite3.Connection] = []
        self._pool_lock = threading.Lock()
        self._created_connections = 0
        
    def _create_connection(self) -> sqlite3.Connection:
        """Create and configure a new database connection with optimal settings.
        
        Configures the connection for performance with WAL mode, row factory for
        dict-like access, and other SQLite-specific optimizations.
        
        Returns:
            Configured SQLite connection ready for use.
            
        Raises:
            DatabaseConnectionError: If connection creation or configuration fails.
        """
        try:
            conn = sqlite3.connect(
                self.config.db_path,
                timeout=self.config.timeout,
                check_same_thread=self.config.check_same_thread,
                isolation_level=self.config.isolation_level
            )
            
            # Configure connection for optimal performance
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            
            self._created_connections += 1
            logger.debug(f"Created new connection #{self._created_connections}")
            
            return conn
            
        except sqlite3.Error as e:
            logger.error(f"Failed to create database connection: {e}")
            raise DatabaseConnectionError(f"Connection creation failed: {e}")
    
    def _validate_connection(self, conn: sqlite3.Connection) -> bool:
        """Validate that a connection is still usable by executing a simple query.
        
        This prevents returning broken connections from the pool which could cause
        application errors. Uses a lightweight SELECT 1 query for validation.
        
        Args:
            conn: Database connection to validate.
            
        Returns:
            True if connection is valid and responsive, False otherwise.
        """
        try:
            conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False
    
    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool with automatic cleanup.
        
        This context manager provides a connection from the pool, creating a new one
        if necessary. It ensures proper cleanup and returns the connection to the pool
        when done. Includes automatic rollback on exceptions and connection validation.
        
        Yields:
            sqlite3.Connection: A validated database connection ready for use.
            
        Raises:
            DatabaseConnectionError: If connection cannot be obtained or is invalid.
            
        Example:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
                results = cursor.fetchall()
        """
        conn = None
        
        try:
            # Acquire connection with pool lock to prevent race conditions
            with self._pool_lock:
                if self._pool:
                    # Try to reuse existing connection from pool
                    conn = self._pool.pop()
                    if self._validate_connection(conn):
                        logger.debug("Reused connection from pool")
                    else:
                        # Connection is stale, close it and create fresh one
                        conn.close()
                        conn = self._create_connection()
                        logger.debug("Replaced invalid connection")
                else:
                    # Pool is empty, create new connection
                    conn = self._create_connection()
                    
            yield conn
            
        except Exception as e:
            # Ensure rollback on any error
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise
            
        finally:
            # Return connection to pool or close if pool is full
            if conn:
                try:
                    if self._validate_connection(conn):
                        with self._pool_lock:
                            if len(self._pool) < self.config.max_connections:
                                self._pool.append(conn)
                                logger.debug("Returned connection to pool")
                            else:
                                conn.close()
                                logger.debug("Pool full, closed connection")
                    else:
                        conn.close()
                        logger.debug("Closed invalid connection")
                except:
                    try:
                        conn.close()
                    except:
                        pass
    
    def close_all_connections(self) -> None:
        """Close all connections in the pool."""
        with self._pool_lock:
            while self._pool:
                conn = self._pool.pop()
                try:
                    conn.close()
                except:
                    pass
            logger.info(f"Closed all connections in pool")
    
    def get_pool_stats(self) -> dict:
        """Get current pool statistics."""
        with self._pool_lock:
            return {
                'pool_size': len(self._pool),
                'max_connections': self.config.max_connections,
                'total_created': self._created_connections
            }
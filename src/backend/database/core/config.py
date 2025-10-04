#!/usr/bin/env python3
"""
Database Configuration for SmartHistory

Handles database connection configuration and validation
following the atomic responsibility principle.
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

@dataclass
class ConnectionConfig:
    """Database connection configuration with validation."""

    # Connection settings
    db_path: str = None
    timeout: float = 30.0
    check_same_thread: bool = False
    isolation_level: Optional[str] = None  # autocommit mode
    
    # Pool settings  
    max_connections: int = 10
    
    def __post_init__(self):
        """Validate configuration and ensure database directory exists."""
        if self.db_path is None:
            self._parse_database_url()
        self._validate_config()
        self._ensure_directory_exists()

    def _parse_database_url(self) -> None:
        """Parse DATABASE_URL environment variable."""
        database_url = os.getenv('DATABASE_URL', 'sqlite:///./smarthistory.db')

        if database_url.startswith('sqlite:///'):
            # Remove sqlite:/// prefix
            self.db_path = database_url[10:]
        else:
            # Fallback for other database types or malformed URLs
            self.db_path = 'smarthistory.db'
    
    def _validate_config(self) -> None:
        """Validate configuration parameters."""
        if not self.db_path:
            raise ValueError("Database path cannot be empty")
            
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
            
        if self.max_connections <= 0:
            raise ValueError("Max connections must be positive")
            
        if self.max_connections > 100:
            raise ValueError("Max connections should not exceed 100")
    
    def _ensure_directory_exists(self) -> None:
        """Ensure the database directory exists."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def get_connection_params(self) -> dict:
        """Get connection parameters as dictionary."""
        return {
            'database': self.db_path,
            'timeout': self.timeout,
            'check_same_thread': self.check_same_thread,
            'isolation_level': self.isolation_level
        }
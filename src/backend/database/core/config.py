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
    db_path: str = os.getenv('SMARTHISTORY_DB_PATH', 'smarthistory.db')
    timeout: float = 30.0
    check_same_thread: bool = False
    isolation_level: Optional[str] = None  # autocommit mode
    
    # Pool settings  
    max_connections: int = 10
    
    def __post_init__(self):
        """Validate configuration and ensure database directory exists."""
        self._validate_config()
        self._ensure_directory_exists()
    
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
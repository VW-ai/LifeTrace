#!/usr/bin/env python3
"""
Database Tests Package for SmartHistory

Provides comprehensive testing for database functionality including:
- Integration tests for CRUD operations
- Migration system testing
- Performance and index testing  
- Data validation testing
- CLI functionality testing
"""

from .test_database_integration import (
    TestDatabaseIntegration,
    TestDatabaseCLI,
    run_all_tests
)

__all__ = [
    'TestDatabaseIntegration',
    'TestDatabaseCLI', 
    'run_all_tests'
]
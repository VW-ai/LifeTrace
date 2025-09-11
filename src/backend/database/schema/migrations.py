#!/usr/bin/env python3
"""
Database Migration System for SmartHistory

Provides version control and migration capabilities for database schema changes.
Supports forward migrations with rollback capability and tracks schema versions.
"""

import os
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

# Avoid circular import by importing DatabaseManager only when needed
def get_db_manager():
    """Get the default database manager instance."""
    from ..core.database_manager import DatabaseManager
    return DatabaseManager.get_instance()

logger = logging.getLogger(__name__)

@dataclass
class Migration:
    """Database migration definition."""
    version: int
    description: str
    up_sql: str
    down_sql: Optional[str] = None
    custom_up: Optional[Callable] = None
    custom_down: Optional[Callable] = None
    
    def validate(self) -> bool:
        """Validate migration definition."""
        if self.version <= 0:
            raise ValueError("Migration version must be positive")
        if not self.description:
            raise ValueError("Migration description is required")
        if not self.up_sql and not self.custom_up:
            raise ValueError("Either up_sql or custom_up function is required")
        return True

class MigrationManager:
    """Database migration manager with version tracking."""
    
    def __init__(self, migrations_dir: Optional[str] = None):
        """Initialize migration manager."""
        self.db = get_db_manager()
        self.migrations_dir = Path(migrations_dir) if migrations_dir else Path(__file__).parent / "migrations"
        self.migrations: Dict[int, Migration] = {}
        
        # Ensure migrations directory exists
        self.migrations_dir.mkdir(exist_ok=True)
        
        # Load built-in migrations
        self._load_builtin_migrations()
        
        # Load migration files
        self._load_migration_files()
    
    def _load_builtin_migrations(self):
        """Load built-in migration definitions."""
        # Migration 2: Ensure Notion tables and columns exist
        def ensure_notion_schema(conn: sqlite3.Connection):
            cur = conn.cursor()
            # Create tables if missing
            cur.execute("""
            CREATE TABLE IF NOT EXISTS notion_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id TEXT NOT NULL UNIQUE,
                title TEXT DEFAULT '',
                url TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_edited_at DATETIME
            )
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS notion_blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_id TEXT NOT NULL UNIQUE,
                page_id TEXT NOT NULL,
                parent_block_id TEXT,
                is_leaf INTEGER DEFAULT 0,
                text TEXT DEFAULT '',
                abstract TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_edited_at DATETIME
            )
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS notion_block_edits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_id TEXT NOT NULL,
                edited_at DATETIME NOT NULL
            )
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS notion_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_id TEXT NOT NULL,
                model TEXT DEFAULT '',
                vector TEXT NOT NULL,
                dim INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(block_id, model)
            )
            """)

            # Ensure columns exist (SQLite lacks IF NOT EXISTS for columns)
            def ensure_column(table: str, column: str, ddl: str):
                cur.execute(f"PRAGMA table_info({table})")
                cols = [row[1] for row in cur.fetchall()]
                if column not in cols:
                    cur.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")

            ensure_column('notion_pages', 'last_edited_at', 'DATETIME')
            ensure_column('notion_blocks', 'last_edited_at', 'DATETIME')
            ensure_column('notion_blocks', 'abstract', 'TEXT')
            ensure_column('notion_blocks', 'is_leaf', 'INTEGER DEFAULT 0')

        self.add_migration(Migration(
            version=2,
            description="Ensure Notion tables and last_edited_at columns",
            up_sql='',
            custom_up=ensure_notion_schema
        ))
    
    def _load_migration_files(self):
        """Load migration files from the migrations directory."""
        if not self.migrations_dir.exists():
            return
            
        for file_path in sorted(self.migrations_dir.glob("*.sql")):
            try:
                version = self._extract_version_from_filename(file_path.name)
                if version:
                    self._load_migration_file(file_path, version)
            except Exception as e:
                logger.error(f"Failed to load migration file {file_path}: {e}")
    
    def _extract_version_from_filename(self, filename: str) -> Optional[int]:
        """Extract version number from migration filename."""
        # Expected format: 001_description.sql, 002_add_indexes.sql, etc.
        try:
            version_str = filename.split('_')[0]
            return int(version_str)
        except (ValueError, IndexError):
            logger.warning(f"Invalid migration filename format: {filename}")
            return None
    
    def _load_migration_file(self, file_path: Path, version: int):
        """Load a single migration file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse SQL content (simple parsing - could be enhanced)
            up_sql = content
            down_sql = None
            description = file_path.stem.replace(f"{version:03d}_", "").replace("_", " ").title()
            
            # Look for DOWN section (optional)
            if "-- DOWN" in content:
                parts = content.split("-- DOWN")
                up_sql = parts[0].strip()
                down_sql = parts[1].strip() if len(parts) > 1 else None
            
            migration = Migration(
                version=version,
                description=description,
                up_sql=up_sql,
                down_sql=down_sql
            )
            
            migration.validate()
            self.migrations[version] = migration
            
            logger.debug(f"Loaded migration {version}: {description}")
            
        except Exception as e:
            logger.error(f"Failed to parse migration file {file_path}: {e}")
            raise
    
    def add_migration(self, migration: Migration):
        """Add a migration programmatically."""
        migration.validate()
        
        if migration.version in self.migrations:
            raise ValueError(f"Migration version {migration.version} already exists")
        
        self.migrations[migration.version] = migration
        logger.info(f"Added migration {migration.version}: {migration.description}")
    
    def get_current_version(self) -> int:
        """Get the current database schema version."""
        try:
            # Check if schema_versions table exists
            if not self.db.table_exists('schema_versions'):
                return 0
            
            result = self.db.execute_query(
                "SELECT MAX(version) as version FROM schema_versions"
            )
            
            return result[0]['version'] if result and result[0]['version'] else 0
            
        except Exception as e:
            logger.error(f"Failed to get current version: {e}")
            return 0
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get migrations that need to be applied."""
        current_version = self.get_current_version()
        
        pending = []
        for version in sorted(self.migrations.keys()):
            if version > current_version:
                pending.append(self.migrations[version])
        
        return pending
    
    def migrate_up(self, target_version: Optional[int] = None) -> bool:
        """Run pending migrations up to target version."""
        current_version = self.get_current_version()
        
        if target_version is None:
            target_version = max(self.migrations.keys()) if self.migrations else current_version
        
        if target_version <= current_version:
            logger.info("No migrations needed")
            return True
        
        logger.info(f"Migrating from version {current_version} to {target_version}")
        
        # Get migrations to apply
        to_apply = []
        for version in sorted(self.migrations.keys()):
            if current_version < version <= target_version:
                to_apply.append(self.migrations[version])
        
        if not to_apply:
            logger.info("No migrations to apply")
            return True
        
        # Apply migrations in transaction
        try:
            with self.db.transaction() as conn:
                for migration in to_apply:
                    logger.info(f"Applying migration {migration.version}: {migration.description}")
                    
                    # Execute custom function or SQL
                    if migration.custom_up:
                        migration.custom_up(conn)
                    else:
                        conn.executescript(migration.up_sql)
                    
                    # Record migration in schema_versions
                    conn.execute(
                        "INSERT INTO schema_versions (version, description) VALUES (?, ?)",
                        (migration.version, migration.description)
                    )
                    
                    logger.info(f"Migration {migration.version} applied successfully")
            
            logger.info(f"Migration completed. New version: {self.get_current_version()}")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def migrate_down(self, target_version: int) -> bool:
        """Roll back migrations to target version."""
        current_version = self.get_current_version()
        
        if target_version >= current_version:
            logger.info("No rollback needed")
            return True
        
        logger.info(f"Rolling back from version {current_version} to {target_version}")
        
        # Get migrations to rollback (in reverse order)
        to_rollback = []
        for version in sorted(self.migrations.keys(), reverse=True):
            if target_version < version <= current_version:
                migration = self.migrations[version]
                if not migration.down_sql and not migration.custom_down:
                    logger.error(f"Migration {version} has no rollback defined")
                    return False
                to_rollback.append(migration)
        
        if not to_rollback:
            logger.info("No migrations to roll back")
            return True
        
        # Rollback migrations in transaction
        try:
            with self.db.transaction() as conn:
                for migration in to_rollback:
                    logger.info(f"Rolling back migration {migration.version}: {migration.description}")
                    
                    # Execute custom function or SQL
                    if migration.custom_down:
                        migration.custom_down(conn)
                    else:
                        conn.executescript(migration.down_sql)
                    
                    # Remove from schema_versions
                    conn.execute(
                        "DELETE FROM schema_versions WHERE version = ?",
                        (migration.version,)
                    )
                    
                    logger.info(f"Migration {migration.version} rolled back successfully")
            
            logger.info(f"Rollback completed. New version: {self.get_current_version()}")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get the history of applied migrations."""
        try:
            if not self.db.table_exists('schema_versions'):
                return []
            
            results = self.db.execute_query(
                "SELECT * FROM schema_versions ORDER BY version"
            )
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Failed to get migration history: {e}")
            return []
    
    def create_migration_file(self, description: str, up_sql: str, down_sql: Optional[str] = None) -> Path:
        """Create a new migration file."""
        # Get next version number
        max_version = max(self.migrations.keys()) if self.migrations else 1
        next_version = max_version + 1
        
        # Create filename
        filename = f"{next_version:03d}_{description.lower().replace(' ', '_')}.sql"
        file_path = self.migrations_dir / filename
        
        # Create file content
        content = f"-- Migration {next_version}: {description}\n"
        content += f"-- Created: {datetime.now().isoformat()}\n\n"
        content += up_sql
        
        if down_sql:
            content += "\n\n-- DOWN\n"
            content += down_sql
        
        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Created migration file: {file_path}")
        return file_path
    
    def validate_schema(self) -> bool:
        """Validate that the current database schema matches expectations."""
        try:
            # Check that all required tables exist
            required_tables = [
                'schema_versions',
                'raw_activities', 
                'processed_activities',
                'tags',
                'activity_tags',
                'user_sessions',
                'tag_generations'
            ]
            
            for table in required_tables:
                if not self.db.table_exists(table):
                    logger.error(f"Required table '{table}' is missing")
                    return False
            
            # Check schema version consistency
            current_version = self.get_current_version()
            if current_version == 0:
                logger.warning("No schema version recorded")
                return False
            
            logger.info(f"Schema validation passed. Current version: {current_version}")
            return True
            
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False

# Convenience functions
def get_migration_manager() -> MigrationManager:
    """Get the global migration manager instance."""
    return MigrationManager()

def migrate_to_latest() -> bool:
    """Migrate database to the latest version."""
    manager = get_migration_manager()
    return manager.migrate_up()

def get_current_schema_version() -> int:
    """Get the current database schema version."""
    manager = get_migration_manager()
    return manager.get_current_version()

def validate_database_schema() -> bool:
    """Validate the current database schema."""
    manager = get_migration_manager()
    return manager.validate_schema()

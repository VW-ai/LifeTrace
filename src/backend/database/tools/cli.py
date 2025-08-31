#!/usr/bin/env python3
"""
Database Management CLI for SmartHistory

Provides command-line tools for database operations including:
- Schema initialization and migration
- Data inspection and validation  
- Backup and restore operations
- Development utilities

Usage:
    python -m src.backend.database.cli --help
    python -m src.backend.database.cli migrate
    python -m src.backend.database.cli status
    python -m src.backend.database.cli validate
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add src to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.database import (
    get_db_manager, initialize_database,
    RawActivityDAO, ProcessedActivityDAO, TagDAO,
    SessionStatus
)
from ..schema.migrations import (
    get_migration_manager, migrate_to_latest,
    get_current_schema_version, validate_database_schema
)

def cmd_status(args):
    """Show database status and information."""
    print("SmartHistory Database Status")
    print("=" * 40)
    
    try:
        # Database connection
        db = get_db_manager()
        print(f"✅ Database connection: OK")
        print(f"📁 Database file: {db.config.db_path}")
        
        # Schema version
        version = get_current_schema_version()
        print(f"📊 Schema version: {version}")
        
        # Migration status
        manager = get_migration_manager()
        pending = manager.get_pending_migrations()
        if pending:
            print(f"⚠️  Pending migrations: {len(pending)}")
            for migration in pending:
                print(f"   - v{migration.version}: {migration.description}")
        else:
            print("✅ Migrations: Up to date")
        
        # Table information
        print("\n📋 Table Statistics:")
        
        # Raw activities count
        try:
            raw_count = db.execute_query("SELECT COUNT(*) as count FROM raw_activities")[0]['count']
            print(f"   Raw Activities: {raw_count:,}")
        except:
            print("   Raw Activities: Table not found")
        
        # Processed activities count
        try:
            processed_count = db.execute_query("SELECT COUNT(*) as count FROM processed_activities")[0]['count']
            print(f"   Processed Activities: {processed_count:,}")
        except:
            print("   Processed Activities: Table not found")
        
        # Tags count
        try:
            tags_count = db.execute_query("SELECT COUNT(*) as count FROM tags")[0]['count']
            print(f"   Tags: {tags_count:,}")
        except:
            print("   Tags: Table not found")
        
        # Recent session info
        try:
            recent_session = db.execute_query(
                "SELECT * FROM user_sessions ORDER BY start_time DESC LIMIT 1"
            )
            if recent_session:
                session = recent_session[0]
                print(f"\n🕐 Last Session:")
                print(f"   Type: {session['session_type']}")
                print(f"   Status: {session['status']}")
                print(f"   Time: {session['start_time']}")
        except:
            print("\n🕐 Last Session: No data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def cmd_migrate(args):
    """Run database migrations."""
    print("SmartHistory Database Migration")
    print("=" * 40)
    
    try:
        manager = get_migration_manager()
        
        if args.version:
            # Migrate to specific version
            current = manager.get_current_version()
            target = int(args.version)
            
            if target > current:
                print(f"Migrating from v{current} to v{target}")
                success = manager.migrate_up(target)
            elif target < current:
                print(f"Rolling back from v{current} to v{target}")
                success = manager.migrate_down(target)
            else:
                print(f"Already at version {target}")
                return True
        else:
            # Migrate to latest
            current = manager.get_current_version()
            pending = manager.get_pending_migrations()
            
            if not pending:
                print(f"Database is up to date (v{current})")
                return True
            
            print(f"Found {len(pending)} pending migrations:")
            for migration in pending:
                print(f"  - v{migration.version}: {migration.description}")
            
            if not args.force:
                confirm = input("\nProceed with migration? (y/N): ").strip().lower()
                if confirm != 'y':
                    print("Migration cancelled")
                    return False
            
            success = migrate_to_latest()
        
        if success:
            new_version = manager.get_current_version()
            print(f"✅ Migration completed successfully (v{new_version})")
        else:
            print("❌ Migration failed")
            return False
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False
    
    return True

def cmd_validate(args):
    """Validate database schema and data integrity."""
    print("SmartHistory Database Validation")
    print("=" * 40)
    
    try:
        # Schema validation
        print("🔍 Validating schema...")
        if validate_database_schema():
            print("✅ Schema validation passed")
        else:
            print("❌ Schema validation failed")
            return False
        
        # Data integrity checks
        print("\n🔍 Checking data integrity...")
        
        db = get_db_manager()
        issues = []
        
        # Check for orphaned activity_tags
        orphaned_activity_tags = db.execute_query("""
            SELECT COUNT(*) as count FROM activity_tags at
            LEFT JOIN processed_activities pa ON at.processed_activity_id = pa.id
            WHERE pa.id IS NULL
        """)[0]['count']
        
        if orphaned_activity_tags > 0:
            issues.append(f"Found {orphaned_activity_tags} orphaned activity-tag relationships")
        
        # Check for orphaned processed activities references
        orphaned_refs = db.execute_query("""
            SELECT pa.id, pa.raw_activity_ids FROM processed_activities pa
        """)
        
        orphaned_count = 0
        for row in orphaned_refs:
            try:
                raw_ids = json.loads(row['raw_activity_ids'])
                for raw_id in raw_ids:
                    exists = db.execute_query(
                        "SELECT 1 FROM raw_activities WHERE id = ?", (raw_id,)
                    )
                    if not exists:
                        orphaned_count += 1
            except:
                pass
        
        if orphaned_count > 0:
            issues.append(f"Found {orphaned_count} references to non-existent raw activities")
        
        # Check tag usage counts
        incorrect_usage = db.execute_query("""
            SELECT t.id, t.name, t.usage_count, 
                   COUNT(at.tag_id) as actual_count
            FROM tags t
            LEFT JOIN activity_tags at ON t.id = at.tag_id
            GROUP BY t.id, t.name, t.usage_count
            HAVING t.usage_count != COUNT(at.tag_id)
        """)
        
        if incorrect_usage:
            issues.append(f"Found {len(incorrect_usage)} tags with incorrect usage counts")
        
        if issues:
            print("⚠️  Data integrity issues found:")
            for issue in issues:
                print(f"   - {issue}")
            
            if args.fix:
                print("\n🔧 Attempting to fix issues...")
                # Fix tag usage counts
                db.execute_update("""
                    UPDATE tags SET usage_count = (
                        SELECT COUNT(*) FROM activity_tags 
                        WHERE tag_id = tags.id
                    )
                """)
                print("✅ Fixed tag usage counts")
        else:
            print("✅ Data integrity checks passed")
            
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False
    
    return True

def cmd_backup(args):
    """Create database backup."""
    print("SmartHistory Database Backup")
    print("=" * 40)
    
    try:
        db = get_db_manager()
        backup_path = args.output or f"smarthistory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        # Simple SQLite backup using .backup command
        with db.get_connection() as conn:
            backup_conn = sqlite3.connect(backup_path)
            conn.backup(backup_conn)
            backup_conn.close()
        
        print(f"✅ Backup created: {backup_path}")
        
    except Exception as e:
        print(f"❌ Backup error: {e}")
        return False
    
    return True

def cmd_info(args):
    """Show detailed database information."""
    print("SmartHistory Database Information")
    print("=" * 40)
    
    try:
        db = get_db_manager()
        
        # Schema information
        tables = ['raw_activities', 'processed_activities', 'tags', 'activity_tags', 'user_sessions']
        
        for table in tables:
            if db.table_exists(table):
                print(f"\n📊 Table: {table}")
                
                # Get column info
                columns = db.get_table_info(table)
                print("   Columns:")
                for col in columns:
                    print(f"     - {col['name']} ({col['type']})")
                
                # Get row count
                count = db.execute_query(f"SELECT COUNT(*) as count FROM {table}")[0]['count']
                print(f"   Rows: {count:,}")
        
        # Migration history
        print(f"\n📝 Migration History:")
        manager = get_migration_manager()
        history = manager.get_migration_history()
        
        if history:
            for record in history:
                print(f"   v{record['version']}: {record['description']} ({record['applied_at']})")
        else:
            print("   No migration history found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SmartHistory Database Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show database status')
    
    # Migration command
    migrate_parser = subparsers.add_parser('migrate', help='Run database migrations')
    migrate_parser.add_argument('--version', help='Target version (default: latest)')
    migrate_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    
    # Validation command
    validate_parser = subparsers.add_parser('validate', help='Validate database')
    validate_parser.add_argument('--fix', action='store_true', help='Attempt to fix issues')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create database backup')
    backup_parser.add_argument('--output', help='Backup file path')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show detailed database information')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Command dispatch
    commands = {
        'status': cmd_status,
        'migrate': cmd_migrate,
        'validate': cmd_validate,
        'backup': cmd_backup,
        'info': cmd_info
    }
    
    try:
        success = commands[args.command](args)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏸️  Operation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
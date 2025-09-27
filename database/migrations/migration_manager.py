"""
Database Migration Manager for PostgreSQL
Handles schema migrations, version tracking, and rollbacks
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import Config

logger = logging.getLogger(__name__)

class MigrationManager:
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or Config.POSTGRESQL_CONNECTION_URI
        self.migrations_dir = os.path.join(os.path.dirname(__file__), 'versions')
        self.schema_version_table = 'schema_migrations'
        
        # Ensure migrations directory exists
        os.makedirs(self.migrations_dir, exist_ok=True)
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(self.connection_string)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def create_migrations_table(self):
        """Create the schema_migrations table if it doesn't exist"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.schema_version_table} (
                        id SERIAL PRIMARY KEY,
                        version VARCHAR(50) UNIQUE NOT NULL,
                        description TEXT,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        checksum VARCHAR(64)
                    )
                """)
                logger.info("Migrations table created/verified")
        finally:
            conn.close()
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    SELECT version FROM {self.schema_version_table} 
                    ORDER BY applied_at
                """)
                return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_pending_migrations(self) -> List[Dict]:
        """Get list of pending migrations"""
        applied = set(self.get_applied_migrations())
        pending = []
        
        for filename in sorted(os.listdir(self.migrations_dir)):
            if filename.endswith('.sql') and not filename.endswith('_rollback.sql'):
                version = filename.replace('.sql', '')
                if version not in applied:
                    pending.append({
                        'version': version,
                        'filename': filename,
                        'path': os.path.join(self.migrations_dir, filename)
                    })
        
        return pending
    
    def apply_migration(self, migration: Dict) -> bool:
        """Apply a single migration"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # Read migration file
                with open(migration['path'], 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                # Calculate checksum
                import hashlib
                checksum = hashlib.sha256(sql_content.encode()).hexdigest()
                
                # Execute migration
                cursor.execute(sql_content)
                
                # Record migration
                cursor.execute(f"""
                    INSERT INTO {self.schema_version_table} (version, description, checksum)
                    VALUES (%s, %s, %s)
                """, (
                    migration['version'],
                    migration.get('description', ''),
                    checksum
                ))
                
                logger.info(f"Applied migration: {migration['version']}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to apply migration {migration['version']}: {e}")
            return False
        finally:
            conn.close()
    
    def rollback_migration(self, version: str) -> bool:
        """Rollback a specific migration"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                # Check if migration exists
                cursor.execute(f"""
                    SELECT version FROM {self.schema_version_table} 
                    WHERE version = %s
                """, (version,))
                
                if not cursor.fetchone():
                    logger.error(f"Migration {version} not found in applied migrations")
                    return False
                
                # Look for rollback file
                rollback_file = os.path.join(self.migrations_dir, f"{version}_rollback.sql")
                if not os.path.exists(rollback_file):
                    logger.error(f"Rollback file not found: {rollback_file}")
                    return False
                
                # Execute rollback
                with open(rollback_file, 'r', encoding='utf-8') as f:
                    rollback_sql = f.read()
                
                cursor.execute(rollback_sql)
                
                # Remove migration record
                cursor.execute(f"""
                    DELETE FROM {self.schema_version_table} 
                    WHERE version = %s
                """, (version,))
                
                logger.info(f"Rolled back migration: {version}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to rollback migration {version}: {e}")
            return False
        finally:
            conn.close()
    
    def migrate(self) -> bool:
        """Run all pending migrations"""
        try:
            # Ensure migrations table exists
            self.create_migrations_table()
            
            # Get pending migrations
            pending = self.get_pending_migrations()
            
            if not pending:
                logger.info("No pending migrations")
                return True
            
            logger.info(f"Found {len(pending)} pending migrations")
            
            # Apply each migration
            for migration in pending:
                if not self.apply_migration(migration):
                    logger.error(f"Migration failed: {migration['version']}")
                    return False
            
            logger.info("All migrations applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def status(self) -> Dict:
        """Get migration status"""
        try:
            self.create_migrations_table()
            applied = self.get_applied_migrations()
            pending = self.get_pending_migrations()
            
            return {
                'applied_count': len(applied),
                'pending_count': len(pending),
                'applied_migrations': applied,
                'pending_migrations': [m['version'] for m in pending]
            }
        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return {'error': str(e)}
    
    def create_migration(self, name: str, description: str = "") -> str:
        """Create a new migration file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = f"{timestamp}_{name}"
        
        # Create migration file
        migration_file = os.path.join(self.migrations_dir, f"{version}.sql")
        with open(migration_file, 'w', encoding='utf-8') as f:
            f.write(f"-- Migration: {version}\n")
            f.write(f"-- Description: {description}\n")
            f.write(f"-- Created: {datetime.now().isoformat()}\n\n")
            f.write("-- Add your SQL statements here\n")
        
        # Create rollback file
        rollback_file = os.path.join(self.migrations_dir, f"{version}_rollback.sql")
        with open(rollback_file, 'w', encoding='utf-8') as f:
            f.write(f"-- Rollback for migration: {version}\n")
            f.write(f"-- Description: {description}\n")
            f.write(f"-- Created: {datetime.now().isoformat()}\n\n")
            f.write("-- Add your rollback SQL statements here\n")
        
        logger.info(f"Created migration: {version}")
        return version

def main():
    """CLI for migration management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Migration Manager')
    parser.add_argument('command', choices=['migrate', 'status', 'create', 'rollback'])
    parser.add_argument('--name', help='Migration name (for create command)')
    parser.add_argument('--description', help='Migration description (for create command)')
    parser.add_argument('--version', help='Migration version (for rollback command)')
    
    args = parser.parse_args()
    
    manager = MigrationManager()
    
    if args.command == 'migrate':
        success = manager.migrate()
        sys.exit(0 if success else 1)
    
    elif args.command == 'status':
        status = manager.status()
        print(f"Applied migrations: {status.get('applied_count', 0)}")
        print(f"Pending migrations: {status.get('pending_count', 0)}")
        if status.get('applied_migrations'):
            print("Applied:", ', '.join(status['applied_migrations']))
        if status.get('pending_migrations'):
            print("Pending:", ', '.join(status['pending_migrations']))
    
    elif args.command == 'create':
        if not args.name:
            print("Error: --name is required for create command")
            sys.exit(1)
        version = manager.create_migration(args.name, args.description or "")
        print(f"Created migration: {version}")
    
    elif args.command == 'rollback':
        if not args.version:
            print("Error: --version is required for rollback command")
            sys.exit(1)
        success = manager.rollback_migration(args.version)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

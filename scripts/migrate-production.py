#!/usr/bin/env python3
"""
Production Database Migration Script
Includes safety checks and backup procedures
"""

import sys
import os
import logging
import subprocess
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.migrations.migration_manager import MigrationManager
from config import Config

def setup_logging():
    """Setup production logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('migration.log'),
            logging.StreamHandler()
        ]
    )

def create_backup():
    """Create database backup before migration"""
    logger = logging.getLogger(__name__)
    
    try:
        # Extract connection details from URI
        # Format: postgresql://user:password@host:port/database
        uri = Config.POSTGRESQL_CONNECTION_URI
        if not uri:
            raise ValueError("POSTGRESQL_CONNECTION_URI not configured")
        
        # Parse URI (simple parsing - in production, use proper URI parsing)
        parts = uri.replace('postgresql://', '').split('@')
        if len(parts) != 2:
            raise ValueError("Invalid connection URI format")
        
        auth_part = parts[0]
        host_part = parts[1]
        
        user, password = auth_part.split(':')
        host_port, database = host_part.split('/')
        host, port = host_port.split(':')
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_{database}_{timestamp}.sql"
        
        # Set PGPASSWORD environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        # Create backup using pg_dump
        cmd = [
            'pg_dump',
            '-h', host,
            '-p', port,
            '-U', user,
            '-d', database,
            '-f', backup_file,
            '--verbose',
            '--no-password'
        ]
        
        logger.info(f"Creating database backup: {backup_file}")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Backup failed: {result.stderr}")
        
        logger.info(f"✅ Backup created successfully: {backup_file}")
        return backup_file
        
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        raise

def verify_connection():
    """Verify database connection before migration"""
    logger = logging.getLogger(__name__)
    
    try:
        manager = MigrationManager()
        conn = manager.get_connection()
        conn.close()
        logger.info("✅ Database connection verified")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def run_migration():
    """Run database migration with safety checks"""
    logger = logging.getLogger(__name__)
    
    try:
        # Verify connection
        if not verify_connection():
            return False
        
        # Create backup
        backup_file = create_backup()
        
        # Run migration
        logger.info("Starting database migration...")
        manager = MigrationManager()
        
        # Check current status
        status = manager.status()
        logger.info(f"Current status: {status['applied_count']} applied, {status['pending_count']} pending")
        
        if status['pending_count'] == 0:
            logger.info("No pending migrations")
            return True
        
        # Run migrations
        success = manager.migrate()
        
        if success:
            logger.info("✅ Migration completed successfully")
            
            # Verify migration
            new_status = manager.status()
            logger.info(f"New status: {new_status['applied_count']} applied, {new_status['pending_count']} pending")
            
            return True
        else:
            logger.error("❌ Migration failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration error: {e}")
        return False

def main():
    """Main production migration function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting production database migration")
    logger.info(f"Environment: {Config.ENVIRONMENT}")
    logger.info(f"Database: {Config.POSTGRESQL_DATABASE_NAME}")
    
    try:
        success = run_migration()
        if success:
            logger.info("🎉 Production migration completed successfully")
            sys.exit(0)
        else:
            logger.error("💥 Production migration failed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

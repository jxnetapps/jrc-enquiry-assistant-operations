#!/usr/bin/env python3
"""
Database Migration CLI Script
Usage: python scripts/migrate.py [command] [options]
"""

import sys
import os
import argparse
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.migrations.migration_manager import MigrationManager
from config import Config

def setup_logging(verbose=False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    parser = argparse.ArgumentParser(
        description='Database Migration Manager for Web ChatBot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/migrate.py migrate                    # Run all pending migrations
  python scripts/migrate.py status                    # Show migration status
  python scripts/migrate.py create --name add_indexes  # Create new migration
  python scripts/migrate.py rollback --version 20241227_000001_initial_schema
        """
    )
    
    parser.add_argument('command', 
                       choices=['migrate', 'status', 'create', 'rollback'],
                       help='Migration command to execute')
    
    parser.add_argument('--name', 
                       help='Migration name (for create command)')
    
    parser.add_argument('--description', 
                       help='Migration description (for create command)')
    
    parser.add_argument('--version', 
                       help='Migration version (for rollback command)')
    
    parser.add_argument('--connection-string', 
                       help='PostgreSQL connection string (overrides config)')
    
    parser.add_argument('--verbose', '-v', 
                       action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize migration manager
        connection_string = args.connection_string or Config.POSTGRESQL_CONNECTION_URI
        manager = MigrationManager(connection_string)
        
        if args.command == 'migrate':
            logger.info("Starting database migration...")
            success = manager.migrate()
            if success:
                logger.info("Migration completed successfully")
                sys.exit(0)
            else:
                logger.error("Migration failed")
                sys.exit(1)
        
        elif args.command == 'status':
            status = manager.status()
            if 'error' in status:
                logger.error(f"Failed to get status: {status['error']}")
                sys.exit(1)
            
            print("\nMigration Status")
            print("=" * 50)
            print(f"Applied migrations: {status['applied_count']}")
            print(f"Pending migrations: {status['pending_count']}")
            
            if status['applied_migrations']:
                print(f"\nApplied migrations:")
                for migration in status['applied_migrations']:
                    print(f"  - {migration}")
            
            if status['pending_migrations']:
                print(f"\nPending migrations:")
                for migration in status['pending_migrations']:
                    print(f"  - {migration}")
            
            if not status['applied_migrations'] and not status['pending_migrations']:
                print("\nNo migrations found")
        
        elif args.command == 'create':
            if not args.name:
                logger.error("--name is required for create command")
                sys.exit(1)
            
            logger.info(f"Creating migration: {args.name}")
            version = manager.create_migration(
                args.name, 
                args.description or ""
            )
            print(f"Created migration: {version}")
            print(f"Migration file: database/migrations/versions/{version}.sql")
            print(f"Rollback file: database/migrations/versions/{version}_rollback.sql")
        
        elif args.command == 'rollback':
            if not args.version:
                logger.error("--version is required for rollback command")
                sys.exit(1)
            
            logger.info(f"Rolling back migration: {args.version}")
            success = manager.rollback_migration(args.version)
            if success:
                logger.info(f"Successfully rolled back migration: {args.version}")
                sys.exit(0)
            else:
                logger.error(f"Failed to rollback migration: {args.version}")
                sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

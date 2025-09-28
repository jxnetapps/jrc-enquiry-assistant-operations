#!/usr/bin/env python3
"""
Unified user management script for PostgreSQL and SQLite.
Replaces multiple redundant user migration scripts.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.user_repository import user_repository
from database.sqlite_user_repository import sqlite_user_repository
from models.user_models import UserCreate, UserRole, UserStatus
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default users for both PostgreSQL and SQLite
DEFAULT_USERS = [
    {
        "username": "admin",
        "email": "admin@webchatbot.com",
        "password": "Wildcat@007",
        "full_name": "System Administrator",
        "role": UserRole.ADMIN,
        "status": UserStatus.ACTIVE
    },
    {
        "username": "edifyho",
        "email": "edifyho@webchatbot.com",
        "password": "Wildcat@007",
        "full_name": "Edify HO User",
        "role": UserRole.USER,
        "status": UserStatus.ACTIVE
    },
    {
        "username": "testuser",
        "email": "test@webchatbot.com",
        "password": "test123",
        "full_name": "Test User",
        "role": UserRole.USER,
        "status": UserStatus.ACTIVE
    }
]

async def setup_postgresql_users():
    """Setup users in PostgreSQL database"""
    try:
        print("Setting up PostgreSQL users...")
        print("-" * 40)
        
        created_count = 0
        for user_data in DEFAULT_USERS:
            try:
                # Check if user already exists
                existing_user = await user_repository.get_user_by_username(user_data["username"])
                if existing_user:
                    print(f"  User '{user_data['username']}' already exists (skipping)")
                    continue
                
                # Create user
                user_create = UserCreate(**user_data)
                user_id = await user_repository.create_user(user_create)
                print(f"  Created user: {user_data['username']} (ID: {user_id})")
                created_count += 1
                
            except Exception as e:
                print(f"  Error creating user '{user_data['username']}': {e}")
        
        print(f"PostgreSQL setup complete: {created_count} users created")
        return True
        
    except Exception as e:
        print(f"Error setting up PostgreSQL users: {e}")
        return False

def setup_sqlite_users():
    """Setup users in SQLite database"""
    try:
        print("Setting up SQLite users...")
        print("-" * 40)
        
        # SQLite users are automatically created when the repository is initialized
        # Let's verify they exist
        user_count = sqlite_user_repository.get_user_count()
        print(f"SQLite users available: {user_count}")
        
        # List existing users
        users = sqlite_user_repository.get_all_users()
        for user in users:
            print(f"  User: {user.username} ({user.role}) - {user.email}")
        
        print("SQLite setup complete")
        return True
        
    except Exception as e:
        print(f"Error setting up SQLite users: {e}")
        return False

async def list_postgresql_users():
    """List all PostgreSQL users"""
    try:
        print("PostgreSQL Users:")
        print("-" * 40)
        
        users = await user_repository.get_all_users()
        for user in users:
            print(f"  {user.username} ({user.role}) - {user.email}")
            print(f"    ID: {user.user_id}")
            print(f"    Status: {user.status}")
            print(f"    Created: {user.created_at}")
            print()
        
        print(f"Total: {len(users)} users")
        return True
        
    except Exception as e:
        print(f"Error listing PostgreSQL users: {e}")
        return False

def list_sqlite_users():
    """List all SQLite users"""
    try:
        print("SQLite Users:")
        print("-" * 40)
        
        users = sqlite_user_repository.get_all_users()
        for user in users:
            print(f"  {user.username} ({user.role}) - {user.email}")
            print(f"    ID: {user.user_id}")
            print(f"    Status: {user.status}")
            print(f"    Created: {user.created_at}")
            print()
        
        print(f"Total: {len(users)} users")
        return True
        
    except Exception as e:
        print(f"Error listing SQLite users: {e}")
        return False

async def test_authentication():
    """Test authentication for both databases"""
    try:
        print("Testing Authentication:")
        print("-" * 40)
        
        # Test PostgreSQL authentication
        print("PostgreSQL Authentication:")
        try:
            admin_user = await user_repository.authenticate_user("admin", "Wildcat@007")
            if admin_user:
                print(f"  ✓ Admin login successful: {admin_user.username}")
            else:
                print("  ✗ Admin login failed")
        except Exception as e:
            print(f"  ✗ PostgreSQL authentication error: {e}")
        
        # Test SQLite authentication
        print("SQLite Authentication:")
        try:
            admin_user = sqlite_user_repository.authenticate_user("admin", "admin123")
            if admin_user:
                print(f"  ✓ Admin login successful: {admin_user.username}")
            else:
                print("  ✗ Admin login failed")
        except Exception as e:
            print(f"  ✗ SQLite authentication error: {e}")
        
        return True
        
    except Exception as e:
        print(f"Error testing authentication: {e}")
        return False

async def migrate_users_to_postgresql():
    """Migrate users from SQLite to PostgreSQL"""
    try:
        print("Migrating users from SQLite to PostgreSQL...")
        print("-" * 50)
        
        # Get SQLite users
        sqlite_users = sqlite_user_repository.get_all_users()
        migrated_count = 0
        
        for user in sqlite_users:
            try:
                # Check if user already exists in PostgreSQL
                existing_user = await user_repository.get_user_by_username(user.username)
                if existing_user:
                    print(f"  User '{user.username}' already exists in PostgreSQL (skipping)")
                    continue
                
                # Create user in PostgreSQL
                user_create = UserCreate(
                    username=user.username,
                    email=user.email,
                    password="migrated_user_password",  # User will need to reset password
                    full_name=user.full_name,
                    role=user.role,
                    status=user.status
                )
                
                user_id = await user_repository.create_user(user_create)
                print(f"  Migrated user: {user.username} (ID: {user_id})")
                migrated_count += 1
                
            except Exception as e:
                print(f"  Error migrating user '{user.username}': {e}")
        
        print(f"Migration complete: {migrated_count} users migrated")
        return True
        
    except Exception as e:
        print(f"Error migrating users: {e}")
        return False

def show_help():
    """Show help information"""
    print("User Management Script")
    print("=" * 50)
    print("Usage: python scripts/manage_users.py [command]")
    print()
    print("Commands:")
    print("  setup-postgresql    - Setup users in PostgreSQL")
    print("  setup-sqlite        - Setup users in SQLite")
    print("  setup-all           - Setup users in both databases")
    print("  list-postgresql     - List PostgreSQL users")
    print("  list-sqlite         - List SQLite users")
    print("  list-all            - List users in both databases")
    print("  test-auth           - Test authentication")
    print("  migrate             - Migrate users from SQLite to PostgreSQL")
    print("  help                - Show this help")
    print()
    print("Examples:")
    print("  python scripts/manage_users.py setup-all")
    print("  python scripts/manage_users.py list-all")
    print("  python scripts/manage_users.py test-auth")

async def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "setup-postgresql":
        await setup_postgresql_users()
    elif command == "setup-sqlite":
        setup_sqlite_users()
    elif command == "setup-all":
        await setup_postgresql_users()
        setup_sqlite_users()
    elif command == "list-postgresql":
        await list_postgresql_users()
    elif command == "list-sqlite":
        list_sqlite_users()
    elif command == "list-all":
        await list_postgresql_users()
        list_sqlite_users()
    elif command == "test-auth":
        await test_authentication()
    elif command == "migrate":
        await migrate_users_to_postgresql()
    elif command == "help":
        show_help()
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    asyncio.run(main())

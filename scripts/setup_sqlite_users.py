#!/usr/bin/env python3
"""
Setup SQLite users database with default users.
This script creates the users table and adds default admin and test users.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.sqlite_user_repository import SQLiteUserRepository
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_sqlite_users():
    """Setup SQLite users database with default users"""
    try:
        print("Setting up SQLite users database...")
        print("=" * 50)
        
        # Initialize SQLite user repository (this creates the table and adds default users)
        user_repo = SQLiteUserRepository()
        
        # Verify the setup
        user_count = user_repo.get_user_count()
        print(f"SQLite users database initialized successfully!")
        print(f"Total users in database: {user_count}")
        
        # List the default users
        print("\nDefault users created:")
        print("-" * 30)
        
        users = user_repo.get_all_users()
        for user in users:
            print(f"  Username: {user.username}")
            print(f"    Email: {user.email}")
            print(f"    Role: {user.role}")
            print(f"    Status: {user.status}")
            print()
        
        print("Default login credentials:")
        print("-" * 30)
        print("  Admin User:")
        print("    Username: admin")
        print("    Password: admin123")
        print("    Role: admin")
        print()
        print("  Test User:")
        print("    Username: testuser")
        print("    Password: test123")
        print("    Role: user")
        print()
        
        print("SQLite users setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error setting up SQLite users: {e}")
        return False

def test_authentication():
    """Test authentication with default users"""
    try:
        print("\nTesting authentication...")
        print("-" * 30)
        
        user_repo = SQLiteUserRepository()
        
        # Test admin authentication
        admin_user = user_repo.authenticate_user("admin", "admin123")
        if admin_user:
            print(f"Admin authentication successful: {admin_user.username} ({admin_user.role})")
        else:
            print("Admin authentication failed")
        
        # Test user authentication
        test_user = user_repo.authenticate_user("testuser", "test123")
        if test_user:
            print(f"Test user authentication successful: {test_user.username} ({test_user.role})")
        else:
            print("Test user authentication failed")
        
        # Test invalid credentials
        invalid_user = user_repo.authenticate_user("admin", "wrongpassword")
        if not invalid_user:
            print("Invalid credentials correctly rejected")
        else:
            print("Invalid credentials incorrectly accepted")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing authentication: {e}")
        return False

if __name__ == "__main__":
    print("SQLite Users Setup Script")
    print("=" * 50)
    
    # Setup users
    if setup_sqlite_users():
        # Test authentication
        test_authentication()
        print("\nAll tasks completed successfully!")
    else:
        print("\nSetup failed!")
        sys.exit(1)

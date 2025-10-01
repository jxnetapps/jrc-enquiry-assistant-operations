#!/usr/bin/env python3
"""
Test SQLite Mode Script
This script tests if the application is properly configured for SQLite mode
"""

import os
import sys
import sqlite3
from pathlib import Path

def test_environment():
    """Test environment variables"""
    print("Testing environment configuration...")
    
    # Check if SQLite mode is forced
    answer_storage_type = os.getenv('ANSWER_STORAGE_TYPE', 'auto')
    if answer_storage_type == 'sqlite':
        print("+ ANSWER_STORAGE_TYPE is set to sqlite")
    else:
        print(f"- ANSWER_STORAGE_TYPE is '{answer_storage_type}' (should be 'sqlite')")
        return False
    
    # Check if PostgreSQL is disabled
    postgres_uri = os.getenv('POSTGRESQL_CONNECTION_URI', '')
    if 'invalid' in postgres_uri:
        print("+ PostgreSQL connection is disabled (invalid URI)")
    else:
        print("- PostgreSQL connection may still be active")
    
    return True

def test_sqlite_databases():
    """Test SQLite database connections"""
    print("\nTesting SQLite databases...")
    
    databases = {
        "users": "database/users.db",
        "chat_inquiries": "database/chat_inquiries.db",
        "collected_answers": "database/collected_answers.db"
    }
    
    results = {}
    
    for name, path in databases.items():
        try:
            # Create database directory if it doesn't exist
            Path(path).parent.mkdir(exist_ok=True)
            
            # Test connection
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            
            print(f"+ {name} database: OK")
            results[name] = True
        except Exception as e:
            print(f"- {name} database: FAILED - {e}")
            results[name] = False
    
    return all(results.values())

def test_application_import():
    """Test if application can be imported in SQLite mode"""
    print("\nTesting application import...")
    
    try:
        # Set environment before importing
        os.environ['ANSWER_STORAGE_TYPE'] = 'sqlite'
        os.environ['POSTGRESQL_CONNECTION_URI'] = 'postgresql://invalid:invalid@localhost:5432/invalid'
        
        # Import the application
        from web_app import app
        print("+ Application imported successfully")
        
        # Test configuration
        from config import Config
        print(f"+ Config loaded - ANSWER_STORAGE_TYPE: {Config.ANSWER_STORAGE_TYPE}")
        
        return True
    except Exception as e:
        print(f"- Application import failed: {e}")
        return False

def test_database_repositories():
    """Test database repositories in SQLite mode"""
    print("\nTesting database repositories...")
    
    try:
        # Test SQLite repositories directly
        from database.sqlite_user_repository import SQLiteUserRepository
        from database.sqlite_inquiry_repository import SQLiteInquiryRepository
        
        # Test user repository
        user_repo = SQLiteUserRepository()
        print("+ SQLiteUserRepository: OK")
        
        # Test inquiry repository
        inquiry_repo = SQLiteInquiryRepository()
        print("+ SQLiteInquiryRepository: OK")
        
        return True
    except Exception as e:
        print(f"- Database repositories test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== SQLite Mode Test ===")
    print()
    
    tests = [
        ("Environment Configuration", test_environment),
        ("SQLite Databases", test_sqlite_databases),
        ("Application Import", test_application_import),
        ("Database Repositories", test_database_repositories)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n=== Test Results ===")
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! SQLite mode is working correctly.")
        print("\nYou can now start the application with:")
        print("  python web_app.py")
    else:
        print("\n✗ Some tests failed. Please check the configuration.")
        print("\nTo force SQLite mode, run:")
        print("  python scripts/force-sqlite.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

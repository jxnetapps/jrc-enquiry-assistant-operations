#!/usr/bin/env python3
"""
Force SQLite Mode Script
This script configures the application to use SQLite instead of PostgreSQL
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with SQLite configuration"""
    env_content = """# SQLite Configuration
ANSWER_STORAGE_TYPE=sqlite

# Disable PostgreSQL (set invalid connection to force fallback)
POSTGRESQL_CONNECTION_URI=postgresql://invalid:invalid@localhost:5432/invalid
POSTGRESQL_DATABASE_NAME=invalid

# Required settings
JWT_SECRET_KEY=your-secret-key-here-change-in-production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Environment
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Vector Database (local SQLite)
VECTOR_DATABASE_TYPE=local
CHAT_BEHAVIOR=knowledge_base

# Optional: OpenAI API Key (if you have one)
# OPENAI_API_KEY=your-openai-key-here
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("+ .env file created with SQLite configuration")

def set_environment_variables():
    """Set environment variables for current session"""
    os.environ['ANSWER_STORAGE_TYPE'] = 'sqlite'
    os.environ['POSTGRESQL_CONNECTION_URI'] = 'postgresql://invalid:invalid@localhost:5432/invalid'
    os.environ['POSTGRESQL_DATABASE_NAME'] = 'invalid'
    
    if not os.environ.get('JWT_SECRET_KEY'):
        os.environ['JWT_SECRET_KEY'] = 'your-secret-key-here-change-in-production'
    
    if not os.environ.get('ADMIN_USERNAME'):
        os.environ['ADMIN_USERNAME'] = 'admin'
    
    if not os.environ.get('ADMIN_PASSWORD'):
        os.environ['ADMIN_PASSWORD'] = 'admin123'
    
    print("+ Environment variables set for SQLite mode")

def check_sqlite_databases():
    """Check if SQLite databases exist"""
    databases = [
        "database/users.db",
        "database/chat_inquiries.db", 
        "database/collected_answers.db"
    ]
    
    print("\nChecking SQLite databases...")
    for db in databases:
        if Path(db).exists():
            print(f"+ {db} exists")
        else:
            print(f"- {db} missing (will be created on first run)")

def test_sqlite_connection():
    """Test SQLite connection"""
    try:
        import sqlite3
        from pathlib import Path
        
        # Create database directory if it doesn't exist
        Path("database").mkdir(exist_ok=True)
        
        # Test connection to users database
        conn = sqlite3.connect("database/users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        
        print("+ SQLite connection test successful")
        return True
    except Exception as e:
        print(f"- SQLite connection test failed: {e}")
        return False

def main():
    """Main function"""
    print("=== Forcing SQLite Mode ===")
    print()
    
    # Create .env file
    print("Creating .env file...")
    create_env_file()
    
    # Set environment variables
    print("Setting environment variables...")
    set_environment_variables()
    
    # Check databases
    check_sqlite_databases()
    
    # Test SQLite connection
    print("\nTesting SQLite connection...")
    if test_sqlite_connection():
        print("\n=== SQLite Mode Configuration Complete ===")
        print()
        print("The application is now configured to use SQLite only.")
        print()
        print("To start the application:")
        print("  python web_app.py")
        print()
        print("Or use the startup script:")
        print("  python start-app.py")
        print()
        print("The application will:")
        print("  - Skip PostgreSQL connection attempts")
        print("  - Use SQLite databases in the database/ folder")
        print("  - Create missing databases automatically")
        print()
        print("Note: This configuration is saved in .env file for persistence.")
    else:
        print("\n=== Configuration Complete with Warnings ===")
        print("SQLite mode is configured, but there may be connection issues.")
        print("The application will attempt to create databases on first run.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Simple test script to check application startup
"""

import sys
import os
import traceback

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import fastapi
        print("+ FastAPI imported successfully")
    except ImportError as e:
        print(f"- FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("+ Uvicorn imported successfully")
    except ImportError as e:
        print(f"- Uvicorn import failed: {e}")
        return False
    
    try:
        from web_app import app
        print("+ Web app imported successfully")
    except Exception as e:
        print(f"- Web app import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config import Config
        print("+ Config loaded successfully")
        print(f"  - Environment: {Config.ENVIRONMENT}")
        print(f"  - Host: {Config.HOST}")
        print(f"  - Port: {Config.PORT}")
        print(f"  - Debug: {Config.DEBUG}")
        return True
    except Exception as e:
        print(f"- Config loading failed: {e}")
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        from database.postgresql_connection import postgresql_connection
        print("+ PostgreSQL connection module imported")
        return True
    except Exception as e:
        print(f"- Database connection test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=== JRC Enquiry Assistant - Startup Test ===")
    print()
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test config
    if not test_config():
        success = False
    
    # Test database
    if not test_database_connection():
        success = False
    
    print("\n=== Test Results ===")
    if success:
        print("+ All tests passed! Application should start successfully.")
        print("\nTo start the application, run:")
        print("  python web_app.py")
    else:
        print("- Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set environment variables or create .env file")
        print("3. Check database configuration")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
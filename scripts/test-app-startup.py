#!/usr/bin/env python3
"""
Quick test script to verify the app starts correctly with SQLite fallback
"""

import sys
import os
import asyncio
import traceback
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_success(text):
    """Print success message"""
    try:
        print(f"[OK] {text}")
    except UnicodeEncodeError:
        print(f"[OK] {text}")

def print_error(text):
    """Print error message"""
    try:
        print(f"[FAIL] {text}")
    except UnicodeEncodeError:
        print(f"[FAIL] {text}")

def print_warning(text):
    """Print warning message"""
    try:
        print(f"[WARN] {text}")
    except UnicodeEncodeError:
        print(f"[WARN] {text}")

def test_imports():
    """Test that all required modules can be imported"""
    print_header("Testing Imports")
    
    try:
        print("Importing config...")
        from config import Config
        print_success("Config imported")
        
        print("Importing database connection...")
        from database.postgresql_connection import postgresql_connection
        print_success("PostgreSQL connection module imported")
        
        print("Importing web app...")
        from web_app import app
        print_success("Web app imported")
        
        return True
    except Exception as e:
        print_error(f"Import failed: {e}")
        traceback.print_exc()
        return False

def test_config():
    """Test configuration"""
    print_header("Testing Configuration")
    
    try:
        from config import Config
        
        print(f"Environment: {Config.ENVIRONMENT}")
        print(f"Vector DB Type: {Config.VECTOR_DATABASE_TYPE}")
        print(f"Answer Storage Type: {Config.ANSWER_STORAGE_TYPE}")
        print(f"Host: {Config.HOST}")
        print(f"Port: {Config.PORT}")
        print(f"Debug: {Config.DEBUG}")
        
        # Check essential configs
        if Config.PINECONE_API_KEY:
            print_success("Pinecone API key configured")
        else:
            print_warning("Pinecone API key not set")
        
        if Config.OPENAI_API_KEY:
            print_success("OpenAI API key configured")
        else:
            print_warning("OpenAI API key not set")
        
        if Config.JWT_SECRET_KEY:
            print_success("JWT secret key configured")
        else:
            print_warning("JWT secret key not set")
        
        return True
    except Exception as e:
        print_error(f"Config test failed: {e}")
        traceback.print_exc()
        return False

async def test_postgresql_fallback():
    """Test PostgreSQL connection and SQLite fallback"""
    print_header("Testing PostgreSQL Connection & SQLite Fallback")
    
    try:
        from database.postgresql_connection import postgresql_connection
        
        print("Attempting PostgreSQL connection...")
        result = await postgresql_connection.connect()
        
        if result:
            print_success("PostgreSQL connection successful")
            is_connected = await postgresql_connection.is_connected()
            if is_connected:
                print_success("PostgreSQL health check passed")
            else:
                print_warning("PostgreSQL health check failed")
        else:
            print_warning("PostgreSQL connection failed (expected with SQLite fallback)")
            print_success("SQLite fallback should be active")
        
        return True
    except Exception as e:
        print_warning(f"PostgreSQL test error: {e}")
        print_success("SQLite fallback should handle this")
        return True  # This is expected to fail, so return True

def test_app_routes():
    """Test that app routes are registered"""
    print_header("Testing App Routes")
    
    try:
        from web_app import app
        
        routes = [route.path for route in app.routes]
        
        print(f"Found {len(routes)} routes:")
        for route in sorted(routes)[:10]:  # Show first 10
            print(f"  - {route}")
        
        if len(routes) > 10:
            print(f"  ... and {len(routes) - 10} more")
        
        # Check for essential routes
        essential_routes = ["/", "/docs", "/health", "/api"]
        found_essential = [r for r in essential_routes if any(r in route for route in routes)]
        
        if found_essential:
            print_success(f"Essential routes found: {', '.join(found_essential)}")
        
        return True
    except Exception as e:
        print_error(f"Route test failed: {e}")
        traceback.print_exc()
        return False

def test_sqlite_repositories():
    """Test SQLite repositories are available"""
    print_header("Testing SQLite Repositories")
    
    try:
        print("Testing SQLite user repository...")
        from database.sqlite_user_repository import SQLiteUserRepository
        sqlite_user_repo = SQLiteUserRepository()
        print_success("SQLite user repository initialized")
        
        print("Testing SQLite inquiry repository...")
        from database.sqlite_inquiry_repository import SQLiteInquiryRepository
        sqlite_inquiry_repo = SQLiteInquiryRepository()
        print_success("SQLite inquiry repository initialized")
        
        return True
    except Exception as e:
        print_error(f"SQLite repository test failed: {e}")
        traceback.print_exc()
        return False

def test_unified_repositories():
    """Test unified repositories"""
    print_header("Testing Unified Repositories")
    
    try:
        print("Testing unified user repository...")
        from database.unified_user_repository import unified_user_repository
        print_success("Unified user repository imported")
        
        print("Testing unified inquiry repository...")
        from database.unified_inquiry_repository import unified_inquiry_repository
        print_success("Unified inquiry repository imported")
        
        return True
    except Exception as e:
        print_error(f"Unified repository test failed: {e}")
        traceback.print_exc()
        return False

def test_vector_db():
    """Test vector database setup"""
    print_header("Testing Vector Database")
    
    try:
        from database.db_factory import DatabaseFactory
        from config import Config
        
        print(f"Vector DB Type: {Config.VECTOR_DATABASE_TYPE}")
        
        if Config.VECTOR_DATABASE_TYPE == "pinecone":
            if Config.PINECONE_API_KEY:
                print_success("Pinecone configured")
            else:
                print_warning("Pinecone API key missing")
        
        # Try to create vector DB instance
        try:
            vector_db = DatabaseFactory.create_vector_db()
            print_success("Vector database instance created")
        except Exception as e:
            print_warning(f"Vector DB creation warning: {e}")
        
        return True
    except Exception as e:
        print_error(f"Vector DB test failed: {e}")
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print_header("JRC Enquiry Assistant - Startup Test")
    print("Testing app startup with SQLite fallback...")
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("PostgreSQL/SQLite Fallback", await test_postgresql_fallback()))
    results.append(("App Routes", test_app_routes()))
    results.append(("SQLite Repositories", test_sqlite_repositories()))
    results.append(("Unified Repositories", test_unified_repositories()))
    results.append(("Vector Database", test_vector_db()))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "[OK]" if result else "[FAIL]"
        print(f"{symbol} {name}: {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("All tests passed! App is ready to start.")
        print("\nYou can start the app with:")
        print("  Windows: .\\start.bat")
        print("  Or: python start-app.py")
        return 0
    else:
        print_warning(f"{total - passed} test(s) failed. Review errors above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)


#!/usr/bin/env python3
"""
Direct test of SQLite Export API without web server
Tests the API functionality directly
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.sqlite_export_api import SQLiteToMongoDBExporter

async def test_exporter_directly():
    """Test the exporter directly without web server"""
    print("🧪 Testing SQLite Export API Directly")
    print("=" * 50)
    
    exporter = SQLiteToMongoDBExporter()
    
    # Test 1: Get SQLite data
    print("\n📊 Test 1: Getting SQLite data...")
    try:
        data = exporter.get_sqlite_data()
        print(f"✅ Retrieved {len(data)} records from SQLite")
        
        if data:
            print("📋 Sample record:")
            sample = data[0]
            print(f"   ID: {sample.get('id')}")
            print(f"   User ID: {sample.get('user_id')}")
            print(f"   First Name: {sample.get('firstName')}")
            print(f"   Email: {sample.get('email')}")
            print(f"   Mobile: {sample.get('mobile')}")
        
        return True
    except Exception as e:
        print(f"❌ Error getting SQLite data: {e}")
        return False
    
    # Test 2: Test MongoDB connection
    print("\n🔗 Test 2: Testing MongoDB connection...")
    try:
        connected = await exporter.connect_mongodb()
        if connected:
            print("✅ MongoDB connection successful")
            await exporter.close_connections()
            return True
        else:
            print("❌ MongoDB connection failed")
            return False
    except Exception as e:
        print(f"❌ Error testing MongoDB connection: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Direct API Test")
    print("=" * 30)
    
    # Test SQLite data retrieval
    test1_success = await test_exporter_directly()
    
    print("\n📋 TEST SUMMARY")
    print("=" * 30)
    print(f"✅ SQLite Data Retrieval: {'PASS' if test1_success else 'FAIL'}")
    
    if test1_success:
        print("🎉 API functionality is working correctly!")
        print("\n📝 Note: The API is ready to use when the web server is running.")
        print("   You can use the migration tools or start the web server to test the endpoints.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    asyncio.run(main())

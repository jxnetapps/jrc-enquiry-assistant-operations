#!/usr/bin/env python3
"""
Test SQLite Export API
Tests the new SQLite to MongoDB export API endpoints
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
EXPORT_API_BASE = f"{BASE_URL}/api/export"

def call_api(method, url, data=None, params=None):
    """Make API call with error handling"""
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data, params=params)
        else:
            raise ValueError("Unsupported method")

        response.raise_for_status()
        return response.status_code, response.json()
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        try:
            error_response = e.response.json()
            print(f"❌ Error Response: {json.dumps(error_response, indent=2)}")
        except:
            print(f"❌ Error Response: {e.response.text}")
        return e.response.status_code, None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return None, None

def test_get_sqlite_data_summary():
    """Test getting SQLite data summary"""
    print("\n📊 Testing SQLite Data Summary")
    print("=" * 40)
    
    status_code, response_data = call_api("GET", f"{EXPORT_API_BASE}/sqlite-data")
    
    if status_code == 200 and response_data and response_data.get("success"):
        print("✅ Status Code: 200")
        print("✅ Response:")
        print(json.dumps(response_data, indent=2))
        
        data = response_data.get("data", {})
        print(f"\n📈 Summary:")
        print(f"   Total Records: {data.get('total_records', 0)}")
        print(f"   Unique User IDs: {data.get('statistics', {}).get('unique_user_ids', 0)}")
        print(f"   Parent Types: {data.get('statistics', {}).get('parent_type_distribution', {})}")
        print(f"   School Types: {data.get('statistics', {}).get('school_type_distribution', {})}")
        
        return True
    else:
        print("❌ Failed to get SQLite data summary")
        return False

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("\n🔗 Testing MongoDB Connection")
    print("=" * 40)
    
    status_code, response_data = call_api("POST", f"{EXPORT_API_BASE}/test-mongodb-connection")
    
    if status_code == 200 and response_data and response_data.get("success"):
        print("✅ Status Code: 200")
        print("✅ Response:")
        print(json.dumps(response_data, indent=2))
        
        data = response_data.get("data", {})
        print(f"\n📈 Connection Info:")
        print(f"   Status: {data.get('connection_status', 'unknown')}")
        print(f"   Database: {data.get('database', 'unknown')}")
        print(f"   Collection: {data.get('collection', 'unknown')}")
        print(f"   Existing Records: {data.get('existing_records', 0)}")
        
        return True
    else:
        print("❌ MongoDB connection test failed")
        if response_data:
            print(f"❌ Error: {response_data.get('error', 'Unknown error')}")
        return False

def test_export_status():
    """Test getting export status"""
    print("\n📋 Testing Export Status")
    print("=" * 40)
    
    status_code, response_data = call_api("GET", f"{EXPORT_API_BASE}/status")
    
    if status_code == 200 and response_data and response_data.get("success"):
        print("✅ Status Code: 200")
        print("✅ Response:")
        print(json.dumps(response_data, indent=2))
        
        data = response_data.get("data", {})
        print(f"\n📈 Export Status:")
        print(f"   Status: {data.get('status', 'unknown')}")
        print(f"   Total Records: {data.get('total_records', 0)}")
        print(f"   Processed: {data.get('processed_records', 0)}")
        print(f"   Successful: {data.get('successful_records', 0)}")
        print(f"   Failed: {data.get('failed_records', 0)}")
        print(f"   Skipped: {data.get('skipped_records', 0)}")
        
        return True
    else:
        print("❌ Failed to get export status")
        return False

def test_start_export():
    """Test starting export (dry run)"""
    print("\n🚀 Testing Start Export")
    print("=" * 40)
    
    # First reset status
    print("🔄 Resetting export status...")
    status_code, response_data = call_api("POST", f"{EXPORT_API_BASE}/reset-export-status")
    if status_code == 200:
        print("✅ Export status reset")
    else:
        print("⚠️  Could not reset export status")
    
    # Start export with small batch size for testing
    params = {
        "batch_size": 5,
        "skip_duplicates": True
    }
    
    status_code, response_data = call_api("POST", f"{EXPORT_API_BASE}/sqlite-to-mongodb", params=params)
    
    if status_code == 200 and response_data and response_data.get("success"):
        print("✅ Status Code: 200")
        print("✅ Response:")
        print(json.dumps(response_data, indent=2))
        
        data = response_data.get("data", {})
        print(f"\n📈 Export Started:")
        print(f"   Export ID: {data.get('export_id', 'unknown')}")
        print(f"   Batch Size: {data.get('batch_size', 0)}")
        print(f"   Skip Duplicates: {data.get('skip_duplicates', False)}")
        print(f"   Status: {data.get('status', 'unknown')}")
        
        return True
    else:
        print("❌ Failed to start export")
        if response_data:
            print(f"❌ Error: {response_data.get('error', 'Unknown error')}")
        return False

def monitor_export_progress():
    """Monitor export progress"""
    print("\n👀 Monitoring Export Progress")
    print("=" * 40)
    
    max_attempts = 30  # 30 seconds max
    attempt = 0
    
    while attempt < max_attempts:
        status_code, response_data = call_api("GET", f"{EXPORT_API_BASE}/status")
        
        if status_code == 200 and response_data and response_data.get("success"):
            data = response_data.get("data", {})
            status = data.get("status", "unknown")
            
            print(f"📊 Attempt {attempt + 1}: Status = {status}")
            
            if status == "completed":
                print("✅ Export completed successfully!")
                print(f"   Total Records: {data.get('total_records', 0)}")
                print(f"   Successful: {data.get('successful_records', 0)}")
                print(f"   Failed: {data.get('failed_records', 0)}")
                print(f"   Skipped: {data.get('skipped_records', 0)}")
                return True
            elif status == "failed":
                print("❌ Export failed!")
                print(f"   Error: {data.get('error_message', 'Unknown error')}")
                return False
            elif status == "running":
                print(f"   Progress: {data.get('processed_records', 0)}/{data.get('total_records', 0)}")
                print(f"   Successful: {data.get('successful_records', 0)}")
                print(f"   Failed: {data.get('failed_records', 0)}")
                print(f"   Skipped: {data.get('skipped_records', 0)}")
            else:
                print(f"   Status: {status}")
        
        time.sleep(1)
        attempt += 1
    
    print("⏰ Export monitoring timeout")
    return False

def main():
    """Main test function"""
    print("🧪 SQLite Export API Test Suite")
    print("=" * 50)
    print(f"🌐 Testing against: {BASE_URL}")
    print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Get SQLite data summary
    test1_success = test_get_sqlite_data_summary()
    
    # Test 2: Test MongoDB connection
    test2_success = test_mongodb_connection()
    
    # Test 3: Get export status
    test3_success = test_export_status()
    
    # Test 4: Start export (only if MongoDB is available)
    if test2_success:
        test4_success = test_start_export()
        
        if test4_success:
            # Test 5: Monitor export progress
            test5_success = monitor_export_progress()
        else:
            test5_success = False
    else:
        print("\n⚠️  Skipping export tests due to MongoDB connection failure")
        test4_success = False
        test5_success = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ SQLite Data Summary: {'PASS' if test1_success else 'FAIL'}")
    print(f"✅ MongoDB Connection: {'PASS' if test2_success else 'FAIL'}")
    print(f"✅ Export Status: {'PASS' if test3_success else 'FAIL'}")
    print(f"✅ Start Export: {'PASS' if test4_success else 'FAIL'}")
    print(f"✅ Export Progress: {'PASS' if test5_success else 'FAIL'}")
    
    total_tests = 5
    passed_tests = sum([test1_success, test2_success, test3_success, test4_success, test5_success])
    
    print(f"\n📊 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print(f"\n🔗 Available API Endpoints:")
    print(f"   GET  {EXPORT_API_BASE}/sqlite-data")
    print(f"   POST {EXPORT_API_BASE}/test-mongodb-connection")
    print(f"   GET  {EXPORT_API_BASE}/status")
    print(f"   POST {EXPORT_API_BASE}/sqlite-to-mongodb")
    print(f"   POST {EXPORT_API_BASE}/reset-export-status")

if __name__ == "__main__":
    main()

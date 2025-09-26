#!/usr/bin/env python3
"""
Test script for the Enhanced Chat Inquiry API
This script tests the insert and get all records functionality.
"""

import requests
import json
import time
from datetime import datetime, date

# Configuration
BASE_URL = "http://localhost:3000"
API_BASE = f"{BASE_URL}/api/v1/chat-inquiry"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_create_single_inquiry():
    """Test creating a single inquiry"""
    print("\n📝 Testing Single Inquiry Creation...")
    
    inquiry_data = {
        "parentType": "New Parent",
        "schoolType": "Day School",
        "firstName": "John Doe",
        "mobile": "9876543210",
        "email": "john.doe@example.com",
        "city": "New York",
        "childName": "Jane Doe",
        "grade": "Grade 1",
        "academicYear": "2024-2025",
        "dateOfBirth": "2020-01-01",
        "schoolName": "Test School"
    }
    
    try:
        response = requests.post(f"{API_BASE}/", json=inquiry_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Single inquiry creation failed: {e}")
        return False

def test_create_bulk_inquiries():
    """Test creating multiple inquiries at once"""
    print("\n📝 Testing Bulk Inquiry Creation...")
    
    bulk_data = {
        "inquiries": [
            {
                "parentType": "Existing Parent",
                "schoolType": "Boarding School",
                "firstName": "Alice Smith",
                "mobile": "9876543211",
                "email": "alice.smith@example.com",
                "city": "Los Angeles",
                "childName": "Bob Smith",
                "grade": "Grade 5",
                "academicYear": "2024-2025",
                "dateOfBirth": "2016-03-15",
                "schoolName": "Elite School"
            },
            {
                "parentType": "Alumni",
                "schoolType": "Online School",
                "firstName": "Charlie Brown",
                "mobile": "9876543212",
                "email": "charlie.brown@example.com",
                "city": "Chicago",
                "childName": "Lucy Brown",
                "grade": "Grade 3",
                "academicYear": "2024-2025",
                "dateOfBirth": "2018-07-20",
                "schoolName": "Digital Academy"
            }
        ]
    }
    
    try:
        response = requests.post(f"{API_BASE}/bulk", json=bulk_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Bulk inquiry creation failed: {e}")
        return False

def test_get_all_inquiries():
    """Test getting all inquiries with pagination"""
    print("\n📊 Testing Get All Inquiries...")
    
    try:
        # Test with default pagination
        response = requests.get(f"{API_BASE}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                records = data['data']['data']
                total = data['data']['total_count']
                print(f"✅ Retrieved {len(records)} records out of {total} total")
                return True
        
        return False
    except Exception as e:
        print(f"❌ Get all inquiries failed: {e}")
        return False

def test_get_inquiries_with_filters():
    """Test getting inquiries with various filters"""
    print("\n🔍 Testing Get Inquiries with Filters...")
    
    try:
        # Test with search filter
        params = {
            "search": "John",
            "page": 1,
            "page_size": 5
        }
        response = requests.get(f"{API_BASE}/", params=params)
        print(f"Search 'John' - Status: {response.status_code}")
        
        # Test with parent type filter
        params = {
            "parent_type": "New Parent",
            "page": 1,
            "page_size": 10
        }
        response = requests.get(f"{API_BASE}/", params=params)
        print(f"Filter by 'New Parent' - Status: {response.status_code}")
        
        # Test with school type filter
        params = {
            "school_type": "Day School",
            "page": 1,
            "page_size": 10
        }
        response = requests.get(f"{API_BASE}/", params=params)
        print(f"Filter by 'Day School' - Status: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Filtered queries failed: {e}")
        return False

def test_get_statistics():
    """Test getting statistics"""
    print("\n📈 Testing Get Statistics...")
    
    try:
        response = requests.get(f"{API_BASE}/stats")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Get statistics failed: {e}")
        return False

def test_export_data():
    """Test exporting data"""
    print("\n📤 Testing Export Data...")
    
    try:
        # Test JSON export
        response = requests.get(f"{API_BASE}/export?format=json&limit=10")
        print(f"JSON Export - Status: {response.status_code}")
        
        # Test CSV export
        response = requests.get(f"{API_BASE}/export?format=csv&limit=10")
        print(f"CSV Export - Status: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Chat Inquiry API Tests")
    print("=" * 60)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    tests = [
        ("Health Check", test_health_check),
        ("Create Single Inquiry", test_create_single_inquiry),
        ("Create Bulk Inquiries", test_create_bulk_inquiries),
        ("Get All Inquiries", test_get_all_inquiries),
        ("Get Inquiries with Filters", test_get_inquiries_with_filters),
        ("Get Statistics", test_get_statistics),
        ("Export Data", test_export_data)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()

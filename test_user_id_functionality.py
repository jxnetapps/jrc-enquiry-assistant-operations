#!/usr/bin/env python3
"""
Test script for user_id functionality in Chat Inquiry APIs
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
SIMPLE_API_BASE = f"{BASE_URL}/api/simple/chat-inquiry"
ENHANCED_API_BASE = f"{BASE_URL}/api/v1/chat-inquiry"

def test_create_inquiry_with_user_id(api_base, user_id, test_name):
    """Test creating an inquiry with user_id"""
    print(f"\n📝 Testing {test_name} - Create Inquiry with user_id: {user_id}")
    
    inquiry_data = {
        "user_id": user_id,
        "parentType": "New Parent",
        "schoolType": "Day School",
        "firstName": f"TestUser{user_id}",
        "mobile": f"987654321{user_id[-1]}",
        "email": f"test{user_id}@example.com",
        "city": f"TestCity{user_id}",
        "childName": f"TestChild{user_id}",
        "grade": "Grade 1",
        "academicYear": "2024-2025",
        "dateOfBirth": "2020-01-01",
        "schoolName": f"TestSchool{user_id}"
    }
    
    try:
        response = requests.post(api_base, json=inquiry_data)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response: {json.dumps(data, indent=2)}")
        return data.get('data', {}).get('inquiry_id')
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if e.response is not None:
            print(f"❌ Error Response: {e.response.text}")
        return None

def test_get_inquiries_by_user_id(api_base, user_id, test_name):
    """Test getting inquiries by user_id"""
    print(f"\n🔍 Testing {test_name} - Get Inquiries by user_id: {user_id}")
    
    try:
        response = requests.get(f"{api_base}/user/{user_id}")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response: {json.dumps(data, indent=2)}")
        return data.get('data', [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if e.response is not None:
            print(f"❌ Error Response: {e.response.text}")
        return []

def test_get_all_inquiries(api_base, test_name):
    """Test getting all inquiries"""
    print(f"\n📊 Testing {test_name} - Get All Inquiries")
    
    try:
        response = requests.get(api_base)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Total Records: {len(data.get('data', []))}")
        
        # Show user_id distribution
        records = data.get('data', [])
        user_ids = {}
        for record in records:
            if isinstance(record, dict):
                user_id = record.get('user_id', 'No user_id')
                user_ids[user_id] = user_ids.get(user_id, 0) + 1
        
        print(f"📈 User ID Distribution: {user_ids}")
        return records
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if e.response is not None:
            print(f"❌ Error Response: {e.response.text}")
        return []

def test_enhanced_api_pagination(api_base, user_id):
    """Test enhanced API pagination for user_id"""
    print(f"\n📄 Testing Enhanced API - Pagination for user_id: {user_id}")
    
    try:
        response = requests.get(f"{api_base}/user/{user_id}?page=1&page_size=5")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response: {json.dumps(data, indent=2)}")
        return data.get('data', [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if e.response is not None:
            print(f"❌ Error Response: {e.response.text}")
        return []

def main():
    print("🚀 Testing User ID Functionality in Chat Inquiry APIs")
    print("=" * 60)
    
    # Give the server a moment to start if it was just launched
    time.sleep(2)
    
    # Test data
    test_user_ids = ["user123", "user456", "user789"]
    
    print("\n" + "="*60)
    print("🔧 TESTING SIMPLE API")
    print("="*60)
    
    # Test Simple API
    for user_id in test_user_ids:
        # Create inquiry with user_id
        inquiry_id = test_create_inquiry_with_user_id(SIMPLE_API_BASE, user_id, "Simple API")
        
        if inquiry_id:
            print(f"✅ Created inquiry {inquiry_id} for user {user_id}")
        
        # Get inquiries by user_id
        user_inquiries = test_get_inquiries_by_user_id(SIMPLE_API_BASE, user_id, "Simple API")
        print(f"📊 Found {len(user_inquiries)} inquiries for user {user_id}")
    
    # Get all inquiries to see user_id distribution
    all_inquiries = test_get_all_inquiries(SIMPLE_API_BASE, "Simple API")
    
    print("\n" + "="*60)
    print("🚀 TESTING ENHANCED API")
    print("="*60)
    
    # Test Enhanced API
    for user_id in test_user_ids:
        # Create inquiry with user_id
        inquiry_id = test_create_inquiry_with_user_id(ENHANCED_API_BASE, user_id, "Enhanced API")
        
        if inquiry_id:
            print(f"✅ Created inquiry {inquiry_id} for user {user_id}")
        
        # Get inquiries by user_id with pagination
        user_inquiries = test_get_inquiries_by_user_id(ENHANCED_API_BASE, user_id, "Enhanced API")
        print(f"📊 Found {len(user_inquiries)} inquiries for user {user_id}")
        
        # Test pagination
        paginated_inquiries = test_enhanced_api_pagination(ENHANCED_API_BASE, user_id)
        print(f"📄 Paginated results: {len(paginated_inquiries)} inquiries")
    
    # Get all inquiries to see user_id distribution
    all_inquiries = test_get_all_inquiries(ENHANCED_API_BASE, "Enhanced API")
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    # Count total inquiries by user_id
    total_by_user = {}
    for inquiry in all_inquiries:
        if isinstance(inquiry, dict):
            user_id = inquiry.get('user_id', 'No user_id')
            total_by_user[user_id] = total_by_user.get(user_id, 0) + 1
    
    print(f"📈 Total inquiries by user_id: {total_by_user}")
    print(f"📊 Total inquiries created: {sum(total_by_user.values())}")
    
    print("\n✅ User ID functionality test completed!")
    print("\n🔗 Available endpoints:")
    print(f"   Simple API: {SIMPLE_API_BASE}/user/{{user_id}}")
    print(f"   Enhanced API: {ENHANCED_API_BASE}/user/{{user_id}}")

if __name__ == "__main__":
    main()

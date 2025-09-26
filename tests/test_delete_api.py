#!/usr/bin/env python3
"""
Test script for the Simple Chat Inquiry API with Delete functionality
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/simple/chat-inquiry"

def test_get_all_inquiries():
    """Test getting all inquiries"""
    print("📊 Testing Get All Inquiries...")
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message')}")
            print(f"Records found: {len(data.get('data', []))}")
            return data.get('data', [])
        else:
            print(f"Error: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_get_inquiry_by_id(inquiry_id):
    """Test getting a specific inquiry by ID"""
    print(f"\n🔍 Testing Get Inquiry by ID: {inquiry_id}...")
    try:
        response = requests.get(f"{API_BASE}/{inquiry_id}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message')}")
            print(f"Data: {json.dumps(data.get('data', {}), indent=2)}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_delete_inquiry(inquiry_id):
    """Test deleting an inquiry by ID"""
    print(f"\n🗑️ Testing Delete Inquiry: {inquiry_id}...")
    try:
        response = requests.delete(f"{API_BASE}/{inquiry_id}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message')}")
            print(f"Deleted ID: {data.get('data', {}).get('deleted_id')}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_create_inquiry():
    """Test creating a new inquiry"""
    print("\n📝 Testing Create Inquiry...")
    inquiry_data = {
        "parentType": "New Parent",
        "schoolType": "Day School",
        "firstName": "Test Delete User",
        "mobile": "9876543210",
        "email": "testdelete@example.com",
        "city": "Test City",
        "childName": "Test Child",
        "grade": "Grade 1",
        "academicYear": "2024-2025",
        "dateOfBirth": "2020-01-01",
        "schoolName": "Test School"
    }
    
    try:
        response = requests.post(f"{API_BASE}/", json=inquiry_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message')}")
            inquiry_id = data.get('data', {}).get('inquiry_id')
            print(f"Created ID: {inquiry_id}")
            return inquiry_id
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_stats():
    """Test getting statistics"""
    print("\n📈 Testing Get Statistics...")
    try:
        response = requests.get(f"{API_BASE}/stats")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message')}")
            stats = data.get('data', {})
            print(f"Total Inquiries: {stats.get('total_inquiries', 0)}")
            print(f"Parent Type Distribution: {stats.get('parent_type_distribution', {})}")
            print(f"School Type Distribution: {stats.get('school_type_distribution', {})}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Simple Chat Inquiry API with Delete Functionality")
    print("=" * 70)
    
    # Test 1: Get initial statistics
    print("\n" + "="*20 + " INITIAL STATE " + "="*20)
    test_stats()
    
    # Test 2: Get all inquiries
    print("\n" + "="*20 + " GET ALL INQUIRIES " + "="*20)
    inquiries = test_get_all_inquiries()
    
    if inquiries:
        print(f"\nFound {len(inquiries)} inquiries:")
        for i, inquiry in enumerate(inquiries[:3], 1):  # Show first 3
            print(f"  {i}. ID: {inquiry.get('id')}, Name: {inquiry.get('firstName')}, Email: {inquiry.get('email')}")
    
    # Test 3: Create a new inquiry for deletion
    print("\n" + "="*20 + " CREATE FOR DELETION " + "="*20)
    new_inquiry_id = test_create_inquiry()
    
    if new_inquiry_id:
        # Test 4: Get the created inquiry
        print("\n" + "="*20 + " GET CREATED INQUIRY " + "="*20)
        test_get_inquiry_by_id(new_inquiry_id)
        
        # Test 5: Delete the inquiry
        print("\n" + "="*20 + " DELETE INQUIRY " + "="*20)
        delete_success = test_delete_inquiry(new_inquiry_id)
        
        if delete_success:
            # Test 6: Try to get the deleted inquiry (should fail)
            print("\n" + "="*20 + " VERIFY DELETION " + "="*20)
            test_get_inquiry_by_id(new_inquiry_id)
    
    # Test 7: Get final statistics
    print("\n" + "="*20 + " FINAL STATE " + "="*20)
    test_stats()
    
    # Test 8: Try to delete a non-existent inquiry
    print("\n" + "="*20 + " DELETE NON-EXISTENT " + "="*20)
    test_delete_inquiry("99999")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()

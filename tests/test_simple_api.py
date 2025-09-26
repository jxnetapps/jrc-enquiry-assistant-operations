#!/usr/bin/env python3
"""
Simple test for the Chat Inquiry API
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1/chat-inquiry"

def test_create_inquiry():
    """Test creating a single inquiry"""
    print("📝 Testing Create Inquiry...")
    
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
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_inquiries():
    """Test getting all inquiries"""
    print("\n📊 Testing Get All Inquiries...")
    
    try:
        response = requests.get(f"{API_BASE}/?page=1&page_size=10")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health():
    """Test health check"""
    print("\n🔍 Testing Health Check...")
    
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Chat Inquiry API")
    print("=" * 40)
    
    # Test health first
    test_health()
    
    # Test create inquiry
    test_create_inquiry()
    
    # Test get inquiries
    test_get_inquiries()
    
    print("\n✅ Tests completed!")

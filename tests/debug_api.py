#!/usr/bin/env python3
"""
Debug script to test the enhanced API
"""

import requests
import json

def test_enhanced_api():
    """Test the enhanced API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Enhanced API Endpoints")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing Health Endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/chat-inquiry/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test create endpoint
    print("\n2. Testing Create Endpoint...")
    try:
        data = {
            "parentType": "New Parent",
            "schoolType": "Day School",
            "firstName": "Debug User",
            "mobile": "9876543210",
            "email": "debug@example.com",
            "city": "Debug City",
            "childName": "Debug Child",
            "grade": "Grade 1",
            "academicYear": "2024-2025",
            "dateOfBirth": "2020-01-01",
            "schoolName": "Debug School"
        }
        response = requests.post(f"{base_url}/api/v1/chat-inquiry/", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test get all endpoint
    print("\n3. Testing Get All Endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/chat-inquiry/?page=1&page_size=5")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test stats endpoint
    print("\n4. Testing Stats Endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/chat-inquiry/stats")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_enhanced_api()

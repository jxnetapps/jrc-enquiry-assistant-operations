"""
Test script for the unified chat inquiry API
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_unified_api():
    """Test the unified chat inquiry API"""
    
    print("Testing Unified Chat Inquiry API")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Health Check
        print("\n1. Testing Health Check...")
        try:
            response = await client.get(f"{BASE_URL}/api/chat-inquiry/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 2: Database Status
        print("\n2. Testing Database Status...")
        try:
            response = await client.get(f"{BASE_URL}/api/chat-inquiry/database/status")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 3: Test PostgreSQL Connection
        print("\n3. Testing PostgreSQL Connection...")
        try:
            response = await client.post(f"{BASE_URL}/api/chat-inquiry/database/test-postgres")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 4: Create Public Inquiry
        print("\n4. Testing Public Inquiry Creation...")
        test_inquiry = {
            "parentType": "New Parent",
            "schoolType": "Day School",
            "firstName": "John",
            "mobile": "9876543210",
            "email": "john.doe@example.com",
            "city": "Mumbai",
            "childName": "Jane",
            "grade": "5th",
            "academicYear": "2024-25",
            "dateOfBirth": "2015-06-15",
            "schoolName": "Test School",
            "user_id": "test_user_123"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/chat-inquiry/public",
                json=test_inquiry
            )
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Response: {result}")
            
            if result.get("success") and result.get("data"):
                inquiry_id = result["data"]["id"]
                print(f"   Created Inquiry ID: {inquiry_id}")
            else:
                inquiry_id = None
                
        except Exception as e:
            print(f"   Error: {e}")
            inquiry_id = None
        
        # Test 5: Get All Inquiries (Public)
        print("\n5. Testing Get All Inquiries (Public)...")
        try:
            response = await client.get(f"{BASE_URL}/api/chat-inquiry/public?page=1&page_size=10")
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Total Inquiries: {result.get('data', {}).get('total_count', 0)}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 6: Get Statistics
        print("\n6. Testing Statistics...")
        try:
            response = await client.get(f"{BASE_URL}/api/chat-inquiry/stats")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 7: Export Status
        print("\n7. Testing Export Status...")
        try:
            response = await client.get(f"{BASE_URL}/api/chat-inquiry/database/export-status")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 8: Start SQLite to PostgreSQL Export
        print("\n8. Testing SQLite to PostgreSQL Export...")
        try:
            response = await client.post(f"{BASE_URL}/api/chat-inquiry/database/export-sqlite-to-postgres")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 9: Check Export Status Again
        print("\n9. Checking Export Status After Start...")
        try:
            response = await client.get(f"{BASE_URL}/api/chat-inquiry/database/export-status")
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Export Status: {result.get('data', {}).get('status')}")
            print(f"   Progress: {result.get('data', {}).get('progress')}%")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 10: Export to JSON
        print("\n10. Testing JSON Export...")
        try:
            response = await client.get(f"{BASE_URL}/api/chat-inquiry/export/json?page=1&page_size=5")
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Exported Records: {result.get('data', {}).get('export_info', {}).get('total_exported', 0)}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 11: Get User Inquiries
        print("\n11. Testing Get User Inquiries...")
        try:
            response = await client.get(f"{BASE_URL}/api/chat-inquiry/public/user/test_user_123")
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   User Inquiries: {len(result.get('data', []))}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 12: Bulk Insert
        print("\n12. Testing Bulk Insert...")
        bulk_data = {
            "inquiries": [
                {
                    "parentType": "Existing Parent",
                    "schoolType": "Boarding School",
                    "firstName": "Alice",
                    "mobile": "9876543211",
                    "email": "alice@example.com",
                    "city": "Delhi",
                    "childName": "Bob",
                    "grade": "3rd",
                    "academicYear": "2024-25",
                    "dateOfBirth": "2017-03-10",
                    "schoolName": "Boarding School",
                    "user_id": "test_user_456"
                },
                {
                    "parentType": "Alumni",
                    "schoolType": "International School",
                    "firstName": "Charlie",
                    "mobile": "9876543212",
                    "email": "charlie@example.com",
                    "city": "Bangalore",
                    "childName": "Diana",
                    "grade": "7th",
                    "academicYear": "2024-25",
                    "dateOfBirth": "2013-11-20",
                    "schoolName": "International School",
                    "user_id": "test_user_789"
                }
            ]
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/chat-inquiry/bulk",
                json=bulk_data
            )
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Success Count: {result.get('data', {}).get('success_count', 0)}")
            print(f"   Failed Count: {result.get('data', {}).get('failed_count', 0)}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("Unified API Testing Complete!")

if __name__ == "__main__":
    asyncio.run(test_unified_api())

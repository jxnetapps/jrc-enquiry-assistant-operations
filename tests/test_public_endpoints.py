"""
Test script for public endpoints of the unified chat inquiry API
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_public_endpoints():
    """Test the public endpoints of the unified API"""
    
    print("Testing Public Endpoints")
    print("=" * 40)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Create Public Inquiry
        print("\n1. Testing Public Inquiry Creation...")
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
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success')}")
                print(f"   Message: {result.get('message')}")
                if result.get('data'):
                    print(f"   Inquiry ID: {result['data'].get('id')}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
        
        # Test 2: Get All Inquiries (Public)
        print("\n2. Testing Get All Inquiries (Public)...")
        try:
            response = await client.get(f"{BASE_URL}/api/chat-inquiry/public?page=1&page_size=5")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success')}")
                if result.get('data'):
                    data = result['data']
                    print(f"   Total Count: {data.get('total_count', 0)}")
                    print(f"   Page: {data.get('page', 0)}")
                    print(f"   Page Size: {data.get('page_size', 0)}")
                    print(f"   Inquiries: {len(data.get('data', []))}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
        
        # Test 3: Get Statistics
        print("\n3. Testing Statistics...")
        try:
            response = await client.get(f"{BASE_URL}/api/chat-inquiry/stats")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success')}")
                if result.get('data'):
                    data = result['data']
                    print(f"   Total Inquiries: {data.get('total_inquiries', 0)}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
        
        # Test 4: Database Status
        print("\n4. Testing Database Status...")
        try:
            response = await client.get(f"{BASE_URL}/api/chat-inquiry/database/status")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success')}")
                if result.get('data'):
                    data = result['data']
                    print(f"   PostgreSQL Connected: {data.get('postgresql_connected')}")
                    print(f"   SQLite Available: {data.get('sqlite_available')}")
                    print(f"   SQLite Count: {data.get('sqlite_count', 0)}")
                    print(f"   PostgreSQL Count: {data.get('postgresql_count', 0)}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
        
        # Test 5: Export Status
        print("\n5. Testing Export Status...")
        try:
            response = await client.get(f"{BASE_URL}/api/chat-inquiry/database/export-status")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success')}")
                if result.get('data'):
                    data = result['data']
                    print(f"   Export Status: {data.get('status')}")
                    print(f"   Progress: {data.get('progress', 0)}%")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
    
    print("\n" + "=" * 40)
    print("Public Endpoints Testing Complete!")

if __name__ == "__main__":
    asyncio.run(test_public_endpoints())

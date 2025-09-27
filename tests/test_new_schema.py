"""
Test the new PostgreSQL schema with CRUD operations
"""

import asyncio
import httpx
from datetime import date

async def test_new_schema():
    """Test CRUD operations with the new PostgreSQL schema"""
    
    print("Testing New PostgreSQL Schema")
    print("=" * 40)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Create Inquiry
        print("\n1. Testing Create Inquiry...")
        inquiry_data = {
            "parentType": "New Parent",
            "schoolType": "Day School",
            "firstName": "John",
            "mobile": "9876543210",
            "email": f"john.test.{asyncio.get_event_loop().time()}@example.com",
            "city": "Test City",
            "childName": "Jane",
            "grade": "5th",
            "academicYear": "2025-2026",
            "dateOfBirth": "2015-01-15",
            "schoolName": "Test School",
            "user_id": "12345678-1234-1234-1234-123456789012"
        }
        
        try:
            response = await client.post("http://localhost:8000/api/chat-inquiry/public", json=inquiry_data)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success')}")
                if result.get('data'):
                    data = result['data']
                    print(f"   Inquiry ID: {data.get('id')}")
                    print(f"   Status: {data.get('status')}")
                    print(f"   User ID: {data.get('user_id')}")
                    inquiry_id = data.get('id')
                else:
                    print(f"   Error: No data in response")
                    return
            else:
                print(f"   Error: {response.text}")
                return
        except Exception as e:
            print(f"   Exception: {e}")
            return
        
        # Test 2: Get Inquiry by ID
        print("\n2. Testing Get Inquiry by ID...")
        try:
            response = await client.get(f"http://localhost:8000/api/chat-inquiry/public/{inquiry_id}")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success')}")
                if result.get('data'):
                    data = result['data']
                    print(f"   Found Inquiry: {data.get('firstName')} - {data.get('childName')}")
                    print(f"   Status: {data.get('status')}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
        
        # Test 3: Get All Inquiries
        print("\n3. Testing Get All Inquiries...")
        try:
            response = await client.get("http://localhost:8000/api/chat-inquiry/public?page=1&page_size=5")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success')}")
                if result.get('data'):
                    data = result['data']
                    print(f"   Total Count: {data.get('total_count', 0)}")
                    print(f"   Records: {len(data.get('records', []))}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
        
        # Test 4: Get Statistics
        print("\n4. Testing Statistics...")
        try:
            response = await client.get("http://localhost:8000/api/chat-inquiry/stats")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success')}")
                if result.get('data'):
                    data = result['data']
                    print(f"   Total Inquiries: {data.get('total_inquiries', 0)}")
                    print(f"   Status Distribution: {data.get('status_distribution', {})}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
        
        # Test 5: Test PostgreSQL Connection
        print("\n5. Testing PostgreSQL Connection...")
        try:
            response = await client.post("http://localhost:8000/api/chat-inquiry/database/test-postgres")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success')}")
                print(f"   Message: {result.get('message')}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
    
    print("\n" + "=" * 40)
    print("New Schema Testing Complete!")

if __name__ == "__main__":
    asyncio.run(test_new_schema())

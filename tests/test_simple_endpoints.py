"""
Simple test to check if endpoints are accessible
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_simple_endpoints():
    """Test basic endpoint accessibility"""
    
    print("Testing Simple Endpoints")
    print("=" * 30)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Root endpoint
        print("\n1. Testing Root Endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/")
            print(f"   Status: {response.status_code}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 2: Health endpoint
        print("\n2. Testing Health Endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 3: API Health endpoint
        print("\n3. Testing API Health Endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/api/chat-inquiry/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 4: Database Status endpoint
        print("\n4. Testing Database Status Endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/api/chat-inquiry/database/status")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success')}")
                print(f"   SQLite Count: {result.get('data', {}).get('sqlite_count', 0)}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 5: Stats endpoint (should be public)
        print("\n5. Testing Stats Endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/api/chat-inquiry/stats")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success')}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 6: Public endpoint (should be public)
        print("\n6. Testing Public Endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/api/chat-inquiry/public")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success')}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n" + "=" * 30)
    print("Simple Endpoints Testing Complete!")

if __name__ == "__main__":
    asyncio.run(test_simple_endpoints())

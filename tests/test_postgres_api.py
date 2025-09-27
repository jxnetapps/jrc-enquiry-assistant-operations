"""
Test PostgreSQL connection through the API
"""

import asyncio
import httpx

async def test_postgres_api():
    """Test PostgreSQL connection through the API"""
    
    print("Testing PostgreSQL Connection via API")
    print("=" * 40)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Database Status
        print("\n1. Testing Database Status...")
        try:
            response = await client.get("http://localhost:8000/api/chat-inquiry/database/status")
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
        
        # Test 2: Test PostgreSQL Connection
        print("\n2. Testing PostgreSQL Connection...")
        try:
            response = await client.post("http://localhost:8000/api/chat-inquiry/database/test-postgres")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success')}")
                print(f"   Message: {result.get('message')}")
                if result.get('data'):
                    data = result['data']
                    print(f"   Connected: {data.get('connected')}")
                    print(f"   Tables Created: {data.get('tables_created')}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
        
        # Test 3: Health Check
        print("\n3. Testing Health Check...")
        try:
            response = await client.get("http://localhost:8000/api/chat-inquiry/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success')}")
                if result.get('data'):
                    data = result['data']
                    print(f"   PostgreSQL: {data.get('postgresql')}")
                    print(f"   SQLite: {data.get('sqlite')}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
    
    print("\n" + "=" * 40)
    print("PostgreSQL API Testing Complete!")

if __name__ == "__main__":
    asyncio.run(test_postgres_api())

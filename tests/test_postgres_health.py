#!/usr/bin/env python3
"""
Test script for PostgreSQL health check endpoints
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_health_endpoints():
    """Test all health check endpoints"""
    
    endpoints = [
        "/api/chat-inquiry/health",
        "/api/chat-inquiry/database/status", 
        "/api/chat-inquiry/database/postgres-health",
        "/api/chat-inquiry/database/test-postgres"
    ]
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Testing PostgreSQL Health Check Endpoints")
        print("=" * 60)
        
        for endpoint in endpoints:
            try:
                print(f"\n📡 Testing: {endpoint}")
                print("-" * 40)
                
                async with session.get(f"{BASE_URL}{endpoint}") as response:
                    data = await response.json()
                    
                    print(f"Status Code: {response.status}")
                    print(f"Success: {data.get('success', False)}")
                    print(f"Message: {data.get('message', 'N/A')}")
                    
                    if 'data' in data:
                        print("Data:")
                        print(json.dumps(data['data'], indent=2, default=str))
                    
                    if 'error' in data:
                        print(f"Error: {data['error']}")
                        
            except Exception as e:
                print(f"❌ Error testing {endpoint}: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Health check testing completed!")

async def test_postgres_connection_switch():
    """Test switching between Supabase and local PostgreSQL"""
    
    print("\n🔄 Testing Database Connection Switching")
    print("=" * 60)
    
    # Test with different PostgreSQL configurations
    test_cases = [
        {"description": "Using Supabase Database"},
        {"description": "Using Local Database"}
    ]
    
    for test_case in test_cases:
        print(f"\n📊 {test_case['description']}")
        print("-" * 40)
        
        # Note: In a real test, you would set environment variables
        # For this demo, we'll just show what the response would look like
        print("Expected behavior:")
        
        if "Supabase" in test_case['description']:
            print("  - Connection Type: PostgreSQL")
            print("  - Host: db.umwxkbcvqvqqybjwcash.supabase.co")
            print("  - Database: postgres")
            print("  - Port: 5432")
        else:
            print("  - Connection Type: Local PostgreSQL")
            print("  - Host: localhost (or configured host)")
            print("  - Database: jrc_chatbot_assistant_dev (or configured database)")
            print("  - Port: 5432")

if __name__ == "__main__":
    print("🚀 PostgreSQL Health Check Test Suite")
    print("Make sure the application is running on http://localhost:8000")
    print()
    
    # Run the tests
    asyncio.run(test_health_endpoints())
    asyncio.run(test_postgres_connection_switch())
    
    print("\n📋 Available Health Check Endpoints:")
    print("1. GET  /api/chat-inquiry/health - General service health")
    print("2. GET  /api/chat-inquiry/database/status - Database status with counts")
    print("3. GET  /api/chat-inquiry/database/postgres-health - Detailed PostgreSQL health")
    print("4. POST /api/chat-inquiry/database/test-postgres - Test PostgreSQL connection")
    
    print("\n💡 Usage Examples:")
    print("curl http://localhost:8000/api/chat-inquiry/health")
    print("curl http://localhost:8000/api/chat-inquiry/database/status")
    print("curl http://localhost:8000/api/chat-inquiry/database/postgres-health")
    print("curl -X POST http://localhost:8000/api/chat-inquiry/database/test-postgres")

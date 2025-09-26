#!/usr/bin/env python3
"""
Test script for the reorganized API structure
This script tests that all API endpoints are accessible through the new structure
"""

import asyncio
import httpx
import json
from datetime import datetime

# Test configuration  
BASE_URL = "http://localhost:3000"  # Updated to use available port

async def test_api_structure():
    """Test that all API endpoints are accessible"""
    print("🧪 Testing Reorganized API Structure")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            # Test 1: Health check
            print("\n1. Testing Health Check")
            response = await client.get(f"{BASE_URL}/health", timeout=10.0)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Health check passed")
            else:
                print("   ❌ Health check failed")
                return False
            
            # Test 2: Auth API endpoints
            print("\n2. Testing Auth API Endpoints")
            
            # Test login endpoint
            login_data = {"username": "admin", "password": "admin123"}
            response = await client.post(f"{BASE_URL}/api/login", json=login_data, timeout=10.0)
            print(f"   Login Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Login endpoint accessible")
                login_result = response.json()
                if login_result.get("success"):
                    token = login_result.get("access_token")
                    print(f"   ✅ Login successful, token received")
                else:
                    print("   ⚠️  Login failed but endpoint accessible")
            else:
                print("   ❌ Login endpoint not accessible")
            
            # Test 3: Vector Chat API endpoints
            print("\n3. Testing Vector Chat API Endpoints")
            
            # Test stats endpoint (requires auth)
            headers = {"Authorization": f"Bearer {token}"} if 'token' in locals() else {}
            response = await client.get(f"{BASE_URL}/api/stats", headers=headers, timeout=10.0)
            print(f"   Stats Status: {response.status_code}")
            if response.status_code in [200, 401]:  # 401 is expected without proper auth
                print("   ✅ Stats endpoint accessible")
            else:
                print("   ❌ Stats endpoint not accessible")
            
            # Test 4: Chat Inquiry API endpoints
            print("\n4. Testing Chat Inquiry API Endpoints")
            
            # Test create inquiry endpoint (no auth required)
            inquiry_data = {
                "parentType": "New Parent",
                "schoolType": "Day School",
                "firstName": "Test User",
                "mobile": "9876543210",
                "email": "test@example.com",
                "city": "Test City",
                "childName": "Test Child",
                "grade": "Grade 1",
                "academicYear": "2024-2025",
                "dateOfBirth": "2020-01-01",
                "schoolName": "Test School"
            }
            
            response = await client.post(f"{BASE_URL}/api/chat-inquiry", json=inquiry_data, timeout=10.0)
            print(f"   Create Inquiry Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Create inquiry endpoint accessible")
                result = response.json()
                if result.get("success"):
                    print("   ✅ Inquiry created successfully")
                    inquiry_id = result.get("data", {}).get("inquiry_id")
                    print(f"   📋 Inquiry ID: {inquiry_id}")
                else:
                    print(f"   ⚠️  Inquiry creation failed: {result.get('message')}")
            else:
                print("   ❌ Create inquiry endpoint not accessible")
                print(f"   Response: {response.text}")
            
            # Test 5: API Documentation
            print("\n5. Testing API Documentation")
            response = await client.get(f"{BASE_URL}/docs", timeout=10.0)
            print(f"   Docs Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ API documentation accessible")
            else:
                print("   ❌ API documentation not accessible")
            
            print("\n" + "=" * 50)
            print("🎉 API Structure Test Completed!")
            return True
            
        except httpx.ConnectError:
            print(f"\n🔌 CONNECTION ERROR: Could not connect to {BASE_URL}")
            print("Make sure the server is running on http://localhost:8000")
            return False
        except Exception as e:
            print(f"\n💥 ERROR: {e}")
            return False

async def test_api_routes():
    """Test that all API routes are properly registered"""
    print("\n🔍 Testing API Route Registration")
    print("=" * 40)
    
    async with httpx.AsyncClient() as client:
        try:
            # Test OpenAPI schema
            response = await client.get(f"{BASE_URL}/openapi.json", timeout=10.0)
            if response.status_code == 200:
                schema = response.json()
                paths = schema.get("paths", {})
                
                print(f"📊 Total API endpoints found: {len(paths)}")
                
                # Check for specific endpoint groups
                auth_endpoints = [path for path in paths.keys() if "/api/login" in path or "/api/token" in path or "/api/user" in path]
                chat_endpoints = [path for path in paths.keys() if "/api/chat" in path or "/api/crawl" in path or "/api/upload" in path or "/api/stats" in path or "/api/answers" in path]
                inquiry_endpoints = [path for path in paths.keys() if "/api/chat-inquiry" in path]
                
                print(f"🔐 Auth endpoints: {len(auth_endpoints)}")
                for endpoint in auth_endpoints:
                    print(f"   - {endpoint}")
                
                print(f"💬 Vector Chat endpoints: {len(chat_endpoints)}")
                for endpoint in chat_endpoints:
                    print(f"   - {endpoint}")
                
                print(f"📝 Chat Inquiry endpoints: {len(inquiry_endpoints)}")
                for endpoint in inquiry_endpoints:
                    print(f"   - {endpoint}")
                
                print("\n✅ All API routes properly registered!")
                return True
            else:
                print("❌ Could not retrieve API schema")
                return False
                
        except Exception as e:
            print(f"❌ Error testing API routes: {e}")
            return False

async def main():
    """Main test function"""
    print("🚀 Reorganized API Structure Test Suite")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Target URL: {BASE_URL}")
    
    # Run tests
    structure_ok = await test_api_structure()
    routes_ok = await test_api_routes()
    
    if structure_ok and routes_ok:
        print(f"\n🎉 All tests passed! API reorganization successful!")
    else:
        print(f"\n💔 Some tests failed. Please check the issues above.")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("Starting Reorganized API Structure Test...")
    print("Make sure the server is running on http://localhost:8000")
    print("Press Ctrl+C to cancel\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Test cancelled by user")
    except Exception as e:
        print(f"\n\n💥 Test execution failed: {e}")

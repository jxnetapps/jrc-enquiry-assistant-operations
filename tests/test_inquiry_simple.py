#!/usr/bin/env python3
"""
Simple test script for Chat Inquiry API
This script tests the API without authentication for basic functionality
"""

import asyncio
import httpx
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:3000"  # Updated to use available port

# Sample test data
TEST_DATA = {
    "parentType": "New Parent",
    "schoolType": "Day School", 
    "firstName": "Agarwal",
    "mobile": "9885659894",
    "email": "sai@g.in",
    "city": "6987",
    "childName": "Janith",
    "grade": "MYP 4",
    "academicYear": "2026-2027",
    "dateOfBirth": "2025-09-01",
    "schoolName": "Edify"
}

async def test_create_inquiry():
    """Test creating a chat inquiry"""
    print("🚀 Testing Chat Inquiry Creation")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            print(f"📤 Sending POST request to {BASE_URL}/api/chat-inquiry")
            print(f"📋 Data: {json.dumps(TEST_DATA, indent=2)}")
            
            response = await client.post(
                f"{BASE_URL}/api/chat-inquiry",
                json=TEST_DATA,
                timeout=30.0
            )
            
            print(f"\n📊 Response Status: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"📝 Response Body: {json.dumps(response_data, indent=2)}")
                
                if response.status_code == 200 and response_data.get("success"):
                    inquiry_id = response_data.get("data", {}).get("inquiry_id")
                    print(f"\n✅ SUCCESS: Inquiry created with ID: {inquiry_id}")
                    return inquiry_id
                else:
                    print(f"\n❌ FAILED: {response_data.get('message', 'Unknown error')}")
                    return None
                    
            except json.JSONDecodeError:
                print(f"📝 Response Body (raw): {response.text}")
                print(f"\n❌ FAILED: Invalid JSON response")
                return None
                
        except httpx.TimeoutException:
            print(f"\n⏰ TIMEOUT: Request timed out after 30 seconds")
            return None
        except httpx.ConnectError:
            print(f"\n🔌 CONNECTION ERROR: Could not connect to {BASE_URL}")
            print("Make sure the server is running on http://localhost:8000")
            return None
        except Exception as e:
            print(f"\n💥 ERROR: {e}")
            return None

async def test_health_check():
    """Test the health check endpoint"""
    print("\n🏥 Testing Health Check")
    print("=" * 30)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health", timeout=10.0)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📝 Response: {json.dumps(data, indent=2)}")
                print("✅ Health check passed")
                return True
            else:
                print(f"❌ Health check failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

async def main():
    """Main test function"""
    print("🧪 Chat Inquiry API Test Suite")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Target URL: {BASE_URL}")
    
    # Test health check first
    health_ok = await test_health_check()
    
    if not health_ok:
        print("\n❌ Health check failed. Please check if the server is running.")
        return
    
    # Test creating inquiry
    inquiry_id = await test_create_inquiry()
    
    if inquiry_id:
        print(f"\n🎉 Test completed successfully!")
        print(f"📋 Created inquiry ID: {inquiry_id}")
    else:
        print(f"\n💔 Test failed!")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("Starting Chat Inquiry API Test...")
    print("Make sure the server is running on http://localhost:8000")
    print("Press Ctrl+C to cancel\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Test cancelled by user")
    except Exception as e:
        print(f"\n\n💥 Test execution failed: {e}")

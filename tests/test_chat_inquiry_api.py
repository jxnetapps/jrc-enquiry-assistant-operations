import asyncio
import httpx
import json
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
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

async def test_chat_inquiry_api():
    """Test the chat inquiry API endpoints"""
    
    async with httpx.AsyncClient() as client:
        print("🚀 Testing Chat Inquiry API")
        print("=" * 50)
        
        # Test 1: Create a new chat inquiry
        print("\n1. Testing POST /api/chat-inquiry")
        try:
            response = await client.post(
                f"{BASE_URL}/api/chat-inquiry",
                json=TEST_DATA,
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                inquiry_id = response.json().get("data", {}).get("inquiry_id")
                print(f"✅ Inquiry created successfully with ID: {inquiry_id}")
                
                # Test 2: Get the created inquiry
                print(f"\n2. Testing GET /api/chat-inquiry/{inquiry_id}")
                response = await client.get(
                    f"{BASE_URL}/api/chat-inquiry/{inquiry_id}",
                    timeout=30.0
                )
                
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.json()}")
                
                if response.status_code == 200:
                    print("✅ Inquiry retrieved successfully")
                    
                    # Test 3: Update the inquiry
                    print(f"\n3. Testing PUT /api/chat-inquiry/{inquiry_id}")
                    update_data = {
                        "status": "contacted",
                        "firstName": "Agarwal Updated"
                    }
                    
                    response = await client.put(
                        f"{BASE_URL}/api/chat-inquiry/{inquiry_id}",
                        json=update_data,
                        timeout=30.0
                    )
                    
                    print(f"Status Code: {response.status_code}")
                    print(f"Response: {response.json()}")
                    
                    if response.status_code == 200:
                        print("✅ Inquiry updated successfully")
                    
                    # Test 4: Search inquiries
                    print(f"\n4. Testing POST /api/chat-inquiry/search")
                    search_data = {
                        "parentType": "New Parent",
                        "skip": 0,
                        "limit": 10
                    }
                    
                    response = await client.post(
                        f"{BASE_URL}/api/chat-inquiry/search",
                        json=search_data,
                        timeout=30.0
                    )
                    
                    print(f"Status Code: {response.status_code}")
                    print(f"Response: {response.json()}")
                    
                    if response.status_code == 200:
                        print("✅ Search completed successfully")
                    
                    # Test 5: Get inquiry by email
                    print(f"\n5. Testing GET /api/chat-inquiry/by-email/{TEST_DATA['email']}")
                    response = await client.get(
                        f"{BASE_URL}/api/chat-inquiry/by-email/{TEST_DATA['email']}",
                        timeout=30.0
                    )
                    
                    print(f"Status Code: {response.status_code}")
                    print(f"Response: {response.json()}")
                    
                    if response.status_code == 200:
                        print("✅ Inquiry found by email")
                    
                    # Test 6: Get inquiry by mobile
                    print(f"\n6. Testing GET /api/chat-inquiry/by-mobile/{TEST_DATA['mobile']}")
                    response = await client.get(
                        f"{BASE_URL}/api/chat-inquiry/by-mobile/{TEST_DATA['mobile']}",
                        timeout=30.0
                    )
                    
                    print(f"Status Code: {response.status_code}")
                    print(f"Response: {response.json()}")
                    
                    if response.status_code == 200:
                        print("✅ Inquiry found by mobile")
                    
                    # Test 7: Get statistics
                    print(f"\n7. Testing GET /api/chat-inquiry/stats")
                    response = await client.get(
                        f"{BASE_URL}/api/chat-inquiry/stats",
                        timeout=30.0
                    )
                    
                    print(f"Status Code: {response.status_code}")
                    print(f"Response: {response.json()}")
                    
                    if response.status_code == 200:
                        print("✅ Statistics retrieved successfully")
                    
                    # Test 8: Delete the inquiry
                    print(f"\n8. Testing DELETE /api/chat-inquiry/{inquiry_id}")
                    response = await client.delete(
                        f"{BASE_URL}/api/chat-inquiry/{inquiry_id}",
                        timeout=30.0
                    )
                    
                    print(f"Status Code: {response.status_code}")
                    print(f"Response: {response.json()}")
                    
                    if response.status_code == 200:
                        print("✅ Inquiry deleted successfully")
                
            else:
                print("❌ Failed to create inquiry")
                
        except Exception as e:
            print(f"❌ Error during testing: {e}")
        
        print("\n" + "=" * 50)
        print("🏁 Testing completed")

async def test_validation_errors():
    """Test validation errors"""
    
    async with httpx.AsyncClient() as client:
        print("\n🔍 Testing Validation Errors")
        print("=" * 50)
        
        # Test with invalid data
        invalid_data = {
            "parentType": "Invalid Type",
            "schoolType": "Day School",
            "firstName": "",  # Empty name
            "mobile": "123",  # Invalid mobile
            "email": "invalid-email",  # Invalid email
            "city": "6987",
            "childName": "Janith",
            "grade": "MYP 4",
            "academicYear": "invalid-year",  # Invalid year format
            "dateOfBirth": "invalid-date",  # Invalid date format
            "schoolName": "Edify"
        }
        
        print("\n1. Testing with invalid data")
        try:
            response = await client.post(
                f"{BASE_URL}/api/chat-inquiry",
                json=invalid_data,
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 422:  # Validation error
                print("✅ Validation errors caught correctly")
            else:
                print("❌ Validation errors not caught")
                
        except Exception as e:
            print(f"❌ Error during validation testing: {e}")

if __name__ == "__main__":
    print("Starting Chat Inquiry API Tests...")
    print("Make sure the server is running on http://localhost:8000")
    print("Press Ctrl+C to cancel")
    
    try:
        # Run the tests
        asyncio.run(test_chat_inquiry_api())
        asyncio.run(test_validation_errors())
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Test execution failed: {e}")

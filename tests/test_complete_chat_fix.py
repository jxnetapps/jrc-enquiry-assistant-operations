#!/usr/bin/env python3
"""
Complete test to verify the chat flow fix with session persistence.
"""

import os
import sys
import logging
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_api_chat_flow():
    """Test the complete chat flow through the API"""
    print("Testing API Chat Flow")
    print("=" * 50)
    
    # Set to pre_trained mode
    Config.CHAT_BEHAVIOR = "pre_trained"
    
    base_url = "http://localhost:8000"
    user_id = "api_test_user"
    
    # Test messages
    test_messages = [
        "Hello",  # Should ask about parent type
        "New Parent",  # Should ask about school type
        "Day",  # Should ask for name
        "John Doe",  # Should ask for mobile
        "1234567890",  # Should ask if they want to know more
        "Yes",  # Should allow knowledge queries
    ]
    
    try:
        # Login first
        print("1. Logging in...")
        login_response = requests.post(f"{base_url}/api/login", json={
            "username": "admin",
            "password": "admin"
        })
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed: {login_response.status_code}")
            return False
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("   ✅ Login successful")
        
        # Test each message
        for i, message in enumerate(test_messages):
            print(f"\n{i+1}. Sending: '{message}'")
            
            response = requests.post(f"{base_url}/api/chat", 
                                   json={"message": message, "user_id": user_id},
                                   headers=headers)
            
            if response.status_code != 200:
                print(f"   ❌ Request failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
            
            data = response.json()
            print(f"   State: {data.get('state')}")
            print(f"   Response: {data.get('response')[:60]}...")
            print(f"   Options: {data.get('options', [])}")
            print(f"   Collected data: {data.get('collected_data', {})}")
            
            # Check if we're progressing through states
            if i == 0 and data.get('state') != 'parent_type':
                print(f"   ❌ Expected 'parent_type', got '{data.get('state')}'")
                return False
            elif i == 1 and data.get('state') != 'school_type':
                print(f"   ❌ Expected 'school_type', got '{data.get('state')}'")
                return False
            elif i == 2 and data.get('state') != 'collect_name':
                print(f"   ❌ Expected 'collect_name', got '{data.get('state')}'")
                return False
            elif i == 3 and data.get('state') != 'collect_mobile':
                print(f"   ❌ Expected 'collect_mobile', got '{data.get('state')}'")
                return False
            elif i == 4 and data.get('state') != 'know_more':
                print(f"   ❌ Expected 'know_more', got '{data.get('state')}'")
                return False
            elif i == 5 and data.get('state') != 'knowledge_query':
                print(f"   ❌ Expected 'knowledge_query', got '{data.get('state')}'")
                return False
        
        print("\n   ✅ All API requests successful!")
        return True
        
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        return False

def test_session_reset_api():
    """Test session reset through API"""
    print("\n" + "=" * 50)
    print("Testing Session Reset API")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    user_id = "reset_test_user"
    
    try:
        # Login
        login_response = requests.post(f"{base_url}/api/login", json={
            "username": "admin",
            "password": "admin"
        })
        
        if login_response.status_code != 200:
            print("   ❌ Login failed")
            return False
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Start conversation
        print("1. Starting conversation...")
        response = requests.post(f"{base_url}/api/chat", 
                               json={"message": "Hello", "user_id": user_id},
                               headers=headers)
        data = response.json()
        print(f"   State: {data.get('state')}")
        
        # Advance conversation
        print("2. Advancing conversation...")
        response = requests.post(f"{base_url}/api/chat", 
                               json={"message": "New Parent", "user_id": user_id},
                               headers=headers)
        data = response.json()
        print(f"   State: {data.get('state')}")
        
        # Reset session
        print("3. Resetting session...")
        reset_response = requests.post(f"{base_url}/api/chat/reset", 
                                     params={"user_id": user_id},
                                     headers=headers)
        
        if reset_response.status_code != 200:
            print(f"   ❌ Reset failed: {reset_response.status_code}")
            return False
        
        # Check if session is reset
        print("4. Checking if session is reset...")
        response = requests.post(f"{base_url}/api/chat", 
                               json={"message": "Hello again", "user_id": user_id},
                               headers=headers)
        data = response.json()
        print(f"   State: {data.get('state')}")
        
        if data.get('state') == 'parent_type':
            print("   ✅ Session reset successful!")
            return True
        else:
            print(f"   ❌ Session reset failed. Expected 'parent_type', got '{data.get('state')}'")
            return False
        
    except Exception as e:
        print(f"   ❌ Session reset test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Complete Chat Fix Test")
    print("=" * 50)
    
    # Wait for web app to be ready
    print("Waiting for web application to be ready...")
    time.sleep(2)
    
    tests = [
        ("API Chat Flow", test_api_chat_flow),
        ("Session Reset API", test_session_reset_api),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The chat flow fix is working correctly.")
        print("The issue with getting stuck on 'Are you a new or existing parent?' is FIXED!")
    else:
        print("❌ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test script for auto-login and answer storage functionality.
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

def test_auto_login():
    """Test auto-login functionality"""
    print("Testing Auto-Login")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test auto-login endpoint
        response = requests.post(f"{base_url}/api/auto-login")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Auto-login successful")
            print(f"   Username: {data.get('username')}")
            print(f"   Welcome message: {data.get('welcome_message')}")
            print(f"   Token: {data.get('access_token')[:20]}...")
            return data.get('access_token')
        else:
            print(f"❌ Auto-login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Auto-login test failed: {e}")
        return None

def test_chat_with_storage(token):
    """Test chat functionality with answer storage"""
    print("\n" + "=" * 50)
    print("Testing Chat with Answer Storage")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    headers = {"Authorization": f"Bearer {token}"}
    user_id = "test_storage_user"
    
    # Test messages for pre_trained flow
    test_messages = [
        "Hello",  # Should trigger parent type question
        "New Parent",  # Should move to school type
        "Day",  # Should move to name collection
        "John Doe",  # Should move to mobile collection
        "1234567890",  # Should move to know more
    ]
    
    try:
        for i, message in enumerate(test_messages):
            print(f"\n{i+1}. Sending: '{message}'")
            
            response = requests.post(f"{base_url}/api/chat", 
                                   json={"message": message, "user_id": user_id},
                                   headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   State: {data.get('state')}")
                print(f"   Response: {data.get('response')[:60]}...")
                print(f"   Collected data: {data.get('collected_data', {})}")
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                return False
        
        print("\n✅ Chat flow completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False

def test_answer_storage_api(token):
    """Test answer storage API endpoints"""
    print("\n" + "=" * 50)
    print("Testing Answer Storage API")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test get all answers
        print("1. Testing get all answers...")
        response = requests.get(f"{base_url}/api/answers", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Retrieved {data.get('count', 0)} stored answers")
            
            # Show first few answers
            answers = data.get('answers', [])
            for i, answer in enumerate(answers[:3]):
                print(f"   Answer {i+1}: {answer.get('name', 'N/A')} - {answer.get('parent_type', 'N/A')}")
        else:
            print(f"   ❌ Failed to get answers: {response.status_code}")
            return False
        
        # Test get specific user answers
        print("\n2. Testing get specific user answers...")
        response = requests.get(f"{base_url}/api/answers/admin/test_storage_user", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Retrieved user-specific answers")
            print(f"   Data: {data.get('answers', {})}")
        else:
            print(f"   ❌ Failed to get user answers: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Answer storage API test failed: {e}")
        return False

def test_welcome_message():
    """Test that welcome message is displayed"""
    print("\n" + "=" * 50)
    print("Testing Welcome Message")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test auto-login and check welcome message
        response = requests.post(f"{base_url}/api/auto-login")
        
        if response.status_code == 200:
            data = response.json()
            welcome_msg = data.get('welcome_message')
            
            if welcome_msg == "Hello, Welcome to Edify Education!!!":
                print("✅ Welcome message is correct!")
                print(f"   Message: {welcome_msg}")
                return True
            else:
                print(f"❌ Welcome message is incorrect: {welcome_msg}")
                return False
        else:
            print(f"❌ Auto-login failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Welcome message test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Auto-Login and Answer Storage Test")
    print("=" * 60)
    
    # Wait for web app to be ready
    print("Waiting for web application to be ready...")
    time.sleep(3)
    
    tests = [
        ("Welcome Message", test_welcome_message),
        ("Auto-Login", test_auto_login),
    ]
    
    results = []
    token = None
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_name == "Auto-Login":
                token = test_func()
                result = token is not None
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Test chat and storage if auto-login succeeded
    if token:
        chat_tests = [
            ("Chat with Storage", lambda: test_chat_with_storage(token)),
            ("Answer Storage API", lambda: test_answer_storage_api(token)),
        ]
        
        for test_name, test_func in chat_tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with error: {e}")
                results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Auto-login and answer storage are working correctly.")
    else:
        print("❌ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()

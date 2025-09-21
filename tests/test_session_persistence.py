#!/usr/bin/env python3
"""
Test script to verify session persistence fix.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from chatbot.chat_interface import ChatBot

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_session_persistence():
    """Test that sessions persist across ChatBot instances"""
    print("Testing Session Persistence")
    print("=" * 50)
    
    # Set to pre_trained mode
    Config.CHAT_BEHAVIOR = "pre_trained"
    
    user_id = "test_persistence"
    
    # Create first ChatBot instance
    print("1. Creating first ChatBot instance...")
    chatbot1 = ChatBot()
    
    # Start conversation
    print("2. Starting conversation...")
    response1 = chatbot1.chat("Hello", user_id)
    print(f"   Response: {response1.get('response')[:50]}...")
    print(f"   State: {response1.get('state')}")
    
    # Select option
    print("3. Selecting 'New Parent'...")
    response2 = chatbot1.chat("New Parent", user_id)
    print(f"   Response: {response2.get('response')[:50]}...")
    print(f"   State: {response2.get('state')}")
    print(f"   Collected data: {response2.get('collected_data')}")
    
    # Create second ChatBot instance (simulating new request)
    print("4. Creating second ChatBot instance (new request)...")
    chatbot2 = ChatBot()
    
    # Continue conversation
    print("5. Continuing conversation with 'Day'...")
    response3 = chatbot2.chat("Day", user_id)
    print(f"   Response: {response3.get('response')[:50]}...")
    print(f"   State: {response3.get('state')}")
    print(f"   Collected data: {response3.get('collected_data')}")
    
    # Check if we're still in the right state
    if response3.get('state') == 'collect_name':
        print("   ✅ SUCCESS: Session persisted correctly!")
        return True
    else:
        print(f"   ❌ FAILED: Expected 'collect_name', got '{response3.get('state')}'")
        return False

def test_multiple_users():
    """Test that different users have separate sessions"""
    print("\n" + "=" * 50)
    print("Testing Multiple Users")
    print("=" * 50)
    
    Config.CHAT_BEHAVIOR = "pre_trained"
    
    user1 = "user1"
    user2 = "user2"
    
    chatbot = ChatBot()
    
    # User 1 starts conversation
    print("1. User1 starts conversation...")
    response1 = chatbot.chat("Hello", user1)
    print(f"   User1 state: {response1.get('state')}")
    
    # User 2 starts conversation
    print("2. User2 starts conversation...")
    response2 = chatbot.chat("Hello", user2)
    print(f"   User2 state: {response2.get('state')}")
    
    # User 1 continues
    print("3. User1 selects 'New Parent'...")
    response3 = chatbot.chat("New Parent", user1)
    print(f"   User1 state: {response3.get('state')}")
    
    # User 2 should still be in initial state
    print("4. User2 should still be in parent_type state...")
    response4 = chatbot.chat("Hello again", user2)
    print(f"   User2 state: {response4.get('state')}")
    
    if response3.get('state') == 'school_type' and response4.get('state') == 'parent_type':
        print("   ✅ SUCCESS: Users have separate sessions!")
        return True
    else:
        print("   ❌ FAILED: Users don't have separate sessions!")
        return False

def test_session_reset():
    """Test session reset functionality"""
    print("\n" + "=" * 50)
    print("Testing Session Reset")
    print("=" * 50)
    
    Config.CHAT_BEHAVIOR = "pre_trained"
    
    user_id = "test_reset"
    chatbot = ChatBot()
    
    # Start conversation and advance it
    print("1. Starting and advancing conversation...")
    chatbot.chat("Hello", user_id)
    chatbot.chat("New Parent", user_id)
    chatbot.chat("Day", user_id)
    
    # Check state
    response = chatbot.chat("John Doe", user_id)
    print(f"   State before reset: {response.get('state')}")
    print(f"   Collected data: {response.get('collected_data')}")
    
    # Reset session
    print("2. Resetting session...")
    chatbot.reset_chat_session(user_id)
    
    # Check state after reset
    response = chatbot.chat("Hello again", user_id)
    print(f"   State after reset: {response.get('state')}")
    print(f"   Collected data: {response.get('collected_data')}")
    
    if response.get('state') == 'parent_type' and not response.get('collected_data'):
        print("   ✅ SUCCESS: Session reset correctly!")
        return True
    else:
        print("   ❌ FAILED: Session reset didn't work!")
        return False

def main():
    """Main test function"""
    print("Session Persistence Test")
    print("=" * 50)
    
    tests = [
        ("Session Persistence", test_session_persistence),
        ("Multiple Users", test_multiple_users),
        ("Session Reset", test_session_reset),
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
        print("🎉 All tests passed! Session persistence is working correctly.")
    else:
        print("❌ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()

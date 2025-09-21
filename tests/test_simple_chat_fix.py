#!/usr/bin/env python3
"""
Simple test to verify the chat flow fix without web app.
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

def test_chat_flow_with_persistence():
    """Test the complete chat flow with session persistence"""
    print("Testing Chat Flow with Session Persistence")
    print("=" * 60)
    
    # Set to pre_trained mode
    Config.CHAT_BEHAVIOR = "pre_trained"
    
    user_id = "test_persistence_fix"
    
    # Test messages that simulate clicking option buttons
    test_messages = [
        "Hello",  # Should trigger initial state
        "New Parent",  # Should move to school type
        "Day",  # Should move to collect name
        "John Doe",  # Should move to collect mobile
        "1234567890",  # Should move to know more
        "Yes",  # Should move to knowledge query
    ]
    
    print("Testing with multiple ChatBot instances (simulating web requests)...")
    print("-" * 60)
    
    for i, message in enumerate(test_messages):
        print(f"\nStep {i+1}: Sending '{message}'")
        
        # Create a new ChatBot instance (simulating new web request)
        chatbot = ChatBot()
        response = chatbot.chat(message, user_id)
        
        print(f"  State: {response.get('state')}")
        print(f"  Response: {response.get('response')[:60]}...")
        print(f"  Options: {response.get('options', [])}")
        print(f"  Collected data: {response.get('collected_data', {})}")
        
        # Check if we're progressing correctly
        expected_states = [
            'parent_type',    # After "Hello"
            'school_type',    # After "New Parent"
            'collect_name',   # After "Day"
            'collect_mobile', # After "John Doe"
            'know_more',      # After "1234567890"
            'knowledge_query' # After "Yes"
        ]
        
        if i < len(expected_states):
            expected = expected_states[i]
            actual = response.get('state')
            if actual == expected:
                print(f"  ✅ Correct state transition: {actual}")
            else:
                print(f"  ❌ Wrong state! Expected: {expected}, Got: {actual}")
                return False
        
        # Check if we're stuck in parent_type
        if i > 0 and response.get('state') == 'parent_type':
            print(f"  ❌ ERROR: Got stuck in parent_type state at step {i+1}!")
            return False
    
    print("\n" + "=" * 60)
    print("✅ SUCCESS: Chat flow with session persistence is working correctly!")
    print("The issue with getting stuck on 'Are you a new or existing parent?' is FIXED!")
    return True

def test_multiple_users_separate_sessions():
    """Test that different users have separate sessions"""
    print("\n" + "=" * 60)
    print("Testing Multiple Users with Separate Sessions")
    print("=" * 60)
    
    Config.CHAT_BEHAVIOR = "pre_trained"
    
    user1 = "user1_test"
    user2 = "user2_test"
    
    # User 1 starts conversation
    print("1. User1 starts conversation...")
    chatbot1 = ChatBot()
    response1 = chatbot1.chat("Hello", user1)
    print(f"   User1 state: {response1.get('state')}")
    
    # User 2 starts conversation
    print("2. User2 starts conversation...")
    chatbot2 = ChatBot()
    response2 = chatbot2.chat("Hello", user2)
    print(f"   User2 state: {response2.get('state')}")
    
    # User 1 continues
    print("3. User1 selects 'New Parent'...")
    chatbot3 = ChatBot()
    response3 = chatbot3.chat("New Parent", user1)
    print(f"   User1 state: {response3.get('state')}")
    
    # User 2 should still be in initial state
    print("4. User2 should still be in parent_type state...")
    chatbot4 = ChatBot()
    response4 = chatbot4.chat("Hello again", user2)
    print(f"   User2 state: {response4.get('state')}")
    
    if response3.get('state') == 'school_type' and response4.get('state') == 'parent_type':
        print("   ✅ SUCCESS: Users have separate sessions!")
        return True
    else:
        print("   ❌ FAILED: Users don't have separate sessions!")
        return False

def main():
    """Main test function"""
    print("Simple Chat Flow Fix Test")
    print("=" * 60)
    
    tests = [
        ("Chat Flow with Persistence", test_chat_flow_with_persistence),
        ("Multiple Users Separate Sessions", test_multiple_users_separate_sessions),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            import traceback
            traceback.print_exc()
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
        print("🎉 All tests passed! The chat flow fix is working correctly.")
        print("The issue with getting stuck on 'Are you a new or existing parent?' is FIXED!")
    else:
        print("❌ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()

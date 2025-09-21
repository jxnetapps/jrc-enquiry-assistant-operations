#!/usr/bin/env python3
"""
Test script to verify the chat flow fix.
Tests the pre-trained mode with option selections.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from chatbot.chat_interface import ChatBot

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_chat_flow():
    """Test the complete chat flow with option selections"""
    print("Testing Chat Flow Fix")
    print("=" * 50)
    
    # Set to pre_trained mode
    Config.CHAT_BEHAVIOR = "pre_trained"
    
    try:
        chatbot = ChatBot()
        user_id = "test_user_flow"
        
        # Test messages that simulate clicking option buttons
        test_messages = [
            "Hello",  # Should trigger initial state
            "New Parent",  # Should move to school type
            "Day",  # Should move to collect name
            "John Doe",  # Should move to collect mobile
            "1234567890",  # Should move to know more
            "Yes",  # Should move to knowledge query
            "What are the school timings?"  # Should use knowledge base
        ]
        
        print("Testing option selection flow...")
        print("-" * 30)
        
        for i, message in enumerate(test_messages):
            print(f"\nStep {i+1}: Sending '{message}'")
            response = chatbot.chat(message, user_id)
            
            print(f"  State: {response.get('state')}")
            print(f"  Response: {response.get('response')[:80]}...")
            print(f"  Options: {response.get('options', [])}")
            print(f"  Collected data: {response.get('collected_data', {})}")
            
            # Check if we're stuck in the same state
            if i > 0 and response.get('state') == 'parent_type':
                print("  ❌ ERROR: Stuck in parent_type state!")
                return False
            
            if response.get('conversation_complete'):
                print("  ✅ Conversation completed!")
                break
        
        print("\n" + "=" * 50)
        print("✅ Chat flow test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Chat flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_option_matching():
    """Test different option matching scenarios"""
    print("\nTesting Option Matching")
    print("=" * 50)
    
    from chatbot.chat_states import PreTrainedChatFlow
    
    flow = PreTrainedChatFlow()
    user_id = "test_matching"
    
    # Test different ways users might respond
    test_cases = [
        ("New Parent", "parent_type"),
        ("new parent", "parent_type"),
        ("new", "parent_type"),
        ("1", "parent_type"),
        ("Existing Parent", "parent_type"),
        ("existing parent", "parent_type"),
        ("existing", "parent_type"),
        ("2", "parent_type"),
    ]
    
    print("Testing parent type matching...")
    for message, expected_state in test_cases:
        # Reset session for each test
        flow.reset_session(user_id)
        
        # Send initial message to get to parent_type state
        flow.process_message(user_id, "hello")
        
        # Send the test message
        response = flow.process_message(user_id, message)
        actual_state = response.get('state')
        
        status = "✅" if actual_state != "parent_type" else "❌"
        print(f"  {status} '{message}' -> State: {actual_state} (Expected: not parent_type)")
    
    return True

def main():
    """Main test function"""
    print("Chat Flow Fix Test")
    print("=" * 50)
    
    # Test option matching
    matching_success = test_option_matching()
    
    # Test complete flow
    flow_success = test_chat_flow()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(f"Option Matching: {'✅ PASS' if matching_success else '❌ FAIL'}")
    print(f"Chat Flow: {'✅ PASS' if flow_success else '❌ FAIL'}")
    
    if matching_success and flow_success:
        print("\n🎉 All tests passed! The chat flow fix is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()

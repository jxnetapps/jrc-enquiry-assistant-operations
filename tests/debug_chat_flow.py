#!/usr/bin/env python3
"""
Debug script to investigate the chat flow issue.
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
from chatbot.chat_states import PreTrainedChatFlow, ChatState

# Setup detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def debug_chat_flow():
    """Debug the chat flow step by step"""
    print("Debug Chat Flow")
    print("=" * 50)
    
    # Set to pre_trained mode
    Config.CHAT_BEHAVIOR = "pre_trained"
    
    flow = PreTrainedChatFlow()
    user_id = "debug_user"
    
    # Test step by step
    print("\n1. Initial message:")
    response1 = flow.process_message(user_id, "Hello")
    print(f"   State: {response1.get('state')}")
    print(f"   Response: {response1.get('response')}")
    print(f"   Options: {response1.get('options')}")
    
    # Check session state
    session = flow.get_or_create_session(user_id)
    print(f"   Session state: {session.state}")
    print(f"   Collected data: {session.collected_data}")
    
    print("\n2. Select 'New Parent':")
    response2 = flow.process_message(user_id, "New Parent")
    print(f"   State: {response2.get('state')}")
    print(f"   Response: {response2.get('response')}")
    print(f"   Options: {response2.get('options')}")
    
    # Check session state again
    session = flow.get_or_create_session(user_id)
    print(f"   Session state: {session.state}")
    print(f"   Collected data: {session.collected_data}")
    
    print("\n3. Select 'New Parent' again (should stay in school_type):")
    response3 = flow.process_message(user_id, "New Parent")
    print(f"   State: {response3.get('state')}")
    print(f"   Response: {response3.get('response')}")
    print(f"   Options: {response3.get('options')}")
    
    # Check session state again
    session = flow.get_or_create_session(user_id)
    print(f"   Session state: {session.state}")
    print(f"   Collected data: {session.collected_data}")

def test_session_persistence():
    """Test if sessions are being persisted correctly"""
    print("\n" + "=" * 50)
    print("Testing Session Persistence")
    print("=" * 50)
    
    flow = PreTrainedChatFlow()
    user_id = "persistence_test"
    
    # Create a session and advance it
    print("1. Creating session and advancing to school_type...")
    flow.process_message(user_id, "Hello")
    flow.process_message(user_id, "New Parent")
    
    session = flow.get_or_create_session(user_id)
    print(f"   Session state: {session.state}")
    print(f"   Should be: {ChatState.SCHOOL_TYPE}")
    print(f"   Match: {session.state == ChatState.SCHOOL_TYPE}")
    
    # Test with a new flow instance (simulating web app restart)
    print("\n2. Creating new flow instance...")
    flow2 = PreTrainedChatFlow()
    session2 = flow2.get_or_create_session(user_id)
    print(f"   New session state: {session2.state}")
    print(f"   Should be: {ChatState.INITIAL}")
    print(f"   Match: {session2.state == ChatState.INITIAL}")

def test_state_transitions():
    """Test individual state transitions"""
    print("\n" + "=" * 50)
    print("Testing State Transitions")
    print("=" * 50)
    
    flow = PreTrainedChatFlow()
    user_id = "transition_test"
    
    # Test each transition
    states_to_test = [
        ("Hello", ChatState.INITIAL, ChatState.PARENT_TYPE),
        ("New Parent", ChatState.PARENT_TYPE, ChatState.SCHOOL_TYPE),
        ("Day", ChatState.SCHOOL_TYPE, ChatState.COLLECT_NAME),
        ("John Doe", ChatState.COLLECT_NAME, ChatState.COLLECT_MOBILE),
        ("1234567890", ChatState.COLLECT_MOBILE, ChatState.KNOW_MORE),
        ("Yes", ChatState.KNOW_MORE, ChatState.KNOWLEDGE_QUERY),
    ]
    
    for message, from_state, to_state in states_to_test:
        print(f"\nTesting: '{message}' ({from_state.value} -> {to_state.value})")
        
        # Reset session
        flow.reset_session(user_id)
        
        # Get to the from_state
        if from_state != ChatState.INITIAL:
            flow.process_message(user_id, "Hello")
            if from_state == ChatState.SCHOOL_TYPE:
                flow.process_message(user_id, "New Parent")
            elif from_state == ChatState.COLLECT_NAME:
                flow.process_message(user_id, "Hello")
                flow.process_message(user_id, "New Parent")
                flow.process_message(user_id, "Day")
            # Add more conditions as needed
        
        # Check current state
        session = flow.get_or_create_session(user_id)
        print(f"   Current state: {session.state}")
        print(f"   Expected from: {from_state}")
        print(f"   State match: {session.state == from_state}")
        
        if session.state == from_state:
            # Send the message
            response = flow.process_message(user_id, message)
            session = flow.get_or_create_session(user_id)
            print(f"   New state: {session.state}")
            print(f"   Expected to: {to_state}")
            print(f"   Transition success: {session.state == to_state}")
        else:
            print(f"   ❌ Wrong starting state!")

def main():
    """Main debug function"""
    print("Chat Flow Debug Analysis")
    print("=" * 50)
    
    debug_chat_flow()
    test_session_persistence()
    test_state_transitions()
    
    print("\n" + "=" * 50)
    print("Debug Complete")

if __name__ == "__main__":
    main()

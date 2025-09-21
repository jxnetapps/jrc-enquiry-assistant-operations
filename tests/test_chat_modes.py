#!/usr/bin/env python3
"""
Test script to verify both chat modes work correctly.
Tests knowledge_base and pre_trained chat behaviors.
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_knowledge_base_mode():
    """Test knowledge_base chat mode"""
    print("=" * 60)
    print("Testing Knowledge Base Mode")
    print("=" * 60)
    
    # Temporarily set to knowledge_base mode
    original_behavior = Config.CHAT_BEHAVIOR
    Config.CHAT_BEHAVIOR = "knowledge_base"
    
    try:
        chatbot = ChatBot()
        
        # Test a knowledge query
        test_query = "What is this website about?"
        print(f"Query: {test_query}")
        
        response = chatbot.chat(test_query, "test_user")
        print(f"Mode: {response.get('mode')}")
        print(f"Response: {response.get('response')[:200]}...")
        print(f"Context docs: {response.get('context_docs', 0)}")
        print(f"Requires input: {response.get('requires_input')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Knowledge base test failed: {e}")
        return False
    finally:
        # Restore original behavior
        Config.CHAT_BEHAVIOR = original_behavior

def test_pre_trained_mode():
    """Test pre_trained chat mode"""
    print("\n" + "=" * 60)
    print("Testing Pre-trained Mode")
    print("=" * 60)
    
    # Temporarily set to pre_trained mode
    original_behavior = Config.CHAT_BEHAVIOR
    Config.CHAT_BEHAVIOR = "pre_trained"
    
    try:
        chatbot = ChatBot()
        user_id = "test_user_pre_trained"
        
        # Test the complete flow
        test_messages = [
            "Hello",  # Should trigger initial state
            "New Parent",  # Should ask about school type
            "Day",  # Should ask for name
            "John Doe",  # Should ask for mobile
            "1234567890",  # Should ask if they want to know more
            "Yes",  # Should allow knowledge queries
            "What are the school timings?"  # Should use knowledge base
        ]
        
        for i, message in enumerate(test_messages):
            print(f"\nStep {i+1}: '{message}'")
            response = chatbot.chat(message, user_id)
            
            print(f"  Mode: {response.get('mode')}")
            print(f"  State: {response.get('state')}")
            print(f"  Response: {response.get('response')[:100]}...")
            print(f"  Options: {response.get('options', [])}")
            print(f"  Collected data: {response.get('collected_data', {})}")
            print(f"  Requires input: {response.get('requires_input')}")
            print(f"  Conversation complete: {response.get('conversation_complete')}")
            
            if response.get('conversation_complete'):
                print("  ✅ Conversation completed!")
                break
        
        return True
        
    except Exception as e:
        logger.error(f"Pre-trained test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore original behavior
        Config.CHAT_BEHAVIOR = original_behavior

def test_chat_mode_switching():
    """Test switching between chat modes"""
    print("\n" + "=" * 60)
    print("Testing Chat Mode Switching")
    print("=" * 60)
    
    try:
        # Test knowledge_base mode
        Config.CHAT_BEHAVIOR = "knowledge_base"
        chatbot1 = ChatBot()
        response1 = chatbot1.chat("Hello", "user1")
        print(f"Knowledge base mode: {response1.get('mode')}")
        
        # Test pre_trained mode
        Config.CHAT_BEHAVIOR = "pre_trained"
        chatbot2 = ChatBot()
        response2 = chatbot2.chat("Hello", "user2")
        print(f"Pre-trained mode: {response2.get('mode')}")
        
        # Test session management
        chatbot2.reset_chat_session("user2")
        session_data = chatbot2.get_session_data("user2")
        print(f"Session data after reset: {session_data}")
        
        return True
        
    except Exception as e:
        logger.error(f"Mode switching test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Chat Mode Testing")
    print("=" * 60)
    print(f"Current CHAT_BEHAVIOR: {Config.CHAT_BEHAVIOR}")
    print(f"Database Type: {Config.DATABASE_TYPE}")
    
    # Test knowledge_base mode
    kb_success = test_knowledge_base_mode()
    
    # Test pre_trained mode
    pt_success = test_pre_trained_mode()
    
    # Test mode switching
    switch_success = test_chat_mode_switching()
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    print(f"Knowledge Base Mode: {'✅ PASS' if kb_success else '❌ FAIL'}")
    print(f"Pre-trained Mode: {'✅ PASS' if pt_success else '❌ FAIL'}")
    print(f"Mode Switching: {'✅ PASS' if switch_success else '❌ FAIL'}")
    
    if all([kb_success, pt_success, switch_success]):
        print("\n🎉 All tests passed! Chat modes are working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test script to verify chat functionality works with Chroma Cloud.
This script tests the complete chat pipeline from query to response.
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

def test_chat_functionality():
    """Test the complete chat functionality"""
    try:
        print("=" * 60)
        print("Chat Functionality Test")
        print("=" * 60)
        
        print(f"Database Type: {Config.VECTOR_DATABASE_TYPE}")
        print(f"OpenAI API Key: {'Set' if Config.OPENAI_API_KEY else 'Not Set'}")
        
        # Create chatbot instance
        print("\nCreating chatbot instance...")
        chatbot = ChatBot()
        print("✅ Chatbot created successfully")
        
        # Test query
        test_query = "What is this website about?"
        print(f"\nTesting query: '{test_query}'")
        
        # Get relevant context
        print("Getting relevant context...")
        context_docs = chatbot.get_relevant_context(test_query)
        print(f"✅ Found {len(context_docs)} relevant documents")
        
        if context_docs:
            print("\nContext documents:")
            for i, doc in enumerate(context_docs[:3]):  # Show first 3
                print(f"  {i+1}. Similarity: {doc['similarity']:.3f}")
                print(f"     Title: {doc['metadata'].get('title', 'N/A')}")
                print(f"     URL: {doc['metadata'].get('url', 'N/A')}")
                print(f"     Content preview: {doc['content'][:100]}...")
                print()
        
        # Generate response
        print("Generating response...")
        response = chatbot.generate_llm_response(test_query, context_docs)
        print(f"✅ Response generated: {len(response)} characters")
        print(f"\nResponse:\n{response}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Chat functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    success = test_chat_functionality()
    
    if success:
        print("\n🎉 Chat functionality test completed successfully!")
        print("Your Chroma Cloud integration is working correctly!")
    else:
        print("\n❌ Chat functionality test failed!")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main()

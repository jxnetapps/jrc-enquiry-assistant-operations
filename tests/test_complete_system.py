#!/usr/bin/env python3
"""
Complete system test for both chat modes and web application.
Tests the entire flow from configuration to API responses.
"""

import os
import sys
import time
import requests
import json
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

def test_configuration():
    """Test that configuration is properly loaded"""
    print("Testing Configuration...")
    print("-" * 30)
    
    print(f"Database Type: {Config.DATABASE_TYPE}")
    print(f"Chat Behavior: {Config.CHAT_BEHAVIOR}")
    print(f"OpenAI API Key: {'Set' if Config.OPENAI_API_KEY else 'Not Set'}")
    
    if Config.DATABASE_TYPE == "cloud":
        print(f"Chroma Cloud API Key: {'Set' if Config.CHROMA_CLOUD_API_KEY else 'Not Set'}")
        print(f"Chroma Cloud Tenant ID: {'Set' if Config.CHROMA_CLOUD_TENANT_ID else 'Not Set'}")
        print(f"Chroma Cloud Database ID: {'Set' if Config.CHROMA_CLOUD_DATABASE_ID else 'Not Set'}")
    
    return True

def test_chat_modes():
    """Test both chat modes programmatically"""
    print("\nTesting Chat Modes...")
    print("-" * 30)
    
    try:
        from chatbot.chat_interface import ChatBot
        
        # Test knowledge base mode
        print("Testing Knowledge Base Mode...")
        Config.CHAT_BEHAVIOR = "knowledge_base"
        chatbot_kb = ChatBot()
        response_kb = chatbot_kb.chat("Hello", "test_user_kb")
        print(f"  Mode: {response_kb.get('mode')}")
        print(f"  Response: {response_kb.get('response')[:100]}...")
        
        # Test pre-trained mode
        print("Testing Pre-trained Mode...")
        Config.CHAT_BEHAVIOR = "pre_trained"
        chatbot_pt = ChatBot()
        
        # Test the flow
        messages = ["Hello", "New Parent", "Day", "John Doe", "1234567890", "Yes"]
        for i, message in enumerate(messages):
            response = chatbot_pt.chat(message, "test_user_pt")
            print(f"  Step {i+1}: {response.get('state')} - {response.get('response')[:50]}...")
            if response.get('conversation_complete'):
                break
        
        print("✅ Chat modes test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Chat modes test failed: {e}")
        return False

def test_web_api():
    """Test the web API endpoints"""
    print("\nTesting Web API...")
    print("-" * 30)
    
    # Start web application
    print("Starting web application...")
    process = subprocess.Popen([sys.executable, "web_app.py"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    
    try:
        # Wait for startup
        time.sleep(10)
        
        # Test health endpoint
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health endpoint working")
                health_data = response.json()
                print(f"  Status: {health_data.get('status')}")
                print(f"  Version: {health_data.get('version')}")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
            return False
        
        # Test login (you'll need to implement this based on your auth system)
        print("Testing authentication...")
        try:
            login_data = {"username": "admin", "password": "admin"}
            login_response = requests.post("http://localhost:8000/api/login", 
                                         json=login_data, timeout=5)
            if login_response.status_code == 200:
                token_data = login_response.json()
                token = token_data.get('access_token')
                print("✅ Authentication working")
                
                # Test chat endpoint
                print("Testing chat endpoint...")
                headers = {"Authorization": f"Bearer {token}"}
                
                # Test knowledge base mode
                chat_data = {
                    "message": "Hello, what can you tell me?",
                    "user_id": "test_user"
                }
                chat_response = requests.post("http://localhost:8000/api/chat", 
                                            json=chat_data, 
                                            headers=headers, 
                                            timeout=10)
                
                if chat_response.status_code == 200:
                    chat_result = chat_response.json()
                    print("✅ Chat endpoint working")
                    print(f"  Mode: {chat_result.get('mode')}")
                    print(f"  Response: {chat_result.get('response')[:100]}...")
                else:
                    print(f"❌ Chat endpoint failed: {chat_response.status_code}")
                    print(f"  Error: {chat_response.text}")
                    return False
                
            else:
                print(f"❌ Authentication failed: {login_response.status_code}")
                print("Note: You may need to set up authentication credentials")
                return False
                
        except Exception as e:
            print(f"❌ API test error: {e}")
            return False
        
        return True
        
    finally:
        # Clean up
        print("Stopping web application...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

def test_database_connection():
    """Test database connection"""
    print("\nTesting Database Connection...")
    print("-" * 30)
    
    try:
        from database.db_factory import DatabaseFactory
        
        vector_db = DatabaseFactory.create_vector_db()
        stats = vector_db.get_collection_stats()
        print(f"✅ Database connected successfully")
        print(f"  Collection stats: {stats}")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main test function"""
    print("Complete System Test")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Database Connection", test_database_connection),
        ("Chat Modes", test_chat_modes),
        ("Web API", test_web_api),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is working correctly.")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    main()

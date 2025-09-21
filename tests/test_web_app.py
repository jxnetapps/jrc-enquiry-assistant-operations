#!/usr/bin/env python3
"""
Simple test script to verify the web application starts correctly.
"""

import os
import sys
import time
import requests
import subprocess
import signal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_web_app():
    """Test that the web application starts and responds correctly"""
    print("Testing Web Application...")
    print("=" * 50)
    
    # Start the web application
    print("Starting web application...")
    process = subprocess.Popen([sys.executable, "web_app.py"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    
    try:
        # Wait for the app to start
        print("Waiting for application to start...")
        time.sleep(10)
        
        # Test if the app is running
        try:
            response = requests.get("http://localhost:8000", timeout=5)
            if response.status_code == 200:
                print("✅ Web application is running successfully!")
                print(f"Status Code: {response.status_code}")
                print(f"Response Length: {len(response.text)} characters")
                
                # Test health endpoint
                health_response = requests.get("http://localhost:8000/health", timeout=5)
                if health_response.status_code == 200:
                    print("✅ Health endpoint is working!")
                    print(f"Health Response: {health_response.json()}")
                else:
                    print("❌ Health endpoint failed")
                
                return True
            else:
                print(f"❌ Web application returned status code: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to web application: {e}")
            return False
            
    finally:
        # Clean up - terminate the process
        print("Stopping web application...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("Web application stopped.")

def main():
    """Main test function"""
    print("Web Application Test")
    print("=" * 50)
    
    # Check if required dependencies are installed
    try:
        import fastapi
        import uvicorn
        import requests
        print("✅ Required dependencies are installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False
    
    # Test the web application
    success = test_web_app()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Web application test passed!")
        print("The application is ready to use.")
    else:
        print("❌ Web application test failed!")
        print("Please check the error messages above.")
    
    return success

if __name__ == "__main__":
    main()

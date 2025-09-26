#!/usr/bin/env python3
"""
Comprehensive test runner for Web ChatBot Enhanced
This script runs all available tests in the correct order
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path

def run_test_script(script_name, description):
    """Run a test script and return success status"""
    print(f"\n{'='*60}")
    print(f"🧪 Running: {description}")
    print(f"📄 Script: {script_name}")
    print(f"{'='*60}")
    
    try:
        # Change to the tests directory
        os.chdir(Path(__file__).parent)
        
        # Run the test script
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            if result.stdout:
                print("📝 Output:")
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr:
                print("💥 Error:")
                print(result.stderr)
            if result.stdout:
                print("📝 Output:")
                print(result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT (5 minutes)")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False

def main():
    """Main test runner function"""
    print("🚀 Web ChatBot Enhanced - Test Suite Runner")
    print("=" * 60)
    print("This script will run all available tests in the correct order")
    print("Make sure the server is running on http://localhost:8000")
    print("Press Ctrl+C to cancel\n")
    
    # Define test scripts in order of execution
    test_scripts = [
        ("test_reorganized_api.py", "API Structure Test"),
        ("test_inquiry_simple.py", "Chat Inquiry API Test"),
        ("test_chat_inquiry_api.py", "Comprehensive Chat Inquiry Test"),
        ("test_web_app.py", "Web Application Test"),
        ("test_chat_functionality.py", "Chat Functionality Test"),
        ("test_chat_modes.py", "Chat Modes Test"),
        ("test_session_persistence.py", "Session Persistence Test"),
        ("test_auto_login_and_storage.py", "Auto Login and Storage Test"),
        ("test_complete_system.py", "Complete System Test"),
        ("test_cloud_config.py", "Cloud Configuration Test"),
        ("test_database_config.py", "Database Configuration Test"),
        ("test_simple_chat_fix.py", "Simple Chat Fix Test"),
        ("test_complete_chat_fix.py", "Complete Chat Fix Test"),
        ("test_chat_flow_fix.py", "Chat Flow Fix Test"),
    ]
    
    # Track results
    results = []
    passed = 0
    failed = 0
    
    try:
        for script_name, description in test_scripts:
            # Check if script exists
            if not os.path.exists(script_name):
                print(f"⚠️  Skipping {description} - {script_name} not found")
                continue
            
            success = run_test_script(script_name, description)
            results.append((description, success))
            
            if success:
                passed += 1
            else:
                failed += 1
        
        # Print summary
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total: {passed + failed}")
        
        if failed == 0:
            print("\n🎉 All tests passed! System is working correctly.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please check the issues above.")
        
        print(f"\n{'='*60}")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test execution cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Test runner failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

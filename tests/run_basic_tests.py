#!/usr/bin/env python3
"""
Basic test runner for Web ChatBot Enhanced
Runs only the essential tests for quick verification
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path

def run_test_script(script_name, description):
    """Run a test script and return success status"""
    print(f"\n{'='*50}")
    print(f"🧪 {description}")
    print(f"{'='*50}")
    
    try:
        # Change to the tests directory
        os.chdir(Path(__file__).parent)
        
        # Run the test script
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              timeout=120)  # 2 minute timeout
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr:
                print("💥 Error:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False

def main():
    """Main function for basic tests"""
    print("🚀 Web ChatBot Enhanced - Basic Test Runner")
    print("=" * 50)
    print("Running essential tests only...")
    print("Make sure the server is running on http://localhost:8000\n")
    
    # Essential tests only
    basic_tests = [
        ("test_reorganized_api.py", "API Structure Test"),
        ("test_inquiry_simple.py", "Chat Inquiry Test"),
    ]
    
    passed = 0
    failed = 0
    
    try:
        for script_name, description in basic_tests:
            if os.path.exists(script_name):
                success = run_test_script(script_name, description)
                if success:
                    passed += 1
                else:
                    failed += 1
            else:
                print(f"⚠️  {script_name} not found, skipping...")
        
        print(f"\n{'='*50}")
        print("📊 BASIC TEST SUMMARY")
        print(f"{'='*50}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed == 0:
            print("\n🎉 Basic tests passed!")
        else:
            print(f"\n⚠️  {failed} test(s) failed.")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests cancelled by user")

if __name__ == "__main__":
    main()

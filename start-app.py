#!/usr/bin/env python3
"""
Simple script to start the application with proper error handling
Note: This script should be run from within the virtual environment
"""

import sys
import os
import traceback
import uvicorn
from config import Config

def check_venv():
    """Check if running in virtual environment"""
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
        os.environ.get('VIRTUAL_ENV') is not None
    )
    
    if not in_venv:
        print("WARNING: Not running in virtual environment!")
        print("For best results, activate the virtual environment first:")
        print("  Windows: venv\\Scripts\\activate.bat")
        print("  Linux/Mac: source venv/bin/activate")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting. Please activate virtual environment and try again.")
            sys.exit(1)
        print()

def main():
    """Start the application"""
    print("Starting JRC Enquiry Assistant Operations...")
    check_venv()
    print(f"Environment: {Config.ENVIRONMENT}")
    print(f"Host: {Config.HOST}")
    print(f"Port: {Config.PORT}")
    print(f"Debug: {Config.DEBUG}")
    print()
    
    try:
        # Import the app
        from web_app import app
        print("+ Application imported successfully")
        
        # Start the server
        print("Starting server...")
        if Config.DEBUG:
            uvicorn.run("web_app:app", host=Config.HOST, port=Config.PORT, reload=True)
        else:
            uvicorn.run(app, host=Config.HOST, port=Config.PORT)
            
    except Exception as e:
        print(f"- Failed to start application: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

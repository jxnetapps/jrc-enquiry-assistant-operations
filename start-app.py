#!/usr/bin/env python3
"""
Simple script to start the application with proper error handling
"""

import sys
import traceback
import uvicorn
from config import Config

def main():
    """Start the application"""
    print("Starting JRC Enquiry Assistant Operations...")
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

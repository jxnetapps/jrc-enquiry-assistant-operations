#!/usr/bin/env python3
"""
Debug script to help troubleshoot Chroma Cloud configuration.
This script will help you verify your Chroma Cloud credentials and connection.
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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_chroma_cloud_config():
    """Debug Chroma Cloud configuration"""
    print("=" * 60)
    print("Chroma Cloud Configuration Debug")
    print("=" * 60)
    
    # Check configuration values
    print(f"Database Type: {Config.VECTOR_DATABASE_TYPE}")
    print(f"Chroma Cloud API Key: {Config.CHROMA_CLOUD_API_KEY[:10]}..." if Config.CHROMA_CLOUD_API_KEY else "NOT SET")
    print(f"Chroma Cloud Tenant ID: {Config.CHROMA_CLOUD_TENANT_ID}")
    print(f"Chroma Cloud Database ID: {Config.CHROMA_CLOUD_DATABASE_ID}")
    print(f"Chroma Cloud Collection: {Config.CHROMA_CLOUD_COLLECTION_NAME}")
    
    print("\n" + "=" * 60)
    print("Chroma Cloud Setup Instructions:")
    print("=" * 60)
    
    print("""
1. Go to https://cloud.trychroma.com/
2. Sign up for a free account
3. Create a new tenant (this will be your TENANT_ID)
4. Create a database within your tenant (this will be your DATABASE_ID)
5. Generate an API key (this will be your API_KEY)
6. Update your .env file with these values:

VECTOR_DATABASE_TYPE=cloud
CHROMA_CLOUD_API_KEY=your_api_key_here
CHROMA_CLOUD_TENANT_ID=your_tenant_id_here
CHROMA_CLOUD_DATABASE_ID=your_database_id_here
CHROMA_CLOUD_COLLECTION_NAME=web_content

7. The API endpoint will be: https://{TENANT_ID}.trychroma.com
""")
    
    if Config.VECTOR_DATABASE_TYPE != "cloud":
        print("❌ VECTOR_DATABASE_TYPE is not set to 'cloud'")
        return False
    
    if not Config.CHROMA_CLOUD_API_KEY:
        print("❌ CHROMA_CLOUD_API_KEY is not set")
        return False
        
    if not Config.CHROMA_CLOUD_TENANT_ID:
        print("❌ CHROMA_CLOUD_TENANT_ID is not set")
        return False
        
    if not Config.CHROMA_CLOUD_DATABASE_ID:
        print("❌ CHROMA_CLOUD_DATABASE_ID is not set")
        return False
    
    print("\n✅ All required configuration values are set!")
    
    # Test connection
    print("\n" + "=" * 60)
    print("Testing Chroma Cloud Connection:")
    print("=" * 60)
    
    try:
        import chromadb
        from chromadb.config import Settings
        
        # Test with the correct endpoint format
        tenant_id = Config.CHROMA_CLOUD_TENANT_ID
        api_key = Config.CHROMA_CLOUD_API_KEY
        
        print(f"Testing connection to: https://{tenant_id}.trychroma.com")
        
        client = chromadb.HttpClient(
            host=f"https://{tenant_id}.trychroma.com",
            settings=Settings(
                chroma_api_impl="chromadb.api.fastapi.FastAPI",
                chroma_server_headers={
                    "X-Chroma-Token": api_key
                }
            )
        )
        
        # Try to list collections to test the connection
        collections = client.list_collections()
        print(f"✅ Connection successful! Found {len(collections)} collections.")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Verify your API key is correct")
        print("2. Verify your tenant ID is correct")
        print("3. Make sure your database exists")
        print("4. Check if your API key has the right permissions")
        return False

def main():
    """Main debug function"""
    success = debug_chroma_cloud_config()
    
    if success:
        print("\n🎉 Chroma Cloud configuration looks good!")
        print("You can now run: python test_cloud_config.py")
    else:
        print("\n❌ Please fix the configuration issues above.")
        print("Then run this script again to verify.")

if __name__ == "__main__":
    main()

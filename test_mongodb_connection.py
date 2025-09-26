#!/usr/bin/env python3
"""
Test script to verify MongoDB connection
"""

import asyncio
import logging
from database.mongodb_connection import mongodb_connection
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mongodb_connection():
    """Test MongoDB connection"""
    print("🔍 Testing MongoDB Connection")
    print("=" * 40)
    
    print(f"📋 Connection URI: {Config.MONGODB_CONNECTION_URI}")
    print(f"📋 Database Name: {Config.MONGODB_DATABASE_NAME}")
    print(f"📋 Collection Name: {Config.MONGODB_CHAT_INQUIRY_COLLECTION}")
    
    try:
        # Test connection
        print("\n🔄 Attempting to connect to MongoDB...")
        await mongodb_connection.connect()
        
        # Test health check
        print("🔄 Testing health check...")
        is_healthy = await mongodb_connection.health_check()
        
        if is_healthy:
            print("✅ MongoDB connection successful!")
            
            # Test database operations
            print("🔄 Testing database operations...")
            database = mongodb_connection.get_database()
            collection = database[Config.MONGODB_CHAT_INQUIRY_COLLECTION]
            
            # Test insert
            test_doc = {
                "test": True,
                "message": "MongoDB connection test",
                "timestamp": "2024-12-26"
            }
            
            result = await collection.insert_one(test_doc)
            print(f"✅ Test document inserted with ID: {result.inserted_id}")
            
            # Test find
            found_doc = await collection.find_one({"_id": result.inserted_id})
            if found_doc:
                print("✅ Test document retrieved successfully")
                print(f"📄 Document: {found_doc}")
            
            # Clean up test document
            await collection.delete_one({"_id": result.inserted_id})
            print("✅ Test document cleaned up")
            
        else:
            print("❌ MongoDB health check failed")
            
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Disconnect
        print("\n🔄 Disconnecting from MongoDB...")
        await mongodb_connection.disconnect()
        print("✅ Disconnected from MongoDB")

async def test_alternative_connection():
    """Test alternative connection methods"""
    print("\n🔍 Testing Alternative Connection Methods")
    print("=" * 50)
    
    # Test 1: Without TLS
    print("\n🔄 Test 1: Connection without TLS...")
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        # Try without TLS first
        uri_without_tls = Config.MONGODB_CONNECTION_URI.replace("&tls=true&tlsAllowInvalidCertificates=true", "")
        client = AsyncIOMotorClient(uri_without_tls, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        print("✅ Connection without TLS successful!")
        client.close()
        
    except Exception as e:
        print(f"❌ Connection without TLS failed: {e}")
    
    # Test 2: With different TLS settings
    print("\n🔄 Test 2: Connection with different TLS settings...")
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        client = AsyncIOMotorClient(
            Config.MONGODB_CONNECTION_URI,
            tls=True,
            tlsInsecure=True,
            serverSelectionTimeoutMS=5000
        )
        await client.admin.command('ping')
        print("✅ Connection with tlsInsecure=True successful!")
        client.close()
        
    except Exception as e:
        print(f"❌ Connection with tlsInsecure=True failed: {e}")

if __name__ == "__main__":
    print("🚀 MongoDB Connection Test")
    print("=" * 50)
    
    asyncio.run(test_mongodb_connection())
    asyncio.run(test_alternative_connection())
    
    print("\n✅ MongoDB connection test completed!")

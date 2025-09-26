#!/usr/bin/env python3
"""
Quick Migration Script: SQLite to MongoDB
Simple script to migrate data when MongoDB connectivity is restored
"""

import asyncio
import sqlite3
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

async def quick_migrate():
    """Quick migration from SQLite to MongoDB"""
    print("🚀 Quick Migration: SQLite → MongoDB")
    print("=" * 50)
    
    # Step 1: Read SQLite data
    print("📖 Reading SQLite data...")
    try:
        with sqlite3.connect("chat_inquiries.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM chat_inquiry_information ORDER BY id')
            rows = cursor.fetchall()
            
            sqlite_data = [dict(row) for row in rows]
            print(f"✅ Found {len(sqlite_data)} records in SQLite")
            
    except Exception as e:
        print(f"❌ Error reading SQLite: {e}")
        return
    
    if not sqlite_data:
        print("⚠️  No data to migrate")
        return
    
    # Step 2: Connect to MongoDB
    print("🔗 Connecting to MongoDB...")
    try:
        client = AsyncIOMotorClient(Config.MONGODB_CONNECTION_URI)
        db = client[Config.MONGODB_DATABASE_NAME]
        collection = db[Config.MONGODB_CHAT_INQUIRY_COLLECTION]
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB")
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("📋 Make sure MongoDB is accessible and try again")
        return
    
    # Step 3: Migrate data
    print("🔄 Migrating data...")
    migrated = 0
    skipped = 0
    
    for record in sqlite_data:
        try:
            # Prepare MongoDB document
            mongo_doc = {
                "parentType": record.get("parentType"),
                "schoolType": record.get("schoolType"),
                "firstName": record.get("firstName"),
                "mobile": record.get("mobile"),
                "email": record.get("email"),
                "city": record.get("city"),
                "childName": record.get("childName"),
                "grade": record.get("grade"),
                "academicYear": record.get("academicYear"),
                "dateOfBirth": record.get("dateOfBirth"),
                "schoolName": record.get("schoolName"),
                "status": record.get("status", "new"),
                "source": record.get("source", "migrated_from_sqlite"),
                "user_id": record.get("user_id"),
                "created_at": record.get("created_at"),
                "updated_at": record.get("updated_at"),
                "migration_info": {
                    "migrated_at": datetime.utcnow().isoformat(),
                    "original_sqlite_id": str(record.get("id"))
                }
            }
            
            # Check for duplicates
            existing = await collection.find_one({
                "$or": [
                    {"email": record.get("email")},
                    {"mobile": record.get("mobile")}
                ]
            })
            
            if existing:
                print(f"⏭️  Skipping duplicate: {record.get('email')}")
                skipped += 1
                continue
            
            # Insert document
            await collection.insert_one(mongo_doc)
            migrated += 1
            
            if migrated % 10 == 0:
                print(f"📊 Migrated {migrated} records...")
                
        except Exception as e:
            print(f"❌ Error migrating record {record.get('id')}: {e}")
            continue
    
    # Step 4: Summary
    print("\n📋 MIGRATION SUMMARY")
    print("=" * 30)
    print(f"✅ Migrated: {migrated} records")
    print(f"⏭️  Skipped: {skipped} records")
    print(f"📊 Total processed: {migrated + skipped}")
    
    # Check final count
    final_count = await collection.count_documents({})
    print(f"📊 MongoDB now has: {final_count} total records")
    
    await client.close()
    print("✅ Migration completed!")

if __name__ == "__main__":
    asyncio.run(quick_migrate())

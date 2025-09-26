#!/usr/bin/env python3
"""
Data Export/Import Utility
Export data from SQLite and import to MongoDB or vice versa
"""

import asyncio
import sqlite3
import json
import csv
from datetime import datetime
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

class DataExporter:
    """Handles data export and import operations"""
    
    def __init__(self):
        self.sqlite_db = "chat_inquiries.db"
        self.mongodb_client = None
        self.mongodb_collection = None
    
    async def connect_mongodb(self):
        """Connect to MongoDB"""
        try:
            self.mongodb_client = AsyncIOMotorClient(Config.MONGODB_CONNECTION_URI)
            db = self.mongodb_client[Config.MONGODB_DATABASE_NAME]
            self.mongodb_collection = db[Config.MONGODB_CHAT_INQUIRY_COLLECTION]
            await self.mongodb_client.admin.command('ping')
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            return False
    
    def export_sqlite_to_json(self, filename: str = None) -> str:
        """Export SQLite data to JSON file"""
        if not filename:
            filename = f"sqlite_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with sqlite3.connect(self.sqlite_db) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM chat_inquiry_information ORDER BY id')
                rows = cursor.fetchall()
                
                data = [dict(row) for row in rows]
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
                
                print(f"✅ Exported {len(data)} records to {filename}")
                return filename
                
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return None
    
    def export_sqlite_to_csv(self, filename: str = None) -> str:
        """Export SQLite data to CSV file"""
        if not filename:
            filename = f"sqlite_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            with sqlite3.connect(self.sqlite_db) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM chat_inquiry_information ORDER BY id')
                rows = cursor.fetchall()
                
                if not rows:
                    print("⚠️  No data to export")
                    return None
                
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows([dict(row) for row in rows])
                
                print(f"✅ Exported {len(rows)} records to {filename}")
                return filename
                
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return None
    
    async def export_mongodb_to_json(self, filename: str = None) -> str:
        """Export MongoDB data to JSON file"""
        if not await self.connect_mongodb():
            return None
        
        if not filename:
            filename = f"mongodb_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            data = []
            async for doc in self.mongodb_collection.find():
                # Convert ObjectId to string
                doc['_id'] = str(doc['_id'])
                data.append(doc)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            print(f"✅ Exported {len(data)} records to {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return None
    
    def import_json_to_sqlite(self, filename: str) -> bool:
        """Import JSON data to SQLite"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with sqlite3.connect(self.sqlite_db) as conn:
                cursor = conn.cursor()
                
                for record in data:
                    cursor.execute('''
                        INSERT OR REPLACE INTO chat_inquiry_information
                        (id, user_id, parentType, schoolType, firstName, mobile, email, city,
                         childName, grade, academicYear, dateOfBirth, schoolName, status, source,
                         created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        record.get('id'),
                        record.get('user_id'),
                        record.get('parentType'),
                        record.get('schoolType'),
                        record.get('firstName'),
                        record.get('mobile'),
                        record.get('email'),
                        record.get('city'),
                        record.get('childName'),
                        record.get('grade'),
                        record.get('academicYear'),
                        record.get('dateOfBirth'),
                        record.get('schoolName'),
                        record.get('status', 'new'),
                        record.get('source', 'imported'),
                        record.get('created_at'),
                        record.get('updated_at')
                    ))
                
                conn.commit()
                print(f"✅ Imported {len(data)} records to SQLite")
                return True
                
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return False
    
    async def import_json_to_mongodb(self, filename: str) -> bool:
        """Import JSON data to MongoDB"""
        if not await self.connect_mongodb():
            return False
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported = 0
            skipped = 0
            
            for record in data:
                try:
                    # Check for duplicates
                    existing = await self.mongodb_collection.find_one({
                        "$or": [
                            {"email": record.get("email")},
                            {"mobile": record.get("mobile")}
                        ]
                    })
                    
                    if existing:
                        skipped += 1
                        continue
                    
                    # Prepare document
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
                        "source": record.get("source", "imported"),
                        "user_id": record.get("user_id"),
                        "created_at": record.get("created_at"),
                        "updated_at": record.get("updated_at"),
                        "import_metadata": {
                            "imported_at": datetime.utcnow().isoformat(),
                            "original_id": record.get("id")
                        }
                    }
                    
                    await self.mongodb_collection.insert_one(mongo_doc)
                    imported += 1
                    
                except Exception as e:
                    print(f"❌ Error importing record: {e}")
                    continue
            
            print(f"✅ Imported {imported} records to MongoDB")
            print(f"⏭️  Skipped {skipped} duplicates")
            return True
            
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return False
    
    async def close_mongodb(self):
        """Close MongoDB connection"""
        if self.mongodb_client:
            await self.mongodb_client.close()

async def main():
    """Main function with menu options"""
    print("🔄 Data Export/Import Utility")
    print("=" * 40)
    
    exporter = DataExporter()
    
    while True:
        print("\n📋 Available Operations:")
        print("1. Export SQLite to JSON")
        print("2. Export SQLite to CSV")
        print("3. Export MongoDB to JSON")
        print("4. Import JSON to SQLite")
        print("5. Import JSON to MongoDB")
        print("6. Quick Migration (SQLite → MongoDB)")
        print("7. Exit")
        
        choice = input("\nSelect operation (1-7): ").strip()
        
        if choice == '1':
            filename = input("Enter filename (or press Enter for auto): ").strip() or None
            exporter.export_sqlite_to_json(filename)
        
        elif choice == '2':
            filename = input("Enter filename (or press Enter for auto): ").strip() or None
            exporter.export_sqlite_to_csv(filename)
        
        elif choice == '3':
            filename = input("Enter filename (or press Enter for auto): ").strip() or None
            await exporter.export_mongodb_to_json(filename)
        
        elif choice == '4':
            filename = input("Enter JSON filename: ").strip()
            if filename:
                exporter.import_json_to_sqlite(filename)
        
        elif choice == '5':
            filename = input("Enter JSON filename: ").strip()
            if filename:
                await exporter.import_json_to_mongodb(filename)
        
        elif choice == '6':
            print("🚀 Quick Migration: SQLite → MongoDB")
            if await exporter.connect_mongodb():
                # Export from SQLite
                json_file = exporter.export_sqlite_to_json()
                if json_file:
                    # Import to MongoDB
                    await exporter.import_json_to_mongodb(json_file)
                await exporter.close_mongodb()
        
        elif choice == '7':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())

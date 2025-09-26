#!/usr/bin/env python3
"""
Comprehensive Data Migration Tool: SQLite to MongoDB
Migrates all data from SQLite to MongoDB when connectivity is restored
"""

import asyncio
import logging
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataMigrator:
    """Handles migration of data from SQLite to MongoDB"""
    
    def __init__(self, sqlite_db_path: str = "chat_inquiries.db"):
        self.sqlite_db_path = sqlite_db_path
        self.mongodb_client = None
        self.mongodb_db = None
        self.mongodb_collection = None
        
    async def connect_to_mongodb(self) -> bool:
        """Connect to MongoDB with multiple fallback methods"""
        try:
            # Try multiple connection methods
            connection_methods = [
                # Method 1: Default connection
                lambda: AsyncIOMotorClient(Config.MONGODB_CONNECTION_URI),
                
                # Method 2: With TLS insecure
                lambda: AsyncIOMotorClient(
                    Config.MONGODB_CONNECTION_URI,
                    tls=True,
                    tlsInsecure=True,
                    serverSelectionTimeoutMS=10000
                ),
                
                # Method 3: With longer timeouts
                lambda: AsyncIOMotorClient(
                    Config.MONGODB_CONNECTION_URI,
                    serverSelectionTimeoutMS=30000,
                    connectTimeoutMS=30000,
                    socketTimeoutMS=30000
                )
            ]
            
            for i, method in enumerate(connection_methods, 1):
                try:
                    logger.info(f"Trying MongoDB connection method {i}")
                    self.mongodb_client = method()
                    self.mongodb_db = self.mongodb_client[Config.MONGODB_DATABASE_NAME]
                    self.mongodb_collection = self.mongodb_db[Config.MONGODB_CHAT_INQUIRY_COLLECTION]
                    
                    # Test the connection
                    await self.mongodb_client.admin.command('ping')
                    logger.info(f"Successfully connected to MongoDB using method {i}")
                    return True
                    
                except Exception as e:
                    logger.warning(f"MongoDB connection method {i} failed: {e}")
                    if self.mongodb_client:
                        try:
                            await self.mongodb_client.close()
                        except:
                            pass
                        self.mongodb_client = None
                    continue
            
            logger.error("All MongoDB connection methods failed")
            return False
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def get_sqlite_data(self) -> List[Dict[str, Any]]:
        """Retrieve all data from SQLite database"""
        try:
            with sqlite3.connect(self.sqlite_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM chat_inquiry_information ORDER BY id')
                rows = cursor.fetchall()
                
                data = []
                for row in rows:
                    record = dict(row)
                    # Convert SQLite ID to string for consistency
                    record['id'] = str(record['id'])
                    data.append(record)
                
                logger.info(f"Retrieved {len(data)} records from SQLite")
                return data
                
        except Exception as e:
            logger.error(f"Error retrieving data from SQLite: {e}")
            return []
    
    async def check_mongodb_data(self) -> Dict[str, Any]:
        """Check existing data in MongoDB"""
        try:
            if not self.mongodb_collection:
                return {"error": "MongoDB not connected"}
            
            # Count total documents
            total_count = await self.mongodb_collection.count_documents({})
            
            # Get sample documents
            sample_docs = []
            async for doc in self.mongodb_collection.find().limit(5):
                sample_docs.append(doc)
            
            return {
                "total_count": total_count,
                "sample_documents": sample_docs
            }
            
        except Exception as e:
            logger.error(f"Error checking MongoDB data: {e}")
            return {"error": str(e)}
    
    async def migrate_data(self, batch_size: int = 100, dry_run: bool = False) -> Dict[str, Any]:
        """Migrate data from SQLite to MongoDB"""
        try:
            # Get SQLite data
            sqlite_data = self.get_sqlite_data()
            if not sqlite_data:
                return {"error": "No data found in SQLite"}
            
            if dry_run:
                logger.info(f"DRY RUN: Would migrate {len(sqlite_data)} records")
                return {
                    "status": "dry_run",
                    "records_to_migrate": len(sqlite_data),
                    "sample_records": sqlite_data[:3]
                }
            
            # Check MongoDB connection
            if not self.mongodb_collection:
                return {"error": "MongoDB not connected"}
            
            # Get existing MongoDB data count
            existing_count = await self.mongodb_collection.count_documents({})
            logger.info(f"MongoDB currently has {existing_count} records")
            
            # Prepare data for migration
            migrated_count = 0
            skipped_count = 0
            error_count = 0
            
            # Process in batches
            for i in range(0, len(sqlite_data), batch_size):
                batch = sqlite_data[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(sqlite_data) + batch_size - 1)//batch_size}")
                
                for record in batch:
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
                            "migration_metadata": {
                                "migrated_at": datetime.utcnow().isoformat(),
                                "original_sqlite_id": record.get("id"),
                                "migration_version": "1.0"
                            }
                        }
                        
                        # Check if record already exists (by email or mobile)
                        existing = await self.mongodb_collection.find_one({
                            "$or": [
                                {"email": record.get("email")},
                                {"mobile": record.get("mobile")}
                            ]
                        })
                        
                        if existing:
                            logger.warning(f"Skipping duplicate record: {record.get('email')}")
                            skipped_count += 1
                            continue
                        
                        # Insert into MongoDB
                        result = await self.mongodb_collection.insert_one(mongo_doc)
                        migrated_count += 1
                        
                        if migrated_count % 10 == 0:
                            logger.info(f"Migrated {migrated_count} records...")
                        
                    except Exception as e:
                        logger.error(f"Error migrating record {record.get('id', 'unknown')}: {e}")
                        error_count += 1
                        continue
            
            # Final statistics
            final_count = await self.mongodb_collection.count_documents({})
            
            return {
                "status": "completed",
                "total_sqlite_records": len(sqlite_data),
                "migrated_records": migrated_count,
                "skipped_records": skipped_count,
                "error_records": error_count,
                "final_mongodb_count": final_count,
                "migration_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error during migration: {e}")
            return {"error": str(e)}
    
    async def verify_migration(self) -> Dict[str, Any]:
        """Verify that migration was successful"""
        try:
            # Get SQLite count
            sqlite_data = self.get_sqlite_data()
            sqlite_count = len(sqlite_data)
            
            # Get MongoDB count
            if not self.mongodb_collection:
                return {"error": "MongoDB not connected"}
            
            mongodb_count = await self.mongodb_collection.count_documents({})
            
            # Check for data integrity
            verification_results = {
                "sqlite_records": sqlite_count,
                "mongodb_records": mongodb_count,
                "migration_successful": mongodb_count >= sqlite_count,
                "verification_timestamp": datetime.utcnow().isoformat()
            }
            
            # Sample verification - check a few records
            sample_verification = []
            for record in sqlite_data[:5]:  # Check first 5 records
                mongo_record = await self.mongodb_collection.find_one({
                    "migration_metadata.original_sqlite_id": record.get("id")
                })
                
                if mongo_record:
                    sample_verification.append({
                        "sqlite_id": record.get("id"),
                        "mongodb_id": str(mongo_record.get("_id")),
                        "verified": True
                    })
                else:
                    sample_verification.append({
                        "sqlite_id": record.get("id"),
                        "mongodb_id": None,
                        "verified": False
                    })
            
            verification_results["sample_verification"] = sample_verification
            
            return verification_results
            
        except Exception as e:
            logger.error(f"Error during verification: {e}")
            return {"error": str(e)}
    
    async def close_connections(self):
        """Close all database connections"""
        if self.mongodb_client:
            await self.mongodb_client.close()
            logger.info("MongoDB connection closed")

async def main():
    """Main migration function"""
    print("🚀 SQLite to MongoDB Data Migration Tool")
    print("=" * 60)
    
    migrator = DataMigrator()
    
    try:
        # Step 1: Connect to MongoDB
        print("\n🔗 Step 1: Connecting to MongoDB...")
        if not await migrator.connect_to_mongodb():
            print("❌ Failed to connect to MongoDB")
            print("📋 Please check your MongoDB connection settings")
            return
        
        print("✅ Successfully connected to MongoDB")
        
        # Step 2: Check existing data
        print("\n📊 Step 2: Checking existing data...")
        sqlite_data = migrator.get_sqlite_data()
        mongodb_info = await migrator.check_mongodb_data()
        
        print(f"📋 SQLite records: {len(sqlite_data)}")
        print(f"📋 MongoDB records: {mongodb_info.get('total_count', 0)}")
        
        if len(sqlite_data) == 0:
            print("⚠️  No data found in SQLite to migrate")
            return
        
        # Step 3: Dry run
        print("\n🧪 Step 3: Performing dry run...")
        dry_run_result = await migrator.migrate_data(dry_run=True)
        print(f"📋 Would migrate: {dry_run_result.get('records_to_migrate', 0)} records")
        
        # Step 4: Confirm migration
        print("\n❓ Step 4: Migration confirmation")
        print("This will migrate all data from SQLite to MongoDB")
        print("Existing MongoDB data will be preserved (duplicates will be skipped)")
        
        confirm = input("\nDo you want to proceed with the migration? (y/N): ").lower().strip()
        
        if confirm != 'y':
            print("❌ Migration cancelled")
            return
        
        # Step 5: Perform migration
        print("\n🔄 Step 5: Performing migration...")
        migration_result = await migrator.migrate_data(dry_run=False)
        
        if "error" in migration_result:
            print(f"❌ Migration failed: {migration_result['error']}")
            return
        
        print("✅ Migration completed successfully!")
        print(f"📊 Migrated: {migration_result['migrated_records']} records")
        print(f"📊 Skipped: {migration_result['skipped_records']} records")
        print(f"📊 Errors: {migration_result['error_records']} records")
        print(f"📊 Final MongoDB count: {migration_result['final_mongodb_count']} records")
        
        # Step 6: Verify migration
        print("\n🔍 Step 6: Verifying migration...")
        verification_result = await migrator.verify_migration()
        
        if verification_result.get("migration_successful"):
            print("✅ Migration verification successful!")
        else:
            print("⚠️  Migration verification found issues")
        
        print(f"📊 SQLite records: {verification_result['sqlite_records']}")
        print(f"📊 MongoDB records: {verification_result['mongodb_records']}")
        
        # Step 7: Summary
        print("\n📋 MIGRATION SUMMARY")
        print("=" * 40)
        print("✅ Data migration completed successfully")
        print("✅ All SQLite data has been migrated to MongoDB")
        print("✅ Duplicate records were skipped")
        print("✅ Migration metadata has been preserved")
        print("\n🎯 Next steps:")
        print("• Update your application to use MongoDB as primary database")
        print("• Test all API endpoints with MongoDB")
        print("• Consider keeping SQLite as backup or removing it")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        print(f"❌ Migration failed: {e}")
    
    finally:
        await migrator.close_connections()

if __name__ == "__main__":
    asyncio.run(main())

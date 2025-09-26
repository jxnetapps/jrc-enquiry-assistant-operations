#!/usr/bin/env python3
"""
SQLite to MongoDB Export API
Provides endpoints to export data from SQLite to MongoDB
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import sqlite3
import asyncio
import logging
from datetime import datetime
from config import Config

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/export", tags=["SQLite Export"])

# Response models
class ExportStatus(BaseModel):
    """Export status model"""
    status: str  # "running", "completed", "failed"
    total_records: int
    processed_records: int
    successful_records: int
    failed_records: int
    skipped_records: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None

class ExportResponse(BaseModel):
    """Export response model"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Global export status tracking
export_status = {
    "status": "idle",
    "total_records": 0,
    "processed_records": 0,
    "successful_records": 0,
    "failed_records": 0,
    "skipped_records": 0,
    "start_time": None,
    "end_time": None,
    "error_message": None
}

class SQLiteToMongoDBExporter:
    """Handles SQLite to MongoDB export operations"""
    
    def __init__(self):
        self.sqlite_db = "chat_inquiries.db"
        self.mongodb_client = None
        self.mongodb_collection = None
    
    async def connect_mongodb(self) -> bool:
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
                    self.mongodb_collection = self.mongodb_client[Config.MONGODB_DATABASE_NAME][Config.MONGODB_CHAT_INQUIRY_COLLECTION]
                    
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
            with sqlite3.connect(self.sqlite_db) as conn:
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
    
    async def export_data(self, batch_size: int = 100, skip_duplicates: bool = True) -> Dict[str, Any]:
        """Export data from SQLite to MongoDB"""
        global export_status
        
        try:
            # Update status
            export_status.update({
                "status": "running",
                "start_time": datetime.utcnow(),
                "end_time": None,
                "error_message": None
            })
            
            # Get SQLite data
            sqlite_data = self.get_sqlite_data()
            if not sqlite_data:
                export_status.update({
                    "status": "failed",
                    "error_message": "No data found in SQLite",
                    "end_time": datetime.utcnow()
                })
                return {"error": "No data found in SQLite"}
            
            export_status["total_records"] = len(sqlite_data)
            
            # Connect to MongoDB
            if not await self.connect_mongodb():
                export_status.update({
                    "status": "failed",
                    "error_message": "Failed to connect to MongoDB",
                    "end_time": datetime.utcnow()
                })
                return {"error": "Failed to connect to MongoDB"}
            
            # Export data
            successful = 0
            failed = 0
            skipped = 0
            
            for i, record in enumerate(sqlite_data):
                try:
                    # Update progress
                    export_status["processed_records"] = i + 1
                    
                    # Check for duplicates if enabled
                    if skip_duplicates:
                        existing = await self.mongodb_collection.find_one({
                            "$or": [
                                {"email": record.get("email")},
                                {"mobile": record.get("mobile")}
                            ]
                        })
                        
                        if existing:
                            skipped += 1
                            export_status["skipped_records"] = skipped
                            continue
                    
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
                        "source": record.get("source", "exported_from_sqlite"),
                        "user_id": record.get("user_id"),
                        "created_at": record.get("created_at"),
                        "updated_at": record.get("updated_at"),
                        "export_metadata": {
                            "exported_at": datetime.utcnow().isoformat(),
                            "original_sqlite_id": record.get("id"),
                            "export_version": "1.0"
                        }
                    }
                    
                    # Insert into MongoDB
                    await self.mongodb_collection.insert_one(mongo_doc)
                    successful += 1
                    export_status["successful_records"] = successful
                    
                    # Process in batches
                    if (i + 1) % batch_size == 0:
                        logger.info(f"Processed {i + 1}/{len(sqlite_data)} records...")
                        # Small delay to prevent overwhelming the database
                        await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error exporting record {record.get('id', 'unknown')}: {e}")
                    failed += 1
                    export_status["failed_records"] = failed
                    continue
            
            # Final statistics
            final_count = await self.mongodb_collection.count_documents({})
            
            # Update final status
            export_status.update({
                "status": "completed",
                "end_time": datetime.utcnow(),
                "successful_records": successful,
                "failed_records": failed,
                "skipped_records": skipped
            })
            
            return {
                "status": "completed",
                "total_sqlite_records": len(sqlite_data),
                "successful_records": successful,
                "failed_records": failed,
                "skipped_records": skipped,
                "final_mongodb_count": final_count,
                "export_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error during export: {e}")
            export_status.update({
                "status": "failed",
                "error_message": str(e),
                "end_time": datetime.utcnow()
            })
            return {"error": str(e)}
        
        finally:
            # Close MongoDB connection
            if self.mongodb_client:
                await self.mongodb_client.close()

# Global exporter instance
exporter = SQLiteToMongoDBExporter()

@router.get("/status", response_model=ExportResponse)
async def get_export_status():
    """
    Get the current export status
    """
    try:
        return ExportResponse(
            success=True,
            message="Export status retrieved successfully",
            data=export_status
        )
    except Exception as e:
        logger.error(f"Error getting export status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/sqlite-to-mongodb", response_model=ExportResponse)
async def start_export(
    background_tasks: BackgroundTasks,
    batch_size: int = Query(100, ge=1, le=1000, description="Number of records to process in each batch"),
    skip_duplicates: bool = Query(True, description="Skip duplicate records based on email/mobile")
):
    """
    Start exporting data from SQLite to MongoDB
    
    - **batch_size**: Number of records to process in each batch (1-1000)
    - **skip_duplicates**: Whether to skip duplicate records
    """
    try:
        # Check if export is already running
        if export_status["status"] == "running":
            return ExportResponse(
                success=False,
                message="Export is already running",
                error="Another export operation is in progress"
            )
        
        # Reset status
        export_status.update({
            "status": "idle",
            "total_records": 0,
            "processed_records": 0,
            "successful_records": 0,
            "failed_records": 0,
            "skipped_records": 0,
            "start_time": None,
            "end_time": None,
            "error_message": None
        })
        
        # Start export in background
        background_tasks.add_task(exporter.export_data, batch_size, skip_duplicates)
        
        return ExportResponse(
            success=True,
            message="Export started successfully",
            data={
                "export_id": f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "batch_size": batch_size,
                "skip_duplicates": skip_duplicates,
                "status": "started"
            }
        )
        
    except Exception as e:
        logger.error(f"Error starting export: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/sqlite-data", response_model=ExportResponse)
async def get_sqlite_data_summary():
    """
    Get summary of SQLite data without exporting
    """
    try:
        data = exporter.get_sqlite_data()
        
        if not data:
            return ExportResponse(
                success=True,
                message="No data found in SQLite",
                data={"total_records": 0, "sample_records": []}
            )
        
        # Get sample records
        sample_records = data[:5] if len(data) > 5 else data
        
        # Get statistics
        user_ids = [record.get('user_id') for record in data if record.get('user_id')]
        parent_types = [record.get('parentType') for record in data if record.get('parentType')]
        school_types = [record.get('schoolType') for record in data if record.get('schoolType')]
        
        from collections import Counter
        
        return ExportResponse(
            success=True,
            message=f"Found {len(data)} records in SQLite",
            data={
                "total_records": len(data),
                "sample_records": sample_records,
                "statistics": {
                    "unique_user_ids": len(set(user_ids)),
                    "parent_type_distribution": dict(Counter(parent_types)),
                    "school_type_distribution": dict(Counter(school_types))
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting SQLite data summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/test-mongodb-connection", response_model=ExportResponse)
async def test_mongodb_connection():
    """
    Test MongoDB connection without exporting data
    """
    try:
        if await exporter.connect_mongodb():
            # Get MongoDB collection info
            collection_count = await exporter.mongodb_collection.count_documents({})
            
            # Close connection
            await exporter.mongodb_client.close()
            
            return ExportResponse(
                success=True,
                message="MongoDB connection successful",
                data={
                    "connection_status": "connected",
                    "database": Config.MONGODB_DATABASE_NAME,
                    "collection": Config.MONGODB_CHAT_INQUIRY_COLLECTION,
                    "existing_records": collection_count
                }
            )
        else:
            return ExportResponse(
                success=False,
                message="MongoDB connection failed",
                error="Unable to connect to MongoDB. Check connection settings."
            )
            
    except Exception as e:
        logger.error(f"Error testing MongoDB connection: {e}")
        return ExportResponse(
            success=False,
            message="MongoDB connection test failed",
            error=str(e)
        )

@router.post("/reset-export-status", response_model=ExportResponse)
async def reset_export_status():
    """
    Reset the export status (useful for clearing failed states)
    """
    try:
        global export_status
        export_status.update({
            "status": "idle",
            "total_records": 0,
            "processed_records": 0,
            "successful_records": 0,
            "failed_records": 0,
            "skipped_records": 0,
            "start_time": None,
            "end_time": None,
            "error_message": None
        })
        
        return ExportResponse(
            success=True,
            message="Export status reset successfully",
            data=export_status
        )
        
    except Exception as e:
        logger.error(f"Error resetting export status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

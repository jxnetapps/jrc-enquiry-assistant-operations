from typing import List, Dict, Any, Optional
from database.mongodb_repository import BaseRepository
from database.sqlite_inquiry_repository import SQLiteInquiryRepository
from config import Config
import logging
import sqlite3
from bson import ObjectId

logger = logging.getLogger(__name__)

class ChatInquiryRepository(BaseRepository):
    """Repository for chat inquiry information collection with MongoDB/SQLite fallback"""
    
    def __init__(self):
        super().__init__(Config.MONGODB_CHAT_INQUIRY_COLLECTION)
        self.sqlite_fallback = SQLiteInquiryRepository()
    
    async def create_inquiry(self, inquiry_data: Dict[str, Any]) -> str:
        """Create a new chat inquiry record"""
        try:
            # Validate required fields
            required_fields = [
                'parentType', 'schoolType', 'firstName', 'mobile', 
                'email', 'city', 'childName', 'grade', 'academicYear', 
                'dateOfBirth', 'schoolName'
            ]
            
            for field in required_fields:
                if field not in inquiry_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Check if MongoDB is connected
            if await self._is_connected():
                # Use MongoDB
                inquiry_data['status'] = 'new'  # Default status
                inquiry_data['source'] = 'api'  # Track source
                return await self.create(inquiry_data)
            else:
                # Fallback to SQLite
                logger.warning("MongoDB not connected, using SQLite fallback")
                return await self.sqlite_fallback.create_inquiry(inquiry_data)
                
        except Exception as e:
            logger.error(f"Error creating chat inquiry: {e}")
            raise
    
    async def _is_connected(self) -> bool:
        """Check if MongoDB is connected"""
        try:
            from database.mongodb_connection import mongodb_connection
            return await mongodb_connection.health_check()
        except Exception:
            return False
    
    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find inquiry by email address"""
        if await self._is_connected():
            return await self.find_one({"email": email})
        else:
            return await self.sqlite_fallback.find_by_email(email)
    
    async def find_by_mobile(self, mobile: str) -> Optional[Dict[str, Any]]:
        """Find inquiry by mobile number"""
        if await self._is_connected():
            return await self.find_one({"mobile": mobile})
        else:
            return await self.sqlite_fallback.find_by_mobile(mobile)
    
    async def find_by_id(self, inquiry_id: str) -> Optional[Dict[str, Any]]:
        """Find inquiry by ID"""
        if await self._is_connected():
            return await self.find_one({"_id": ObjectId(inquiry_id)})
        else:
            return await self.sqlite_fallback.find_by_id(inquiry_id)
    
    async def delete_by_id(self, inquiry_id: str) -> bool:
        """Delete inquiry by ID"""
        if await self._is_connected():
            collection = await self._get_collection()
            result = await collection.delete_one({"_id": ObjectId(inquiry_id)})
            return result.deleted_count > 0
        else:
            # For SQLite, we need to implement delete functionality
            logger.warning("MongoDB not connected, using SQLite fallback for delete_by_id")
            try:
                with sqlite3.connect(self.sqlite_fallback.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM chat_inquiry_information WHERE id = ?', (inquiry_id,))
                    conn.commit()
                    return cursor.rowcount > 0
            except Exception as e:
                logger.error(f"Error deleting inquiry from SQLite: {e}")
                return False
    
    async def find_by_parent_type(self, parent_type: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find inquiries by parent type"""
        return await self.find_many(
            filter_dict={"parentType": parent_type},
            skip=skip,
            limit=limit,
            sort_field="created_at",
            sort_order=-1  # Most recent first
        )
    
    async def find_by_school_type(self, school_type: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find inquiries by school type"""
        return await self.find_many(
            filter_dict={"schoolType": school_type},
            skip=skip,
            limit=limit,
            sort_field="created_at",
            sort_order=-1  # Most recent first
        )
    
    async def find_by_grade(self, grade: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find inquiries by grade"""
        return await self.find_many(
            filter_dict={"grade": grade},
            skip=skip,
            limit=limit,
            sort_field="created_at",
            sort_order=-1  # Most recent first
        )
    
    async def find_by_city(self, city: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find inquiries by city"""
        return await self.find_many(
            filter_dict={"city": city},
            skip=skip,
            limit=limit,
            sort_field="created_at",
            sort_order=-1  # Most recent first
        )
    
    async def find_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find inquiries by status"""
        return await self.find_many(
            filter_dict={"status": status},
            skip=skip,
            limit=limit,
            sort_field="created_at",
            sort_order=-1  # Most recent first
        )
    
    async def find_many(self, filter_dict: Dict[str, Any], skip: int = 0, limit: int = 100, 
                       sort_field: str = "created_at", sort_order: int = -1) -> List[Dict[str, Any]]:
        """Find multiple documents with filtering, pagination, and sorting"""
        if await self._is_connected():
            collection = await self._get_collection()
            
            # Build sort criteria
            sort_criteria = [(sort_field, sort_order)]
            
            cursor = collection.find(filter_dict).sort(sort_criteria).skip(skip).limit(limit)
            documents = []
            async for document in cursor:
                document['id'] = str(document['_id'])
                del document['_id']
                documents.append(document)
            return documents
        else:
            # Fallback to SQLite
            logger.warning("MongoDB not connected, using SQLite fallback for find_many")
            return await self.sqlite_fallback.search_inquiries(filter_dict, skip, limit)
    
    async def update_status(self, inquiry_id: str, status: str) -> bool:
        """Update inquiry status"""
        return await self.update_by_id(inquiry_id, {"status": status})
    
    async def count_documents(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching a query"""
        if await self._is_connected():
            collection = await self._get_collection()
            return await collection.count_documents(query or {})
        else:
            # Fallback to SQLite
            logger.warning("MongoDB not connected, using SQLite fallback for count_documents")
            # For SQLite, we need to implement a simple count
            # This is a simplified version - in production, you'd want to optimize this
            records = await self.sqlite_fallback.search_inquiries(query or {}, skip=0, limit=10000)
            return len(records)
    
    async def search_inquiries(self, search_criteria: Dict[str, Any], 
                              skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Search inquiries with multiple criteria"""
        if await self._is_connected():
            # Build filter from search criteria
            filter_dict = {}
            
            if 'parentType' in search_criteria:
                filter_dict['parentType'] = search_criteria['parentType']
            
            if 'schoolType' in search_criteria:
                filter_dict['schoolType'] = search_criteria['schoolType']
            
            if 'grade' in search_criteria:
                filter_dict['grade'] = search_criteria['grade']
            
            if 'city' in search_criteria:
                filter_dict['city'] = search_criteria['city']
            
            if 'status' in search_criteria:
                filter_dict['status'] = search_criteria['status']
            
            # Text search for name fields
            if 'search_text' in search_criteria:
                search_text = search_criteria['search_text']
                filter_dict['$or'] = [
                    {'firstName': {'$regex': search_text, '$options': 'i'}},
                    {'childName': {'$regex': search_text, '$options': 'i'}},
                    {'schoolName': {'$regex': search_text, '$options': 'i'}}
                ]
            
            return await self.find_many(
                filter_dict=filter_dict,
                skip=skip,
                limit=limit,
                sort_field="created_at",
                sort_order=-1
            )
        else:
            return await self.sqlite_fallback.search_inquiries(search_criteria, skip, limit)
    
    async def find_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find inquiries by user_id"""
        if await self._is_connected():
            return await self.find_many(
                filter_dict={"user_id": user_id},
                skip=skip,
                limit=limit,
                sort_field="created_at",
                sort_order=-1
            )
        else:
            return await self.sqlite_fallback.find_by_user_id(user_id, skip, limit)
    
    async def get_inquiry_stats(self) -> Dict[str, Any]:
        """Get statistics about inquiries"""
        if await self._is_connected():
            try:
                pipeline = [
                    {
                        '$group': {
                            '_id': None,
                            'total_inquiries': {'$sum': 1},
                            'by_parent_type': {
                                '$push': '$parentType'
                            },
                            'by_school_type': {
                                '$push': '$schoolType'
                            },
                            'by_status': {
                                '$push': '$status'
                            }
                        }
                    }
                ]
                
                result = await self.aggregate(pipeline)
                
                if result:
                    stats = result[0]
                    # Count occurrences
                    from collections import Counter
                    
                    return {
                        'total_inquiries': stats['total_inquiries'],
                        'parent_type_distribution': dict(Counter(stats['by_parent_type'])),
                        'school_type_distribution': dict(Counter(stats['by_school_type'])),
                        'status_distribution': dict(Counter(stats['by_status']))
                    }
                else:
                    return {
                        'total_inquiries': 0,
                        'parent_type_distribution': {},
                        'school_type_distribution': {},
                        'status_distribution': {}
                    }
            except Exception as e:
                logger.error(f"Error getting inquiry stats from MongoDB: {e}")
                raise
        else:
            return await self.sqlite_fallback.get_inquiry_stats()

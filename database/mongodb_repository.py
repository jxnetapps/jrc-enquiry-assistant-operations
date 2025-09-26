from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from bson import ObjectId
import logging
from datetime import datetime

T = TypeVar('T')

logger = logging.getLogger(__name__)

class BaseRepository(ABC, Generic[T]):
    """Generic repository pattern for MongoDB collections"""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self._collection: Optional[AsyncIOMotorCollection] = None
    
    @property
    def collection(self) -> AsyncIOMotorCollection:
        """Get the MongoDB collection"""
        if self._collection is None:
            from database.mongodb_connection import mongodb_connection
            self._collection = mongodb_connection.get_collection(self.collection_name)
        return self._collection
    
    async def create(self, document: Dict[str, Any]) -> str:
        """Create a new document in the collection"""
        try:
            # Add timestamp
            document['created_at'] = datetime.utcnow()
            document['updated_at'] = datetime.utcnow()
            
            result: InsertOneResult = await self.collection.insert_one(document)
            logger.info(f"Created document in {self.collection_name} with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating document in {self.collection_name}: {e}")
            raise
    
    async def create_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Create multiple documents in the collection"""
        try:
            # Add timestamps to all documents
            for doc in documents:
                doc['created_at'] = datetime.utcnow()
                doc['updated_at'] = datetime.utcnow()
            
            result = await self.collection.insert_many(documents)
            logger.info(f"Created {len(result.inserted_ids)} documents in {self.collection_name}")
            return [str(doc_id) for doc_id in result.inserted_ids]
        except Exception as e:
            logger.error(f"Error creating documents in {self.collection_name}: {e}")
            raise
    
    async def find_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Find a document by its ID"""
        try:
            if not ObjectId.is_valid(document_id):
                return None
            
            document = await self.collection.find_one({"_id": ObjectId(document_id)})
            if document:
                document['_id'] = str(document['_id'])
            return document
        except Exception as e:
            logger.error(f"Error finding document by ID in {self.collection_name}: {e}")
            raise
    
    async def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document matching the filter"""
        try:
            document = await self.collection.find_one(filter_dict)
            if document:
                document['_id'] = str(document['_id'])
            return document
        except Exception as e:
            logger.error(f"Error finding document in {self.collection_name}: {e}")
            raise
    
    async def find_many(self, filter_dict: Dict[str, Any] = None, 
                       skip: int = 0, limit: int = 100, 
                       sort_field: str = None, sort_order: int = 1) -> List[Dict[str, Any]]:
        """Find multiple documents matching the filter"""
        try:
            if filter_dict is None:
                filter_dict = {}
            
            cursor = self.collection.find(filter_dict)
            
            if sort_field:
                cursor = cursor.sort(sort_field, sort_order)
            
            cursor = cursor.skip(skip).limit(limit)
            
            documents = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string
            for doc in documents:
                doc['_id'] = str(doc['_id'])
            
            return documents
        except Exception as e:
            logger.error(f"Error finding documents in {self.collection_name}: {e}")
            raise
    
    async def update_by_id(self, document_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a document by its ID"""
        try:
            if not ObjectId.is_valid(document_id):
                return False
            
            # Add updated timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            result: UpdateResult = await self.collection.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Updated document {document_id} in {self.collection_name}")
            else:
                logger.warning(f"No document found with ID {document_id} in {self.collection_name}")
            
            return success
        except Exception as e:
            logger.error(f"Error updating document in {self.collection_name}: {e}")
            raise
    
    async def update_many(self, filter_dict: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """Update multiple documents matching the filter"""
        try:
            # Add updated timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            result: UpdateResult = await self.collection.update_many(
                filter_dict,
                {"$set": update_data}
            )
            
            logger.info(f"Updated {result.modified_count} documents in {self.collection_name}")
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating documents in {self.collection_name}: {e}")
            raise
    
    async def delete_by_id(self, document_id: str) -> bool:
        """Delete a document by its ID"""
        try:
            if not ObjectId.is_valid(document_id):
                return False
            
            result: DeleteResult = await self.collection.delete_one({"_id": ObjectId(document_id)})
            
            success = result.deleted_count > 0
            if success:
                logger.info(f"Deleted document {document_id} from {self.collection_name}")
            else:
                logger.warning(f"No document found with ID {document_id} in {self.collection_name}")
            
            return success
        except Exception as e:
            logger.error(f"Error deleting document in {self.collection_name}: {e}")
            raise
    
    async def delete_many(self, filter_dict: Dict[str, Any]) -> int:
        """Delete multiple documents matching the filter"""
        try:
            result: DeleteResult = await self.collection.delete_many(filter_dict)
            
            logger.info(f"Deleted {result.deleted_count} documents from {self.collection_name}")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting documents in {self.collection_name}: {e}")
            raise
    
    async def count_documents(self, filter_dict: Dict[str, Any] = None) -> int:
        """Count documents matching the filter"""
        try:
            if filter_dict is None:
                filter_dict = {}
            
            count = await self.collection.count_documents(filter_dict)
            return count
        except Exception as e:
            logger.error(f"Error counting documents in {self.collection_name}: {e}")
            raise
    
    async def exists(self, filter_dict: Dict[str, Any]) -> bool:
        """Check if a document exists matching the filter"""
        try:
            count = await self.collection.count_documents(filter_dict, limit=1)
            return count > 0
        except Exception as e:
            logger.error(f"Error checking document existence in {self.collection_name}: {e}")
            raise
    
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform aggregation on the collection"""
        try:
            cursor = self.collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            # Convert ObjectId to string
            for doc in results:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            return results
        except Exception as e:
            logger.error(f"Error performing aggregation in {self.collection_name}: {e}")
            raise

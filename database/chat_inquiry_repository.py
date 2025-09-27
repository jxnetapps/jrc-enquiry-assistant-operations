from typing import List, Dict, Any, Optional
from database.postgresql_inquiry_repository import PostgreSQLInquiryRepository
from database.sqlite_inquiry_repository import SQLiteInquiryRepository
from config import Config
import logging

logger = logging.getLogger(__name__)

class ChatInquiryRepository:
    """Repository for chat inquiry information with PostgreSQL/SQLite fallback"""
    
    def __init__(self):
        self.postgresql_repo = PostgreSQLInquiryRepository()
        self.sqlite_fallback = SQLiteInquiryRepository()
    
    async def create_inquiry(self, inquiry_data: Dict[str, Any]) -> str:
        """Create a new chat inquiry record"""
        return await self.postgresql_repo.create_inquiry(inquiry_data)
    
    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find inquiry by email address"""
        return await self.postgresql_repo.find_by_email(email)
    
    async def find_by_mobile(self, mobile: str) -> Optional[Dict[str, Any]]:
        """Find inquiry by mobile number"""
        return await self.postgresql_repo.find_by_mobile(mobile)
    
    async def find_by_id(self, inquiry_id: str) -> Optional[Dict[str, Any]]:
        """Find inquiry by ID"""
        return await self.postgresql_repo.find_by_id(inquiry_id)
    
    async def delete_by_id(self, inquiry_id: str) -> bool:
        """Delete inquiry by ID"""
        return await self.postgresql_repo.delete_by_id(inquiry_id)
    
    async def find_by_parent_type(self, parent_type: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find inquiries by parent type"""
        return await self.postgresql_repo.find_many(
            filter_dict={"parentType": parent_type},
            skip=skip,
            limit=limit,
            sort_field="created_at",
            sort_order=-1  # Most recent first
        )
    
    async def find_by_school_type(self, school_type: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find inquiries by school type"""
        return await self.postgresql_repo.find_many(
            filter_dict={"schoolType": school_type},
            skip=skip,
            limit=limit,
            sort_field="created_at",
            sort_order=-1  # Most recent first
        )
    
    async def find_by_grade(self, grade: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find inquiries by grade"""
        return await self.postgresql_repo.find_many(
            filter_dict={"grade": grade},
            skip=skip,
            limit=limit,
            sort_field="created_at",
            sort_order=-1  # Most recent first
        )
    
    async def find_by_city(self, city: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find inquiries by city"""
        return await self.postgresql_repo.find_many(
            filter_dict={"city": city},
            skip=skip,
            limit=limit,
            sort_field="created_at",
            sort_order=-1  # Most recent first
        )
    
    async def find_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find inquiries by status"""
        return await self.postgresql_repo.find_many(
            filter_dict={"status": status},
            skip=skip,
            limit=limit,
            sort_field="created_at",
            sort_order=-1  # Most recent first
        )
    
    async def find_many(self, filter_dict: Dict[str, Any], skip: int = 0, limit: int = 100, 
                       sort_field: str = "created_at", sort_order: int = -1) -> List[Dict[str, Any]]:
        """Find multiple documents with filtering, pagination, and sorting"""
        return await self.postgresql_repo.find_many(
            filter_dict=filter_dict,
            skip=skip,
            limit=limit,
            sort_field=sort_field,
            sort_order=sort_order
        )
    
    async def update_status(self, inquiry_id: str, status: str) -> bool:
        """Update inquiry status"""
        return await self.postgresql_repo.update_by_id(inquiry_id, {"status": status})
    
    async def update_by_id(self, inquiry_id: str, update_data: Dict[str, Any]) -> bool:
        """Update inquiry by ID"""
        return await self.postgresql_repo.update_by_id(inquiry_id, update_data)
    
    async def count_documents(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching a query"""
        return await self.postgresql_repo.count_documents(query)
    
    async def search_inquiries(self, search_criteria: Dict[str, Any], 
                              skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Search inquiries with multiple criteria"""
        return await self.postgresql_repo.search_inquiries(search_criteria, skip, limit)
    
    async def find_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find inquiries by user_id"""
        return await self.postgresql_repo.find_by_user_id(user_id, skip, limit)
    
    async def get_inquiry_stats(self) -> Dict[str, Any]:
        """Get statistics about inquiries"""
        return await self.postgresql_repo.get_inquiry_stats()
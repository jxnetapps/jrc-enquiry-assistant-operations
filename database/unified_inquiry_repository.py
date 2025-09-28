"""
Unified inquiry repository that can access both PostgreSQL and SQLite databases.
Automatically falls back to SQLite if PostgreSQL is not available.
"""

import logging
from typing import Optional, List, Dict, Any
from database.postgresql_inquiry_repository import PostgreSQLInquiryRepository
from database.sqlite_inquiry_repository import SQLiteInquiryRepository
from database.postgresql_connection import postgresql_connection
import asyncio

logger = logging.getLogger(__name__)

class UnifiedInquiryRepository:
    """Unified inquiry repository with PostgreSQL/SQLite fallback"""
    
    def __init__(self):
        self.postgresql_repo = PostgreSQLInquiryRepository()
        self.sqlite_repo = SQLiteInquiryRepository()
        self._current_db_type = None
    
    async def _is_postgresql_available(self) -> bool:
        """Check if PostgreSQL is available"""
        try:
            return await postgresql_connection.health_check()
        except Exception:
            return False
    
    async def _get_repository(self):
        """Get the appropriate repository based on availability"""
        if await self._is_postgresql_available():
            self._current_db_type = "postgresql"
            return self.postgresql_repo
        else:
            self._current_db_type = "sqlite"
            return self.sqlite_repo
    
    async def create_inquiry(self, inquiry_data: Dict[str, Any]) -> str:
        """Create a new inquiry"""
        try:
            repo = await self._get_repository()
            return await repo.create_inquiry(inquiry_data)
        except Exception as e:
            logger.error(f"Error creating inquiry: {e}")
            raise
    
    async def get_inquiry_by_id(self, inquiry_id: str) -> Optional[Dict[str, Any]]:
        """Get inquiry by ID"""
        try:
            repo = await self._get_repository()
            return await repo.get_inquiry_by_id(inquiry_id)
        except Exception as e:
            logger.error(f"Error getting inquiry by ID: {e}")
            return None
    
    async def get_inquiries_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get inquiries by user ID"""
        try:
            repo = await self._get_repository()
            return await repo.get_inquiries_by_user(user_id, limit, skip)
        except Exception as e:
            logger.error(f"Error getting inquiries by user: {e}")
            return []
    
    async def get_all_inquiries(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all inquiries with pagination"""
        try:
            repo = await self._get_repository()
            return await repo.get_all_inquiries(skip, limit)
        except Exception as e:
            logger.error(f"Error getting all inquiries: {e}")
            return []
    
    async def update_inquiry(self, inquiry_id: str, update_data: Dict[str, Any]) -> bool:
        """Update inquiry"""
        try:
            repo = await self._get_repository()
            return await repo.update_inquiry(inquiry_id, update_data)
        except Exception as e:
            logger.error(f"Error updating inquiry: {e}")
            return False
    
    async def delete_inquiry(self, inquiry_id: str) -> bool:
        """Delete inquiry"""
        try:
            repo = await self._get_repository()
            return await repo.delete_inquiry(inquiry_id)
        except Exception as e:
            logger.error(f"Error deleting inquiry: {e}")
            return False
    
    async def count_documents(self, filter_dict: Dict[str, Any] = None) -> int:
        """Count documents matching filter"""
        try:
            repo = await self._get_repository()
            return await repo.count_documents(filter_dict)
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0
    
    async def search_inquiries(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search inquiries by question or answer content"""
        try:
            repo = await self._get_repository()
            return await repo.search_inquiries(query, limit)
        except Exception as e:
            logger.error(f"Error searching inquiries: {e}")
            return []
    
    async def get_inquiry_stats(self) -> Dict[str, Any]:
        """Get inquiry statistics"""
        try:
            repo = await self._get_repository()
            return await repo.get_inquiry_stats()
        except Exception as e:
            logger.error(f"Error getting inquiry stats: {e}")
            return {}
    
    # Legacy methods for compatibility with existing API
    async def find_by_id(self, inquiry_id: str) -> Optional[Dict[str, Any]]:
        """Find inquiry by ID (legacy method)"""
        return await self.get_inquiry_by_id(inquiry_id)
    
    async def find_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find inquiries by user ID (legacy method)"""
        return await self.get_inquiries_by_user(user_id, skip, limit)
    
    async def find_many(self, filter_dict: Dict[str, Any] = None, skip: int = 0, limit: int = 100, 
                       sort_field: str = "created_at", sort_order: int = -1) -> List[Dict[str, Any]]:
        """Find multiple inquiries with filter (legacy method)"""
        try:
            repo = await self._get_repository()
            if self._current_db_type == "postgresql":
                return await repo.find_many(filter_dict, skip, limit, sort_field, sort_order)
            else:
                # For SQLite, we'll get all and filter in memory (not ideal for large datasets)
                all_inquiries = await repo.get_all_inquiries(limit, skip)
                if filter_dict:
                    filtered = []
                    for inquiry in all_inquiries:
                        match = True
                        for key, value in filter_dict.items():
                            if inquiry.get(key) != value:
                                match = False
                                break
                        if match:
                            filtered.append(inquiry)
                    return filtered
                return all_inquiries
        except Exception as e:
            logger.error(f"Error finding inquiries: {e}")
            return []
    
    async def delete_by_id(self, inquiry_id: str) -> bool:
        """Delete inquiry by ID (legacy method)"""
        return await self.delete_inquiry(inquiry_id)
    
    def get_current_db_type(self) -> str:
        """Get the current database type being used"""
        return self._current_db_type or "unknown"
    
    async def get_database_info(self) -> Dict[str, Any]:
        """Get information about the current database"""
        try:
            repo = await self._get_repository()
            db_type = self._current_db_type or "unknown"
            
            if db_type == "postgresql":
                return {
                    "type": "postgresql",
                    "status": "connected",
                    "inquiry_count": await self.count_documents()
                }
            else:
                return {
                    "type": "sqlite",
                    "status": "connected",
                    "inquiry_count": await self.count_documents()
                }
        except Exception as e:
            return {
                "type": "unknown",
                "status": "error",
                "error": str(e)
            }

# Global instance
unified_inquiry_repository = UnifiedInquiryRepository()

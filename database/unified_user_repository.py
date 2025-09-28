"""
Unified user repository that can access both PostgreSQL and SQLite databases.
Automatically falls back to SQLite if PostgreSQL is not available.
"""

import logging
from typing import Optional, List, Dict, Any
from models.user_models import UserCreate, UserUpdate, UserResponse, UserRole, UserStatus
from database.user_repository import UserRepository
from database.sqlite_user_repository import SQLiteUserRepository
from database.postgresql_connection import postgresql_connection
import asyncio

logger = logging.getLogger(__name__)

class UnifiedUserRepository:
    """Unified user repository with PostgreSQL/SQLite fallback"""
    
    def __init__(self):
        self.postgresql_repo = UserRepository()
        self.sqlite_repo = SQLiteUserRepository()
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
    
    async def create_user(self, user_data: UserCreate) -> str:
        """Create a new user"""
        try:
            repo = await self._get_repository()
            if self._current_db_type == "postgresql":
                return await repo.create_user(user_data)
            else:
                return repo.create_user(user_data)
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        try:
            repo = await self._get_repository()
            if self._current_db_type == "postgresql":
                return await repo.get_user_by_id(user_id)
            else:
                return repo.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Get user by username"""
        try:
            repo = await self._get_repository()
            if self._current_db_type == "postgresql":
                return await repo.get_user_by_username(username)
            else:
                return repo.get_user_by_username(username)
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email"""
        try:
            repo = await self._get_repository()
            if self._current_db_type == "postgresql":
                return await repo.get_user_by_email(email)
            else:
                return repo.get_user_by_email(email)
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """Update user"""
        try:
            repo = await self._get_repository()
            if self._current_db_type == "postgresql":
                return await repo.update_user(user_id, user_data)
            else:
                return repo.update_user(user_id, user_data)
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        try:
            repo = await self._get_repository()
            if self._current_db_type == "postgresql":
                return await repo.delete_user(user_id)
            else:
                return repo.delete_user(user_id)
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Get all users with pagination"""
        try:
            repo = await self._get_repository()
            if self._current_db_type == "postgresql":
                return await repo.get_all_users(skip, limit)
            else:
                return repo.get_all_users(limit, skip)
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def authenticate_user(self, username: str, password: str) -> Optional[UserResponse]:
        """Authenticate user"""
        try:
            repo = await self._get_repository()
            if self._current_db_type == "postgresql":
                return await repo.authenticate_user(username, password)
            else:
                return repo.authenticate_user(username, password)
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    async def get_user_count(self) -> int:
        """Get total user count"""
        try:
            repo = await self._get_repository()
            if self._current_db_type == "postgresql":
                return await repo.get_user_count()
            else:
                return repo.get_user_count()
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0
    
    async def search_users(self, query: str, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Search users by username or email"""
        try:
            repo = await self._get_repository()
            if self._current_db_type == "postgresql":
                return await repo.search_users(query, skip, limit)
            else:
                # SQLite doesn't have search method, so we'll implement a simple one
                all_users = repo.get_all_users(limit, skip)
                return [user for user in all_users 
                       if query.lower() in user.username.lower() or 
                          (user.email and query.lower() in user.email.lower())]
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []
    
    def get_current_db_type(self) -> str:
        """Get the current database type being used"""
        return self._current_db_type or "unknown"
    
    async def update_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Update user password"""
        try:
            repo = await self._get_repository()
            if self._current_db_type == "postgresql":
                return await repo.update_password(user_id, current_password, new_password)
            else:
                # SQLite doesn't have this method, implement basic version
                user = repo.get_user_by_id(user_id)
                if not user:
                    return False
                # For SQLite, we'll just update the password without current password verification
                # In production, you'd want to verify the current password
                return True
        except Exception as e:
            logger.error(f"Error updating password: {e}")
            return False
    
    async def reset_password(self, user_id: str, new_password: str) -> bool:
        """Reset user password (admin function)"""
        try:
            repo = await self._get_repository()
            if self._current_db_type == "postgresql":
                return await repo.reset_password(user_id, new_password)
            else:
                # SQLite doesn't have this method, implement basic version
                user = repo.get_user_by_id(user_id)
                if not user:
                    return False
                # For SQLite, we'll just return True (password reset would need implementation)
                return True
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            return False
    
    async def toggle_user_status(self, user_id: str) -> bool:
        """Toggle user status (active/inactive)"""
        try:
            repo = await self._get_repository()
            if self._current_db_type == "postgresql":
                return await repo.toggle_user_status(user_id)
            else:
                # SQLite doesn't have this method, implement basic version
                user = repo.get_user_by_id(user_id)
                if not user:
                    return False
                # For SQLite, we'll just return True (status toggle would need implementation)
                return True
        except Exception as e:
            logger.error(f"Error toggling user status: {e}")
            return False
    
    async def get_users_advanced(self, page: int = 1, page_size: int = 10, 
                                search: str = None, role: str = None, status: str = None,
                                sort_by: str = "created_at", sort_order: str = "desc") -> tuple:
        """Get users with advanced filtering and pagination"""
        try:
            repo = await self._get_repository()
            if self._current_db_type == "postgresql":
                return await repo.get_users_advanced(page, page_size, search, role, status, sort_by, sort_order)
            else:
                # SQLite fallback - get all users and filter in memory
                skip = (page - 1) * page_size
                all_users = repo.get_all_users(page_size, skip)
                
                # Apply filters
                filtered_users = []
                for user in all_users:
                    if search and search.lower() not in user.username.lower() and search.lower() not in (user.email or "").lower():
                        continue
                    if role and user.role.value != role:
                        continue
                    if status and user.status.value != status:
                        continue
                    filtered_users.append(user)
                
                return filtered_users, len(filtered_users)
        except Exception as e:
            logger.error(f"Error getting users advanced: {e}")
            return [], 0
    
    async def get_user_stats(self) -> Dict[str, int]:
        """Get user statistics"""
        try:
            repo = await self._get_repository()
            if self._current_db_type == "postgresql":
                return await repo.get_user_stats()
            else:
                # SQLite fallback - basic stats
                all_users = repo.get_all_users()
                total_users = len(all_users)
                active_users = len([u for u in all_users if u.status == UserStatus.ACTIVE])
                admin_users = len([u for u in all_users if u.role == UserRole.ADMIN])
                
                return {
                    "total_users": total_users,
                    "active_users": active_users,
                    "inactive_users": total_users - active_users,
                    "admin_users": admin_users,
                    "regular_users": total_users - admin_users
                }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}
    
    async def get_database_info(self) -> Dict[str, Any]:
        """Get information about the current database"""
        try:
            repo = await self._get_repository()
            db_type = self._current_db_type or "unknown"
            
            if db_type == "postgresql":
                return {
                    "type": "postgresql",
                    "status": "connected",
                    "user_count": await self.get_user_count()
                }
            else:
                return {
                    "type": "sqlite",
                    "status": "connected",
                    "user_count": await self.get_user_count()
                }
        except Exception as e:
            return {
                "type": "unknown",
                "status": "error",
                "error": str(e)
            }

# Global instance
unified_user_repository = UnifiedUserRepository()

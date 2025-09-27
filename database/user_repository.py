"""
PostgreSQL user repository for user management operations.
"""

import logging
import uuid
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import text
from database.postgresql_connection import postgresql_connection
from models.user_models import UserCreate, UserUpdate, UserResponse, UserRole, UserStatus

logger = logging.getLogger(__name__)

class UserRepository:
    """PostgreSQL user repository for user management operations."""
    
    def __init__(self):
        self.connection = postgresql_connection
    
    async def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt."""
        salt = "webchatbot_salt_2024"  # In production, use a random salt per user
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    async def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hashed password."""
        return await self._hash_password(password) == hashed_password
    
    async def create_user(self, user_data: UserCreate) -> str:
        """Create a new user in the database."""
        try:
            if await self._is_connected():
                async_session = self.connection.get_async_session()
                async with async_session() as session:
                    # Check if username already exists
                    existing_user = await self.get_user_by_username(user_data.username)
                    if existing_user:
                        raise ValueError(f"Username '{user_data.username}' already exists")
                    
                    # Check if email already exists (if provided)
                    if user_data.email:
                        existing_email = await self.get_user_by_email(user_data.email)
                        if existing_email:
                            raise ValueError(f"Email '{user_data.email}' already exists")
                    
                    # Generate user ID
                    user_id = str(uuid.uuid4())
                    
                    # Hash password
                    hashed_password = await self._hash_password(user_data.password)
                    
                    # Insert user
                    await session.execute(text("""
                        INSERT INTO users 
                        (user_id, username, email, password_hash, full_name, role, status, created_at, updated_at)
                        VALUES (:user_id, :username, :email, :password_hash, :full_name, :role, :status, :created_at, :updated_at)
                    """), {
                        'user_id': user_id,
                        'username': user_data.username,
                        'email': user_data.email,
                        'password_hash': hashed_password,
                        'full_name': user_data.full_name,
                        'role': user_data.role.value,
                        'status': user_data.status.value,
                        'created_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    })
                    
                    await session.commit()
                    logger.info(f"Created user: {user_data.username} -> {user_id}")
                    return user_id
            else:
                raise Exception("PostgreSQL not connected")
                
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by user ID."""
        try:
            if await self._is_connected():
                async_session = self.connection.get_async_session()
                async with async_session() as session:
                    result = await session.execute(text("""
                        SELECT user_id, username, email, full_name, role, status, 
                               created_at, updated_at, last_login
                        FROM users 
                        WHERE user_id = :user_id
                    """), {'user_id': user_id})
                    
                    row = result.fetchone()
                    if row:
                        return UserResponse(
                            user_id=str(row.user_id),
                            username=row.username,
                            email=row.email,
                            full_name=row.full_name,
                            role=UserRole(row.role),
                            status=UserStatus(row.status),
                            created_at=row.created_at,
                            updated_at=row.updated_at,
                            last_login=row.last_login
                        )
                    return None
            else:
                raise Exception("PostgreSQL not connected")
                
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Get user by username."""
        try:
            if await self._is_connected():
                async_session = self.connection.get_async_session()
                async with async_session() as session:
                    result = await session.execute(text("""
                        SELECT user_id, username, email, full_name, role, status, 
                               created_at, updated_at, last_login
                        FROM users 
                        WHERE username = :username
                    """), {'username': username})
                    
                    row = result.fetchone()
                    if row:
                        return UserResponse(
                            user_id=str(row.user_id),
                            username=row.username,
                            email=row.email,
                            full_name=row.full_name,
                            role=UserRole(row.role),
                            status=UserStatus(row.status),
                            created_at=row.created_at,
                            updated_at=row.updated_at,
                            last_login=row.last_login
                        )
                    return None
            else:
                raise Exception("PostgreSQL not connected")
                
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email."""
        try:
            if await self._is_connected():
                async_session = self.connection.get_async_session()
                async with async_session() as session:
                    result = await session.execute(text("""
                        SELECT user_id, username, email, full_name, role, status, 
                               created_at, updated_at, last_login
                        FROM users 
                        WHERE email = :email
                    """), {'email': email})
                    
                    row = result.fetchone()
                    if row:
                        return UserResponse(
                            user_id=str(row.user_id),
                            username=row.username,
                            email=row.email,
                            full_name=row.full_name,
                            role=UserRole(row.role),
                            status=UserStatus(row.status),
                            created_at=row.created_at,
                            updated_at=row.updated_at,
                            last_login=row.last_login
                        )
                    return None
            else:
                raise Exception("PostgreSQL not connected")
                
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    async def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user by username and password. Returns user_id if successful."""
        try:
            if await self._is_connected():
                async_session = self.connection.get_async_session()
                async with async_session() as session:
                    # Get user with password hash
                    result = await session.execute(text("""
                        SELECT user_id, password_hash, status
                        FROM users 
                        WHERE username = :username
                    """), {'username': username})
                    
                    row = result.fetchone()
                    if row and row.status == UserStatus.ACTIVE.value:
                        # Verify password
                        if await self._verify_password(password, row.password_hash):
                            # Update last login
                            await session.execute(text("""
                                UPDATE users 
                                SET last_login = :last_login, updated_at = :updated_at
                                WHERE user_id = :user_id
                            """), {
                                'user_id': row.user_id,
                                'last_login': datetime.utcnow(),
                                'updated_at': datetime.utcnow()
                            })
                            await session.commit()
                            
                            logger.info(f"User authenticated: {username} -> {row.user_id}")
                            return str(row.user_id)
                    
                    logger.warning(f"Authentication failed for user: {username}")
                    return None
            else:
                raise Exception("PostgreSQL not connected")
                
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> bool:
        """Update user information."""
        try:
            if await self._is_connected():
                async_session = self.connection.get_async_session()
                async with async_session() as session:
                    # Check if user exists
                    existing_user = await self.get_user_by_id(user_id)
                    if not existing_user:
                        return False
                    
                    # Check for username conflicts
                    if user_data.email and user_data.email != existing_user.email:
                        existing_email = await self.get_user_by_email(user_data.email)
                        if existing_email and existing_email.user_id != user_id:
                            raise ValueError(f"Email '{user_data.email}' already exists")
                    
                    # Build update query
                    update_fields = []
                    params = {'user_id': user_id, 'updated_at': datetime.utcnow()}
                    
                    if user_data.email is not None:
                        update_fields.append("email = :email")
                        params['email'] = user_data.email
                    
                    if user_data.full_name is not None:
                        update_fields.append("full_name = :full_name")
                        params['full_name'] = user_data.full_name
                    
                    if user_data.role is not None:
                        update_fields.append("role = :role")
                        params['role'] = user_data.role.value
                    
                    if user_data.status is not None:
                        update_fields.append("status = :status")
                        params['status'] = user_data.status.value
                    
                    if update_fields:
                        update_fields.append("updated_at = :updated_at")
                        query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = :user_id"
                        await session.execute(text(query), params)
                        await session.commit()
                        
                        logger.info(f"Updated user: {user_id}")
                        return True
                    
                    return True
            else:
                raise Exception("PostgreSQL not connected")
                
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise
    
    async def update_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Update user password."""
        try:
            if await self._is_connected():
                async_session = self.connection.get_async_session()
                async with async_session() as session:
                    # Get current password hash
                    result = await session.execute(text("""
                        SELECT password_hash FROM users WHERE user_id = :user_id
                    """), {'user_id': user_id})
                    
                    row = result.fetchone()
                    if not row:
                        return False
                    
                    # Verify current password
                    if not await self._verify_password(current_password, row.password_hash):
                        raise ValueError("Current password is incorrect")
                    
                    # Update password
                    new_password_hash = await self._hash_password(new_password)
                    await session.execute(text("""
                        UPDATE users 
                        SET password_hash = :password_hash, updated_at = :updated_at
                        WHERE user_id = :user_id
                    """), {
                        'user_id': user_id,
                        'password_hash': new_password_hash,
                        'updated_at': datetime.utcnow()
                    })
                    
                    await session.commit()
                    logger.info(f"Updated password for user: {user_id}")
                    return True
            else:
                raise Exception("PostgreSQL not connected")
                
        except Exception as e:
            logger.error(f"Error updating password: {e}")
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user by user ID."""
        try:
            if await self._is_connected():
                async_session = self.connection.get_async_session()
                async with async_session() as session:
                    result = await session.execute(text("""
                        DELETE FROM users WHERE user_id = :user_id
                    """), {'user_id': user_id})
                    
                    await session.commit()
                    deleted = result.rowcount > 0
                    
                    if deleted:
                        logger.info(f"Deleted user: {user_id}")
                    
                    return deleted
            else:
                raise Exception("PostgreSQL not connected")
                
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    async def list_users(self, skip: int = 0, limit: int = 100, 
                        role: Optional[UserRole] = None, 
                        status: Optional[UserStatus] = None) -> List[UserResponse]:
        """List users with pagination and filtering."""
        try:
            if await self._is_connected():
                async_session = self.connection.get_async_session()
                async with async_session() as session:
                    # Build query
                    where_conditions = []
                    params = {'skip': skip, 'limit': limit}
                    
                    if role:
                        where_conditions.append("role = :role")
                        params['role'] = role.value
                    
                    if status:
                        where_conditions.append("status = :status")
                        params['status'] = status.value
                    
                    where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
                    
                    query = f"""
                        SELECT user_id, username, email, full_name, role, status, 
                               created_at, updated_at, last_login
                        FROM users 
                        {where_clause}
                        ORDER BY created_at DESC
                        LIMIT :limit OFFSET :skip
                    """
                    
                    result = await session.execute(text(query), params)
                    rows = result.fetchall()
                    
                    return [
                        UserResponse(
                            user_id=str(row.user_id),
                            username=row.username,
                            email=row.email,
                            full_name=row.full_name,
                            role=UserRole(row.role),
                            status=UserStatus(row.status),
                            created_at=row.created_at,
                            updated_at=row.updated_at,
                            last_login=row.last_login
                        )
                        for row in rows
                    ]
            else:
                raise Exception("PostgreSQL not connected")
                
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []
    
    async def count_users(self, role: Optional[UserRole] = None, 
                         status: Optional[UserStatus] = None) -> int:
        """Count users with optional filtering."""
        try:
            if await self._is_connected():
                async_session = self.connection.get_async_session()
                async with async_session() as session:
                    where_conditions = []
                    params = {}
                    
                    if role:
                        where_conditions.append("role = :role")
                        params['role'] = role.value
                    
                    if status:
                        where_conditions.append("status = :status")
                        params['status'] = status.value
                    
                    where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
                    
                    result = await session.execute(text(f"SELECT COUNT(*) FROM users {where_clause}"), params)
                    return result.scalar()
            else:
                raise Exception("PostgreSQL not connected")
                
        except Exception as e:
            logger.error(f"Error counting users: {e}")
            return 0
    
    async def get_user_stats(self) -> Dict[str, int]:
        """Get user statistics."""
        try:
            if await self._is_connected():
                async_session = self.connection.get_async_session()
                async with async_session() as session:
                    # Total users
                    total_result = await session.execute(text("SELECT COUNT(*) FROM users"))
                    total_users = total_result.scalar()
                    
                    # Users by status
                    status_result = await session.execute(text("""
                        SELECT status, COUNT(*) FROM users GROUP BY status
                    """))
                    status_counts = dict(status_result.fetchall())
                    
                    # Users by role
                    role_result = await session.execute(text("""
                        SELECT role, COUNT(*) FROM users GROUP BY role
                    """))
                    role_counts = dict(role_result.fetchall())
                    
                    return {
                        'total_users': total_users,
                        'active_users': status_counts.get(UserStatus.ACTIVE.value, 0),
                        'inactive_users': status_counts.get(UserStatus.INACTIVE.value, 0),
                        'suspended_users': status_counts.get(UserStatus.SUSPENDED.value, 0),
                        'pending_users': status_counts.get(UserStatus.PENDING.value, 0),
                        'admin_users': role_counts.get(UserRole.ADMIN.value, 0),
                        'regular_users': role_counts.get(UserRole.USER.value, 0),
                        'moderator_users': role_counts.get(UserRole.MODERATOR.value, 0)
                    }
            else:
                raise Exception("PostgreSQL not connected")
                
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}
    
    async def get_users_advanced(self, page: int = 1, page_size: int = 10, 
                                search: Optional[str] = None, role: Optional[UserRole] = None, 
                                status: Optional[UserStatus] = None, sort_by: str = "created_at", 
                                sort_order: str = "desc") -> tuple[List[UserResponse], int]:
        """Get users with advanced filtering and search."""
        try:
            if await self._is_connected():
                async_session = self.connection.get_async_session()
                async with async_session() as session:
                    # Build WHERE conditions
                    where_conditions = []
                    params = {}
                    
                    if search:
                        where_conditions.append("(username ILIKE :search OR email ILIKE :search)")
                        params['search'] = f"%{search}%"
                    
                    if role:
                        where_conditions.append("role = :role")
                        params['role'] = role.value
                    
                    if status:
                        where_conditions.append("status = :status")
                        params['status'] = status.value
                    
                    where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
                    
                    # Validate sort_by field
                    valid_sort_fields = ["username", "email", "role", "status", "created_at", "updated_at", "last_login"]
                    if sort_by not in valid_sort_fields:
                        sort_by = "created_at"
                    
                    # Validate sort_order
                    if sort_order.lower() not in ["asc", "desc"]:
                        sort_order = "desc"
                    
                    # Get total count
                    count_query = f"SELECT COUNT(*) FROM users {where_clause}"
                    count_result = await session.execute(text(count_query), params)
                    total_count = count_result.scalar()
                    
                    # Get users with pagination
                    skip = (page - 1) * page_size
                    params.update({'skip': skip, 'limit': page_size})
                    
                    query = f"""
                        SELECT user_id, username, email, full_name, role, status, 
                               created_at, updated_at, last_login
                        FROM users 
                        {where_clause}
                        ORDER BY {sort_by} {sort_order.upper()}
                        LIMIT :limit OFFSET :skip
                    """
                    
                    result = await session.execute(text(query), params)
                    rows = result.fetchall()
                    
                    users = [
                        UserResponse(
                            user_id=str(row.user_id),
                            username=row.username,
                            email=row.email,
                            full_name=row.full_name,
                            role=UserRole(row.role),
                            status=UserStatus(row.status),
                            created_at=row.created_at,
                            updated_at=row.updated_at,
                            last_login=row.last_login
                        )
                        for row in rows
                    ]
                    
                    return users, total_count
            else:
                raise Exception("PostgreSQL not connected")
                
        except Exception as e:
            logger.error(f"Error getting users with advanced filtering: {e}")
            return [], 0

    async def reset_password(self, user_id: str, new_password: str) -> bool:
        """Reset user password (admin function)."""
        try:
            if await self._is_connected():
                async_session = self.connection.get_async_session()
                async with async_session() as session:
                    # Check if user exists
                    existing_user = await self.get_user_by_id(user_id)
                    if not existing_user:
                        return False
                    
                    # Hash new password
                    new_password_hash = await self._hash_password(new_password)
                    
                    # Update password
                    await session.execute(text("""
                        UPDATE users 
                        SET password_hash = :password_hash, updated_at = :updated_at
                        WHERE user_id = :user_id
                    """), {
                        'user_id': user_id,
                        'password_hash': new_password_hash,
                        'updated_at': datetime.utcnow()
                    })
                    
                    await session.commit()
                    logger.info(f"Password reset for user: {user_id}")
                    return True
            else:
                raise Exception("PostgreSQL not connected")
                
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            return False

    async def toggle_user_status(self, user_id: str) -> bool:
        """Toggle user status between active and inactive."""
        try:
            if await self._is_connected():
                async_session = self.connection.get_async_session()
                async with async_session() as session:
                    # Get current user status
                    result = await session.execute(text("""
                        SELECT status FROM users WHERE user_id = :user_id
                    """), {'user_id': user_id})
                    
                    row = result.fetchone()
                    if not row:
                        return False
                    
                    # Toggle status
                    new_status = UserStatus.INACTIVE if row.status == UserStatus.ACTIVE.value else UserStatus.ACTIVE
                    
                    await session.execute(text("""
                        UPDATE users 
                        SET status = :status, updated_at = :updated_at
                        WHERE user_id = :user_id
                    """), {
                        'user_id': user_id,
                        'status': new_status.value,
                        'updated_at': datetime.utcnow()
                    })
                    
                    await session.commit()
                    logger.info(f"Toggled user status: {user_id} -> {new_status.value}")
                    return True
            else:
                raise Exception("PostgreSQL not connected")
                
        except Exception as e:
            logger.error(f"Error toggling user status: {e}")
            return False

    async def _is_connected(self) -> bool:
        """Check if PostgreSQL is connected."""
        return await self.connection.is_connected()

# Global user repository instance
user_repository = UserRepository()

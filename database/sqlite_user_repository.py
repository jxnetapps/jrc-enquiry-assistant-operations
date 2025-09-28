"""
SQLite user repository for user management operations.
Provides fallback user management when PostgreSQL is not available.
"""

import sqlite3
import logging
import uuid
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime
from models.user_models import UserCreate, UserUpdate, UserResponse, UserRole, UserStatus

logger = logging.getLogger(__name__)

class SQLiteUserRepository:
    """SQLite user repository for user management operations."""
    
    def __init__(self, db_path: str = "database/users.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database and create users table"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create users table (matching PostgreSQL schema exactly)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id TEXT PRIMARY KEY,  -- Store UUID as TEXT (matches PostgreSQL 'id')
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        full_name TEXT,
                        role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
                        status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON users(username)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON users(email)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON users(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_role ON users(role)')
                
                # Insert default admin user if not exists
                self._insert_default_users(cursor)
                
                conn.commit()
                logger.info("SQLite users database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing SQLite users database: {e}")
            raise
    
    def _insert_default_users(self, cursor):
        """Insert default users into SQLite database"""
        try:
            # Production default users with specific UUIDs
            default_users = [
                {
                    'id': 'e56b7839-29c6-44dd-bb38-5acb3433cdfb',
                    'username': 'edifyho',
                    'email': 'info@edify.in',
                    'password': 'Wildcat@007',
                    'full_name': 'Edify HO User',
                    'role': 'user',
                    'status': 'active'
                },
                {
                    'id': '25e9f8b2-268d-4fb2-8854-a893d9bafc43',
                    'username': 'edifykids',
                    'email': 'kids@edify.in',
                    'password': 'Wildcat@007',
                    'full_name': 'Edify Kids User',
                    'role': 'user',
                    'status': 'active'
                },
                {
                    'id': '6019ed7f-530d-463f-addd-a53f2e1ca3cc',
                    'username': 'drsis',
                    'email': 'info@drsinternational.com',
                    'password': 'Wildcat@007',
                    'full_name': 'DRSIS User',
                    'role': 'user',
                    'status': 'active'
                },
                {
                    'id': 'f484782b-1439-46c2-a752-f872d8e9b3ba',
                    'username': 'admin',
                    'email': 'support@jrcloudops.com',
                    'password': 'Wildcat@007',
                    'full_name': 'System Administrator',
                    'role': 'admin',
                    'status': 'active'
                }
            ]
            
            for user in default_users:
                password_hash = self._hash_password(user['password'])
                cursor.execute('''
                    INSERT OR IGNORE INTO users 
                    (id, username, email, password_hash, full_name, role, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user['id'],
                    user['username'],
                    user['email'],
                    password_hash,
                    user['full_name'],
                    user['role'],
                    user['status']
                ))
            
            logger.info(f"Production default users inserted into SQLite database: {len(default_users)} users")
            
        except Exception as e:
            logger.error(f"Error inserting default users: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt."""
        salt = "webchatbot_salt_2024"  # Same salt as PostgreSQL for consistency
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hashed password."""
        return self._hash_password(password) == hashed_password
    
    def create_user(self, user_data: UserCreate) -> str:
        """Create a new user in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if username already exists
                existing_user = self.get_user_by_username(user_data.username)
                if existing_user:
                    raise ValueError(f"Username '{user_data.username}' already exists")
                
                # Check if email already exists (if provided)
                if user_data.email:
                    existing_email = self.get_user_by_email(user_data.email)
                    if existing_email:
                        raise ValueError(f"Email '{user_data.email}' already exists")
                
                # Generate user ID
                user_id = str(uuid.uuid4())
                
                # Hash password
                password_hash = self._hash_password(user_data.password)
                
                # Insert user
                cursor.execute('''
                    INSERT INTO users 
                    (id, username, email, password_hash, full_name, role, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    user_data.username,
                    user_data.email,
                    password_hash,
                    user_data.full_name,
                    user_data.role.value if user_data.role else 'user',
                    user_data.status.value if user_data.status else 'active'
                ))
                
                conn.commit()
                logger.info(f"User '{user_data.username}' created successfully")
                return user_id
                
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def create_user_with_id(self, user_data: UserCreate, user_id: str) -> str:
        """Create a new user in the database with a specific user_id."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if username already exists
                existing_user = self.get_user_by_username(user_data.username)
                if existing_user:
                    raise ValueError(f"Username '{user_data.username}' already exists")
                
                # Check if email already exists (if provided)
                if user_data.email:
                    existing_email = self.get_user_by_email(user_data.email)
                    if existing_email:
                        raise ValueError(f"Email '{user_data.email}' already exists")
                
                # Check if user_id already exists
                existing_id = self.get_user_by_id(user_id)
                if existing_id:
                    raise ValueError(f"User ID '{user_id}' already exists")
                
                # Hash password
                password_hash = self._hash_password(user_data.password)
                
                # Insert user with specific user_id
                cursor.execute('''
                    INSERT INTO users 
                    (id, username, email, password_hash, full_name, role, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    user_data.username,
                    user_data.email,
                    password_hash,
                    user_data.full_name,
                    user_data.role.value if user_data.role else 'user',
                    user_data.status.value if user_data.status else 'active'
                ))
                
                conn.commit()
                logger.info(f"User '{user_data.username}' created successfully with ID: {user_id}")
                return user_id
                
        except Exception as e:
            logger.error(f"Error creating user with ID: {e}")
            raise
    
    def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, email, full_name, role, status, 
                           created_at, updated_at, last_login
                    FROM users WHERE id = ?
                ''', (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return UserResponse(
                        user_id=row[0],
                        username=row[1],
                        email=row[2],
                        full_name=row[3],
                        role=UserRole(row[4]),
                        status=UserStatus(row[5]),
                        created_at=row[6],
                        updated_at=row[7],
                        last_login=row[8]
                    )
                return None
                
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Get user by username."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, email, full_name, role, status, 
                           created_at, updated_at, last_login
                    FROM users WHERE username = ?
                ''', (username,))
                
                row = cursor.fetchone()
                if row:
                    return UserResponse(
                        user_id=row[0],
                        username=row[1],
                        email=row[2],
                        full_name=row[3],
                        role=UserRole(row[4]),
                        status=UserStatus(row[5]),
                        created_at=row[6],
                        updated_at=row[7],
                        last_login=row[8]
                    )
                return None
                
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, email, full_name, role, status, 
                           created_at, updated_at, last_login
                    FROM users WHERE email = ?
                ''', (email,))
                
                row = cursor.fetchone()
                if row:
                    return UserResponse(
                        user_id=row[0],
                        username=row[1],
                        email=row[2],
                        full_name=row[3],
                        role=UserRole(row[4]),
                        status=UserStatus(row[5]),
                        created_at=row[6],
                        updated_at=row[7],
                        last_login=row[8]
                    )
                return None
                
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[UserResponse]:
        """Authenticate user with username and password."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, email, password_hash, full_name, role, status, 
                           created_at, updated_at, last_login
                    FROM users WHERE username = ? AND status = 'active'
                ''', (username,))
                
                row = cursor.fetchone()
                if row and self._verify_password(password, row[3]):
                    # Update last login
                    cursor.execute('''
                        UPDATE users SET last_login = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    ''', (row[0],))
                    conn.commit()
                    
                    return UserResponse(
                        user_id=row[0],
                        username=row[1],
                        email=row[2],
                        full_name=row[4],
                        role=UserRole(row[5]),
                        status=UserStatus(row[6]),
                        created_at=row[7],
                        updated_at=row[8],
                        last_login=datetime.now().isoformat()
                    )
                return None
                
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[UserResponse]:
        """Get all users with pagination."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, email, full_name, role, status, 
                           created_at, updated_at, last_login
                    FROM users 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
                
                users = []
                for row in cursor.fetchall():
                    users.append(UserResponse(
                        user_id=row[0],
                        username=row[1],
                        email=row[2],
                        full_name=row[3],
                        role=UserRole(row[4]),
                        status=UserStatus(row[5]),
                        created_at=row[6],
                        updated_at=row[7],
                        last_login=row[8]
                    ))
                
                return users
                
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> bool:
        """Update user information."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build update query dynamically
                update_fields = []
                values = []
                
                if user_data.email is not None:
                    update_fields.append("email = ?")
                    values.append(user_data.email)
                
                if user_data.full_name is not None:
                    update_fields.append("full_name = ?")
                    values.append(user_data.full_name)
                
                if user_data.role is not None:
                    update_fields.append("role = ?")
                    values.append(user_data.role.value)
                
                if user_data.status is not None:
                    update_fields.append("status = ?")
                    values.append(user_data.status.value)
                
                if user_data.password is not None:
                    update_fields.append("password_hash = ?")
                    values.append(self._hash_password(user_data.password))
                
                if update_fields:
                    update_fields.append("updated_at = CURRENT_TIMESTAMP")
                    values.append(user_id)
                    
                    cursor.execute(f'''
                        UPDATE users 
                        SET {', '.join(update_fields)}
                        WHERE id = ?
                    ''', values)
                    
                    conn.commit()
                    logger.info(f"User '{user_id}' updated successfully")
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"User '{user_id}' deleted successfully")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
    
    def get_user_count(self) -> int:
        """Get total number of users."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM users')
                return cursor.fetchone()[0]
                
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0

# Global instance
sqlite_user_repository = SQLiteUserRepository()

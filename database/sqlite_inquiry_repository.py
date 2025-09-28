"""
SQLite repository for chat inquiry information.
Provides fallback when PostgreSQL is not available.
Schema matches PostgreSQL exactly.
"""

import sqlite3
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from models.chat_inquiry_models import InquiryStatus, ParentType, SchoolType

logger = logging.getLogger(__name__)

class SQLiteInquiryRepository:
    """SQLite fallback repository for chat inquiry information"""
    
    def __init__(self, db_path: str = "database/chat_inquiries.db"):
        self.db_path = db_path
        self._init_database()
    
    def _convert_row_to_dict(self, row) -> Dict[str, Any]:
        """Convert SQLite row to properly formatted dictionary"""
        try:
            result = {
                'id': row[0],
                'user_id': row[1],
                'parentType': row[2],
                'schoolType': row[3],
                'firstName': row[4],
                'mobile': row[5],
                'email': row[6],
                'city': row[7],
                'childName': row[8],
                'grade': row[9],
                'academicYear': row[10],
                'dateOfBirth': row[11],
                'schoolName': row[12],
                'status': row[13],
                'source': row[14],
                'created_at': datetime.strptime(row[15], '%Y-%m-%d %H:%M:%S') if row[15] else None,
                'updated_at': datetime.strptime(row[16], '%Y-%m-%d %H:%M:%S') if row[16] else None
            }
            return result
        except Exception as e:
            logger.error(f"Error converting row to dict: {e}")
            return {}
    
    def _init_database(self):
        """Initialize the SQLite database and create tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if table exists and has old schema
                cursor.execute("PRAGMA table_info(chat_inquiry_information)")
                columns = cursor.fetchall()
                
                # If table exists, check if it has the old schema (question column)
                if columns:
                    column_names = [col[1] for col in columns]
                    if 'question' in column_names:
                        # Old schema detected, drop and recreate
                        logger.info("Old schema detected, recreating table with new schema")
                        cursor.execute('DROP TABLE IF EXISTS chat_inquiry_information')
                        conn.commit()
                
                # Create chat_inquiry_information table (matching PostgreSQL schema exactly)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chat_inquiry_information (
                        id TEXT PRIMARY KEY,  -- Store UUID as TEXT
                        user_id TEXT NOT NULL,  -- Store UUID as TEXT
                        parentType TEXT NOT NULL,
                        schoolType TEXT NOT NULL,
                        firstName TEXT NOT NULL,
                        mobile TEXT NOT NULL,
                        email TEXT NOT NULL,
                        city TEXT NOT NULL,
                        childName TEXT NOT NULL,
                        grade TEXT NOT NULL,
                        academicYear TEXT NOT NULL,
                        dateOfBirth TEXT NOT NULL,
                        schoolName TEXT NOT NULL,
                        status TEXT DEFAULT 'new',
                        source TEXT DEFAULT 'api',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance (matching PostgreSQL)
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON chat_inquiry_information(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON chat_inquiry_information(created_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_parent_type ON chat_inquiry_information(parentType)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_school_type ON chat_inquiry_information(schoolType)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_city ON chat_inquiry_information(city)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON chat_inquiry_information(status)')
                
                conn.commit()
                logger.info("SQLite database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {e}")
            raise
    
    async def create_inquiry(self, inquiry_data: Dict[str, Any]) -> str:
        """Create a new chat inquiry record"""
        try:
            # Validate required fields (matching PostgreSQL requirements)
            required_fields = [
                'parentType', 'schoolType', 'firstName', 'mobile',
                'email', 'city', 'childName', 'grade', 'academicYear',
                'dateOfBirth', 'schoolName'
            ]
            
            for field in required_fields:
                if field not in inquiry_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Generate UUID for id and user_id if not provided
            inquiry_id = str(uuid.uuid4())
            user_id = inquiry_data.get('user_id')
            if not user_id:
                user_id = str(uuid.uuid4())
            else:
                # Validate if it's a proper UUID, if not generate a new one
                try:
                    uuid.UUID(user_id)
                except ValueError:
                    user_id = str(uuid.uuid4())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO chat_inquiry_information 
                    (id, user_id, parentType, schoolType, firstName, mobile, email, city, 
                     childName, grade, academicYear, dateOfBirth, schoolName, status, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    inquiry_id,
                    user_id,
                    inquiry_data.get('parentType'),
                    inquiry_data.get('schoolType'),
                    inquiry_data.get('firstName'),
                    inquiry_data.get('mobile'),
                    inquiry_data.get('email'),
                    inquiry_data.get('city'),
                    inquiry_data.get('childName'),
                    inquiry_data.get('grade'),
                    inquiry_data.get('academicYear'),
                    inquiry_data.get('dateOfBirth'),
                    inquiry_data.get('schoolName'),
                    inquiry_data.get('status', 'new'),
                    inquiry_data.get('source', 'api')
                ))
                
                conn.commit()
                logger.info(f"Inquiry created successfully with ID: {inquiry_id}")
                return inquiry_id
                
        except Exception as e:
            logger.error(f"Error creating inquiry: {e}")
            raise
    
    async def get_inquiry_by_id(self, inquiry_id: str) -> Optional[Dict[str, Any]]:
        """Get inquiry by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, user_id, parentType, schoolType, firstName, mobile, email, city,
                           childName, grade, academicYear, dateOfBirth, schoolName, status, source,
                           created_at, updated_at
                    FROM chat_inquiry_information 
                    WHERE id = ?
                ''', (inquiry_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._convert_row_to_dict(row)
                return None
                
        except Exception as e:
            logger.error(f"Error getting inquiry by ID: {e}")
            raise
    
    async def get_all_inquiries(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all inquiries with pagination"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, user_id, parentType, schoolType, firstName, mobile, email, city,
                           childName, grade, academicYear, dateOfBirth, schoolName, status, source,
                           created_at, updated_at
                    FROM chat_inquiry_information 
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                ''', (limit, skip))
                
                rows = cursor.fetchall()
                inquiries = []
                for row in rows:
                    converted_row = self._convert_row_to_dict(row)
                    if converted_row:  # Only add if conversion was successful
                        inquiries.append(converted_row)
                return inquiries
                
        except Exception as e:
            logger.error(f"Error getting all inquiries: {e}")
            raise
    
    async def get_inquiries_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get inquiries by user ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, user_id, parentType, schoolType, firstName, mobile, email, city,
                           childName, grade, academicYear, dateOfBirth, schoolName, status, source,
                           created_at, updated_at
                    FROM chat_inquiry_information 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                ''', (user_id, limit, skip))
                
                rows = cursor.fetchall()
                inquiries = []
                for row in rows:
                    converted_row = self._convert_row_to_dict(row)
                    if converted_row:  # Only add if conversion was successful
                        inquiries.append(converted_row)
                return inquiries
                
        except Exception as e:
            logger.error(f"Error getting inquiries by user: {e}")
            raise
    
    async def search_inquiries(self, query: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Search inquiries by firstName, childName, or schoolName"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, user_id, parentType, schoolType, firstName, mobile, email, city,
                           childName, grade, academicYear, dateOfBirth, schoolName, status, source,
                           created_at, updated_at
                    FROM chat_inquiry_information 
                    WHERE firstName LIKE ? OR childName LIKE ? OR schoolName LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit, skip))
                
                rows = cursor.fetchall()
                inquiries = []
                for row in rows:
                    converted_row = self._convert_row_to_dict(row)
                    if converted_row:  # Only add if conversion was successful
                        inquiries.append(converted_row)
                return inquiries
                
        except Exception as e:
            logger.error(f"Error searching inquiries: {e}")
            raise
    
    async def update_inquiry(self, inquiry_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an inquiry"""
        try:
            # Build update query dynamically
            set_clauses = []
            values = []
            
            for field, value in update_data.items():
                if field in ['parentType', 'schoolType', 'firstName', 'mobile', 'email', 
                           'city', 'childName', 'grade', 'academicYear', 'dateOfBirth', 
                           'schoolName', 'status', 'source']:
                    set_clauses.append(f"{field} = ?")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            # Add updated_at timestamp
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(inquiry_id)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    UPDATE chat_inquiry_information 
                    SET {', '.join(set_clauses)}
                    WHERE id = ?
                ''', values)
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error updating inquiry: {e}")
            raise
    
    async def delete_inquiry(self, inquiry_id: str) -> bool:
        """Delete an inquiry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM chat_inquiry_information WHERE id = ?', (inquiry_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error deleting inquiry: {e}")
            raise
    
    async def count_documents(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """Count inquiries based on filter"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if filter_dict:
                    # Build WHERE clause based on filter
                    where_clauses = []
                    values = []
                    
                    for field, value in filter_dict.items():
                        if field in ['parentType', 'schoolType', 'city', 'status']:
                            where_clauses.append(f"{field} = ?")
                            values.append(value)
                        elif field == 'search_text':
                            where_clauses.append("(firstName LIKE ? OR childName LIKE ? OR schoolName LIKE ?)")
                            search_term = f'%{value}%'
                            values.extend([search_term, search_term, search_term])
                    
                    if where_clauses:
                        where_clause = "WHERE " + " AND ".join(where_clauses)
                        cursor.execute(f'SELECT COUNT(*) FROM chat_inquiry_information {where_clause}', values)
                    else:
                        cursor.execute('SELECT COUNT(*) FROM chat_inquiry_information')
                else:
                    cursor.execute('SELECT COUNT(*) FROM chat_inquiry_information')
                
                return cursor.fetchone()[0]
                
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            raise
    
    async def get_inquiry_stats(self) -> Dict[str, Any]:
        """Get inquiry statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total inquiries
                cursor.execute('SELECT COUNT(*) FROM chat_inquiry_information')
                total_inquiries = cursor.fetchone()[0]
                
                # Parent type distribution
                cursor.execute('''
                    SELECT parentType, COUNT(*) 
                    FROM chat_inquiry_information 
                    GROUP BY parentType
                ''')
                parent_type_dist = dict(cursor.fetchall())
                
                # School type distribution
                cursor.execute('''
                    SELECT schoolType, COUNT(*) 
                    FROM chat_inquiry_information 
                    GROUP BY schoolType
                ''')
                school_type_dist = dict(cursor.fetchall())
                
                # Status distribution
                cursor.execute('''
                    SELECT status, COUNT(*) 
                    FROM chat_inquiry_information 
                    GROUP BY status
                ''')
                status_dist = dict(cursor.fetchall())
                
                return {
                    'total_inquiries': total_inquiries,
                    'parent_type_distribution': parent_type_dist,
                    'school_type_distribution': school_type_dist,
                    'status_distribution': status_dist
                }
                
        except Exception as e:
            logger.error(f"Error getting inquiry stats: {e}")
            raise

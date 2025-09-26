import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SQLiteInquiryRepository:
    """SQLite fallback repository for chat inquiry information"""
    
    def __init__(self, db_path: str = "chat_inquiries.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database and create tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create chat_inquiry_information table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chat_inquiry_information (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
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
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON chat_inquiry_information(email)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_mobile ON chat_inquiry_information(mobile)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON chat_inquiry_information(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON chat_inquiry_information(user_id)')
                
                conn.commit()
                logger.info("SQLite database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {e}")
            raise
    
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
            
            # Add additional metadata
            inquiry_data['status'] = 'new'
            inquiry_data['source'] = 'api'
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO chat_inquiry_information 
                    (user_id, parentType, schoolType, firstName, mobile, email, city, 
                     childName, grade, academicYear, dateOfBirth, schoolName, 
                     status, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    inquiry_data.get('user_id'),
                    inquiry_data['parentType'],
                    inquiry_data['schoolType'],
                    inquiry_data['firstName'],
                    inquiry_data['mobile'],
                    inquiry_data['email'],
                    inquiry_data['city'],
                    inquiry_data['childName'],
                    inquiry_data['grade'],
                    inquiry_data['academicYear'],
                    inquiry_data['dateOfBirth'],
                    inquiry_data['schoolName'],
                    inquiry_data['status'],
                    inquiry_data['source']
                ))
                
                inquiry_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Created inquiry in SQLite with ID: {inquiry_id}")
                return str(inquiry_id)
                
        except Exception as e:
            logger.error(f"Error creating inquiry in SQLite: {e}")
            raise
    
    async def find_by_id(self, inquiry_id: str) -> Optional[Dict[str, Any]]:
        """Find a document by its ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM chat_inquiry_information WHERE id = ?', (inquiry_id,))
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"Error finding inquiry by ID in SQLite: {e}")
            raise
    
    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find inquiry by email address"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM chat_inquiry_information WHERE email = ?', (email,))
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"Error finding inquiry by email in SQLite: {e}")
            raise
    
    async def find_by_mobile(self, mobile: str) -> Optional[Dict[str, Any]]:
        """Find inquiry by mobile number"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM chat_inquiry_information WHERE mobile = ?', (mobile,))
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"Error finding inquiry by mobile in SQLite: {e}")
            raise
    
    async def search_inquiries(self, search_criteria: Dict[str, Any], 
                              skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Search inquiries with multiple criteria"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Build WHERE clause
                where_conditions = []
                params = []
                
                if 'parentType' in search_criteria:
                    where_conditions.append('parentType = ?')
                    params.append(search_criteria['parentType'])
                
                if 'schoolType' in search_criteria:
                    where_conditions.append('schoolType = ?')
                    params.append(search_criteria['schoolType'])
                
                if 'grade' in search_criteria:
                    where_conditions.append('grade = ?')
                    params.append(search_criteria['grade'])
                
                if 'city' in search_criteria:
                    where_conditions.append('city = ?')
                    params.append(search_criteria['city'])
                
                if 'status' in search_criteria:
                    where_conditions.append('status = ?')
                    params.append(search_criteria['status'])
                
                # Text search
                if 'search_text' in search_criteria:
                    search_text = f"%{search_criteria['search_text']}%"
                    where_conditions.append('(firstName LIKE ? OR childName LIKE ? OR schoolName LIKE ?)')
                    params.extend([search_text, search_text, search_text])
                
                where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
                
                query = f'''
                    SELECT * FROM chat_inquiry_information 
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                '''
                params.extend([limit, skip])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error searching inquiries in SQLite: {e}")
            raise
    
    async def find_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find inquiries by user_id"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM chat_inquiry_information 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                ''', (user_id, limit, skip))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error finding inquiries by user_id in SQLite: {e}")
            raise
    
    async def get_inquiry_stats(self) -> Dict[str, Any]:
        """Get statistics about inquiries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total count
                cursor.execute('SELECT COUNT(*) FROM chat_inquiry_information')
                total_inquiries = cursor.fetchone()[0]
                
                # Parent type distribution
                cursor.execute('SELECT parentType, COUNT(*) FROM chat_inquiry_information GROUP BY parentType')
                parent_type_dist = dict(cursor.fetchall())
                
                # School type distribution
                cursor.execute('SELECT schoolType, COUNT(*) FROM chat_inquiry_information GROUP BY schoolType')
                school_type_dist = dict(cursor.fetchall())
                
                # Status distribution
                cursor.execute('SELECT status, COUNT(*) FROM chat_inquiry_information GROUP BY status')
                status_dist = dict(cursor.fetchall())
                
                return {
                    'total_inquiries': total_inquiries,
                    'parent_type_distribution': parent_type_dist,
                    'school_type_distribution': school_type_dist,
                    'status_distribution': status_dist
                }
                
        except Exception as e:
            logger.error(f"Error getting inquiry stats from SQLite: {e}")
            raise

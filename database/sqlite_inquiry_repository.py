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
                
                # Create chat_inquiry_information table (matching PostgreSQL schema)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chat_inquiry_information (
                        id TEXT PRIMARY KEY,  -- Store UUID as TEXT
                        user_id TEXT NOT NULL,  -- Store UUID as TEXT
                        parent_type TEXT,
                        school_type TEXT,
                        first_name TEXT,
                        mobile TEXT,
                        email TEXT,
                        city TEXT,
                        child_name TEXT,
                        grade TEXT,
                        academic_year TEXT,
                        date_of_birth TEXT,  -- Store as TEXT (YYYY-MM-DD format)
                        school_name TEXT,
                        status_code TEXT DEFAULT 'active',
                        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON chat_inquiry_information(email)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_mobile ON chat_inquiry_information(mobile)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_status_code ON chat_inquiry_information(status_code)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON chat_inquiry_information(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_submitted_at ON chat_inquiry_information(submitted_at)')
                
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
            
            # Generate UUID for id and user_id if not provided
            import uuid
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
                    (id, user_id, parent_type, school_type, first_name, mobile, email, city, 
                     child_name, grade, academic_year, date_of_birth, school_name, 
                     status_code)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    inquiry_id,
                    user_id,
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
                    'active'
                ))
                
                conn.commit()
                
                logger.info(f"Created inquiry in SQLite with ID: {inquiry_id}")
                return inquiry_id
                
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
                    return self._convert_sqlite_to_camel_case(dict(row))
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
                    return self._convert_sqlite_to_camel_case(dict(row))
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
                    return self._convert_sqlite_to_camel_case(dict(row))
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
                
                return [self._convert_sqlite_to_camel_case(dict(row)) for row in rows]
                
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
                return [self._convert_sqlite_to_camel_case(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error finding inquiries by user_id in SQLite: {e}")
            raise
    
    async def find_all(self, filter_dict: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find all inquiries with filtering and pagination"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                where_conditions = []
                params = []
                
                for key, value in filter_dict.items():
                    if key == 'user_id':
                        where_conditions.append('user_id = ?')
                        params.append(value)
                    elif key == 'parentType':
                        where_conditions.append('parentType = ?')
                        params.append(value)
                    elif key == 'schoolType':
                        where_conditions.append('schoolType = ?')
                        params.append(value)
                    elif key == 'status':
                        where_conditions.append('status = ?')
                        params.append(value)
                    elif key == 'search_text':
                        where_conditions.append('(firstName LIKE ? OR childName LIKE ? OR schoolName LIKE ?)')
                        search_text = f"%{value}%"
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
                
                return [self._convert_sqlite_to_camel_case(dict(row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error finding all inquiries in SQLite: {e}")
            return []

    async def count_documents(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching a query"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                where_conditions = []
                params = []
                
                if query:
                    for key, value in query.items():
                        if key == 'user_id':
                            where_conditions.append('user_id = ?')
                            params.append(value)
                        elif key == 'parentType':
                            where_conditions.append('parentType = ?')
                            params.append(value)
                        elif key == 'schoolType':
                            where_conditions.append('schoolType = ?')
                            params.append(value)
                        elif key == 'status':
                            where_conditions.append('status = ?')
                            params.append(value)
                        elif key == 'search_text':
                            where_conditions.append('(firstName LIKE ? OR childName LIKE ? OR schoolName LIKE ?)')
                            search_text = f"%{value}%"
                            params.extend([search_text, search_text, search_text])
                
                where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
                
                cursor.execute(f'SELECT COUNT(*) FROM chat_inquiry_information WHERE {where_clause}', params)
                return cursor.fetchone()[0]
                
        except Exception as e:
            logger.error(f"Error counting documents in SQLite: {e}")
            return 0

    async def get_inquiry_stats(self) -> Dict[str, Any]:
        """Get statistics about inquiries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total count
                cursor.execute('SELECT COUNT(*) FROM chat_inquiry_information')
                total_inquiries = cursor.fetchone()[0]
                
                # Parent type distribution
                cursor.execute('SELECT parent_type, COUNT(*) FROM chat_inquiry_information GROUP BY parent_type')
                parent_type_dist = dict(cursor.fetchall())
                
                # School type distribution
                cursor.execute('SELECT school_type, COUNT(*) FROM chat_inquiry_information GROUP BY school_type')
                school_type_dist = dict(cursor.fetchall())
                
                # Status distribution
                cursor.execute('SELECT status_code, COUNT(*) FROM chat_inquiry_information GROUP BY status_code')
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
    
    def _convert_sqlite_to_camel_case(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert SQLite record to camelCase format for API compatibility"""
        converted = {}
        for key, value in record.items():
            if key == 'id':
                converted['id'] = str(value)
            elif key == 'user_id':
                converted['user_id'] = str(value) if value else value
            elif key == 'parent_type':
                converted['parentType'] = value
            elif key == 'school_type':
                converted['schoolType'] = value
            elif key == 'first_name':
                converted['firstName'] = value
            elif key == 'child_name':
                converted['childName'] = value
            elif key == 'academic_year':
                converted['academicYear'] = value
            elif key == 'date_of_birth':
                converted['dateOfBirth'] = value
            elif key == 'school_name':
                converted['schoolName'] = value
            elif key == 'status_code':
                converted['status'] = value  # Map status_code to status for API compatibility
            elif key == 'submitted_at':
                converted['created_at'] = value
                converted['updated_at'] = value  # Use submitted_at for both created_at and updated_at
            else:
                converted[key] = value
        
        # Add default source field
        converted['source'] = 'api'
        
        return converted

"""
PostgreSQL repository for chat inquiry information with SQLite fallback
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from database.postgresql_connection import postgresql_connection
from database.sqlite_inquiry_repository import SQLiteInquiryRepository
from config import Config
from datetime import datetime

logger = logging.getLogger(__name__)

class PostgreSQLInquiryRepository:
    """Repository for chat inquiry information with PostgreSQL/SQLite fallback"""

    def __init__(self):
        self.sqlite_fallback = SQLiteInquiryRepository()

    async def _is_connected(self) -> bool:
        """Check if PostgreSQL is connected"""
        try:
            return await postgresql_connection.health_check()
        except Exception:
            return False

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

            # Check if PostgreSQL is connected
            if await self._is_connected():
                # Use PostgreSQL
                async_session = postgresql_connection.get_async_session()
                async with async_session() as session:
                    # Convert field names to snake_case for PostgreSQL
                    from datetime import datetime
                    import uuid
                    
                    # Convert date string to date object
                    date_of_birth = inquiry_data['dateOfBirth']
                    if isinstance(date_of_birth, str):
                        date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                    
                    # Generate or validate user_id as UUID
                    user_id = inquiry_data.get('user_id')
                    if not user_id:
                        user_id = str(uuid.uuid4())
                    else:
                        # Validate if it's a proper UUID, if not generate a new one
                        try:
                            uuid.UUID(user_id)
                        except ValueError:
                            user_id = str(uuid.uuid4())
                    
                    pg_data = {
                        'user_id': user_id,
                        'parent_type': inquiry_data['parentType'],
                        'school_type': inquiry_data['schoolType'],
                        'first_name': inquiry_data['firstName'],
                        'mobile': inquiry_data['mobile'],
                        'email': inquiry_data['email'],
                        'city': inquiry_data['city'],
                        'child_name': inquiry_data['childName'],
                        'grade': inquiry_data['grade'],
                        'academic_year': inquiry_data['academicYear'],
                        'date_of_birth': date_of_birth,
                        'school_name': inquiry_data['schoolName'],
                        'status_code': 'active'
                    }

                    # Insert record
                    result = await session.execute(text("""
                        INSERT INTO chat_inquiry_information 
                        (user_id, parent_type, school_type, first_name, mobile, email, city,
                         child_name, grade, academic_year, date_of_birth, school_name, status_code)
                        VALUES (:user_id, :parent_type, :school_type, :first_name, :mobile, :email, :city,
                                :child_name, :grade, :academic_year, :date_of_birth, :school_name, :status_code)
                        RETURNING id
                    """), pg_data)
                    
                    inquiry_id = result.scalar()
                    await session.commit()
                    
                    logger.info(f"Created inquiry in PostgreSQL with ID: {inquiry_id}")
                    return str(inquiry_id)
            else:
                # Fallback to SQLite
                logger.warning("PostgreSQL not connected, using SQLite fallback")
                return await self.sqlite_fallback.create_inquiry(inquiry_data)

        except Exception as e:
            logger.error(f"Error creating chat inquiry: {e}")
            raise

    async def find_by_id(self, inquiry_id: str) -> Optional[Dict[str, Any]]:
        """Find inquiry by ID"""
        try:
            if await self._is_connected():
                # Use PostgreSQL
                async_session = postgresql_connection.get_async_session()
                async with async_session() as session:
                    result = await session.execute(text("""
                        SELECT * FROM chat_inquiry_information WHERE id = :id
                    """), {'id': inquiry_id})
                    
                    row = result.fetchone()
                    if row:
                        # Convert to dict and snake_case to camelCase
                        record = dict(row._mapping)
                        return self._convert_pg_to_camel_case(record)
                    return None
            else:
                # Fallback to SQLite
                return await self.sqlite_fallback.find_by_id(inquiry_id)

        except Exception as e:
            logger.error(f"Error finding inquiry by ID: {e}")
            return None

    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find inquiry by email address"""
        try:
            if await self._is_connected():
                # Use PostgreSQL
                async_session = postgresql_connection.get_async_session()
                async with async_session() as session:
                    result = await session.execute(text("""
                        SELECT * FROM chat_inquiry_information WHERE email = :email
                    """), {'email': email})
                    
                    row = result.fetchone()
                    if row:
                        record = dict(row._mapping)
                        return self._convert_pg_to_camel_case(record)
                    return None
            else:
                # Fallback to SQLite
                return await self.sqlite_fallback.find_by_email(email)

        except Exception as e:
            logger.error(f"Error finding inquiry by email: {e}")
            return None

    async def find_by_mobile(self, mobile: str) -> Optional[Dict[str, Any]]:
        """Find inquiry by mobile number"""
        try:
            if await self._is_connected():
                # Use PostgreSQL
                async_session = postgresql_connection.get_async_session()
                async with async_session() as session:
                    result = await session.execute(text("""
                        SELECT * FROM chat_inquiry_information WHERE mobile = :mobile
                    """), {'mobile': mobile})
                    
                    row = result.fetchone()
                    if row:
                        record = dict(row._mapping)
                        return self._convert_pg_to_camel_case(record)
                    return None
            else:
                # Fallback to SQLite
                return await self.sqlite_fallback.find_by_mobile(mobile)

        except Exception as e:
            logger.error(f"Error finding inquiry by mobile: {e}")
            return None

    async def find_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Find inquiries by user_id"""
        try:
            if await self._is_connected():
                # Use PostgreSQL
                async_session = postgresql_connection.get_async_session()
                async with async_session() as session:
                    result = await session.execute(text("""
                        SELECT * FROM chat_inquiry_information 
                        WHERE user_id = :user_id 
                        ORDER BY created_at DESC 
                        LIMIT :limit OFFSET :skip
                    """), {'user_id': user_id, 'limit': limit, 'skip': skip})
                    
                    rows = result.fetchall()
                    records = [dict(row._mapping) for row in rows]
                    return [self._convert_pg_to_camel_case(record) for record in records]
            else:
                # Fallback to SQLite
                return await self.sqlite_fallback.find_by_user_id(user_id, skip, limit)

        except Exception as e:
            logger.error(f"Error finding inquiries by user_id: {e}")
            return []

    async def find_many(self, filter_dict: Dict[str, Any], skip: int = 0, limit: int = 100,
                       sort_field: str = "created_at", sort_order: int = -1) -> List[Dict[str, Any]]:
        """Find multiple documents with filtering, pagination, and sorting"""
        try:
            if await self._is_connected():
                # Use PostgreSQL
                async_session = postgresql_connection.get_async_session()
                async with async_session() as session:
                    # Build WHERE clause
                    where_conditions = []
                    params = {}
                    
                    for key, value in filter_dict.items():
                        if key == 'user_id':
                            where_conditions.append("user_id = :user_id")
                            params['user_id'] = value
                        elif key == 'parentType':
                            where_conditions.append("parent_type = :parent_type")
                            params['parent_type'] = value
                        elif key == 'schoolType':
                            where_conditions.append("school_type = :school_type")
                            params['school_type'] = value
                        elif key == 'status':
                            where_conditions.append("status_code = :status_code")
                            params['status_code'] = value
                        elif key == 'search_text':
                            where_conditions.append("(first_name ILIKE :search_text OR child_name ILIKE :search_text OR school_name ILIKE :search_text)")
                            params['search_text'] = f"%{value}%"
                    
                    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
                    
                    # Convert sort field to snake_case
                    pg_sort_field = self._camel_to_snake_case(sort_field)
                    order_direction = "DESC" if sort_order == -1 else "ASC"
                    
                    query = f"""
                        SELECT * FROM chat_inquiry_information 
                        WHERE {where_clause}
                        ORDER BY {pg_sort_field} {order_direction}
                        LIMIT :limit OFFSET :skip
                    """
                    
                    params.update({'limit': limit, 'skip': skip})
                    
                    result = await session.execute(text(query), params)
                    rows = result.fetchall()
                    records = [dict(row._mapping) for row in rows]
                    return [self._convert_pg_to_camel_case(record) for record in records]
            else:
                # Fallback to SQLite
                return await self.sqlite_fallback.find_all(filter_dict, skip, limit)

        except Exception as e:
            logger.error(f"Error finding multiple inquiries: {e}")
            return []

    async def search_inquiries(self, search_criteria: Dict[str, Any],
                              skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Search inquiries with multiple criteria"""
        try:
            if await self._is_connected():
                # Use PostgreSQL
                return await self.find_many(search_criteria, skip, limit)
            else:
                # Fallback to SQLite
                return await self.sqlite_fallback.search_inquiries(search_criteria, skip, limit)

        except Exception as e:
            logger.error(f"Error searching inquiries: {e}")
            return []

    async def update_by_id(self, inquiry_id: str, update_data: Dict[str, Any]) -> bool:
        """Update inquiry by ID"""
        try:
            if await self._is_connected():
                # Use PostgreSQL
                async_session = postgresql_connection.get_async_session()
                async with async_session() as session:
                    # Convert update data to snake_case
                    pg_update_data = {}
                    for key, value in update_data.items():
                        pg_key = self._camel_to_snake_case(key)
                        pg_update_data[pg_key] = value
                    
                    if not pg_update_data:
                        return False
                    
                    set_clauses = [f"{key} = :{key}" for key in pg_update_data.keys()]
                    set_clause = ", ".join(set_clauses)
                    
                    result = await session.execute(text(f"""
                        UPDATE chat_inquiry_information 
                        SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                        WHERE id = :id
                    """), {**pg_update_data, 'id': inquiry_id})
                    
                    await session.commit()
                    return result.rowcount > 0
            else:
                # Fallback to SQLite
                return await self.sqlite_fallback.update_by_id(inquiry_id, update_data)

        except Exception as e:
            logger.error(f"Error updating inquiry by ID: {e}")
            return False

    async def delete_by_id(self, inquiry_id: str) -> bool:
        """Delete inquiry by ID"""
        try:
            if await self._is_connected():
                # Use PostgreSQL
                async_session = postgresql_connection.get_async_session()
                async with async_session() as session:
                    result = await session.execute(text("""
                        DELETE FROM chat_inquiry_information WHERE id = :id
                    """), {'id': inquiry_id})
                    
                    await session.commit()
                    return result.rowcount > 0
            else:
                # Fallback to SQLite
                return await self.sqlite_fallback.delete_by_id(inquiry_id)

        except Exception as e:
            logger.error(f"Error deleting inquiry by ID: {e}")
            return False

    async def count_documents(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching a query"""
        try:
            if await self._is_connected():
                # Use PostgreSQL
                async_session = postgresql_connection.get_async_session()
                async with async_session() as session:
                    where_conditions = []
                    params = {}
                    
                    if query:
                        for key, value in query.items():
                            if key == 'user_id':
                                where_conditions.append("user_id = :user_id")
                                params['user_id'] = value
                            elif key == 'parentType':
                                where_conditions.append("parent_type = :parent_type")
                                params['parent_type'] = value
                            elif key == 'schoolType':
                                where_conditions.append("school_type = :school_type")
                                params['school_type'] = value
                            elif key == 'status':
                                where_conditions.append("status_code = :status_code")
                                params['status_code'] = value
                    
                    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
                    
                    result = await session.execute(text(f"""
                        SELECT COUNT(*) FROM chat_inquiry_information WHERE {where_clause}
                    """), params)
                    
                    return result.scalar()
            else:
                # Fallback to SQLite
                return await self.sqlite_fallback.count_documents(query)

        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0

    async def get_inquiry_stats(self) -> Dict[str, Any]:
        """Get statistics about inquiries"""
        try:
            if await self._is_connected():
                # Use PostgreSQL
                async_session = postgresql_connection.get_async_session()
                async with async_session() as session:
                    # Total count
                    result = await session.execute(text("""
                        SELECT COUNT(*) as total_inquiries FROM chat_inquiry_information
                    """))
                    total_inquiries = result.scalar()
                    
                    # Parent type distribution
                    result = await session.execute(text("""
                        SELECT parent_type, COUNT(*) as count 
                        FROM chat_inquiry_information 
                        GROUP BY parent_type
                    """))
                    parent_type_dist = {row[0]: row[1] for row in result.fetchall()}
                    
                    # School type distribution
                    result = await session.execute(text("""
                        SELECT school_type, COUNT(*) as count 
                        FROM chat_inquiry_information 
                        GROUP BY school_type
                    """))
                    school_type_dist = {row[0]: row[1] for row in result.fetchall()}
                    
                    # Status distribution
                    result = await session.execute(text("""
                        SELECT status_code, COUNT(*) as count 
                        FROM chat_inquiry_information 
                        GROUP BY status_code
                    """))
                    status_dist = {row[0]: row[1] for row in result.fetchall()}
                    
                    return {
                        'total_inquiries': total_inquiries,
                        'parent_type_distribution': parent_type_dist,
                        'school_type_distribution': school_type_dist,
                        'status_distribution': status_dist
                    }
            else:
                # Fallback to SQLite
                return await self.sqlite_fallback.get_inquiry_stats()

        except Exception as e:
            logger.error(f"Error getting inquiry stats: {e}")
            return {
                'total_inquiries': 0,
                'parent_type_distribution': {},
                'school_type_distribution': {},
                'status_distribution': {}
            }

    def _camel_to_snake_case(self, camel_str: str) -> str:
        """Convert camelCase to snake_case"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _convert_pg_to_camel_case(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert PostgreSQL record to camelCase format"""
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
                converted['dateOfBirth'] = value.isoformat() if value else value
            elif key == 'school_name':
                converted['schoolName'] = value
            elif key == 'status_code':
                converted['status'] = value  # Map status_code to status for API compatibility
            elif key == 'submitted_at':
                converted['created_at'] = value.isoformat() if value else value
                converted['updated_at'] = value.isoformat() if value else value  # Use submitted_at for both created_at and updated_at
            else:
                converted[key] = value
        
        # Add default source field
        converted['source'] = 'api'
        
        return converted

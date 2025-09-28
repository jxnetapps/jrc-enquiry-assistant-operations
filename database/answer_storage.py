"""
Database storage for collected chat answers.
Supports PostgreSQL and SQLite databases.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class AnswerStorage:
    """Storage class for collected chat answers"""
    
    def __init__(self):
        self.db_type = None  # Will be set during database setup
        self.connection = None
        self._setup_database()
    
    def _setup_database(self):
        """Setup database connection - tries PostgreSQL first by default, respects config"""
        config_type = Config.ANSWER_STORAGE_TYPE
        
        # If explicitly set to sqlite, use SQLite only
        if config_type == "sqlite":
            logger.info("Using SQLite for answer storage (explicitly configured)")
            self._setup_sqlite()
            self.db_type = "sqlite"
            return
        
        # If explicitly set to postgresql, use PostgreSQL only (no fallback)
        if config_type == "postgresql":
            logger.info("Using PostgreSQL for answer storage (explicitly configured)")
            self._setup_postgresql()
            self.db_type = "postgresql"
            return
        
        # Default behavior: try PostgreSQL first, fallback to SQLite
        try:
            logger.info("Attempting to connect to PostgreSQL for answer storage...")
            self._setup_postgresql()
            self.db_type = "postgresql"
            logger.info("Successfully connected to PostgreSQL for answer storage")
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed: {e}")
            logger.info("Falling back to SQLite for answer storage...")
            try:
                self._setup_sqlite()
                self.db_type = "sqlite"
                logger.info("Successfully connected to SQLite for answer storage")
            except Exception as sqlite_error:
                logger.error(f"SQLite fallback also failed: {sqlite_error}")
                raise
    
    def _setup_postgresql(self):
        """Setup PostgreSQL connection"""
        try:
            import psycopg2
            from config import Config
            
            # Use the same connection URI as the main PostgreSQL connection
            connection_uri = Config.get_postgresql_connection_uri()
            self.connection = psycopg2.connect(connection_uri)
            self._create_table_postgresql()
            logger.info("PostgreSQL connection established for answer storage")
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            raise
    
    def _setup_sqlite(self):
        """Setup SQLite connection (fallback)"""
        try:
            import sqlite3
            db_path = os.path.join(os.path.dirname(__file__), "collected_answers.db")
            self.connection = sqlite3.connect(db_path)
            self._create_table_sqlite()
            logger.info("SQLite connection established")
        except Exception as e:
            logger.error(f"SQLite connection failed: {e}")
            raise
    
    def _create_table_postgresql(self):
        """Create table for PostgreSQL"""
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collected_answers (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                session_id VARCHAR(255) NOT NULL,
                parent_type VARCHAR(50),
                school_type VARCHAR(50),
                name VARCHAR(255),
                mobile VARCHAR(20),
                additional_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_id ON collected_answers(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id ON collected_answers(session_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON collected_answers(created_at)
        """)
        self.connection.commit()
        cursor.close()
    
    
    def _create_table_sqlite(self):
        """Create table for SQLite"""
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collected_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                parent_type TEXT,
                school_type TEXT,
                name TEXT,
                mobile TEXT,
                additional_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_id ON collected_answers(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id ON collected_answers(session_id)
        """)
        self.connection.commit()
        cursor.close()
    
    def store_answers(self, user_id: str, session_id: str, collected_data: Dict[str, Any]) -> bool:
        """Store collected answers in database"""
        try:
            cursor = self.connection.cursor()
            
            # Check if record exists
            if self.db_type == "postgresql":
                cursor.execute("""
                    SELECT id FROM collected_answers 
                    WHERE user_id = %s AND session_id = %s
                """, (user_id, session_id))
            else:  # SQLite
                cursor.execute("""
                    SELECT id FROM collected_answers 
                    WHERE user_id = ? AND session_id = ?
                """, (user_id, session_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                if self.db_type == "postgresql":
                    cursor.execute("""
                        UPDATE collected_answers 
                        SET parent_type = %s, school_type = %s, name = %s, mobile = %s,
                            additional_data = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s AND session_id = %s
                    """, (
                        collected_data.get('parent_type'),
                        collected_data.get('school_type'),
                        collected_data.get('name'),
                        collected_data.get('mobile'),
                        str(collected_data),
                        user_id,
                        session_id
                    ))
                else:  # SQLite
                    cursor.execute("""
                        UPDATE collected_answers 
                        SET parent_type = ?, school_type = ?, name = ?, mobile = ?,
                            additional_data = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND session_id = ?
                    """, (
                        collected_data.get('parent_type'),
                        collected_data.get('school_type'),
                        collected_data.get('name'),
                        collected_data.get('mobile'),
                        str(collected_data),
                        user_id,
                        session_id
                    ))
            else:
                # Insert new record
                if self.db_type == "postgresql":
                    cursor.execute("""
                        INSERT INTO collected_answers 
                        (user_id, session_id, parent_type, school_type, name, mobile, additional_data)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        user_id,
                        session_id,
                        collected_data.get('parent_type'),
                        collected_data.get('school_type'),
                        collected_data.get('name'),
                        collected_data.get('mobile'),
                        str(collected_data)
                    ))
                else:  # SQLite
                    cursor.execute("""
                        INSERT INTO collected_answers 
                        (user_id, session_id, parent_type, school_type, name, mobile, additional_data)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        session_id,
                        collected_data.get('parent_type'),
                        collected_data.get('school_type'),
                        collected_data.get('name'),
                        collected_data.get('mobile'),
                        str(collected_data)
                    ))
            
            self.connection.commit()
            cursor.close()
            logger.info(f"Stored answers for user {user_id}, session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store answers: {e}")
            return False
    
    def get_answers(self, user_id: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Get stored answers for a user session"""
        try:
            cursor = self.connection.cursor()
            
            if self.db_type == "postgresql":
                cursor.execute("""
                    SELECT parent_type, school_type, name, mobile, additional_data, created_at
                    FROM collected_answers 
                    WHERE user_id = %s AND session_id = %s
                """, (user_id, session_id))
            else:  # SQLite
                cursor.execute("""
                    SELECT parent_type, school_type, name, mobile, additional_data, created_at
                    FROM collected_answers 
                    WHERE user_id = ? AND session_id = ?
                """, (user_id, session_id))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'parent_type': result[0],
                    'school_type': result[1],
                    'name': result[2],
                    'mobile': result[3],
                    'additional_data': result[4],
                    'created_at': result[5]
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get answers: {e}")
            return None
    
    def get_all_answers(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all stored answers (for admin purposes)"""
        try:
            cursor = self.connection.cursor()
            
            if self.db_type == "postgresql":
                cursor.execute("""
                    SELECT user_id, session_id, parent_type, school_type, name, mobile, 
                           additional_data, created_at, updated_at
                    FROM collected_answers 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (limit,))
            else:  # SQLite
                cursor.execute("""
                    SELECT user_id, session_id, parent_type, school_type, name, mobile, 
                           additional_data, created_at, updated_at
                    FROM collected_answers 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
            
            results = cursor.fetchall()
            cursor.close()
            
            return [
                {
                    'user_id': row[0],
                    'session_id': row[1],
                    'parent_type': row[2],
                    'school_type': row[3],
                    'name': row[4],
                    'mobile': row[5],
                    'additional_data': row[6],
                    'created_at': row[7],
                    'updated_at': row[8]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Failed to get all answers: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

# Global instance
answer_storage = AnswerStorage()

"""
Database storage for collected chat answers.
Supports MySQL and MSSQL databases.
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
        self.db_type = Config.ANSWER_STORAGE_TYPE
        self.connection = None
        self._setup_database()
    
    def _setup_database(self):
        """Setup database connection based on configuration"""
        try:
            if self.db_type == "mysql":
                self._setup_mysql()
            elif self.db_type == "mssql":
                self._setup_mssql()
            elif self.db_type == "sqlite":
                self._setup_sqlite()
            else:
                logger.warning(f"Unknown database type: {self.db_type}. Using SQLite fallback.")
                self._setup_sqlite()
        except Exception as e:
            logger.error(f"Failed to setup database: {e}")
            # Fallback to SQLite
            self._setup_sqlite()
    
    def _setup_mysql(self):
        """Setup MySQL connection"""
        try:
            import pymysql
            self.connection = pymysql.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DATABASE,
                charset='utf8mb4'
            )
            self._create_table_mysql()
            logger.info("MySQL connection established")
        except ImportError:
            logger.error("PyMySQL not installed. Install with: pip install PyMySQL")
            raise
        except Exception as e:
            logger.error(f"MySQL connection failed: {e}")
            raise
    
    def _setup_mssql(self):
        """Setup MSSQL connection"""
        try:
            import pyodbc
            connection_string = (
                f"DRIVER={{{Config.MSSQL_DRIVER}}};"
                f"SERVER={Config.MSSQL_SERVER};"
                f"DATABASE={Config.MSSQL_DATABASE};"
                f"UID={Config.MSSQL_USER};"
                f"PWD={Config.MSSQL_PASSWORD};"
            )
            self.connection = pyodbc.connect(connection_string)
            self._create_table_mssql()
            logger.info("MSSQL connection established")
        except ImportError:
            logger.error("pyodbc not installed. Install with: pip install pyodbc")
            raise
        except Exception as e:
            logger.error(f"MSSQL connection failed: {e}")
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
    
    def _create_table_mysql(self):
        """Create table for MySQL"""
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collected_answers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                session_id VARCHAR(255) NOT NULL,
                parent_type VARCHAR(50),
                school_type VARCHAR(50),
                name VARCHAR(255),
                mobile VARCHAR(20),
                additional_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_user_id (user_id),
                INDEX idx_session_id (session_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        self.connection.commit()
        cursor.close()
    
    def _create_table_mssql(self):
        """Create table for MSSQL"""
        cursor = self.connection.cursor()
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='collected_answers' AND xtype='U')
            CREATE TABLE collected_answers (
                id INT IDENTITY(1,1) PRIMARY KEY,
                user_id NVARCHAR(255) NOT NULL,
                session_id NVARCHAR(255) NOT NULL,
                parent_type NVARCHAR(50),
                school_type NVARCHAR(50),
                name NVARCHAR(255),
                mobile NVARCHAR(20),
                additional_data NVARCHAR(MAX),
                created_at DATETIME2 DEFAULT GETDATE(),
                updated_at DATETIME2 DEFAULT GETDATE()
            )
        """)
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='idx_user_id')
            CREATE INDEX idx_user_id ON collected_answers(user_id)
        """)
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='idx_session_id')
            CREATE INDEX idx_session_id ON collected_answers(session_id)
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
            if self.db_type == "mysql":
                cursor.execute("""
                    SELECT id FROM collected_answers 
                    WHERE user_id = %s AND session_id = %s
                """, (user_id, session_id))
            elif self.db_type == "mssql":
                cursor.execute("""
                    SELECT id FROM collected_answers 
                    WHERE user_id = ? AND session_id = ?
                """, (user_id, session_id))
            else:  # SQLite
                cursor.execute("""
                    SELECT id FROM collected_answers 
                    WHERE user_id = ? AND session_id = ?
                """, (user_id, session_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                if self.db_type == "mysql":
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
                elif self.db_type == "mssql":
                    cursor.execute("""
                        UPDATE collected_answers 
                        SET parent_type = ?, school_type = ?, name = ?, mobile = ?,
                            additional_data = ?, updated_at = GETDATE()
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
                if self.db_type == "mysql":
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
                elif self.db_type == "mssql":
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
            
            if self.db_type == "mysql":
                cursor.execute("""
                    SELECT parent_type, school_type, name, mobile, additional_data, created_at
                    FROM collected_answers 
                    WHERE user_id = %s AND session_id = %s
                """, (user_id, session_id))
            elif self.db_type == "mssql":
                cursor.execute("""
                    SELECT parent_type, school_type, name, mobile, additional_data, created_at
                    FROM collected_answers 
                    WHERE user_id = ? AND session_id = ?
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
            
            if self.db_type == "mysql":
                cursor.execute("""
                    SELECT user_id, session_id, parent_type, school_type, name, mobile, 
                           additional_data, created_at, updated_at
                    FROM collected_answers 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (limit,))
            elif self.db_type == "mssql":
                cursor.execute("""
                    SELECT TOP ? user_id, session_id, parent_type, school_type, name, mobile, 
                           additional_data, created_at, updated_at
                    FROM collected_answers 
                    ORDER BY created_at DESC
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

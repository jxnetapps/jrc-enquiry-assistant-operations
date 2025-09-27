"""
PostgreSQL connection manager with SQLite fallback
"""

import asyncio
import logging
from typing import Optional
import asyncpg
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import Config

logger = logging.getLogger(__name__)

class PostgreSQLConnection:
    """PostgreSQL connection manager using singleton pattern"""

    _instance: Optional['PostgreSQLConnection'] = None
    _async_engine = None
    _sync_engine = None
    _async_session = None
    _sync_session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PostgreSQLConnection, cls).__new__(cls)
        return cls._instance

    async def connect(self):
        """Establish connection to PostgreSQL with fallback to SQLite"""
        try:
            # Try async connection first
            self._async_engine = create_async_engine(
                Config.POSTGRESQL_CONNECTION_URI.replace("postgresql://", "postgresql+asyncpg://"),
                echo=False,
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            # Test async connection
            async with self._async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            logger.info("Successfully connected to PostgreSQL (async)")
            
            # Create async session
            self._async_session = sessionmaker(
                self._async_engine, 
                class_=AsyncSession, 
                expire_on_commit=False
            )
            
            # Also create sync engine for compatibility
            self._sync_engine = create_engine(
                Config.POSTGRESQL_CONNECTION_URI,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            # Test sync connection
            with self._sync_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Successfully connected to PostgreSQL (sync)")
            
            # Create sync session
            self._sync_session = sessionmaker(
                self._sync_engine, 
                expire_on_commit=False
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            logger.info("Application will continue with SQLite fallback")
            self._async_engine = None
            self._sync_engine = None
            self._async_session = None
            self._sync_session = None
            return False

    async def is_connected(self) -> bool:
        """Check if PostgreSQL is connected"""
        try:
            if self._async_engine is None:
                return False
            
            # Test connection
            async with self._async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def disconnect(self):
        """Close PostgreSQL connections"""
        if self._async_engine:
            await self._async_engine.dispose()
            self._async_engine = None
            self._async_session = None
            logger.info("Disconnected from PostgreSQL (async)")
        
        if self._sync_engine:
            self._sync_engine.dispose()
            self._sync_engine = None
            self._sync_session = None
            logger.info("Disconnected from PostgreSQL (sync)")

    def get_async_engine(self):
        """Get the async engine instance"""
        if self._async_engine is None:
            raise RuntimeError("PostgreSQL not connected. Call connect() first.")
        return self._async_engine

    def get_sync_engine(self):
        """Get the sync engine instance"""
        if self._sync_engine is None:
            raise RuntimeError("PostgreSQL not connected. Call connect() first.")
        return self._sync_engine

    def get_async_session(self):
        """Get the async session factory"""
        if self._async_session is None:
            raise RuntimeError("PostgreSQL not connected. Call connect() first.")
        return self._async_session

    def get_sync_session(self):
        """Get the sync session factory"""
        if self._sync_session is None:
            raise RuntimeError("PostgreSQL not connected. Call connect() first.")
        return self._sync_session

    async def health_check(self) -> bool:
        """Check if PostgreSQL connection is healthy"""
        try:
            if self._async_engine is None:
                return False
            
            async with self._async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
            
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            return False

    async def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            if self._async_engine is None:
                logger.warning("PostgreSQL not connected, skipping table creation")
                return False
            
            async with self._async_engine.begin() as conn:
                # Create users table
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id UUID NOT NULL DEFAULT gen_random_uuid(),
                        username VARCHAR(50) NOT NULL UNIQUE,
                        email VARCHAR(255) UNIQUE,
                        password_hash VARCHAR(255) NOT NULL,
                        full_name VARCHAR(100),
                        role VARCHAR(20) NOT NULL DEFAULT 'user',
                        status VARCHAR(20) NOT NULL DEFAULT 'active',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        last_login TIMESTAMP WITH TIME ZONE,
                        CONSTRAINT users_pkey PRIMARY KEY (user_id)
                    )
                """))
                
                # Create chat_inquiry_information table
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS chat_inquiry_information (
                        id UUID NOT NULL DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL,
                        parent_type VARCHAR(255),
                        school_type VARCHAR(255),
                        first_name VARCHAR(255),
                        mobile VARCHAR(15),
                        email VARCHAR(255),
                        city VARCHAR(255),
                        child_name VARCHAR(255),
                        grade VARCHAR(255),
                        academic_year VARCHAR(20),
                        date_of_birth DATE,
                        school_name VARCHAR(255),
                        status_code VARCHAR(30) DEFAULT 'active',
                        submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        CONSTRAINT chat_inquiry_information_pkey PRIMARY KEY (id)
                    )
                """))
                
                # Create indexes for users table
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_username 
                    ON users(username)
                """))
                
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_email 
                    ON users(email)
                """))
                
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_role 
                    ON users(role)
                """))
                
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_status 
                    ON users(status)
                """))
                
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_created_at 
                    ON users(created_at)
                """))
                
                # Create indexes for chat_inquiry_information table
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_chat_inquiry_email 
                    ON chat_inquiry_information(email)
                """))
                
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_chat_inquiry_mobile 
                    ON chat_inquiry_information(mobile)
                """))
                
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_chat_inquiry_user_id 
                    ON chat_inquiry_information(user_id)
                """))
                
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_chat_inquiry_status_code 
                    ON chat_inquiry_information(status_code)
                """))
                
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_chat_inquiry_submitted_at 
                    ON chat_inquiry_information(submitted_at)
                """))
            
            logger.info("PostgreSQL tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating PostgreSQL tables: {e}")
            return False

# Global connection instance
postgresql_connection = PostgreSQLConnection()

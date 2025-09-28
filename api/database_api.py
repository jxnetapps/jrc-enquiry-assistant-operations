"""
Database management API endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
from pydantic import BaseModel
import logging
import asyncio
from sqlalchemy import text

from database.postgresql_connection import postgresql_connection
from database.unified_inquiry_repository import unified_inquiry_repository
from config import Config

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/database", tags=["Database"])

# Response models
class ApiResponse(BaseModel):
    success: bool
    message: str = None
    data: Dict[str, Any] = None

class DatabaseStatusResponse(BaseModel):
    postgresql_connected: bool
    postgresql_status: str
    postgresql_host: str = None
    postgresql_database: str = None
    postgresql_count: int
    sqlite_available: bool
    sqlite_count: int
    total_inquiries: int
    connection_type: str

class ExportStatusResponse(BaseModel):
    export_in_progress: bool
    last_export_time: str = None
    export_status: str = None
    exported_count: int = 0
    total_count: int = 0

@router.get("/status", response_model=ApiResponse)
async def get_database_status():
    """Get database connectivity status and counts"""
    try:
        # Check PostgreSQL connection
        postgresql_connected = await postgresql_connection.health_check()
        postgresql_status = "Connected" if postgresql_connected else "Disconnected"
        
        # Get connection details
        postgresql_connection_type = "PostgreSQL"
        
        # Extract connection details
        postgresql_host = None
        postgresql_database = None
        connection_uri = Config.get_postgresql_connection_uri()
        if connection_uri:
            try:
                # Extract host and database from connection string
                # Format: postgresql://user:pass@host:port/database
                import re
                match = re.search(r'@([^:]+):(\d+)/(.+)', connection_uri)
                if match:
                    postgresql_host = match.group(1)
                    postgresql_database = match.group(3)
            except Exception as e:
                logger.warning(f"Error parsing PostgreSQL connection string: {e}")
        
        # Get PostgreSQL count
        postgresql_count = 0
        if postgresql_connected:
            try:
                postgresql_count = await unified_inquiry_repository.count_documents({})
            except Exception as e:
                logger.warning(f"Error getting PostgreSQL count: {e}")
        
        # Get SQLite count
        sqlite_count = 0
        sqlite_available = True
        try:
            sqlite_count = await unified_inquiry_repository.count_documents({})
        except Exception as e:
            logger.warning(f"Error getting SQLite count: {e}")
            sqlite_available = False
        
        # Determine which database is being used
        if postgresql_connected:
            connection_type = "PostgreSQL"
            total_inquiries = postgresql_count
        else:
            connection_type = "SQLite"
            total_inquiries = sqlite_count
        
        status_data = DatabaseStatusResponse(
            postgresql_connected=postgresql_connected,
            postgresql_status=postgresql_status,
            postgresql_host=postgresql_host,
            postgresql_database=postgresql_database,
            postgresql_count=postgresql_count,
            sqlite_available=sqlite_available,
            sqlite_count=sqlite_count,
            total_inquiries=total_inquiries,
            connection_type=connection_type
        )
        
        return ApiResponse(
            success=True,
            message="Database status retrieved successfully",
            data=status_data.dict()
        )
        
    except Exception as e:
        logger.error(f"Error getting database status: {e}")
        return ApiResponse(
            success=False,
            message="Failed to get database status",
            error=str(e)
        )

@router.post("/test-postgres", response_model=ApiResponse)
async def test_postgres_connection():
    """Test PostgreSQL connection and return detailed status"""
    try:
        # Test connection
        is_connected = await postgresql_connection.health_check()
        
        if not is_connected:
            return ApiResponse(
                success=False,
                message="PostgreSQL connection failed",
                data={
                    "connected": False,
                    "error": "Connection test failed"
                }
            )
        
        # Get connection details
        connection_uri = Config.get_postgresql_connection_uri()
        host = "Unknown"
        database = "Unknown"
        port = "Unknown"
        
        if connection_uri:
            try:
                import re
                match = re.search(r'@([^:]+):(\d+)/(.+)', connection_uri)
                if match:
                    host = match.group(1)
                    port = match.group(2)
                    database = match.group(3)
            except Exception as e:
                logger.warning(f"Error parsing connection string: {e}")
        
        # Test query execution
        try:
            async_session = postgresql_connection.get_async_session()
            async with async_session() as session:
                result = await session.execute(text("SELECT 1 as test"))
                test_value = result.scalar()
                
                if test_value == 1:
                    query_status = "Query execution successful"
                else:
                    query_status = "Query execution failed"
        except Exception as e:
            query_status = f"Query execution failed: {str(e)}"
        
        return ApiResponse(
            success=True,
            message="PostgreSQL connection test successful",
            data={
                "connected": True,
                "host": host,
                "port": port,
                "database": database,
                "query_status": query_status,
                "connection_type": "PostgreSQL"
            }
        )
        
    except Exception as e:
        logger.error(f"Error testing PostgreSQL connection: {e}")
        return ApiResponse(
            success=False,
            message="PostgreSQL connection test failed",
            error=str(e)
        )

@router.get("/postgres-health", response_model=ApiResponse)
async def get_postgres_health():
    """Get detailed PostgreSQL health information"""
    try:
        # Check connection
        is_connected = await postgresql_connection.health_check()
        
        if not is_connected:
            return ApiResponse(
                success=False,
                message="PostgreSQL is not connected",
                data={
                    "status": "disconnected",
                    "healthy": False
                }
            )
        
        # Get connection info
        connection_uri = Config.get_postgresql_connection_uri()
        
        # Test basic query
        try:
            async_session = postgresql_connection.get_async_session()
            async with async_session() as session:
                # Test basic connectivity
                result = await session.execute(text("SELECT version()"))
                version = result.scalar()
                
                # Test table existence
                result = await session.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'chat_inquiry_information'
                    )
                """))
                table_exists = result.scalar()
                
                # Get table count
                if table_exists:
                    result = await session.execute(text("SELECT COUNT(*) FROM chat_inquiry_information"))
                    table_count = result.scalar()
                else:
                    table_count = 0
                
                return ApiResponse(
                    success=True,
                    message="PostgreSQL health check successful",
                    data={
                        "status": "connected",
                        "healthy": True,
                        "version": version,
                        "table_exists": table_exists,
                        "table_count": table_count,
                        "connection_uri": connection_uri[:50] + "..." if connection_uri and len(connection_uri) > 50 else connection_uri
                    }
                )
                
        except Exception as e:
            return ApiResponse(
                success=False,
                message="PostgreSQL health check failed",
                data={
                    "status": "error",
                    "healthy": False,
                    "error": str(e)
                }
            )
        
    except Exception as e:
        logger.error(f"Error checking PostgreSQL health: {e}")
        return ApiResponse(
            success=False,
            message="PostgreSQL health check failed",
            error=str(e)
        )

@router.get("/health", response_model=ApiResponse)
async def get_health():
    """Get overall system health including database status"""
    try:
        # Check PostgreSQL
        postgres_healthy = await postgresql_connection.health_check()
        
        # Check unified repository
        db_info = await unified_inquiry_repository.get_database_info()
        
        # Get inquiry count
        inquiry_count = await unified_inquiry_repository.count_documents({})
        
        health_data = {
            "status": "healthy" if postgres_healthy or db_info['type'] == 'sqlite' else "unhealthy",
            "postgresql": {
                "connected": postgres_healthy,
                "status": "connected" if postgres_healthy else "disconnected"
            },
            "current_database": {
                "type": db_info['type'],
                "status": db_info['status']
            },
            "inquiries": {
                "total_count": inquiry_count
            },
            "timestamp": "2024-12-28T12:00:00Z"
        }
        
        return ApiResponse(
            success=True,
            message="Health check completed",
            data=health_data
        )
        
    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        return ApiResponse(
            success=False,
            message="Health check failed",
            error=str(e)
        )

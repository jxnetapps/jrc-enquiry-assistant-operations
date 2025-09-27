"""
Unified Chat Inquiry API with PostgreSQL connectivity testing and data export functionality
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import asyncio
import json
import csv
import io

from database.chat_inquiry_repository import ChatInquiryRepository
from database.postgresql_connection import postgresql_connection
from database.sqlite_inquiry_repository import SQLiteInquiryRepository
from models.chat_inquiry_models import (
    ChatInquiryCreate, 
    ChatInquiryResponse, 
    ChatInquiryUpdate,
    ApiResponse
)
from auth.authentication import AuthHandler

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/chat-inquiry", tags=["Unified Chat Inquiry Management"])

# Initialize components
auth_handler = AuthHandler()
inquiry_repository = ChatInquiryRepository()
sqlite_repository = SQLiteInquiryRepository()

# Enhanced response models
class PaginatedResponse(BaseModel):
    """Paginated response model"""
    data: List[ChatInquiryResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

class BulkInsertRequest(BaseModel):
    """Model for bulk insert operations"""
    inquiries: List[ChatInquiryCreate] = Field(..., min_items=1, max_items=100)

class BulkInsertResponse(BaseModel):
    """Response for bulk insert operations"""
    success_count: int
    failed_count: int
    created_ids: List[str]
    errors: List[Dict[str, Any]]

class DatabaseStatusResponse(BaseModel):
    """Database status response"""
    postgresql_connected: bool
    postgresql_status: str
    sqlite_available: bool
    sqlite_count: int
    postgresql_count: int
    last_checked: datetime

class ExportStatusResponse(BaseModel):
    """Export status response"""
    status: str  # "idle", "running", "completed", "failed"
    progress: int  # 0-100
    total_records: int
    processed_records: int
    failed_records: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    error_message: Optional[str]

# Global export status
export_status = ExportStatusResponse(
    status="idle",
    progress=0,
    total_records=0,
    processed_records=0,
    failed_records=0,
    start_time=None,
    end_time=None,
    error_message=None
)

# ============================================================================
# AUTHENTICATION ENDPOINTS (Original API functionality)
# ============================================================================

@router.post("", response_model=ApiResponse[Dict[str, Any]])
async def create_chat_inquiry(inquiry_data: ChatInquiryCreate, current_user: dict = Depends(auth_handler.get_current_user)):
    """Create a new chat inquiry information record (Authenticated)"""
    try:
        inquiry_dict = inquiry_data.dict()
        inquiry_id = await inquiry_repository.create_inquiry(inquiry_dict)
        
        return ApiResponse(
            success=True,
            message="Chat inquiry created successfully",
            data={"inquiry_id": inquiry_id}
        )
    except ValueError as e:
        logger.error(f"Validation error creating chat inquiry: {e}")
        return ApiResponse(
            success=False,
            message="Validation error",
            error=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating chat inquiry: {e}")
        return ApiResponse(
            success=False,
            message="Failed to create chat inquiry",
            error=str(e)
        )

@router.get("/{inquiry_id}", response_model=ApiResponse[ChatInquiryResponse])
async def get_chat_inquiry(inquiry_id: str, current_user: dict = Depends(auth_handler.get_current_user)):
    """Get a chat inquiry by ID (Authenticated)"""
    try:
        inquiry = await inquiry_repository.find_by_id(inquiry_id)
        if not inquiry:
            return ApiResponse(
                success=False,
                message="Inquiry not found",
                error="No inquiry found with the given ID"
            )
        
        return ApiResponse(
            success=True,
            message="Inquiry retrieved successfully",
            data=inquiry
        )
    except Exception as e:
        logger.error(f"Error getting inquiry by ID: {e}")
        return ApiResponse(
            success=False,
            message="Failed to get inquiry",
            error=str(e)
        )

@router.put("/{inquiry_id}", response_model=ApiResponse[Dict[str, Any]])
async def update_chat_inquiry(
    inquiry_id: str, 
    inquiry_data: ChatInquiryUpdate, 
    current_user: dict = Depends(auth_handler.get_current_user)
):
    """Update a chat inquiry by ID (Authenticated)"""
    try:
        update_dict = inquiry_data.dict(exclude_unset=True)
        success = await inquiry_repository.update_by_id(inquiry_id, update_dict)
        
        if not success:
            return ApiResponse(
                success=False,
                message="Inquiry not found or update failed",
                error="No inquiry found with the given ID or update failed"
            )
        
        return ApiResponse(
            success=True,
            message="Inquiry updated successfully",
            data={"inquiry_id": inquiry_id}
        )
    except Exception as e:
        logger.error(f"Error updating inquiry: {e}")
        return ApiResponse(
            success=False,
            message="Failed to update inquiry",
            error=str(e)
        )

@router.delete("/{inquiry_id}", response_model=ApiResponse[Dict[str, Any]])
async def delete_chat_inquiry(inquiry_id: str, current_user: dict = Depends(auth_handler.get_current_user)):
    """Delete a chat inquiry by ID (Authenticated)"""
    try:
        success = await inquiry_repository.delete_by_id(inquiry_id)
        
        if not success:
            return ApiResponse(
                success=False,
                message="Inquiry not found or delete failed",
                error="No inquiry found with the given ID or delete failed"
            )
        
        return ApiResponse(
            success=True,
            message="Inquiry deleted successfully",
            data={"inquiry_id": inquiry_id}
        )
    except Exception as e:
        logger.error(f"Error deleting inquiry: {e}")
        return ApiResponse(
            success=False,
            message="Failed to delete inquiry",
            error=str(e)
        )

# ============================================================================
# PUBLIC ENDPOINTS (Enhanced API functionality)
# ============================================================================

@router.post("/public", response_model=ApiResponse[ChatInquiryResponse])
async def create_inquiry_public(inquiry: ChatInquiryCreate):
    """
    Create a new chat inquiry record (Public - No Authentication Required)
    
    - **parentType**: Type of parent (New Parent, Existing Parent, Alumni)
    - **schoolType**: Type of school (Day School, Boarding School, International School)
    - **firstName**: Parent's first name
    - **mobile**: Mobile number
    - **email**: Email address
    - **city**: City name
    - **childName**: Child's name
    - **grade**: Grade/Class
    - **academicYear**: Academic year
    - **dateOfBirth**: Child's date of birth
    - **schoolName**: School name
    - **user_id**: Optional user ID for tracking
    """
    try:
        inquiry_dict = inquiry.dict()
        inquiry_id = await inquiry_repository.create_inquiry(inquiry_dict)
        
        # Get the created inquiry
        created_inquiry = await inquiry_repository.find_by_id(inquiry_id)
        
        # Ensure ID is a string for Pydantic validation
        if created_inquiry and 'id' in created_inquiry and not isinstance(created_inquiry['id'], str):
            created_inquiry['id'] = str(created_inquiry['id'])
        
        return ApiResponse(
            success=True,
            message="Inquiry created successfully",
            data=created_inquiry
        )
    except Exception as e:
        logger.error(f"Error creating inquiry: {e}")
        return ApiResponse(
            success=False,
            message="Failed to create inquiry",
            error=str(e)
        )

@router.get("/public", response_model=ApiResponse[PaginatedResponse])
async def get_all_inquiries_public(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    parent_type: Optional[str] = Query(None, description="Filter by parent type"),
    school_type: Optional[str] = Query(None, description="Filter by school type"),
    grade: Optional[str] = Query(None, description="Filter by grade"),
    city: Optional[str] = Query(None, description="Filter by city"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in names and school"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order")
):
    """
    Get all inquiries with pagination and filtering (Public - No Authentication Required)
    """
    try:
        # Build filter criteria
        filter_criteria = {}
        if parent_type:
            filter_criteria["parentType"] = parent_type
        if school_type:
            filter_criteria["schoolType"] = school_type
        if grade:
            filter_criteria["grade"] = grade
        if city:
            filter_criteria["city"] = city
        if status:
            filter_criteria["status"] = status
        if search:
            filter_criteria["search_text"] = search
        
        # Calculate pagination
        skip = (page - 1) * page_size
        
        # Get sort order
        sort_order_int = -1 if sort_order == "desc" else 1
        
        # Get inquiries
        inquiries = await inquiry_repository.find_many(
            filter_dict=filter_criteria,
            skip=skip,
            limit=page_size,
            sort_field=sort_by,
            sort_order=sort_order_int
        )
        
        # Get total count
        total_count = await inquiry_repository.count_documents(filter_criteria)
        
        # Calculate pagination info
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_previous = page > 1
        
        # Convert to response format
        response_data = []
        for inquiry in inquiries:
            try:
                # Ensure 'id' is a string for Pydantic validation
                if '_id' in inquiry:
                    inquiry['id'] = str(inquiry.pop('_id'))
                elif 'id' in inquiry and not isinstance(inquiry['id'], str):
                    inquiry['id'] = str(inquiry['id'])
                
                response_data.append(ChatInquiryResponse(**inquiry))
            except Exception as e:
                logger.warning(f"Error converting inquiry to response model: {e}")
                continue
        
        paginated_response = PaginatedResponse(
            data=response_data,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )
        
        return ApiResponse(
            success=True,
            message="Inquiries retrieved successfully",
            data=paginated_response
        )
        
    except Exception as e:
        logger.error(f"Error getting inquiries: {e}")
        return ApiResponse(
            success=False,
            message="Failed to get inquiries",
            error=str(e)
        )

@router.get("/public/{inquiry_id}", response_model=ApiResponse[ChatInquiryResponse])
async def get_inquiry_public(inquiry_id: str):
    """Get a specific inquiry by ID (Public - No Authentication Required)"""
    try:
        inquiry = await inquiry_repository.find_by_id(inquiry_id)
        if not inquiry:
            return ApiResponse(
                success=False,
                message="Inquiry not found",
                error="No inquiry found with the given ID"
            )
        
        return ApiResponse(
            success=True,
            message="Inquiry retrieved successfully",
            data=inquiry
        )
    except Exception as e:
        logger.error(f"Error getting inquiry: {e}")
        return ApiResponse(
            success=False,
            message="Failed to get inquiry",
            error=str(e)
        )

@router.get("/public/user/{user_id}", response_model=ApiResponse[List[ChatInquiryResponse]])
async def get_inquiries_by_user_public(
    user_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page")
):
    """Get inquiries by user ID (Public - No Authentication Required)"""
    try:
        skip = (page - 1) * page_size
        inquiries = await inquiry_repository.find_by_user_id(user_id, skip, page_size)
        
        # Convert to response format
        response_data = []
        for inquiry in inquiries:
            try:
                if '_id' in inquiry:
                    inquiry['id'] = str(inquiry.pop('_id'))
                elif 'id' in inquiry and not isinstance(inquiry['id'], str):
                    inquiry['id'] = str(inquiry['id'])
                
                response_data.append(ChatInquiryResponse(**inquiry))
            except Exception as e:
                logger.warning(f"Error converting inquiry to response model: {e}")
                continue
        
        return ApiResponse(
            success=True,
            message="User inquiries retrieved successfully",
            data=response_data
        )
    except Exception as e:
        logger.error(f"Error getting user inquiries: {e}")
        return ApiResponse(
            success=False,
            message="Failed to get user inquiries",
            error=str(e)
        )

# ============================================================================
# BULK OPERATIONS
# ============================================================================

@router.post("/bulk", response_model=ApiResponse[BulkInsertResponse])
async def bulk_create_inquiries(bulk_request: BulkInsertRequest):
    """Create multiple inquiries at once (Public - No Authentication Required)"""
    try:
        created_ids = []
        errors = []
        
        for i, inquiry in enumerate(bulk_request.inquiries):
            try:
                inquiry_dict = inquiry.dict()
                inquiry_id = await inquiry_repository.create_inquiry(inquiry_dict)
                created_ids.append(inquiry_id)
            except Exception as e:
                errors.append({
                    "index": i,
                    "error": str(e),
                    "data": inquiry.dict()
                })
        
        response = BulkInsertResponse(
            success_count=len(created_ids),
            failed_count=len(errors),
            created_ids=created_ids,
            errors=errors
        )
        
        return ApiResponse(
            success=True,
            message=f"Bulk insert completed. {len(created_ids)} successful, {len(errors)} failed",
            data=response
        )
    except Exception as e:
        logger.error(f"Error in bulk create: {e}")
        return ApiResponse(
            success=False,
            message="Failed to create inquiries",
            error=str(e)
        )

# ============================================================================
# STATISTICS AND ANALYTICS
# ============================================================================

@router.get("/stats", response_model=ApiResponse[Dict[str, Any]])
async def get_inquiry_stats():
    """Get inquiry statistics (Public - No Authentication Required)"""
    try:
        stats = await inquiry_repository.get_inquiry_stats()
        return ApiResponse(
            success=True,
            message="Statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return ApiResponse(
            success=False,
            message="Failed to get statistics",
            error=str(e)
        )

# ============================================================================
# DATABASE CONNECTIVITY AND EXPORT
# ============================================================================

@router.get("/database/status", response_model=ApiResponse[DatabaseStatusResponse])
async def get_database_status():
    """Get database connectivity status and counts"""
    try:
        # Check PostgreSQL connection
        postgresql_connected = await postgresql_connection.health_check()
        postgresql_status = "Connected" if postgresql_connected else "Disconnected"
        
        # Get PostgreSQL count
        postgresql_count = 0
        if postgresql_connected:
            try:
                postgresql_count = await inquiry_repository.count_documents({})
            except Exception as e:
                logger.warning(f"Error getting PostgreSQL count: {e}")
        
        # Get SQLite count
        sqlite_count = 0
        sqlite_available = True
        try:
            sqlite_count = await sqlite_repository.count_documents({})
        except Exception as e:
            logger.warning(f"Error getting SQLite count: {e}")
            sqlite_available = False
        
        status_response = DatabaseStatusResponse(
            postgresql_connected=postgresql_connected,
            postgresql_status=postgresql_status,
            sqlite_available=sqlite_available,
            sqlite_count=sqlite_count,
            postgresql_count=postgresql_count,
            last_checked=datetime.now()
        )
        
        return ApiResponse(
            success=True,
            message="Database status retrieved successfully",
            data=status_response
        )
    except Exception as e:
        logger.error(f"Error getting database status: {e}")
        return ApiResponse(
            success=False,
            message="Failed to get database status",
            error=str(e)
        )

@router.post("/database/test-postgres", response_model=ApiResponse[Dict[str, Any]])
async def test_postgres_connection():
    """Test PostgreSQL connection and create tables if needed"""
    try:
        # Test connection
        connected = await postgresql_connection.health_check()
        
        if not connected:
            # Try to connect
            await postgresql_connection.connect()
            connected = await postgresql_connection.health_check()
        
        if connected:
            # Create tables
            tables_created = await postgresql_connection.create_tables()
            
            return ApiResponse(
                success=True,
                message="PostgreSQL connection successful",
                data={
                    "connected": True,
                    "tables_created": tables_created,
                    "timestamp": datetime.now().isoformat()
                }
            )
        else:
            return ApiResponse(
                success=False,
                message="PostgreSQL connection failed",
                error="Unable to connect to PostgreSQL database"
            )
    except Exception as e:
        logger.error(f"Error testing PostgreSQL connection: {e}")
        return ApiResponse(
            success=False,
            message="PostgreSQL connection test failed",
            error=str(e)
        )

@router.get("/database/export-status", response_model=ApiResponse[ExportStatusResponse])
async def get_export_status():
    """Get current export status"""
    return ApiResponse(
        success=True,
        message="Export status retrieved successfully",
        data=export_status
    )

@router.post("/database/export-sqlite-to-postgres", response_model=ApiResponse[Dict[str, Any]])
async def start_sqlite_to_postgres_export(background_tasks: BackgroundTasks):
    """Start exporting SQLite data to PostgreSQL"""
    global export_status
    
    if export_status.status == "running":
        return ApiResponse(
            success=False,
            message="Export is already running",
            error="An export operation is currently in progress"
        )
    
    # Start background task
    background_tasks.add_task(export_sqlite_to_postgres)
    
    return ApiResponse(
        success=True,
        message="Export started successfully",
        data={
            "status": "started",
            "timestamp": datetime.now().isoformat()
        }
    )

async def export_sqlite_to_postgres():
    """Background task to export SQLite data to PostgreSQL"""
    global export_status
    
    try:
        # Update status
        export_status.status = "running"
        export_status.start_time = datetime.now()
        export_status.end_time = None
        export_status.error_message = None
        export_status.progress = 0
        export_status.processed_records = 0
        export_status.failed_records = 0
        
        # Check PostgreSQL connection
        if not await postgresql_connection.health_check():
            await postgresql_connection.connect()
            if not await postgresql_connection.health_check():
                raise Exception("PostgreSQL connection failed")
        
        # Get all SQLite records
        sqlite_records = await sqlite_repository.find_all({}, skip=0, limit=10000)
        export_status.total_records = len(sqlite_records)
        
        if export_status.total_records == 0:
            export_status.status = "completed"
            export_status.end_time = datetime.now()
            export_status.progress = 100
            return
        
        # Export records to PostgreSQL
        for i, record in enumerate(sqlite_records):
            try:
                # Convert SQLite record to PostgreSQL format
                inquiry_data = {
                    'user_id': record.get('user_id'),
                    'parentType': record.get('parentType'),
                    'schoolType': record.get('schoolType'),
                    'firstName': record.get('firstName'),
                    'mobile': record.get('mobile'),
                    'email': record.get('email'),
                    'city': record.get('city'),
                    'childName': record.get('childName'),
                    'grade': record.get('grade'),
                    'academicYear': record.get('academicYear'),
                    'dateOfBirth': record.get('dateOfBirth'),
                    'schoolName': record.get('schoolName')
                }
                
                # Create in PostgreSQL
                await inquiry_repository.create_inquiry(inquiry_data)
                export_status.processed_records += 1
                
            except Exception as e:
                logger.warning(f"Error exporting record {i}: {e}")
                export_status.failed_records += 1
            
            # Update progress
            export_status.progress = int((i + 1) / export_status.total_records * 100)
        
        # Mark as completed
        export_status.status = "completed"
        export_status.end_time = datetime.now()
        export_status.progress = 100
        
        logger.info(f"Export completed: {export_status.processed_records} successful, {export_status.failed_records} failed")
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        export_status.status = "failed"
        export_status.end_time = datetime.now()
        export_status.error_message = str(e)

@router.post("/database/reset-export-status", response_model=ApiResponse[Dict[str, Any]])
async def reset_export_status():
    """Reset export status to idle"""
    global export_status
    
    export_status = ExportStatusResponse(
        status="idle",
        progress=0,
        total_records=0,
        processed_records=0,
        failed_records=0,
        start_time=None,
        end_time=None,
        error_message=None
    )
    
    return ApiResponse(
        success=True,
        message="Export status reset successfully",
        data={"status": "reset"}
    )

# ============================================================================
# DATA EXPORT (JSON/CSV)
# ============================================================================

@router.get("/export/json", response_model=ApiResponse[Dict[str, Any]])
async def export_to_json(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(1000, ge=1, le=10000, description="Number of items per page")
):
    """Export inquiries to JSON format"""
    try:
        skip = (page - 1) * page_size
        inquiries = await inquiry_repository.find_many({}, skip=skip, limit=page_size)
        
        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "page": page,
                "page_size": page_size,
                "total_exported": len(inquiries)
            },
            "inquiries": inquiries
        }
        
        return ApiResponse(
            success=True,
            message="JSON export completed successfully",
            data=export_data
        )
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        return ApiResponse(
            success=False,
            message="Failed to export to JSON",
            error=str(e)
        )

@router.get("/export/csv")
async def export_to_csv(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(1000, ge=1, le=10000, description="Number of items per page")
):
    """Export inquiries to CSV format"""
    try:
        skip = (page - 1) * page_size
        inquiries = await inquiry_repository.find_many({}, skip=skip, limit=page_size)
        
        if not inquiries:
            raise HTTPException(status_code=404, detail="No data to export")
        
        # Create CSV content
        output = io.StringIO()
        fieldnames = [
            'id', 'user_id', 'parentType', 'schoolType', 'firstName', 'mobile',
            'email', 'city', 'childName', 'grade', 'academicYear', 'dateOfBirth',
            'schoolName', 'status', 'source', 'created_at', 'updated_at'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for inquiry in inquiries:
            # Convert to CSV format
            csv_row = {}
            for field in fieldnames:
                value = inquiry.get(field, '')
                if isinstance(value, datetime):
                    csv_row[field] = value.isoformat()
                else:
                    csv_row[field] = str(value) if value is not None else ''
            writer.writerow(csv_row)
        
        csv_content = output.getvalue()
        output.close()
        
        from fastapi.responses import Response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=inquiries_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export to CSV: {str(e)}")

# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health", response_model=ApiResponse[Dict[str, Any]])
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connections
        postgresql_healthy = await postgresql_connection.health_check()
        
        sqlite_healthy = True
        try:
            await sqlite_repository.count_documents({})
        except Exception:
            sqlite_healthy = False
        
        return ApiResponse(
            success=True,
            message="Service is healthy",
            data={
                "status": "healthy",
                "postgresql": "connected" if postgresql_healthy else "disconnected",
                "sqlite": "connected" if sqlite_healthy else "disconnected",
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return ApiResponse(
            success=False,
            message="Service is unhealthy",
            error=str(e)
        )

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from database.chat_inquiry_repository import ChatInquiryRepository
from models.chat_inquiry_models import (
    ChatInquiryCreate, 
    ChatInquiryResponse, 
    ChatInquiryUpdate,
    ApiResponse
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/chat-inquiry", tags=["Chat Inquiry Management"])

# Initialize repository
inquiry_repository = ChatInquiryRepository()

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

@router.post("/", response_model=ApiResponse[ChatInquiryResponse])
async def create_inquiry(inquiry: ChatInquiryCreate):
    """
    Create a new chat inquiry record
    
    - **parentType**: Type of parent (New Parent, Existing Parent, Alumni)
    - **schoolType**: Type of school (Day School, Boarding School, Online School)
    - **firstName**: First name of the parent
    - **mobile**: Mobile number (10-15 digits)
    - **email**: Email address
    - **city**: City of residence
    - **childName**: Name of the child
    - **grade**: Grade the child is applying for
    - **academicYear**: Academic year (YYYY-YYYY format)
    - **dateOfBirth**: Date of birth (YYYY-MM-DD)
    - **schoolName**: Name of the school
    """
    try:
        # Convert Pydantic model to dict
        inquiry_data = inquiry.dict()
        
        # Create the inquiry
        inquiry_id = await inquiry_repository.create_inquiry(inquiry_data)
        
        # Fetch the created record
        created_inquiry = await inquiry_repository.find_by_id(inquiry_id)
        
        if not created_inquiry:
            raise HTTPException(status_code=500, detail="Failed to retrieve created inquiry")
        
        # Convert to response model
        # Ensure 'id' is a string for Pydantic validation
        if '_id' in created_inquiry:
            created_inquiry['id'] = str(created_inquiry.pop('_id'))
        elif 'id' in created_inquiry and not isinstance(created_inquiry['id'], str):
            created_inquiry['id'] = str(created_inquiry['id'])
        
        response_data = ChatInquiryResponse(**created_inquiry)
        
        return ApiResponse(
            success=True,
            message="Chat inquiry created successfully",
            data=response_data
        )
        
    except ValueError as e:
        logger.error(f"Validation error creating inquiry: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating inquiry: {e}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

@router.post("/bulk", response_model=ApiResponse[BulkInsertResponse])
async def create_bulk_inquiries(request: BulkInsertRequest):
    """
    Create multiple chat inquiry records in a single request
    
    - **inquiries**: List of inquiry objects (max 100)
    """
    try:
        created_ids = []
        errors = []
        
        for i, inquiry in enumerate(request.inquiries):
            try:
                inquiry_data = inquiry.dict()
                inquiry_id = await inquiry_repository.create_inquiry(inquiry_data)
                created_ids.append(inquiry_id)
            except Exception as e:
                errors.append({
                    "index": i,
                    "error": str(e),
                    "data": inquiry.dict()
                })
        
        response_data = BulkInsertResponse(
            success_count=len(created_ids),
            failed_count=len(errors),
            created_ids=created_ids,
            errors=errors
        )
        
        return ApiResponse(
            success=True,
            message=f"Bulk insert completed. {len(created_ids)} successful, {len(errors)} failed",
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"Error in bulk insert: {e}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

@router.get("/", response_model=ApiResponse[PaginatedResponse])
async def get_all_inquiries(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of records per page"),
    search: Optional[str] = Query(None, description="Search term for filtering"),
    parent_type: Optional[str] = Query(None, description="Filter by parent type"),
    school_type: Optional[str] = Query(None, description="Filter by school type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order")
):
    """
    Get all chat inquiry records with pagination and filtering
    
    - **page**: Page number (starts from 1)
    - **page_size**: Number of records per page (1-100)
    - **search**: Search term for filtering across multiple fields
    - **parent_type**: Filter by parent type
    - **school_type**: Filter by school type
    - **status**: Filter by status
    - **sort_by**: Field to sort by
    - **sort_order**: Sort order (asc/desc)
    """
    try:
        # Calculate skip value
        skip = (page - 1) * page_size
        
        # Build search criteria
        search_criteria = {}
        if search:
            search_criteria['search_text'] = search
        if parent_type:
            search_criteria['parentType'] = parent_type
        if school_type:
            search_criteria['schoolType'] = school_type
        if status:
            search_criteria['status'] = status
        
        # Get records
        records = await inquiry_repository.search_inquiries(
            search_criteria=search_criteria,
            skip=skip,
            limit=page_size
        )
        
        # Get total count
        total_count = await inquiry_repository.count_documents(search_criteria)
        
        # Calculate pagination info
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_previous = page > 1
        
        # Convert to response models
        response_records = []
        for record in records:
            try:
                # Ensure 'id' is a string for Pydantic validation
                if '_id' in record:
                    record['id'] = str(record.pop('_id'))
                elif 'id' in record and not isinstance(record['id'], str):
                    record['id'] = str(record['id'])
                
                response_records.append(ChatInquiryResponse(**record))
            except Exception as e:
                logger.warning(f"Error converting record to response model: {e}")
                continue
        
        paginated_data = PaginatedResponse(
            data=response_records,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )
        
        return ApiResponse(
            success=True,
            message=f"Retrieved {len(response_records)} records",
            data=paginated_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving inquiries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

@router.get("/user/{user_id}", response_model=ApiResponse[List[Dict[str, Any]]])
async def get_inquiries_by_user_id(
    user_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Records per page")
):
    """
    Get chat inquiry records by user_id with pagination
    
    - **user_id**: The user ID to filter by
    - **page**: Page number (default: 1)
    - **page_size**: Records per page (default: 10, max: 100)
    """
    try:
        skip = (page - 1) * page_size
        limit = page_size
        
        records = await inquiry_repository.find_by_user_id(user_id, skip, limit)
        
        # Convert records to response format
        response_records = []
        for record in records:
            try:
                # Ensure 'id' is a string for Pydantic validation
                if '_id' in record:
                    record['id'] = str(record.pop('_id'))
                elif 'id' in record and not isinstance(record['id'], str):
                    record['id'] = str(record['id'])
                
                response_records.append(record)
            except Exception as e:
                logger.warning(f"Error converting record to response format: {e}")
                continue
        
        return ApiResponse(
            success=True,
            message=f"Retrieved {len(response_records)} records for user {user_id}",
            data=response_records
        )
        
    except Exception as e:
        logger.error(f"Error retrieving inquiries by user_id: {e}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

@router.get("/stats", response_model=ApiResponse[Dict[str, Any]])
async def get_inquiry_statistics():
    """
    Get statistics about chat inquiries
    
    Returns:
    - Total count
    - Distribution by parent type
    - Distribution by school type
    - Distribution by status
    - Recent activity
    """
    try:
        stats = await inquiry_repository.get_inquiry_stats()
        
        return ApiResponse(
            success=True,
            message="Statistics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

@router.get("/export", response_model=ApiResponse[Dict[str, Any]])
async def export_inquiries(
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum records to export")
):
    """
    Export chat inquiries to JSON or CSV format
    
    - **format**: Export format (json or csv)
    - **limit**: Maximum number of records to export
    """
    try:
        # Get all records
        records = await inquiry_repository.search_inquiries(
            search_criteria={},
            skip=0,
            limit=limit
        )
        
        if format == "json":
            return ApiResponse(
                success=True,
                message=f"Exported {len(records)} records as JSON",
                data={
                    "format": "json",
                    "count": len(records),
                    "records": records
                }
            )
        elif format == "csv":
            # Convert to CSV format
            if not records:
                csv_data = "No records found"
            else:
                # Get headers from first record
                headers = list(records[0].keys())
                csv_lines = [",".join(headers)]
                
                for record in records:
                    row = []
                    for header in headers:
                        value = str(record.get(header, ""))
                        # Escape commas and quotes
                        if "," in value or '"' in value:
                            value = f'"{value.replace('"', '""')}"'
                        row.append(value)
                    csv_lines.append(",".join(row))
                
                csv_data = "\n".join(csv_lines)
            
            return ApiResponse(
                success=True,
                message=f"Exported {len(records)} records as CSV",
                data={
                    "format": "csv",
                    "count": len(records),
                    "data": csv_data
                }
            )
        
    except Exception as e:
        logger.error(f"Error exporting inquiries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

@router.get("/health", response_model=ApiResponse[Dict[str, Any]])
async def health_check():
    """
    Health check for the chat inquiry service
    """
    try:
        # Test database connection
        stats = await inquiry_repository.get_inquiry_stats()
        
        return ApiResponse(
            success=True,
            message="Chat inquiry service is healthy",
            data={
                "status": "healthy",
                "database": "connected",
                "total_records": stats.get("total_inquiries", 0)
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return ApiResponse(
            success=False,
            message="Chat inquiry service is unhealthy",
            data={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )

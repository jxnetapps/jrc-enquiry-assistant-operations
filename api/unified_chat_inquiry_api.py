"""
Unified Chat Inquiry API - Clean version without database endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from database.unified_inquiry_repository import unified_inquiry_repository
from models.chat_inquiry_models import (
    ChatInquiryCreate, 
    ChatInquiryResponse, 
    ChatInquiryUpdate,
    ApiResponse
)
from auth.authentication import AuthHandler

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/chat-inquiry", tags=["Chat Inquiry"])

# Initialize components
auth_handler = AuthHandler()
inquiry_repository = unified_inquiry_repository

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

# ============================================================================
# AUTHENTICATION ENDPOINTS
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

# Moved to after public routes to avoid route conflicts

@router.put("/{inquiry_id}", response_model=ApiResponse[Dict[str, Any]])
async def update_chat_inquiry(
    inquiry_id: str, 
    inquiry_data: ChatInquiryUpdate, 
    current_user: dict = Depends(auth_handler.get_current_user)
):
    """Update a chat inquiry by ID (Authenticated)"""
    try:
        update_dict = inquiry_data.dict(exclude_unset=True)
        success = await inquiry_repository.update_inquiry(inquiry_id, update_dict)
        
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
        success = await inquiry_repository.delete_inquiry(inquiry_id)
        
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
# PUBLIC ENDPOINTS
# ============================================================================

@router.post("/public", response_model=ApiResponse[ChatInquiryResponse])
async def create_inquiry_public(inquiry: ChatInquiryCreate):
    """Create a new chat inquiry record (Public - No Authentication Required)"""
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
    search: Optional[str] = Query(None, description="Search in question or answer"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order")
):
    """Get all inquiries with pagination and filtering (Public - No Authentication Required)"""
    try:
        # Calculate pagination
        skip = (page - 1) * page_size
        
        # Get inquiries
        if search:
            inquiries = await inquiry_repository.search_inquiries(search, page_size)
        else:
            inquiries = await inquiry_repository.get_all_inquiries(skip, page_size)
        
        # Get total count
        total_count = await inquiry_repository.count_documents({})
        
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
# AUTHENTICATED ENDPOINTS (moved after public to avoid route conflicts)
# ============================================================================

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

@router.get("/health", response_model=ApiResponse[Dict[str, Any]])
async def health_check():
    """Health check endpoint for inquiry service"""
    try:
        # Test inquiry repository
        inquiry_count = await inquiry_repository.count_documents({})
        
        return ApiResponse(
            success=True,
            message="Inquiry service is healthy",
            data={
                "status": "healthy",
                "inquiry_count": inquiry_count,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Inquiry service health check failed: {e}")
        return ApiResponse(
            success=False,
            message="Inquiry service is unhealthy",
            data={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

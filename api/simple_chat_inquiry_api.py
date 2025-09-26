from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging

from database.chat_inquiry_repository import ChatInquiryRepository
from models.chat_inquiry_models import ChatInquiryCreate, ApiResponse

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/simple/chat-inquiry", tags=["Simple Chat Inquiry"])

# Initialize repository
inquiry_repository = ChatInquiryRepository()

@router.post("/", response_model=ApiResponse[Dict[str, Any]])
async def create_inquiry(inquiry: ChatInquiryCreate):
    """
    Create a new chat inquiry record
    """
    try:
        # Convert Pydantic model to dict
        inquiry_data = inquiry.dict()
        
        # Create the inquiry
        inquiry_id = await inquiry_repository.create_inquiry(inquiry_data)
        
        return ApiResponse(
            success=True,
            message="Chat inquiry created successfully",
            data={"inquiry_id": inquiry_id}
        )
        
    except ValueError as e:
        logger.error(f"Validation error creating inquiry: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating inquiry: {e}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

@router.get("/stats", response_model=ApiResponse[Dict[str, Any]])
async def get_stats():
    """
    Get statistics about inquiries
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

@router.get("/{inquiry_id}", response_model=ApiResponse[Dict[str, Any]])
async def get_inquiry_by_id(inquiry_id: str):
    """
    Get a specific chat inquiry record by ID
    
    - **inquiry_id**: The ID of the inquiry to retrieve
    """
    try:
        inquiry = await inquiry_repository.find_by_id(inquiry_id)
        
        if not inquiry:
            raise HTTPException(status_code=404, detail="Inquiry not found")
        
        return ApiResponse(
            success=True,
            message="Inquiry retrieved successfully",
            data=inquiry
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving inquiry: {e}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

@router.delete("/{inquiry_id}", response_model=ApiResponse[Dict[str, Any]])
async def delete_inquiry(inquiry_id: str):
    """
    Delete a chat inquiry record by ID
    
    - **inquiry_id**: The ID of the inquiry to delete
    """
    try:
        # First check if the inquiry exists
        existing_inquiry = await inquiry_repository.find_by_id(inquiry_id)
        
        if not existing_inquiry:
            raise HTTPException(status_code=404, detail="Inquiry not found")
        
        # Delete the inquiry
        success = await inquiry_repository.delete_by_id(inquiry_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete inquiry")
        
        return ApiResponse(
            success=True,
            message="Inquiry deleted successfully",
            data={"deleted_id": inquiry_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting inquiry: {e}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

@router.get("/user/{user_id}", response_model=ApiResponse[List[Dict[str, Any]]])
async def get_inquiries_by_user_id(user_id: str, skip: int = 0, limit: int = 100):
    """
    Get chat inquiry records by user_id
    
    - **user_id**: The user ID to filter by
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    try:
        records = await inquiry_repository.find_by_user_id(user_id, skip, limit)
        
        return ApiResponse(
            success=True,
            message=f"Retrieved {len(records)} records for user {user_id}",
            data=records
        )
        
    except Exception as e:
        logger.error(f"Error retrieving inquiries by user_id: {e}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

@router.get("/", response_model=ApiResponse[List[Dict[str, Any]]])
async def get_all_inquiries():
    """
    Get all chat inquiry records
    """
    try:
        # Get all records using search with empty criteria
        records = await inquiry_repository.search_inquiries(
            search_criteria={},
            skip=0,
            limit=1000
        )
        
        return ApiResponse(
            success=True,
            message=f"Retrieved {len(records)} records",
            data=records
        )
        
    except Exception as e:
        logger.error(f"Error retrieving inquiries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

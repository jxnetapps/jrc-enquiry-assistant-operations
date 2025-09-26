from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import logging
from database.mongodb_connection import mongodb_connection
from database.chat_inquiry_repository import ChatInquiryRepository
from models.chat_inquiry_models import (
    ChatInquiryCreate, ChatInquiryResponse, ChatInquiryUpdate, 
    InquirySearchRequest, InquiryStatsResponse, ApiResponse as InquiryApiResponse
)
from auth.authentication import AuthHandler

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/chat-inquiry", tags=["Chat Inquiry"])

# Initialize components
auth_handler = AuthHandler()
chat_inquiry_repo = ChatInquiryRepository()

@router.post("", response_model=InquiryApiResponse)
async def create_chat_inquiry(inquiry_data: ChatInquiryCreate):
    """Create a new chat inquiry information record"""
    try:
        # Convert Pydantic model to dict
        inquiry_dict = inquiry_data.dict()
        
        # Create inquiry in MongoDB
        inquiry_id = await chat_inquiry_repo.create_inquiry(inquiry_dict)
        
        return InquiryApiResponse(
            success=True,
            message="Chat inquiry created successfully",
            data={"inquiry_id": inquiry_id}
        )
    except ValueError as e:
        logger.error(f"Validation error creating chat inquiry: {e}")
        return InquiryApiResponse(
            success=False,
            message="Validation error",
            error=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating chat inquiry: {e}")
        return InquiryApiResponse(
            success=False,
            message="Failed to create chat inquiry",
            error=str(e)
        )

@router.get("/{inquiry_id}", response_model=InquiryApiResponse)
async def get_chat_inquiry(inquiry_id: str, current_user: str = Depends(auth_handler.get_current_user)):
    """Get a specific chat inquiry by ID"""
    try:
        inquiry = await chat_inquiry_repo.find_by_id(inquiry_id)
        
        if not inquiry:
            return InquiryApiResponse(
                success=False,
                message="Inquiry not found"
            )
        
        return InquiryApiResponse(
            success=True,
            message="Inquiry retrieved successfully",
            data=inquiry
        )
    except Exception as e:
        logger.error(f"Error getting chat inquiry: {e}")
        return InquiryApiResponse(
            success=False,
            message="Failed to get chat inquiry",
            error=str(e)
        )

@router.put("/{inquiry_id}", response_model=InquiryApiResponse)
async def update_chat_inquiry(
    inquiry_id: str, 
    update_data: ChatInquiryUpdate,
    current_user: str = Depends(auth_handler.get_current_user)
):
    """Update a chat inquiry"""
    try:
        # Convert Pydantic model to dict, excluding None values
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        
        if not update_dict:
            return InquiryApiResponse(
                success=False,
                message="No valid fields to update"
            )
        
        success = await chat_inquiry_repo.update_by_id(inquiry_id, update_dict)
        
        if success:
            return InquiryApiResponse(
                success=True,
                message="Inquiry updated successfully"
            )
        else:
            return InquiryApiResponse(
                success=False,
                message="Inquiry not found or no changes made"
            )
    except ValueError as e:
        logger.error(f"Validation error updating chat inquiry: {e}")
        return InquiryApiResponse(
            success=False,
            message="Validation error",
            error=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating chat inquiry: {e}")
        return InquiryApiResponse(
            success=False,
            message="Failed to update chat inquiry",
            error=str(e)
        )

@router.delete("/{inquiry_id}", response_model=InquiryApiResponse)
async def delete_chat_inquiry(inquiry_id: str, current_user: str = Depends(auth_handler.get_current_user)):
    """Delete a chat inquiry"""
    try:
        success = await chat_inquiry_repo.delete_by_id(inquiry_id)
        
        if success:
            return InquiryApiResponse(
                success=True,
                message="Inquiry deleted successfully"
            )
        else:
            return InquiryApiResponse(
                success=False,
                message="Inquiry not found"
            )
    except Exception as e:
        logger.error(f"Error deleting chat inquiry: {e}")
        return InquiryApiResponse(
            success=False,
            message="Failed to delete chat inquiry",
            error=str(e)
        )

@router.post("/search", response_model=InquiryApiResponse)
async def search_chat_inquiries(
    search_request: InquirySearchRequest,
    current_user: str = Depends(auth_handler.get_current_user)
):
    """Search chat inquiries with filters"""
    try:
        # Convert Pydantic model to dict, excluding None values
        search_criteria = {k: v for k, v in search_request.dict().items() if v is not None}
        
        # Remove pagination fields from search criteria
        skip = search_criteria.pop('skip', 0)
        limit = search_criteria.pop('limit', 100)
        
        inquiries = await chat_inquiry_repo.search_inquiries(search_criteria, skip, limit)
        
        return InquiryApiResponse(
            success=True,
            message="Search completed successfully",
            data={
                "inquiries": inquiries,
                "count": len(inquiries),
                "skip": skip,
                "limit": limit
            }
        )
    except Exception as e:
        logger.error(f"Error searching chat inquiries: {e}")
        return InquiryApiResponse(
            success=False,
            message="Failed to search inquiries",
            error=str(e)
        )

@router.get("/stats", response_model=InquiryApiResponse)
async def get_inquiry_stats(current_user: str = Depends(auth_handler.get_current_user)):
    """Get inquiry statistics"""
    try:
        stats = await chat_inquiry_repo.get_inquiry_stats()
        
        return InquiryApiResponse(
            success=True,
            message="Statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error getting inquiry stats: {e}")
        return InquiryApiResponse(
            success=False,
            message="Failed to get statistics",
            error=str(e)
        )

@router.get("/by-email/{email}", response_model=InquiryApiResponse)
async def get_inquiry_by_email(email: str, current_user: str = Depends(auth_handler.get_current_user)):
    """Get inquiry by email address"""
    try:
        inquiry = await chat_inquiry_repo.find_by_email(email)
        
        if not inquiry:
            return InquiryApiResponse(
                success=False,
                message="No inquiry found with this email"
            )
        
        return InquiryApiResponse(
            success=True,
            message="Inquiry retrieved successfully",
            data=inquiry
        )
    except Exception as e:
        logger.error(f"Error getting inquiry by email: {e}")
        return InquiryApiResponse(
            success=False,
            message="Failed to get inquiry by email",
            error=str(e)
        )

@router.get("/by-mobile/{mobile}", response_model=InquiryApiResponse)
async def get_inquiry_by_mobile(mobile: str, current_user: str = Depends(auth_handler.get_current_user)):
    """Get inquiry by mobile number"""
    try:
        inquiry = await chat_inquiry_repo.find_by_mobile(mobile)
        
        if not inquiry:
            return InquiryApiResponse(
                success=False,
                message="No inquiry found with this mobile number"
            )
        
        return InquiryApiResponse(
            success=True,
            message="Inquiry retrieved successfully",
            data=inquiry
        )
    except Exception as e:
        logger.error(f"Error getting inquiry by mobile: {e}")
        return InquiryApiResponse(
            success=False,
            message="Failed to get inquiry by mobile",
            error=str(e)
        )

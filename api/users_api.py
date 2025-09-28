from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import logging

from auth.authentication import AuthHandler, authenticate_user
from database.unified_user_repository import unified_user_repository
from models.user_models import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, UserStatsResponse, 
    UserPasswordUpdate, UserRole, UserStatus
)

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/users", tags=["User Management"])

# Initialize components
auth_handler = AuthHandler()

# Pydantic models
class ApiResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None

class UserPasswordReset(BaseModel):
    password: str

class UserFilters(BaseModel):
    search: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    created_from: Optional[str] = None
    created_to: Optional[str] = None

def require_admin(current_user: str = Depends(auth_handler.get_current_user)):
    """Dependency to require admin access"""
    async def _check_admin():
        current_user_data = await unified_user_repository.get_user_by_id(current_user)
        if not current_user_data or current_user_data.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Admin access required")
        return current_user
    return _check_admin

@router.get("", response_model=ApiResponse)
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search by username or email"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    status: Optional[UserStatus] = Query(None, description="Filter by status"),
    sort_by: str = Query("created_at", description="Sort by field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    current_user: str = Depends(require_admin)
):
    """Get users with pagination and filtering (Admin only)"""
    try:
        # Get users with advanced filtering
        users, total_count = await unified_user_repository.get_users_advanced(
            page=page,
            page_size=page_size,
            search=search,
            role=role,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        total_pages = (total_count + page_size - 1) // page_size
        
        return ApiResponse(
            success=True,
            message="Users retrieved successfully",
            data={
                "users": [user.dict() for user in users],
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        )
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving users")

@router.get("/{user_id}", response_model=ApiResponse)
async def get_user_by_id(
    user_id: str,
    current_user: str = Depends(require_admin)
):
    """Get user by ID (Admin only)"""
    try:
        user = await unified_user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return ApiResponse(
            success=True,
            message="User retrieved successfully",
            data=user.dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving user")

@router.post("", response_model=ApiResponse)
async def create_user(
    user_data: UserCreate,
    current_user: str = Depends(require_admin)
):
    """Create a new user (Admin only)"""
    try:
        user_id = await unified_user_repository.create_user(user_data)
        created_user = await unified_user_repository.get_user_by_id(user_id)
        
        return ApiResponse(
            success=True,
            message="User created successfully",
            data=created_user.dict()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Error creating user")

@router.put("/{user_id}", response_model=ApiResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: str = Depends(require_admin)
):
    """Update user (Admin only)"""
    try:
        # Check if user exists
        existing_user = await unified_user_repository.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = await unified_user_repository.update_user(user_id, user_data)
        if success:
            updated_user = await unified_user_repository.get_user_by_id(user_id)
            return ApiResponse(
                success=True,
                message="User updated successfully",
                data=updated_user.dict()
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to update user")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Error updating user")

@router.delete("/{user_id}", response_model=ApiResponse)
async def delete_user(
    user_id: str,
    current_user: str = Depends(require_admin)
):
    """Delete user (Admin only)"""
    try:
        # Prevent self-deletion
        if user_id == current_user:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
        # Check if user exists
        existing_user = await unified_user_repository.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = await unified_user_repository.delete_user(user_id)
        if success:
            return ApiResponse(
                success=True,
                message="User deleted successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to delete user")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail="Error deleting user")

@router.post("/{user_id}/reset-password", response_model=ApiResponse)
async def reset_user_password(
    user_id: str,
    password_data: UserPasswordReset,
    current_user: str = Depends(require_admin)
):
    """Reset user password (Admin only)"""
    try:
        # Check if user exists
        existing_user = await unified_user_repository.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = await unified_user_repository.reset_password(user_id, password_data.password)
        if success:
            return ApiResponse(
                success=True,
                message="Password reset successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to reset password")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        raise HTTPException(status_code=500, detail="Error resetting password")

@router.post("/{user_id}/toggle-status", response_model=ApiResponse)
async def toggle_user_status(
    user_id: str,
    current_user: str = Depends(require_admin)
):
    """Toggle user status (Admin only)"""
    try:
        # Check if user exists
        existing_user = await unified_user_repository.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent self-status change
        if user_id == current_user:
            raise HTTPException(status_code=400, detail="Cannot change your own status")
        
        success = await unified_user_repository.toggle_user_status(user_id)
        if success:
            updated_user = await unified_user_repository.get_user_by_id(user_id)
            return ApiResponse(
                success=True,
                message=f"User status changed to {updated_user.status}",
                data=updated_user.dict()
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to toggle user status")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling user status: {e}")
        raise HTTPException(status_code=500, detail="Error toggling user status")

@router.get("/stats/overview", response_model=ApiResponse)
async def get_user_stats(
    current_user: str = Depends(require_admin)
):
    """Get user statistics (Admin only)"""
    try:
        stats = await unified_user_repository.get_user_stats()
        return ApiResponse(
            success=True,
            message="User statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving user statistics")

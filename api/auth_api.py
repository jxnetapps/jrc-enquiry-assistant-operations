from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, TypeVar, Generic, List
import logging

from auth.authentication import AuthHandler, authenticate_user
from database.user_repository import user_repository
from models.user_models import (
    UserCreate, UserUpdate, UserResponse, UserLogin, UserLoginResponse,
    UserListResponse, UserStatsResponse, UserPasswordUpdate, UserRole, UserStatus
)

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Initialize components
auth_handler = AuthHandler()

T = TypeVar('T')

# Pydantic models
class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: Optional[str] = None
    access_token: Optional[str] = None
    user_id: Optional[str] = None
    data: Optional[T] = None

@router.post("/login", response_model=UserLoginResponse)
async def login(login_data: UserLogin):
    """User login endpoint"""
    try:
        user_id = await authenticate_user(login_data.username, login_data.password)
        if user_id:
            token = auth_handler.create_token(user_id)
            user_info = await user_repository.get_user_by_id(user_id)
            return UserLoginResponse(
                success=True,
                message="Login successful",
                access_token=token,
                user_id=user_id,
                user_info=user_info
            )
        else:
            return UserLoginResponse(
                success=False,
                message="Invalid credentials"
            )
    except Exception as e:
        logger.error(f"Login error: {e}")
        return UserLoginResponse(
            success=False,
            message="Login failed"
        )

@router.post("/register", response_model=ApiResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        user_id = await user_repository.create_user(user_data)
        return ApiResponse(
            success=True,
            message="User registered successfully",
            user_id=user_id,
            data={"username": user_data.username}
        )
    except ValueError as e:
        return ApiResponse(
            success=False,
            message=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return ApiResponse(
            success=False,
            message="Registration failed"
        )

@router.get("/me", response_model=ApiResponse)
async def get_current_user_info(current_user: str = Depends(auth_handler.get_current_user)):
    """Get current user information"""
    try:
        user_data = await user_repository.get_user_by_id(current_user)
        if user_data:
            return ApiResponse(
                success=True,
                message="User information retrieved successfully",
                user_id=user_data.user_id,
                data=user_data
            )
        else:
            return ApiResponse(
                success=False,
                message="User not found"
            )
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        return ApiResponse(
            success=False,
            message="Error getting user information"
        )

@router.put("/me", response_model=ApiResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: str = Depends(auth_handler.get_current_user)
):
    """Update current user information"""
    try:
        success = await user_repository.update_user(current_user, user_data)
        if success:
            updated_user = await user_repository.get_user_by_id(current_user)
            return ApiResponse(
                success=True,
                message="User updated successfully",
                user_id=current_user,
                data=updated_user
            )
        else:
            return ApiResponse(
                success=False,
                message="User not found"
            )
    except ValueError as e:
        return ApiResponse(
            success=False,
            message=str(e)
        )
    except Exception as e:
        logger.error(f"Update user error: {e}")
        return ApiResponse(
            success=False,
            message="Error updating user"
        )

@router.put("/me/password", response_model=ApiResponse)
async def update_password(
    password_data: UserPasswordUpdate,
    current_user: str = Depends(auth_handler.get_current_user)
):
    """Update current user password"""
    try:
        success = await user_repository.update_password(
            current_user, 
            password_data.current_password, 
            password_data.new_password
        )
        if success:
            return ApiResponse(
                success=True,
                message="Password updated successfully",
                user_id=current_user
            )
        else:
            return ApiResponse(
                success=False,
                message="User not found"
            )
    except ValueError as e:
        return ApiResponse(
            success=False,
            message=str(e)
        )
    except Exception as e:
        logger.error(f"Update password error: {e}")
        return ApiResponse(
            success=False,
            message="Error updating password"
        )

@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    status: Optional[UserStatus] = Query(None, description="Filter by status"),
    current_user: str = Depends(auth_handler.get_current_user)
):
    """List users with pagination and filtering (Admin only)"""
    try:
        # Check if current user is admin
        current_user_data = await user_repository.get_user_by_id(current_user)
        if not current_user_data or current_user_data.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        skip = (page - 1) * page_size
        users = await user_repository.list_users(skip, page_size, role, status)
        total = await user_repository.count_users(role, status)
        pages = (total + page_size - 1) // page_size
        
        return UserListResponse(
            users=users,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List users error: {e}")
        raise HTTPException(status_code=500, detail="Error listing users")

@router.get("/users/stats", response_model=UserStatsResponse)
async def get_user_stats(current_user: str = Depends(auth_handler.get_current_user)):
    """Get user statistics (Admin only)"""
    try:
        # Check if current user is admin
        current_user_data = await user_repository.get_user_by_id(current_user)
        if not current_user_data or current_user_data.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        stats = await user_repository.get_user_stats()
        return UserStatsResponse(**stats)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user stats error: {e}")
        raise HTTPException(status_code=500, detail="Error getting user statistics")

@router.delete("/users/{user_id}", response_model=ApiResponse)
async def delete_user(
    user_id: str,
    current_user: str = Depends(auth_handler.get_current_user)
):
    """Delete user (Admin only)"""
    try:
        # Check if current user is admin
        current_user_data = await user_repository.get_user_by_id(current_user)
        if not current_user_data or current_user_data.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Prevent self-deletion
        if user_id == current_user:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
        success = await user_repository.delete_user(user_id)
        if success:
            return ApiResponse(
                success=True,
                message="User deleted successfully",
                user_id=user_id
            )
        else:
            return ApiResponse(
                success=False,
                message="User not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        return ApiResponse(
            success=False,
            message="Error deleting user"
        )

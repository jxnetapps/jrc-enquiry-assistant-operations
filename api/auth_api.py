from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, TypeVar, Generic, List
import logging

from auth.authentication import AuthHandler, authenticate_user
from database.unified_user_repository import unified_user_repository
from models.user_models import (
    UserCreate, UserUpdate, UserResponse, UserLogin, UserLoginResponse,
    UserListResponse, UserStatsResponse, UserPasswordUpdate, UserRole, UserStatus,
    UserTokenRequest
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
            user_info = await unified_user_repository.get_user_by_id(user_id)
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

@router.post("/token", response_model=ApiResponse)
async def create_token_for_user(token_request: UserTokenRequest):
    """Create a token for a user if their user_id exists in the database"""
    try:
        # Check if user exists in database
        user_data = await unified_user_repository.get_user_by_id(token_request.user_id)
        if not user_data:
            return ApiResponse(
                success=False,
                message="User not found"
            )
        
        # Check if user is active
        if user_data.status != UserStatus.ACTIVE:
            return ApiResponse(
                success=False,
                message="User account is not active"
            )
        
        # Generate token for the user
        token = auth_handler.create_token(token_request.user_id)
        
        return ApiResponse(
            success=True,
            message="Token created successfully",
            access_token=token,
            user_id=token_request.user_id,
            data={
                "username": user_data.username,
                "role": user_data.role,
                "status": user_data.status
            }
        )
    except Exception as e:
        logger.error(f"Token creation error: {e}")
        return ApiResponse(
            success=False,
            message="Token creation failed"
        )

@router.post("/register", response_model=ApiResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        user_id = await unified_user_repository.create_user(user_data)
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
        user_data = await unified_user_repository.get_user_by_id(current_user)
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
        success = await unified_user_repository.update_user(current_user, user_data)
        if success:
            updated_user = await unified_user_repository.get_user_by_id(current_user)
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
        success = await unified_user_repository.update_password(
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


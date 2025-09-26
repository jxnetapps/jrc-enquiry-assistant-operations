from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, TypeVar, Generic
import logging

from auth.authentication import AuthHandler, authenticate_user

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["Authentication"])

# Initialize components
auth_handler = AuthHandler()

T = TypeVar('T')

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenRequest(BaseModel):
    user_id: str

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: Optional[str] = None
    access_token: Optional[str] = None
    user_id: Optional[str] = None
    data: Optional[T] = None

@router.post("/login", response_model=ApiResponse)
async def login(login_data: LoginRequest):
    """User login endpoint"""
    try:
        user_id = authenticate_user(login_data.username, login_data.password)
        if user_id:
            token = auth_handler.create_token(user_id)
            return ApiResponse(
                success=True,
                message="Login successful",
                access_token=token,
                user_id=user_id
            )
        else:
            return ApiResponse(
                success=False,
                message="Invalid credentials"
            )
    except Exception as e:
        logger.error(f"Login error: {e}")
        return ApiResponse(
            success=False,
            message="Login failed"
        )

@router.post("/token", response_model=ApiResponse)
async def create_token(token_data: TokenRequest):
    """Create JWT token for a valid user_id"""
    try:
        from auth.user_store import user_store
        
        # Validate that user_id exists in the user store
        user_data = user_store.get_user_by_id(token_data.user_id)
        if not user_data:
            return ApiResponse(
                success=False,
                message="User not found"
            )
        
        # Create JWT token for the valid user_id
        token = auth_handler.create_token(token_data.user_id)
        
        return ApiResponse(
            success=True,
            message="Token created successfully",
            access_token=token,
            user_id=token_data.user_id,
            data={"username": user_data["user_name"]}
        )
        
    except Exception as e:
        logger.error(f"Token creation error: {e}")
        return ApiResponse(
            success=False,
            message="Error creating token"
        )

@router.get("/user/info", response_model=ApiResponse)
async def get_user_info(current_user: str = Depends(auth_handler.get_current_user)):
    """Get current user information"""
    try:
        from auth.user_store import user_store
        user_data = user_store.get_user_by_id(current_user)
        if user_data:
            return ApiResponse(
                success=True,
                message="User information retrieved successfully",
                user_id=user_data["user_id"],
                data={"username": user_data["user_name"]}
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

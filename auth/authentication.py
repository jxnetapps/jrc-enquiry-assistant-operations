from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from typing import Optional
from config import Config
from database.unified_user_repository import unified_user_repository

security = HTTPBearer()

class AuthHandler:
    def __init__(self):
        self.secret_key = Config.JWT_SECRET_KEY
        self.algorithm = Config.JWT_ALGORITHM
        
    def create_token(self, user_id: str) -> str:
        """Create JWT token with user_id as subject."""
        payload = {
            'exp': datetime.utcnow() + timedelta(hours=Config.JWT_ACCESS_TOKEN_EXPIRE_HOURS),
            'iat': datetime.utcnow(),
            'sub': user_id  # Store user_id instead of username
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return user_id."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload['sub']  # Return user_id
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
        """Get current user_id from JWT token."""
        token = credentials.credentials
        user_id = self.verify_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify user still exists in database
        user = await unified_user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Check if user is active
        if user.status != Config.DEFAULT_USER_STATUS:
            raise HTTPException(status_code=401, detail="User account is not active")
        
        return user_id

async def authenticate_user(username: str, password: str) -> Optional[str]:
    """Authenticate user and return user_id if successful."""
    user_response = await unified_user_repository.authenticate_user(username, password)
    if user_response:
        return user_response.user_id
    return None
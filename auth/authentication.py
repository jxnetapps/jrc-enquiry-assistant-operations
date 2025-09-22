from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from typing import Optional
from config import Config
from .user_store import user_store

security = HTTPBearer()

class AuthHandler:
    def __init__(self):
        self.secret_key = Config.JWT_SECRET_KEY
        self.algorithm = "HS256"
        
    def create_token(self, user_id: str) -> str:
        """Create JWT token with user_id as subject."""
        payload = {
            'exp': datetime.utcnow() + timedelta(hours=24),
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
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
        """Get current user_id from JWT token."""
        token = credentials.credentials
        user_id = self.verify_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify user still exists in user store
        if not user_store.get_user_by_id(user_id):
            raise HTTPException(status_code=401, detail="User not found")
        
        return user_id

def authenticate_user(username: str, password: str) -> Optional[str]:
    """Authenticate user and return user_id if successful."""
    return user_store.authenticate_user(username, password)
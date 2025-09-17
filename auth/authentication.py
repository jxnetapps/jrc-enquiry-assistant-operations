from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from typing import Optional
from config import Config

security = HTTPBearer()

class AuthHandler:
    def __init__(self):
        self.secret_key = Config.JWT_SECRET_KEY
        self.algorithm = "HS256"
        
    def create_token(self, username: str) -> str:
        payload = {
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow(),
            'sub': username
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
        token = credentials.credentials
        username = self.verify_token(token)
        if not username:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return username

def authenticate_user(username: str, password: str) -> bool:
    if Config.ALLOW_ANY_USER:
        # Accept any username/password for testing; data is still namespaced per user
        return True
    return (username == Config.ADMIN_USERNAME and 
            password == Config.ADMIN_PASSWORD)

"""
In-memory user database for storing user credentials and managing user sessions.
"""

from typing import Optional, Dict, List
import uuid
import hashlib
import logging

logger = logging.getLogger(__name__)

class UserStore:
    """In-memory user database with user_id, user_name, and password management."""
    
    def __init__(self):
        self.users: Dict[str, Dict[str, str]] = {}
        self._initialize_default_users()
    
    def _initialize_default_users(self):
        """Initialize with the provided user data."""
        default_users = [
            {
                "user_id": "323a9ded-e05b-4f59-8594-79a8057aa7ec",
                "user_name": "admin",
                "password": "Wildcat@007"
            },
            {
                "user_id": "97439590-78d1-4971-bea0-fee7b6e43be5",
                "user_name": "edifyho",
                "password": "Wildcat@007"
            },
            {
                "user_id": "c0cc3553-7b5d-4283-a512-01092f19da3a",
                "user_name": "edifykids",
                "password": "Wildcat@007"
            },
            {
                "user_id": "6019ed7f-530d-463f-addd-a53f2e1ca3cc",
                "user_name": "drsis",
                "password": "Wildcat@007"
            }
        ]
        
        for user in default_users:
            self.users[user["user_id"]] = {
                "user_id": user["user_id"],
                "user_name": user["user_name"],
                "password": self._hash_password(user["password"])
            }
        
        logger.info(f"Initialized user store with {len(self.users)} users")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, user_name: str, password: str) -> Optional[str]:
        """
        Authenticate user by user_name and password.
        Returns user_id if authentication successful, None otherwise.
        """
        hashed_password = self._hash_password(password)
        
        for user_id, user_data in self.users.items():
            if (user_data["user_name"] == user_name and 
                user_data["password"] == hashed_password):
                logger.info(f"User authenticated: {user_name} -> {user_id}")
                return user_id
        
        logger.warning(f"Authentication failed for user: {user_name}")
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, str]]:
        """Get user data by user_id."""
        return self.users.get(user_id)
    
    def get_user_by_name(self, user_name: str) -> Optional[Dict[str, str]]:
        """Get user data by user_name."""
        for user_data in self.users.values():
            if user_data["user_name"] == user_name:
                return user_data
        return None
    
    def add_user(self, user_name: str, password: str) -> str:
        """Add a new user and return the generated user_id."""
        # Check if user_name already exists
        if self.get_user_by_name(user_name):
            raise ValueError(f"User with name '{user_name}' already exists")
        
        user_id = str(uuid.uuid4())
        self.users[user_id] = {
            "user_id": user_id,
            "user_name": user_name,
            "password": self._hash_password(password)
        }
        
        logger.info(f"Added new user: {user_name} -> {user_id}")
        return user_id
    
    def update_user_password(self, user_id: str, new_password: str) -> bool:
        """Update user password by user_id."""
        if user_id in self.users:
            self.users[user_id]["password"] = self._hash_password(new_password)
            logger.info(f"Updated password for user: {user_id}")
            return True
        return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user by user_id."""
        if user_id in self.users:
            user_name = self.users[user_id]["user_name"]
            del self.users[user_id]
            logger.info(f"Deleted user: {user_name} -> {user_id}")
            return True
        return False
    
    def list_users(self) -> List[Dict[str, str]]:
        """List all users (without passwords)."""
        return [
            {
                "user_id": user_data["user_id"],
                "user_name": user_data["user_name"]
            }
            for user_data in self.users.values()
        ]
    
    def get_user_count(self) -> int:
        """Get total number of users."""
        return len(self.users)

# Global user store instance
user_store = UserStore()

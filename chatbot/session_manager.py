"""
Session manager for persistent chat sessions across requests.
"""

import logging
from typing import Dict, Optional
from chatbot.chat_states import PreTrainedChatFlow

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages chat sessions across requests"""
    
    def __init__(self):
        self._flows: Dict[str, PreTrainedChatFlow] = {}
    
    def get_flow_for_user(self, user_id: str) -> PreTrainedChatFlow:
        """Get or create a PreTrainedChatFlow for a user"""
        if user_id not in self._flows:
            self._flows[user_id] = PreTrainedChatFlow()
            logger.debug(f"Created new flow for user: {user_id}")
        return self._flows[user_id]
    
    def reset_user_session(self, user_id: str) -> None:
        """Reset a user's chat session"""
        if user_id in self._flows:
            self._flows[user_id].reset_session(user_id)
            logger.debug(f"Reset session for user: {user_id}")
    
    def get_user_session_data(self, user_id: str) -> Optional[dict]:
        """Get collected data for a user session"""
        if user_id in self._flows:
            return self._flows[user_id].get_session_data(user_id)
        return None
    
    def remove_user_session(self, user_id: str) -> None:
        """Remove a user's session completely"""
        if user_id in self._flows:
            del self._flows[user_id]
            logger.debug(f"Removed session for user: {user_id}")

# Global session manager instance
session_manager = SessionManager()

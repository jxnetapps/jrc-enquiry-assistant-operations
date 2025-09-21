"""
Chat state management for predefined question flows.
Handles state-driven conversations for pre_trained chat behavior.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class ChatState(Enum):
    """Chat conversation states"""
    INITIAL = "initial"
    PARENT_TYPE = "parent_type"
    SCHOOL_TYPE = "school_type"
    COLLECT_NAME = "collect_name"
    COLLECT_MOBILE = "collect_mobile"
    KNOW_MORE = "know_more"
    KNOWLEDGE_QUERY = "knowledge_query"
    END = "end"

@dataclass
class ChatSession:
    """Represents a chat session with state and collected data"""
    user_id: str
    state: ChatState = ChatState.INITIAL
    collected_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.collected_data is None:
            self.collected_data = {}

class PreTrainedChatFlow:
    """Manages the predefined question flow for pre_trained chat behavior"""
    
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
    
    def get_or_create_session(self, user_id: str) -> ChatSession:
        """Get existing session or create new one"""
        if user_id not in self.sessions:
            self.sessions[user_id] = ChatSession(user_id=user_id)
        return self.sessions[user_id]
    
    def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Process incoming message and return response based on current state"""
        session = self.get_or_create_session(user_id)
        
        # Clean and normalize the message
        original_message = message
        message = message.strip().lower()
        
        # Debug logging
        logger.debug(f"Processing message: '{original_message}' -> '{message}' in state: {session.state}")
        
        try:
            if session.state == ChatState.INITIAL:
                return self._handle_initial_state(session, message)
            elif session.state == ChatState.PARENT_TYPE:
                return self._handle_parent_type(session, message)
            elif session.state == ChatState.SCHOOL_TYPE:
                return self._handle_school_type(session, message)
            elif session.state == ChatState.COLLECT_NAME:
                return self._handle_collect_name(session, message)
            elif session.state == ChatState.COLLECT_MOBILE:
                return self._handle_collect_mobile(session, message)
            elif session.state == ChatState.KNOW_MORE:
                return self._handle_know_more(session, message)
            elif session.state == ChatState.KNOWLEDGE_QUERY:
                return self._handle_knowledge_query(session, message)
            elif session.state == ChatState.END:
                return self._handle_end_state(session, message)
            else:
                return self._create_error_response("Unknown chat state")
                
        except Exception as e:
            logger.error(f"Error processing message in state {session.state}: {e}")
            return self._create_error_response("Sorry, I encountered an error. Let's start over.")
    
    def _handle_initial_state(self, session: ChatSession, message: str) -> Dict[str, Any]:
        """Handle initial state - ask about parent type"""
        session.state = ChatState.PARENT_TYPE
        return {
            "response": "Are you a new or existing parent?",
            "options": ["New Parent", "Existing Parent"],
            "state": session.state.value,
            "requires_input": True
        }
    
    def _handle_parent_type(self, session: ChatSession, message: str) -> Dict[str, Any]:
        """Handle parent type selection"""
        # More robust matching for parent type selection
        if any(keyword in message for keyword in ["new parent", "new", "1"]):
            session.collected_data["parent_type"] = "New Parent"
            session.state = ChatState.SCHOOL_TYPE
            return {
                "response": "What type of school are you looking for?",
                "options": ["Day", "Boarding"],
                "state": session.state.value,
                "requires_input": True
            }
        elif any(keyword in message for keyword in ["existing parent", "existing", "2"]):
            session.collected_data["parent_type"] = "Existing Parent"
            session.state = ChatState.SCHOOL_TYPE
            return {
                "response": "What type of school are you looking for?",
                "options": ["Day", "Boarding"],
                "state": session.state.value,
                "requires_input": True
            }
        else:
            return {
                "response": "Please select one of the options: New Parent or Existing Parent",
                "options": ["New Parent", "Existing Parent"],
                "state": session.state.value,
                "requires_input": True
            }
    
    def _handle_school_type(self, session: ChatSession, message: str) -> Dict[str, Any]:
        """Handle school type selection"""
        if any(keyword in message for keyword in ["day", "1"]):
            session.collected_data["school_type"] = "Day"
        elif any(keyword in message for keyword in ["boarding", "2"]):
            session.collected_data["school_type"] = "Boarding"
        else:
            return {
                "response": "Please select one of the options: Day or Boarding",
                "options": ["Day", "Boarding"],
                "state": session.state.value,
                "requires_input": True
            }
        
        session.state = ChatState.COLLECT_NAME
        return {
            "response": "Please provide your name:",
            "state": session.state.value,
            "requires_input": True
        }
    
    def _handle_collect_name(self, session: ChatSession, message: str) -> Dict[str, Any]:
        """Handle name collection"""
        if len(message.strip()) < 2:
            return {
                "response": "Please provide a valid name (at least 2 characters):",
                "state": session.state.value,
                "requires_input": True
            }
        
        session.collected_data["name"] = message.strip().title()
        session.state = ChatState.COLLECT_MOBILE
        return {
            "response": "Please provide your mobile number:",
            "state": session.state.value,
            "requires_input": True
        }
    
    def _handle_collect_mobile(self, session: ChatSession, message: str) -> Dict[str, Any]:
        """Handle mobile number collection"""
        # Basic mobile number validation
        mobile = ''.join(filter(str.isdigit, message))
        if len(mobile) < 10:
            return {
                "response": "Please provide a valid mobile number (at least 10 digits):",
                "state": session.state.value,
                "requires_input": True
            }
        
        session.collected_data["mobile"] = mobile
        session.state = ChatState.KNOW_MORE
        return {
            "response": "Do you want to know more about the school?",
            "options": ["Yes", "No"],
            "state": session.state.value,
            "requires_input": True
        }
    
    def _handle_know_more(self, session: ChatSession, message: str) -> Dict[str, Any]:
        """Handle know more question"""
        if any(keyword in message for keyword in ["yes", "y", "1"]):
            session.state = ChatState.KNOWLEDGE_QUERY
            return {
                "response": "Great! I'm ready to answer your questions about the school. What would you like to know?",
                "state": session.state.value,
                "requires_input": True,
                "collected_data": session.collected_data
            }
        elif any(keyword in message for keyword in ["no", "n", "2"]):
            session.state = ChatState.END
            return self._create_thank_you_response(session)
        else:
            return {
                "response": "Please select one of the options: Yes or No",
                "options": ["Yes", "No"],
                "state": session.state.value,
                "requires_input": True
            }
    
    def _handle_knowledge_query(self, session: ChatSession, message: str) -> Dict[str, Any]:
        """Handle knowledge-based queries"""
        # This will be handled by the main chat interface
        return {
            "response": "knowledge_query",
            "query": message,
            "state": session.state.value,
            "collected_data": session.collected_data,
            "requires_input": False
        }
    
    def _handle_end_state(self, session: ChatSession, message: str) -> Dict[str, Any]:
        """Handle end state"""
        return self._create_thank_you_response(session)
    
    def _create_thank_you_response(self, session: ChatSession) -> Dict[str, Any]:
        """Create thank you response with collected data summary"""
        data = session.collected_data
        response = f"Thank you for your interest! Here's a summary of your information:\n\n"
        response += f"• Parent Type: {data.get('parent_type', 'N/A')}\n"
        response += f"• School Type: {data.get('school_type', 'N/A')}\n"
        response += f"• Name: {data.get('name', 'N/A')}\n"
        response += f"• Mobile: {data.get('mobile', 'N/A')}\n\n"
        response += "We'll be in touch soon!"
        
        session.state = ChatState.END
        return {
            "response": response,
            "state": session.state.value,
            "collected_data": session.collected_data,
            "requires_input": False,
            "conversation_complete": True
        }
    
    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "response": message,
            "state": "error",
            "requires_input": False,
            "error": True
        }
    
    def reset_session(self, user_id: str) -> None:
        """Reset a user's chat session"""
        if user_id in self.sessions:
            del self.sessions[user_id]
    
    def get_session_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get collected data for a user session"""
        if user_id in self.sessions:
            return self.sessions[user_id].collected_data
        return None

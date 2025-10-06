import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import json

class SessionManager:
    """Manages user sessions and conversation history"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_secret = os.environ.get("SESSION_SECRET", "default_secret_key")
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get or create a session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "messages": [],
                "user_preferences": {},
                "travel_context": {}
            }
        else:
            self.sessions[session_id]["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        return self.sessions[session_id]
    
    def update_session(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Update session data"""
        if session_id in self.sessions:
            session_data["last_updated"] = datetime.now(timezone.utc).isoformat()
            self.sessions[session_id].update(session_data)
        else:
            session_data["created_at"] = datetime.now(timezone.utc).isoformat()
            session_data["last_updated"] = datetime.now(timezone.utc).isoformat()
            self.sessions[session_id] = session_data
    
    def clear_session(self, session_id: str) -> None:
        """Clear conversation history for a session"""
        if session_id in self.sessions:
            # Keep session metadata but clear messages
            self.sessions[session_id]["messages"] = []
            self.sessions[session_id]["last_updated"] = datetime.now(timezone.utc).isoformat()
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session completely"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        return len(self.sessions)
    
    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all session data (admin function)"""
        return self.sessions.copy()
    
    def cleanup_old_sessions(self, hours: int = 24) -> int:
        """Clean up sessions older than specified hours"""
        from datetime import timedelta
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        sessions_to_delete = []
        
        for session_id, session_data in self.sessions.items():
            try:
                last_updated_str = session_data.get("last_updated")
                if last_updated_str:
                    last_updated = datetime.fromisoformat(last_updated_str.replace('Z', '+00:00'))
                    if last_updated < cutoff_time:
                        sessions_to_delete.append(session_id)
            except (ValueError, TypeError):
                # If we can't parse the date, delete the session
                sessions_to_delete.append(session_id)
        
        for session_id in sessions_to_delete:
            del self.sessions[session_id]
        
        return len(sessions_to_delete)
    
    def save_user_preference(self, session_id: str, key: str, value: Any) -> None:
        """Save user preference for future use"""
        session = self.get_session(session_id)
        if "user_preferences" not in session:
            session["user_preferences"] = {}
        session["user_preferences"][key] = value
        self.update_session(session_id, session)
    
    def get_user_preference(self, session_id: str, key: str, default: Any = None) -> Any:
        """Get user preference"""
        session = self.get_session(session_id)
        return session.get("user_preferences", {}).get(key, default)
    
    def save_travel_context(self, session_id: str, context: Dict[str, Any]) -> None:
        """Save travel planning context"""
        session = self.get_session(session_id)
        if "travel_context" not in session:
            session["travel_context"] = {}
        session["travel_context"].update(context)
        self.update_session(session_id, session)
    
    def get_travel_context(self, session_id: str) -> Dict[str, Any]:
        """Get travel planning context"""
        session = self.get_session(session_id)
        return session.get("travel_context", {})

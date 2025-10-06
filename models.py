from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    session_id: str

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    session_id: str

class ClearRequest(BaseModel):
    """Request model for clearing conversation"""
    session_id: str

class SessionInfo(BaseModel):
    """Model for session information"""
    session_id: str
    message_count: int
    created_at: Optional[str] = None
    last_updated: Optional[str] = None

class ConversationMessage(BaseModel):
    """Model for individual messages in conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class TravelIntent(BaseModel):
    """Model for classified travel intents"""
    intent: str
    confidence: float
    key_entities: List[str] = []

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from travel_agent import TravelPlanningAgent
from session_manager import SessionManager
from models import ChatRequest, ChatResponse, ClearRequest

# Initialize FastAPI app
app = FastAPI(title="Travel Planning Chatbot API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
session_manager = SessionManager()
travel_agent = TravelPlanningAgent()

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat messages and return AI responses"""
    try:
        # Get or create session
        session = session_manager.get_session(request.session_id)
        
        # Process message through travel agent
        response = await travel_agent.process_message(
            message=request.message,
            session_id=request.session_id,
            conversation_history=session.get("messages", [])
        )
        
        # Update session with new messages
        if "messages" not in session:
            session["messages"] = []
        
        session["messages"].extend([
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": response}
        ])
        
        session_manager.update_session(request.session_id, session)
        
        return ChatResponse(
            response=response,
            session_id=request.session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.post("/clear")
async def clear_conversation(request: ClearRequest):
    """Clear conversation history for a session"""
    try:
        session_manager.clear_session(request.session_id)
        return {"status": "success", "message": "Conversation cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing conversation: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Travel Planning Chatbot API"}

@app.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get session information"""
    try:
        session = session_manager.get_session(session_id)
        return {
            "session_id": session_id,
            "message_count": len(session.get("messages", [])),
            "created_at": session.get("created_at"),
            "last_updated": session.get("last_updated")
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Session not found: {str(e)}")

if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(
        "backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

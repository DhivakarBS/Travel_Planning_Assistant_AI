# Travel Planning Assistant

## Overview

This is a Travel Planning Assistant application that uses AI to help users plan their trips. The system consists of a Streamlit frontend for user interaction and a FastAPI backend that processes travel-related queries using Google's Gemini AI model. The application uses LangGraph to orchestrate conversational flows and maintains user sessions to provide contextual responses throughout the planning process.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application
- **Session Management**: Client-side session state using UUID-based session identifiers
- **Communication**: REST API calls to backend service
- **Design Pattern**: Single-page application with real-time chat interface

**Rationale**: Streamlit provides a rapid development framework for data-centric applications with built-in state management, making it ideal for prototyping conversational interfaces without complex frontend setup.

### Backend Architecture
- **Framework**: FastAPI for REST API endpoints
- **AI Orchestration**: LangGraph for conversation flow management
- **Conversation Model**: Stateful conversation graph with intent classification
- **Session Storage**: In-memory dictionary-based session store
- **Design Pattern**: Service-oriented architecture with separated concerns (agent, session manager, models)

**Rationale**: FastAPI provides high performance and automatic API documentation. LangGraph enables complex conversational flows with state management. In-memory storage keeps the application lightweight for development/prototyping, though this should be replaced with persistent storage for production.

**Pros**:
- Fast development and deployment
- Built-in async support
- Type safety with Pydantic models

**Cons**:
- In-memory sessions are not persistent across restarts
- Single-instance limitation without external session store

### AI/ML Architecture
- **LLM Provider**: Google Gemini (gemini-2.0-flash model)
- **Conversation Framework**: LangGraph for state machine-based dialogue management
- **Intent Classification**: AI-powered intent recognition for travel-specific queries (destinations, itineraries, budgets, accommodations, transportation, dining, requirements)
- **Context Management**: Session-based conversation history passed to AI for context-aware responses

**Rationale**: Gemini provides strong general knowledge for travel planning. LangGraph enables sophisticated multi-turn conversations with state tracking, allowing the agent to maintain context and handle complex travel planning workflows.

### Data Models
- **Pydantic Models**: Strongly-typed request/response validation
- **Session Structure**: Hierarchical session data with metadata, messages, preferences, and travel context
- **Message Format**: Role-based conversation history (user/assistant)

**Rationale**: Pydantic provides automatic validation and serialization, reducing bugs and improving API contract clarity.

## External Dependencies

### Third-Party Services
1. **Google Gemini AI** (`google-genai` SDK)
   - Purpose: Natural language understanding and response generation
   - Authentication: API key via `GEMINI_API_KEY` environment variable
   - Model: gemini-2.0-flash

2. **LangGraph** (`langgraph`)
   - Purpose: Conversational AI workflow orchestration
   - Provides state machine for multi-step travel planning conversations

3. **LangChain Core** (`langchain_core`)
   - Purpose: Message formatting and abstractions for LLM interactions
   - Used for standardized message types (HumanMessage, AIMessage)

### Frameworks & Libraries
- **FastAPI**: REST API framework with CORS support
- **Streamlit**: Frontend web application framework
- **Uvicorn**: ASGI server for FastAPI
- **Pydantic**: Data validation and settings management
- **Requests**: HTTP client for frontend-to-backend communication

### Environment Configuration
Required environment variables:
- `GEMINI_API_KEY`: Google Gemini API authentication
- `SESSION_SECRET`: Session encryption key (defaults to "default_secret_key")

### Infrastructure
- **Backend Port**: 8000 (FastAPI/Uvicorn)
- **CORS**: Configured to allow all origins (should be restricted in production)
- **Timeout Settings**: 30-second request timeout on frontend
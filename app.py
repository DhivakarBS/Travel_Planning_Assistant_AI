import streamlit as st
import requests
import json
import uuid

# Configure the page
st.set_page_config(
    page_title="Travel Planning Assistant",
    page_icon="✈️",
    layout="wide"
)

# Backend API URL
BACKEND_URL = "http://localhost:8000"

def initialize_session():
    """Initialize session state variables"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False

def send_message(message: str):
    """Send message to backend and get response"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "message": message,
                "session_id": st.session_state.session_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "response": f"Error: {response.status_code} - {response.text}",
                "session_id": st.session_state.session_id
            }
    except requests.exceptions.ConnectionError:
        return {
            "response": "Error: Cannot connect to backend service. Please ensure the FastAPI backend is running on port 8000.",
            "session_id": st.session_state.session_id
        }
    except requests.exceptions.Timeout:
        return {
            "response": "Error: Request timeout. The AI service may be taking longer than expected.",
            "session_id": st.session_state.session_id
        }
    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "session_id": st.session_state.session_id
        }

def clear_conversation():
    """Clear conversation history"""
    try:
        requests.post(
            f"{BACKEND_URL}/clear",
            json={"session_id": st.session_state.session_id}
        )
    except:
        pass  # Ignore errors when clearing
    
    st.session_state.messages = []
    st.session_state.conversation_started = False
    st.rerun()

def main():
    initialize_session()
    
    # Header
    st.title("✈️ Travel Planning Assistant")
    st.markdown("Your AI-powered travel companion to help plan amazing trips!")
    
    # Sidebar with session info and controls
    with st.sidebar:
        st.header("🎯 Session Info")
        st.write(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
        st.write(f"**Messages:** {len(st.session_state.messages)}")
        
        st.divider()
        
        st.header("🛠️ Controls")
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            clear_conversation()
        
        if st.button("🔄 New Session", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.conversation_started = False
            st.rerun()
        
        st.divider()
        
        st.header("💡 Travel Tips")
        st.markdown("""
        **Ask me about:**
        - 🌍 Destination recommendations
        - 🗓️ Trip itinerary planning
        - 💰 Budget estimation
        - 🏨 Accommodation suggestions
        - 🍽️ Local cuisine and dining
        - 🚌 Transportation options
        - 📱 Travel tips and requirements
        """)

    # Main chat interface
    st.divider()
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.info("👋 Welcome! I'm your travel planning assistant. Tell me about your dream destination or ask me anything about travel planning!")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me about travel planning..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.conversation_started = True
        
        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
        
        # Get AI response
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Planning your perfect trip..."):
                    response_data = send_message(prompt)
                    response_text = response_data.get("response", "I'm sorry, I couldn't process your request.")
                    st.markdown(response_text)
        
        # Add assistant response to chat
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.rerun()

    # Footer
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("*Powered by OpenAI GPT-5 and LangGraph*")

if __name__ == "__main__":
    main()

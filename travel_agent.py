import os
import json
from typing import List, Dict, Any
from openai import OpenAI
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage

# Initialize OpenAI client
# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

class TravelPlanningAgent:
    """LangGraph-powered travel planning assistant"""
    
    def __init__(self):
        self.client = openai_client
        self.graph = self._create_conversation_graph()
        
    def _create_conversation_graph(self):
        """Create LangGraph conversation flow"""
        
        def analyze_travel_intent(state: Dict[str, Any]) -> Dict[str, Any]:
            """Analyze user's travel-related intent"""
            message = state.get("current_message", "")
            
            # Use GPT-5 to classify the travel intent
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a travel intent classifier. Analyze the user's message and classify it into one of these categories:
                        - destination_inquiry: asking about places to visit
                        - itinerary_planning: planning day-by-day activities
                        - budget_planning: asking about costs and budgets
                        - accommodation: hotels, stays, lodging
                        - transportation: flights, trains, cars, local transport
                        - dining: restaurants, local food, cuisine
                        - requirements: visas, documents, travel requirements
                        - general_travel: general travel advice or tips
                        - greeting: initial greeting or introduction
                        - other: non-travel related
                        
                        Respond with JSON: {"intent": "category", "confidence": 0.95, "key_entities": ["entity1", "entity2"]}"""
                    },
                    {"role": "user", "content": message}
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=200
            )
            
            try:
                intent_data = json.loads(response.choices[0].message.content)
                state["intent"] = intent_data.get("intent", "general_travel")
                state["entities"] = intent_data.get("key_entities", [])
                state["confidence"] = intent_data.get("confidence", 0.5)
            except:
                state["intent"] = "general_travel"
                state["entities"] = []
                state["confidence"] = 0.5
                
            return state
        
        def generate_travel_response(state: Dict[str, Any]) -> Dict[str, Any]:
            """Generate travel-specific response based on intent"""
            message = state.get("current_message", "")
            intent = state.get("intent", "general_travel")
            history = state.get("conversation_history", [])
            
            # Create context-aware system prompt based on intent
            system_prompts = {
                "destination_inquiry": "You are an expert travel advisor specializing in destination recommendations. Provide detailed, personalized suggestions based on the user's preferences, including best times to visit, must-see attractions, and insider tips.",
                
                "itinerary_planning": "You are a professional itinerary planner. Create detailed day-by-day plans with specific times, locations, and activities. Consider travel time between locations and practical logistics.",
                
                "budget_planning": "You are a travel budget specialist. Provide detailed cost breakdowns for different travel styles (budget, mid-range, luxury) including accommodation, food, transportation, and activities.",
                
                "accommodation": "You are a hotel and accommodation expert. Recommend specific places to stay based on budget, location preferences, and travel style. Include booking tips and alternatives.",
                
                "transportation": "You are a transportation planning expert. Provide detailed advice on flights, ground transportation, and local travel options with specific recommendations and booking strategies.",
                
                "dining": "You are a culinary travel expert. Recommend authentic local restaurants, must-try dishes, food markets, and dining experiences that showcase local culture.",
                
                "requirements": "You are a travel documentation and requirements specialist. Provide accurate, up-to-date information about visas, passports, health requirements, and travel restrictions.",
                
                "greeting": "You are a friendly travel planning assistant. Welcome the user warmly and explain how you can help them plan their perfect trip.",
                
                "general_travel": "You are an experienced travel advisor. Provide helpful, practical travel advice and be ready to assist with any aspect of trip planning."
            }
            
            system_prompt = system_prompts.get(intent, system_prompts["general_travel"])
            
            # Build conversation context
            messages = [
                {"role": "system", "content": f"{system_prompt}\n\nAlways be enthusiastic, helpful, and provide actionable advice. If you need more information to give better recommendations, ask specific follow-up questions."}
            ]
            
            # Add conversation history
            for msg in history[-6:]:  # Keep last 6 messages for context
                messages.append(msg)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Generate response
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=messages,
                max_completion_tokens=800
            )
            
            state["response"] = response.choices[0].message.content
            return state
        
        def should_ask_followup(state: Dict[str, Any]) -> str:
            """Determine if we should ask follow-up questions"""
            intent = state.get("intent", "general_travel")
            confidence = state.get("confidence", 0.5)
            
            # Ask follow-up for high-level inquiries or low confidence
            if intent in ["destination_inquiry", "itinerary_planning", "budget_planning"] and confidence > 0.7:
                return "followup"
            return "respond"
        
        def add_followup_questions(state: Dict[str, Any]) -> Dict[str, Any]:
            """Add relevant follow-up questions to the response"""
            current_response = state.get("response", "")
            intent = state.get("intent", "general_travel")
            
            followup_questions = {
                "destination_inquiry": [
                    "What's your budget range for this trip?",
                    "How many days are you planning to travel?",
                    "What type of activities interest you most (adventure, culture, relaxation, nightlife)?"
                ],
                "itinerary_planning": [
                    "What's your preferred pace (packed schedule vs. relaxed)?",
                    "Are there any specific must-see attractions on your list?",
                    "What's your accommodation preference (location, style)?"
                ],
                "budget_planning": [
                    "What's your total budget range?",
                    "Which expenses are most important to you (accommodation, food, activities)?",
                    "Are you flexible with travel dates for better deals?"
                ]
            }
            
            if intent in followup_questions:
                questions = followup_questions[intent]
                followup_text = f"\n\n🤔 **To help you better, I'd love to know:**\n" + \
                              "\n".join([f"• {q}" for q in questions[:2]])  # Limit to 2 questions
                state["response"] = current_response + followup_text
            
            return state
        
        # Create the graph
        workflow = StateGraph(dict)
        
        # Add nodes
        workflow.add_node("analyze_intent", analyze_travel_intent)
        workflow.add_node("generate_response", generate_travel_response)
        workflow.add_node("add_followup", add_followup_questions)
        
        # Set entry point
        workflow.set_entry_point("analyze_intent")
        
        # Add edges
        workflow.add_edge("analyze_intent", "generate_response")
        workflow.add_conditional_edges(
            "generate_response",
            should_ask_followup,
            {
                "followup": "add_followup",
                "respond": "__end__"
            }
        )
        workflow.add_edge("add_followup", "__end__")
        
        return workflow.compile()
    
    async def process_message(self, message: str, session_id: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Process a user message through the LangGraph workflow"""
        try:
            if conversation_history is None:
                conversation_history = []
            
            # Convert to proper format
            formatted_history = []
            for msg in conversation_history:
                if msg.get("role") == "user":
                    formatted_history.append({"role": "user", "content": msg["content"]})
                elif msg.get("role") == "assistant":
                    formatted_history.append({"role": "assistant", "content": msg["content"]})
            
            # Initial state
            initial_state = {
                "current_message": message,
                "session_id": session_id,
                "conversation_history": formatted_history
            }
            
            # Run through the graph
            result = await self._run_graph_async(initial_state)
            
            return result.get("response", "I'm sorry, I couldn't process your travel request. Please try again!")
            
        except Exception as e:
            return f"I encountered an error while planning your trip: {str(e)}. Please try rephrasing your question."
    
    async def _run_graph_async(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the LangGraph workflow asynchronously"""
        try:
            # Since LangGraph might not have native async support, we'll run it synchronously
            result = self.graph.invoke(initial_state)
            return result
        except Exception as e:
            return {"response": f"Graph execution error: {str(e)}"}

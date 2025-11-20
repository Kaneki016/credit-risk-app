from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging

from backend.utils.ai_client import get_ai_client

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's query string")
    history: Optional[List[ChatMessage]] = []
    context: Optional[Dict[str, Any]] = None

@router.post("/chatbot/query")
async def chatbot_query(request: ChatRequest):
    """
    Process a user query via the AI chatbot.
    """
    try:
        ai_client = get_ai_client()
        
        if not ai_client.is_available():
            return {
                "response": "I apologize, but I am currently offline (API key not configured). Please check the system configuration.",
                "error": "no_api_key"
            }
            
        # Construct prompt with history
        system_prompt = """You are the dedicated AI Assistant for the Credit Risk Prediction System.
        
        Your SOLE purpose is to assist users with this specific application.
        
        SYSTEM CAPABILITIES:
        1. Predict Credit Risk: Analyze loan applications using XGBoost to predict default probability.
        2. Explain Decisions: Use SHAP values to explain why a loan was approved or rejected.
        3. Retrain Models: Learn from new historical data (CSV imports) to improve accuracy.
        4. Manage Data: Import/Export loan data and view database statistics.
        
        STRICT GUIDELINES:
        - ONLY answer questions related to credit risk, banking, loan assessment, or this specific software.
        - If a user asks about general topics (e.g., "Who is the president?", "Write a poem", "Python code"), politely REFUSE.
        - Say: "I can only assist with credit risk assessment and navigating this application."
        - Be professional, concise, and financial-focused.
        - Do not hallucinate features that don't exist (e.g., we don't have image recognition).
        
        CONTEXT:
        The user is interacting with the web dashboard of the Credit Risk Prediction System.
        """
        
        # Build conversation context
        messages_text = ""
        if request.history:
            for msg in request.history[-5:]: # Keep last 5 messages for context
                messages_text += f"{msg.role}: {msg.content}\n"
        
        messages_text += f"user: {request.query}\n"
        
        if request.context:
            messages_text += f"\nContext: {request.context}\n"
            
        prompt = f"""
        Conversation history:
        {messages_text}
        
        Please provide a helpful response to the user's last message, adhering strictly to your role as a Credit Risk Assistant.
        """
        
        # Call AI
        result = await ai_client.generate_with_retry(prompt, system_prompt)
        
        if result.get("error"):
            logger.warning(f"Chatbot error: {result.get('error')}")
            return {
                "response": "I encountered an error processing your request. Please try again later.",
                "error": result.get("error")
            }
            
        return {
            "response": result.get("text", "I'm not sure how to respond to that."),
            "raw": result.get("raw")
        }
        
    except Exception as e:
        logger.error(f"Chatbot exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))

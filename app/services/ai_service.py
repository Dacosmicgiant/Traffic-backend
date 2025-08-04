from abc import ABC, abstractmethod
from typing import List, Dict, Any
import google.generativeai as genai
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class AIServiceInterface(ABC):
    """
    Abstract base class for AI services.
    This makes it easy to swap between different AI providers.
    """
    
    @abstractmethod
    async def generate_response(self, message: str, conversation_history: List[Dict[str, str]]) -> str:
        """
        Generate AI response based on user message and conversation history.
        
        Args:
            message: The user's current message
            conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
            
        Returns:
            AI-generated response as string
        """
        pass


class GeminiAIService(AIServiceInterface):
    """
    Concrete implementation using Google Gemini API.
    Focuses on Indian traffic law queries.
    """
    
    def __init__(self):
        """Initialize Gemini API with configuration"""
        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini AI service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI service: {e}")
            raise

    def _create_system_prompt(self) -> str:
        """Create system prompt focused on Indian traffic laws"""
        return """You are an expert AI assistant specializing in Indian traffic laws and regulations. 

Your primary focus areas include:
- Motor Vehicle Act, 1988 and its amendments
- Traffic rules and regulations in India
- Traffic fines and penalties
- Driving license procedures and requirements
- Vehicle registration processes
- Road safety guidelines
- State-specific traffic regulations

Guidelines for responses:
1. Provide accurate information based on official Indian traffic laws
2. If you're unsure about specific state variations, mention that traffic rules can vary by state
3. Always prioritize safety and legal compliance
4. Use simple, clear language that's easy to understand
5. If asked about non-traffic related topics, politely redirect to traffic law questions

Be helpful, accurate, and focused on Indian traffic law context."""

    def _format_conversation_history(self, conversation_history: List[Dict[str, str]]) -> str:
        """Convert conversation history to a readable format for the AI"""
        if not conversation_history:
            return ""
        
        formatted_history = "\n\nPrevious conversation context:\n"
        for msg in conversation_history[-10:]:  # Only last 10 messages to avoid token limits
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted_history += f"{role}: {msg['content']}\n"
        
        return formatted_history

    async def generate_response(self, message: str, conversation_history: List[Dict[str, str]]) -> str:
        """
        Generate response using Gemini API with Indian traffic law context.
        """
        try:
            # Build the complete prompt
            system_prompt = self._create_system_prompt()
            history_context = self._format_conversation_history(conversation_history)
            
            full_prompt = f"{system_prompt}{history_context}\n\nUser Question: {message}\n\nAssistant:"
            
            # Generate response using Gemini
            response = await self._call_gemini_api(full_prompt)
            
            logger.info(f"Generated response for message: {message[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I apologize, but I'm currently unable to process your question. Please try again later."

    async def _call_gemini_api(self, prompt: str) -> str:
        """
        Make actual API call to Gemini.
        Separated for easier testing and error handling.
        """
        try:
            # Use generate_content method for Gemini
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                logger.warning("Empty response from Gemini API")
                return "I couldn't generate a proper response. Could you please rephrase your question?"
                
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise


# Dependency function for FastAPI
def get_ai_service() -> AIServiceInterface:
    """
    FastAPI dependency to provide AI service instance.
    This is where you can easily swap AI providers:
    - return GeminiAIService() for Gemini
    - return CustomLLMService() for your own LLM
    - return OpenAIService() for OpenAI, etc.
    """
    return GeminiAIService()
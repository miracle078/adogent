"""
Groq client for ADOGENT AI agents.
Handles fast text-based LLM interactions using LangChain-Groq.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from .base_agent import BaseAgent
from ..schemas.ai_schemas import AIRequest, AIResponse, ConversationMessage
from ..config.config import settings


logger = logging.getLogger(__name__)


class GroqClient(BaseAgent):
    """
    Groq client for fast text-based LLM interactions.
    Optimized for quick responses and conversation handling.
    """
    
    def __init__(self):
        super().__init__("groq_client")
        
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        # Simplified Groq client initialization - no base_url needed
        self.client = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL,
            temperature=settings.GROQ_TEMPERATURE,
            max_tokens=settings.GROQ_MAX_TOKENS,
            timeout=settings.GROQ_TIMEOUT
        )
        
        logger.info(f"Initialized Groq client with model: {settings.GROQ_MODEL}")
    
    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process request using Groq LLM."""
        async with self.track_request(request):
            try:
                if not await self.validate_request(request):
                    return self.create_error_response(
                        self.get_conversation_id(request),
                        "Invalid request format",
                        request.interaction_type
                    )
                
                conversation_id = self.get_conversation_id(request)
                
                # Build message history
                messages = await self._build_message_history(conversation_id, request)
                
                # Track start time
                start_time = datetime.utcnow()
                
                # Generate response - simplified without custom callbacks
                response = await self.client.ainvoke(messages)
                
                # Calculate processing time
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                
                # Extract response content
                response_content = response.content if hasattr(response, 'content') else str(response)
                
                # Update conversation history
                self.add_to_conversation(
                    conversation_id,
                    ConversationMessage(role="user", content=request.message)
                )
                self.add_to_conversation(
                    conversation_id,
                    ConversationMessage(role="assistant", content=response_content)
                )
                
                # Estimate token usage (since we can't get exact counts without callbacks)
                estimated_tokens = len(response_content.split()) + len(request.message.split())
                self.total_tokens_used += estimated_tokens
                
                return AIResponse(
                    message=response_content,
                    interaction_type=request.interaction_type,
                    conversation_id=conversation_id,
                    confidence=0.85,
                    tokens_used=estimated_tokens,
                    processing_time=processing_time,
                    model_used=settings.GROQ_MODEL,
                    metadata={
                        "groq_model": settings.GROQ_MODEL,
                        "temperature": settings.GROQ_TEMPERATURE,
                        "max_tokens": settings.GROQ_MAX_TOKENS,
                        "estimated_tokens": True
                    }
                )
                
            except Exception as e:
                logger.error(f"Groq processing error: {e}")
                return self.create_error_response(
                    self.get_conversation_id(request),
                    f"Groq processing error: {str(e)}",
                    request.interaction_type
                )
    
    async def _build_message_history(self, conversation_id: str, request: AIRequest) -> List:
        """Build message history for LLM context."""
        messages = []
        
        # Add system message based on interaction type
        system_prompt = self._get_system_prompt(request.interaction_type)
        
        # Add context instructions if provided
        if hasattr(request, 'context') and request.context and 'instructions' in request.context:
            system_prompt = f"{system_prompt}\n\nAdditional Instructions: {request.context['instructions']}"
        
        messages.append(SystemMessage(content=system_prompt))
        
        # Add conversation history
        if settings.ENABLE_CONVERSATION_CONTEXT:
            history = self.get_conversation_history(conversation_id)
            for msg in history[-5:]:  # Last 5 messages for context
                if msg.role == "user":
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    messages.append(AIMessage(content=msg.content))
        
        # Add current message
        messages.append(HumanMessage(content=request.message))
        
        return messages
    
    def _get_system_prompt(self, interaction_type: str) -> str:
        """Get system prompt based on interaction type."""
        prompts = {
            "product_inquiry": """You are ADOGENT, a concise product information assistant.
                CRITICAL: Keep ALL responses to 2-3 sentences maximum. Be direct and specific.
                - Answer ONLY about the specific product mentioned
                - Focus on the most relevant detail for the question
                - Do NOT provide lists or multiple paragraphs
                - Do NOT repeat product name or price (user already knows)
                Example: "This camera features a 45MP sensor ideal for professional photography. The 8K video capability sets it apart from competitors."
                """,
                
            "product_recommendation": """You are ADOGENT, a luxury e-commerce personal shopping assistant.
                Your primary role is to understand customer preferences deeply and recommend ideal products by considering style, budget, occasion, and personal taste.
                - Start interactions by gathering relevant customer preferences (favorite brands, preferred styles, budget, occasion, condition, sizes, and colors).
                - Recommend 3–5 suitable products, clearly stating why each recommendation aligns with customer needs (brand heritage, exclusivity, style compatibility, condition, and budget match).
                - Briefly describe each recommended item, mentioning unique selling points and key attributes.
                - Offer alternative suggestions to refine choices further based on customer feedback.
                Maintain an insightful, refined, and confident tone in all recommendations.""",

            "product_search": """You are ADOGENT, a product search specialist for a luxury e-commerce platform.
                Your main goal is to assist customers in finding exactly what they seek by accurately interpreting their requests and clearly communicating product details.
                - Carefully analyze search queries to understand specific product requirements, preferences, and context.
                - Provide detailed product information, including key features, specifications, and availability.
                - Suggest related or alternative products that might also interest the customer.
                - Ask clarifying questions when search intent is ambiguous.
                - Always prioritize quality, authenticity, and customer satisfaction in your responses.
                Keep responses informative, concise, and focused on helping customers make informed decisions.""",

            "general_chat": """You are ADOGENT, a friendly luxury e-commerce assistant.
                You help customers with various shopping-related questions and provide exceptional customer service.
                - Be warm, professional, and helpful in all interactions.
                - Provide accurate information about products, services, and policies.
                - Guide customers through their shopping journey with personalized assistance.
                - Handle inquiries about orders, returns, and general shopping advice.
                - Maintain a sophisticated yet approachable tone that reflects luxury service standards.""",

            "customer_support": """You are ADOGENT, a customer support specialist for a luxury e-commerce platform.
                Your role is to resolve customer issues efficiently and maintain high satisfaction levels.
                - Address customer concerns with empathy and professionalism.
                - Provide clear solutions and step-by-step guidance.
                - Escalate complex issues when necessary while keeping customers informed.
                - Follow up to ensure customer satisfaction and issue resolution.
                - Maintain detailed records of customer interactions and resolutions."""
        }
        
        return prompts.get(interaction_type, prompts["general_chat"])
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Groq service health."""
        try:
            # Simple health check without custom callbacks
            test_messages = [
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content="Hello")
            ]
            
            start_time = datetime.utcnow()
            response = await self.client.ainvoke(test_messages)
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "status": "healthy",
                "model": settings.GROQ_MODEL,
                "response_time": processing_time,
                "response_preview": response.content[:50] + "..." if len(response.content) > 50 else response.content,
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Groq health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "model": settings.GROQ_MODEL,
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def generate_product_summary(self, product_data: Dict[str, Any]) -> str:
        """Generate AI summary for product."""
        try:
            prompt = f"""Create a compelling product summary for this luxury item:
            
            Product: {product_data.get('name', 'Unknown')}
            Brand: {product_data.get('brand', 'Unknown')}
            Category: {product_data.get('category', 'Unknown')}
            Price: {product_data.get('price', 'Unknown')}
            Condition: {product_data.get('condition', 'Unknown')}
            
            Create a 2-3 sentence summary that highlights the key features, luxury appeal, and value proposition."""
            
            messages = [
                SystemMessage(content="You are a luxury product copywriter."),
                HumanMessage(content=prompt)
            ]
            
            response = await self.client.ainvoke(messages)
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            logger.error(f"Product summary generation failed: {e}")
            return f"Premium {product_data.get('brand', '')} {product_data.get('name', 'item')} - a luxury addition to your collection."
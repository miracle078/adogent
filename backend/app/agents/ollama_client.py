"""
Ollama client for ADOGENT AI agents.
Handles multimodal interactions using LangChain-Ollama integration.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import base64

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from .base_agent import BaseAgent
from ..schemas.ai_schemas import AIRequest, AIResponse, VisualAnalysisRequest, VisualAnalysisResponse, ConversationMessage
from ..config.config import settings


logger = logging.getLogger(__name__)


class OllamaClient(BaseAgent):
    """
    Ollama client for multimodal interactions.
    Handles both text and image processing using LangChain-Ollama.
    """
    
    def __init__(self):
        super().__init__("ollama_client")
        
        # Simplified Ollama client initialization - no base_url needed
        # LangChain-Ollama connects to local Ollama automatically
        self.client = ChatOllama(
            model=settings.OLLAMA_MODEL,
            temperature=settings.OLLAMA_TEMPERATURE,
            timeout=settings.OLLAMA_TIMEOUT
        )
        
        logger.info(f"Initialized Ollama client with model: {settings.OLLAMA_MODEL}")
    
    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process request using Ollama."""
        async with self.track_request(request):
            try:
                if not await self.validate_request(request):
                    return self.create_error_response(
                        self.get_conversation_id(request),
                        "Invalid request format",
                        request.interaction_type
                    )
                
                conversation_id = self.get_conversation_id(request)
                
                # Handle visual analysis requests
                if isinstance(request, VisualAnalysisRequest):
                    return await self._process_visual_analysis(request, conversation_id)
                
                # Build message history for text requests
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
                
                return AIResponse(
                    message=response_content,
                    interaction_type=request.interaction_type,
                    conversation_id=conversation_id,
                    confidence=0.80,
                    processing_time=processing_time,
                    model_used=settings.OLLAMA_MODEL,
                    metadata={
                        "ollama_model": settings.OLLAMA_MODEL,
                        "temperature": settings.OLLAMA_TEMPERATURE,
                        "multimodal_capable": True
                    }
                )
                
            except Exception as e:
                logger.error(f"Ollama processing error: {e}")
                return self.create_error_response(
                    self.get_conversation_id(request),
                    f"Ollama processing error: {str(e)}",
                    request.interaction_type
                )
    
    async def _process_visual_analysis(self, request: VisualAnalysisRequest, conversation_id: str) -> VisualAnalysisResponse:
        """Process visual analysis request with image."""
        try:
            # Create multimodal message with image
            messages = [
                SystemMessage(content="You are ADOGENT's visual analysis assistant. Analyze images and provide detailed descriptions, focusing on luxury products, style, and key features."),
                HumanMessage(
                    content=[
                        {
                            "type": "text",
                            "text": request.message
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{request.image_data}"
                            }
                        }
                    ]
                )
            ]
            
            start_time = datetime.utcnow()
            response = await self.client.ainvoke(messages)
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            # Update conversation history
            self.add_to_conversation(
                conversation_id,
                ConversationMessage(role="user", content=f"[IMAGE] {request.message}")
            )
            self.add_to_conversation(
                conversation_id,
                ConversationMessage(role="assistant", content=response_content)
            )
            
            return VisualAnalysisResponse(
                message=response_content,
                interaction_type="visual_analysis",
                conversation_id=conversation_id,
                confidence=0.80,
                processing_time=processing_time,
                model_used=settings.OLLAMA_MODEL,
                analysis_results={
                    "image_processed": True,
                    "model_used": settings.OLLAMA_MODEL,
                    "processing_time": processing_time
                },
                metadata={
                    "multimodal_processing": True,
                    "image_analysis": True
                }
            )
            
        except Exception as e:
            logger.error(f"Visual analysis error: {e}")
            return VisualAnalysisResponse(
                message=f"I apologize, but I couldn't analyze the image: {str(e)}",
                interaction_type="visual_analysis",
                conversation_id=conversation_id,
                confidence=0.0,
                analysis_results={"error": str(e)},
                metadata={"error": True, "error_message": str(e)}
            )
    
    async def _build_message_history(self, conversation_id: str, request: AIRequest) -> List:
        """Build message history for LLM context."""
        messages = []
        
        # Add system message
        system_prompt = self._get_system_prompt(request.interaction_type)
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
            "visual_analysis": """You are ADOGENT's visual analysis specialist.
                Analyze images with focus on luxury products, fashion, and lifestyle items.
                - Provide detailed descriptions of visual elements
                - Identify brands, styles, and key features when possible
                - Assess quality, condition, and authenticity markers
                - Suggest styling or usage recommendations
                - Maintain a sophisticated, knowledgeable tone""",
            
            "multimodal": """You are ADOGENT's multimodal assistant.
                Process both text and visual information to provide comprehensive responses.
                - Analyze all provided content (text, images, context)
                - Provide integrated insights combining multiple data sources
                - Focus on luxury commerce and personalized recommendations
                - Maintain contextual awareness across different media types""",
            
            "voice_chat": """You are ADOGENT's voice interaction specialist.
                Optimize responses for voice-based interactions.
                - Use natural, conversational language
                - Keep responses concise but informative
                - Provide clear next steps or follow-up questions
                - Maintain warm, professional tone suitable for voice""",
            
            "general_chat": """You are ADOGENT, a luxury e-commerce assistant.
                Provide helpful, personalized assistance for shopping and general inquiries.
                - Be warm, professional, and knowledgeable
                - Focus on luxury products and premium service
                - Provide detailed, actionable advice
                - Maintain sophisticated, refined communication style"""
        }
        
        return prompts.get(interaction_type, prompts["general_chat"])
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Ollama service health."""
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
                "model": settings.OLLAMA_MODEL,
                "response_time": processing_time,
                "response_preview": response.content[:50] + "..." if len(response.content) > 50 else response.content,
                "multimodal_capable": True,
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "model": settings.OLLAMA_MODEL,
                "last_check": datetime.utcnow().isoformat()
            }
"""
Voice agent for ADOGENT.
Handles multimodal interactions using Ollama LLaVA for voice and visual processing.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import base64
import json

from sqlalchemy.ext.asyncio import AsyncSession

from .base_agent import BaseAgent
from .ollama_client import OllamaClient
from ..schemas.ai_schemas import (
    AIRequest, 
    AIResponse, 
    VisualAnalysisRequest, 
    VisualAnalysisResponse,
    ConversationMessage
)
from ..config.config import settings


logger = logging.getLogger(__name__)


class VoiceAgent(BaseAgent):
    """
    Voice agent for multimodal interactions.
    Specializes in voice processing, visual analysis, and multimodal responses using Ollama LLaVA.
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__("voice_agent")
        self.db = db
        self.ollama_client = OllamaClient()
        
        logger.info("Initialized Voice Agent with Ollama LLaVA multimodal capabilities")
    
    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process voice/multimodal request."""
        async with self.track_request(request):
            try:
                if not await self.validate_request(request):
                    return self.create_error_response(
                        self.get_conversation_id(request),
                        "Invalid request format",
                        request.interaction_type
                    )
                
                conversation_id = self.get_conversation_id(request)
                
                # Route based on interaction type
                if isinstance(request, VisualAnalysisRequest):
                    return await self._process_visual_analysis(request, conversation_id)
                elif request.interaction_type == "voice_chat":
                    return await self._process_voice_chat(request, conversation_id)
                elif request.interaction_type == "multimodal":
                    return await self._process_multimodal_request(request, conversation_id)
                else:
                    return await self._process_general_voice_request(request, conversation_id)
                
            except Exception as e:
                logger.error(f"Voice agent error: {e}")
                return self.create_error_response(
                    self.get_conversation_id(request),
                    f"Voice processing failed: {str(e)}",
                    request.interaction_type
                )
    
    async def _process_visual_analysis(
        self, 
        request: VisualAnalysisRequest, 
        conversation_id: str
    ) -> VisualAnalysisResponse:
        """Process visual analysis using Ollama LLaVA."""
        try:
            start_time = datetime.utcnow()
            
            # Process through Ollama client
            response = await self.ollama_client.process_request(request)
            
            # Update conversation history
            self.add_to_conversation(
                conversation_id,
                ConversationMessage(role="user", content=f"[IMAGE] {request.message}")
            )
            
            self.add_to_conversation(
                conversation_id,
                ConversationMessage(role="assistant", content=response.message)
            )
            
            # Ensure we return VisualAnalysisResponse
            if isinstance(response, VisualAnalysisResponse):
                return response
            else:
                # Convert AIResponse to VisualAnalysisResponse
                return VisualAnalysisResponse(
                    message=response.message,
                    interaction_type=response.interaction_type,
                    conversation_id=response.conversation_id,
                    confidence=response.confidence,
                    processing_time=response.processing_time,
                    model_used=response.model_used or "ollama_llava",
                    analysis_results=response.metadata or {},
                    metadata=response.metadata
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
    
    async def _process_voice_chat(self, request: AIRequest, conversation_id: str) -> AIResponse:
        """Process voice chat request."""
        try:
            start_time = datetime.utcnow()
            
            # Enhanced voice chat prompt
            voice_prompt = f"""You are ADOGENT's voice assistant. Respond to this voice message: "{request.message}"

As a luxury e-commerce voice assistant:
- Use natural, conversational language
- Be warm and personable
- Provide helpful shopping guidance
- Ask clarifying questions when needed
- Suggest next steps clearly

Keep responses concise but informative for voice interaction."""
            
            # Process through Ollama for natural conversation
            ollama_request = AIRequest(
                message=voice_prompt,
                interaction_type="general_chat",
                user_id=request.user_id,
                conversation_id=conversation_id
            )
            
            response = await self.ollama_client.process_request(ollama_request)
            
            # Update conversation history
            self.add_to_conversation(
                conversation_id,
                ConversationMessage(role="user", content=f"[VOICE] {request.message}")
            )
            
            self.add_to_conversation(
                conversation_id,
                ConversationMessage(role="assistant", content=response.message)
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AIResponse(
                message=response.message,
                interaction_type=request.interaction_type,
                conversation_id=conversation_id,
                confidence=response.confidence,
                processing_time=processing_time,
                model_used="ollama_llava",
                metadata={
                    "interaction_mode": "voice",
                    "response_optimized_for_voice": True
                }
            )
            
        except Exception as e:
            logger.error(f"Voice chat error: {e}")
            return self.create_error_response(
                conversation_id,
                f"Voice chat failed: {str(e)}",
                request.interaction_type
            )
    
    async def _process_multimodal_request(self, request: AIRequest, conversation_id: str) -> AIResponse:
        """Process multimodal request (text + potential media)."""
        try:
            start_time = datetime.utcnow()
            
            # Enhanced multimodal prompt
            multimodal_prompt = f"""Process this multimodal request: "{request.message}"

As ADOGENT's multimodal assistant:
- Analyze any visual content if present
- Understand text context
- Provide comprehensive responses
- Consider both visual and textual information
- Offer relevant luxury shopping insights

Provide a helpful, integrated response."""
            
            # Process through Ollama for multimodal handling
            ollama_request = AIRequest(
                message=multimodal_prompt,
                interaction_type="multimodal",
                user_id=request.user_id,
                conversation_id=conversation_id
            )
            
            response = await self.ollama_client.process_request(ollama_request)
            
            # Update conversation history
            self.add_to_conversation(
                conversation_id,
                ConversationMessage(role="user", content=f"[MULTIMODAL] {request.message}")
            )
            
            self.add_to_conversation(
                conversation_id,
                ConversationMessage(role="assistant", content=response.message)
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AIResponse(
                message=response.message,
                interaction_type=request.interaction_type,
                conversation_id=conversation_id,
                confidence=response.confidence,
                processing_time=processing_time,
                model_used="ollama_llava",
                metadata={
                    "interaction_mode": "multimodal",
                    "includes_visual_analysis": True
                }
            )
            
        except Exception as e:
            logger.error(f"Multimodal request error: {e}")
            return self.create_error_response(
                conversation_id,
                f"Multimodal processing failed: {str(e)}",
                request.interaction_type
            )
    
    async def _process_general_voice_request(self, request: AIRequest, conversation_id: str) -> AIResponse:
        """Process general voice request."""
        try:
            start_time = datetime.utcnow()
            
            # General voice processing prompt
            general_prompt = f"""Process this voice request: "{request.message}"

As ADOGENT's voice assistant:
- Understand the user's intent
- Provide helpful guidance
- Use natural, conversational tone
- Keep responses appropriate for voice interaction
- Offer clear next steps

Respond naturally and helpfully."""
            
            # Process through Ollama
            ollama_request = AIRequest(
                message=general_prompt,
                interaction_type="general_chat",
                user_id=request.user_id,
                conversation_id=conversation_id
            )
            
            response = await self.ollama_client.process_request(ollama_request)
            
            # Update conversation history
            self.add_to_conversation(
                conversation_id,
                ConversationMessage(role="user", content=f"[VOICE] {request.message}")
            )
            
            self.add_to_conversation(
                conversation_id,
                ConversationMessage(role="assistant", content=response.message)
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AIResponse(
                message=response.message,
                interaction_type=request.interaction_type,
                conversation_id=conversation_id,
                confidence=response.confidence,
                processing_time=processing_time,
                model_used="ollama_llava",
                metadata={
                    "interaction_mode": "voice",
                    "processing_type": "general_voice"
                }
            )
            
        except Exception as e:
            logger.error(f"General voice request error: {e}")
            return self.create_error_response(
                conversation_id,
                f"Voice processing failed: {str(e)}",
                request.interaction_type
            )
    
    async def process_audio_input(self, audio_data: bytes, format: str = "wav") -> str:
        """
        Process audio input and convert to text.
        This is a placeholder for speech-to-text functionality.
        """
        try:
            # TODO: Implement speech-to-text using OpenAI Whisper or similar
            # For now, return placeholder
            logger.info(f"Processing audio input: {len(audio_data)} bytes in {format} format")
            
            # Placeholder implementation
            return "Audio processing not yet implemented. Please use text input."
            
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            return f"Failed to process audio: {str(e)}"
    
    async def generate_voice_response(self, text: str) -> Dict[str, Any]:
        """
        Generate voice response from text.
        This is a placeholder for text-to-speech functionality.
        """
        try:
            # TODO: Implement text-to-speech using OpenAI TTS or similar
            logger.info(f"Generating voice response for: {text[:50]}...")
            
            # Placeholder implementation
            return {
                "text": text,
                "audio_url": None,
                "duration": 0,
                "format": "mp3",
                "status": "text_only"
            }
            
        except Exception as e:
            logger.error(f"Voice response generation error: {e}")
            return {
                "text": text,
                "error": str(e),
                "status": "error"
            }
    
    async def analyze_product_image(self, image_data: str, query: str) -> Dict[str, Any]:
        """Analyze product image for visual search."""
        try:
            visual_request = VisualAnalysisRequest(
                message=f"Analyze this product image: {query}",
                image_data=image_data,
                analysis_type="product_matching"
            )
            
            response = await self._process_visual_analysis(
                visual_request, 
                f"image_analysis_{datetime.utcnow().timestamp()}"
            )
            
            return {
                "analysis": response.message,
                "confidence": response.confidence,
                "features": response.analysis_results,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Product image analysis error: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the voice agent."""
        try:
            # Check Ollama client health
            ollama_health = await self.ollama_client.health_check()
            
            # Test basic functionality
            test_request = AIRequest(
                message="Hello, testing voice agent",
                interaction_type="voice_chat"
            )
            
            start_time = datetime.utcnow()
            test_response = await self._process_voice_chat(
                test_request, 
                f"health_check_{datetime.utcnow().timestamp()}"
            )
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "status": "healthy" if ollama_health["status"] == "healthy" else "unhealthy",
                "ollama_status": ollama_health["status"],
                "voice_response_time": response_time,
                "multimodal_capabilities": True,
                "visual_analysis_ready": True,
                "last_check": datetime.utcnow().isoformat(),
                "features": {
                    "voice_chat": True,
                    "visual_analysis": True,
                    "multimodal": True,
                    "speech_to_text": False,  # TODO: Implement
                    "text_to_speech": False   # TODO: Implement
                }
            }
            
        except Exception as e:
            logger.error(f"Voice agent health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat(),
                "features": {
                    "voice_chat": False,
                    "visual_analysis": False,
                    "multimodal": False,
                    "speech_to_text": False,
                    "text_to_speech": False
                }
            }
"""
AI service for ADOGENT platform.
Coordinates between different AI agents and handles business logic.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from ..agents.groq_client import GroqClient
from ..agents.ollama_client import OllamaClient
from ..agents.product_agent import ProductAgent
from ..agents.recommendation_agent import RecommendationAgent
from ..agents.voice_agent import VoiceAgent
from ..schemas.ai_schemas import (
    AIRequest, 
    AIResponse, 
    ProductRecommendationRequest, 
    ProductRecommendationResponse,
    VisualAnalysisRequest,
    VisualAnalysisResponse
)
from ..config.config import settings


logger = logging.getLogger(__name__)


class AIService:
    """
    Central AI service that coordinates between different AI agents.
    Handles routing, load balancing, and aggregation of AI responses.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize AI service with database session."""
        self.db = db
        
        # Initialize core AI clients
        self.groq_client = GroqClient()
        try:
            self.ollama_client = OllamaClient()
        except Exception as e:
            logger.warning(f"Ollama client initialization failed: {e}")
            self.ollama_client = None
        
        # Initialize specialized agents
        self.product_agent = ProductAgent(db)
        self.recommendation_agent = RecommendationAgent(db)
        self.voice_agent = VoiceAgent(db)
        
        logger.info("AI Service initialized with all agents")
    
    async def process_chat_request(self, request: AIRequest) -> AIResponse:
        """
        Process chat request by routing to appropriate agent.
        """
        try:
            logger.info(f"Processing chat request: {request.interaction_type}")
            
            # Route based on interaction type
            if request.interaction_type == "product_search":
                return await self.product_agent.process_request(request)
            elif request.interaction_type == "product_details":
                return await self.product_agent.process_request(request)
            elif request.interaction_type == "product_recommendation":
                # Convert to recommendation request
                rec_request = ProductRecommendationRequest(
                    message=request.message,
                    user_id=request.user_id,
                    conversation_id=request.conversation_id,
                    context=request.context
                )
                return await self.recommendation_agent.process_request(rec_request)
            elif request.interaction_type == "voice_chat":
                return await self.voice_agent.process_request(request)
            elif request.interaction_type == "multimodal":
                return await self.voice_agent.process_request(request)
            else:
                # Default to Groq for general chat
                return await self.groq_client.process_request(request)
                
        except Exception as e:
            logger.error(f"Chat request processing failed: {e}")
            return AIResponse(
                message=f"I apologize, but I encountered an error processing your request: {str(e)}",
                interaction_type=request.interaction_type,
                conversation_id=request.conversation_id or f"error_{datetime.utcnow().timestamp()}",
                confidence=0.0,
                metadata={"error": True, "error_message": str(e)}
            )
    
    async def get_product_recommendations(self, request: ProductRecommendationRequest) -> ProductRecommendationResponse:
        """
        Get product recommendations using the recommendation agent.
        """
        try:
            logger.info("Processing product recommendation request")
            return await self.recommendation_agent.process_request(request)
        except Exception as e:
            logger.error(f"Product recommendation failed: {e}")
            return ProductRecommendationResponse(
                message=f"I apologize, but I couldn't generate recommendations: {str(e)}",
                interaction_type="product_recommendation",
                conversation_id=request.conversation_id or f"error_{datetime.utcnow().timestamp()}",
                confidence=0.0,
                recommendations=[],
                total_products_considered=0,
                recommendation_strategy="error_fallback",
                metadata={"error": True, "error_message": str(e)}
            )
    
    async def analyze_image(self, request: VisualAnalysisRequest) -> VisualAnalysisResponse:
        """
        Analyze image using the voice agent (which handles multimodal).
        """
        try:
            logger.info("Processing image analysis request")
            return await self.voice_agent.process_request(request)
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return VisualAnalysisResponse(
                message=f"I apologize, but I couldn't analyze the image: {str(e)}",
                interaction_type="visual_analysis",
                conversation_id=request.conversation_id or f"error_{datetime.utcnow().timestamp()}",
                confidence=0.0,
                analysis_results={"error": str(e)},
                metadata={"error": True, "error_message": str(e)}
            )
    
    async def get_agent_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics from all AI agents.
        """
        try:
            logger.info("Gathering AI agent statistics")
            
            statistics = {
                "timestamp": datetime.utcnow().isoformat(),
                "service_status": "operational",
                "agents": {},
                "summary": {
                    "total_requests": 0,
                    "total_tokens_used": 0,
                    "total_processing_time": 0.0,
                    "average_response_time": 0.0,
                    "active_conversations": 0
                }
            }
            
            # Gather stats from each agent
            agents = [
                ("groq_client", self.groq_client),
                ("product_agent", self.product_agent),
                ("recommendation_agent", self.recommendation_agent),
                ("voice_agent", self.voice_agent)
            ]
            
            # Add ollama if available
            if self.ollama_client:
                agents.append(("ollama_client", self.ollama_client))
            
            for agent_name, agent in agents:
                try:
                    agent_stats = await agent.get_agent_stats()
                    statistics["agents"][agent_name] = agent_stats
                    
                    # Aggregate summary stats
                    statistics["summary"]["total_requests"] += agent_stats.get("request_count", 0)
                    statistics["summary"]["total_tokens_used"] += agent_stats.get("total_tokens_used", 0)
                    statistics["summary"]["total_processing_time"] += agent_stats.get("total_processing_time", 0.0)
                    statistics["summary"]["active_conversations"] += agent_stats.get("active_conversations", 0)
                    
                except Exception as e:
                    logger.warning(f"Failed to get stats from {agent_name}: {e}")
                    statistics["agents"][agent_name] = {
                        "status": "error",
                        "error": str(e),
                        "last_check": datetime.utcnow().isoformat()
                    }
            
            # Calculate average response time
            total_requests = statistics["summary"]["total_requests"]
            if total_requests > 0:
                statistics["summary"]["average_response_time"] = (
                    statistics["summary"]["total_processing_time"] / total_requests
                )
            
            # Add health check info
            statistics["health"] = await self._get_health_summary()
            
            logger.info(f"Agent statistics gathered: {total_requests} total requests")
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to gather agent statistics: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "service_status": "error",
                "error": str(e),
                "agents": {},
                "summary": {
                    "total_requests": 0,
                    "total_tokens_used": 0,
                    "total_processing_time": 0.0,
                    "average_response_time": 0.0,
                    "active_conversations": 0
                }
            }
    
    async def _get_health_summary(self) -> Dict[str, Any]:
        """Get health summary of all agents."""
        health_summary = {
            "overall_status": "unknown",
            "healthy_agents": 0,
            "total_agents": 0,
            "agent_health": {}
        }
        
        agents = [
            ("groq_client", self.groq_client),
            ("product_agent", self.product_agent),
            ("recommendation_agent", self.recommendation_agent),
            ("voice_agent", self.voice_agent)
        ]
        
        if self.ollama_client:
            agents.append(("ollama_client", self.ollama_client))
        
        for agent_name, agent in agents:
            try:
                health = await agent.health_check()
                health_summary["agent_health"][agent_name] = health
                health_summary["total_agents"] += 1
                
                if health.get("status") == "healthy":
                    health_summary["healthy_agents"] += 1
                    
            except Exception as e:
                health_summary["agent_health"][agent_name] = {
                    "status": "error",
                    "error": str(e)
                }
                health_summary["total_agents"] += 1
        
        # Determine overall status
        if health_summary["healthy_agents"] == health_summary["total_agents"]:
            health_summary["overall_status"] = "healthy"
        elif health_summary["healthy_agents"] > 0:
            health_summary["overall_status"] = "partial"
        else:
            health_summary["overall_status"] = "unhealthy"
        
        return health_summary
    
    async def cleanup(self):
        """Cleanup all agents."""
        try:
            agents = [
                self.groq_client,
                self.product_agent,
                self.recommendation_agent,
                self.voice_agent
            ]
            
            if self.ollama_client:
                agents.append(self.ollama_client)
            
            for agent in agents:
                if hasattr(agent, 'cleanup'):
                    await agent.cleanup()
            
            logger.info("AI Service cleanup completed")
        except Exception as e:
            logger.error(f"AI Service cleanup failed: {e}")
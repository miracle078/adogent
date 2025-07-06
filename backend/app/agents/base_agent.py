"""
Base agent class for ADOGENT AI agents.
Provides common functionality and abstract methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import asyncio
import logging
from contextlib import asynccontextmanager

from ..schemas.ai_schemas import AIRequest, AIResponse, ConversationMessage
from ..config.config import settings


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    Provides common functionality for conversation management, error handling, and logging.
    """
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.conversation_history: Dict[str, List[ConversationMessage]] = {}
        self.agent_id = str(uuid.uuid4())
        
        # Performance tracking
        self.request_count = 0
        self.total_tokens_used = 0
        self.total_processing_time = 0.0
        
        logger.info(f"Initialized {agent_name} agent with ID: {self.agent_id}")
    
    @abstractmethod
    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process an AI request and return a response."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the agent and its dependencies."""
        pass
    
    def get_conversation_id(self, request: AIRequest) -> str:
        """Generate or retrieve conversation ID."""
        if request.conversation_id:
            return request.conversation_id
        return f"{self.agent_name}_{request.user_id}_{uuid.uuid4().hex[:8]}"
    
    def add_to_conversation(self, conversation_id: str, message: ConversationMessage):
        """Add message to conversation history."""
        if not settings.ENABLE_CONVERSATION_CONTEXT:
            return
        
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []
        
        self.conversation_history[conversation_id].append(message)
        
        # Limit conversation history
        if len(self.conversation_history[conversation_id]) > settings.MAX_CONVERSATION_HISTORY:
            self.conversation_history[conversation_id] = self.conversation_history[conversation_id][-settings.MAX_CONVERSATION_HISTORY:]
    
    def get_conversation_history(self, conversation_id: str) -> List[ConversationMessage]:
        """Get conversation history for a conversation ID."""
        return self.conversation_history.get(conversation_id, [])
    
    def clear_conversation(self, conversation_id: str):
        """Clear conversation history for a conversation ID."""
        if conversation_id in self.conversation_history:
            del self.conversation_history[conversation_id]
    
    @asynccontextmanager
    async def track_request(self, request: AIRequest):
        """Context manager for tracking request metrics."""
        start_time = datetime.utcnow()
        self.request_count += 1
        
        try:
            yield
        finally:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.total_processing_time += processing_time
            
            logger.info(
                f"Agent {self.agent_name} processed request in {processing_time:.2f}s | "
                f"Total requests: {self.request_count} | "
                f"Avg processing time: {self.total_processing_time / self.request_count:.2f}s"
            )
    
    async def validate_request(self, request: AIRequest) -> bool:
        """Validate incoming request."""
        try:
            if not request.message.strip():
                raise ValueError("Message cannot be empty")
            
            if len(request.message) > 4000:
                raise ValueError("Message too long")
            
            return True
        except Exception as e:
            logger.error(f"Request validation failed: {e}")
            return False
    
    def create_error_response(
        self, 
        conversation_id: str, 
        error_message: str, 
        interaction_type: str = "general_chat"
    ) -> AIResponse:
        """Create error response."""
        return AIResponse(
            message=f"I apologize, but I encountered an error: {error_message}",
            interaction_type=interaction_type,
            conversation_id=conversation_id,
            confidence=0.0,
            metadata={"error": True, "error_message": error_message}
        )
    
    async def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        avg_processing_time = self.total_processing_time / self.request_count if self.request_count > 0 else 0
        
        return {
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "request_count": self.request_count,
            "total_tokens_used": self.total_tokens_used,
            "total_processing_time": self.total_processing_time,
            "average_processing_time": avg_processing_time,
            "active_conversations": len(self.conversation_history),
            "uptime": datetime.utcnow().isoformat(),
        }
    
    async def cleanup(self):
        """Cleanup agent resources."""
        logger.info(f"Cleaning up agent {self.agent_name}")
        self.conversation_history.clear()
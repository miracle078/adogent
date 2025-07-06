"""
AI schemas for ADOGENT agents.
Pydantic models for AI requests, responses, and conversation management.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from enum import Enum


class ConversationMessage(BaseModel):
    """Individual message in a conversation."""
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional message metadata")
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['user', 'assistant', 'system']
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of: {allowed_roles}")
        return v


class AIRequest(BaseModel):
    """Base AI request schema."""
    message: str = Field(..., description="User message or query")
    interaction_type: str = Field(default="general_chat", description="Type of interaction")
    user_id: Optional[UUID] = Field(default=None, description="User ID if authenticated")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID for context")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class AIResponse(BaseModel):
    """Base AI response schema."""
    message: str = Field(..., description="AI response message")
    interaction_type: str = Field(..., description="Type of interaction")
    conversation_id: str = Field(..., description="Conversation ID")
    confidence: float = Field(default=0.0, description="Response confidence score")
    processing_time: Optional[float] = Field(default=None, description="Processing time in seconds")
    model_used: Optional[str] = Field(default=None, description="AI model used")
    tokens_used: Optional[int] = Field(default=None, description="Tokens consumed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ProductRecommendation(BaseModel):
    """Product recommendation schema."""
    product_id: UUID = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    price: float = Field(..., description="Product price")
    confidence: float = Field(..., description="Recommendation confidence")
    reason: str = Field(..., description="Reason for recommendation")
    category: Optional[str] = Field(default=None, description="Product category")
    brand: Optional[str] = Field(default=None, description="Product brand")
    image_url: Optional[str] = Field(default=None, description="Product image URL")


class ProductRecommendationRequest(AIRequest):
    """Product recommendation request schema."""
    interaction_type: str = Field(default="product_recommendation", description="Interaction type")
    category_preferences: Optional[List[str]] = Field(default=None, description="Preferred categories")
    price_range: Optional[Dict[str, float]] = Field(default=None, description="Price range filter")
    brand_preferences: Optional[List[str]] = Field(default=None, description="Preferred brands")
    exclude_products: Optional[List[UUID]] = Field(default=None, description="Products to exclude")


class ProductRecommendationResponse(AIResponse):
    """Product recommendation response schema."""
    recommendations: List[ProductRecommendation] = Field(..., description="Product recommendations")
    total_products_considered: int = Field(..., description="Total products considered")
    recommendation_strategy: str = Field(..., description="Strategy used for recommendations")


class VisualAnalysisRequest(AIRequest):
    """Visual analysis request schema."""
    interaction_type: str = Field(default="visual_analysis", description="Interaction type")
    image_url: Optional[str] = Field(default=None, description="Image URL to analyze")
    image_data: Optional[str] = Field(default=None, description="Base64 encoded image data")
    analysis_type: str = Field(default="product_matching", description="Type of analysis")


class VisualAnalysisResponse(AIResponse):
    """Visual analysis response schema."""
    analysis_results: Dict[str, Any] = Field(..., description="Analysis results")


class ConversationHistory(BaseModel):
    """Conversation history schema."""
    conversation_id: str = Field(..., description="Conversation ID")
    messages: List[ConversationMessage] = Field(..., description="Conversation messages")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Conversation start time")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update time")


class AIHealthCheck(BaseModel):
    """AI system health check schema."""
    groq_status: str = Field(..., description="Groq service status")
    ollama_status: str = Field(..., description="Ollama service status")
    groq_response_time: Optional[float] = Field(default=None, description="Groq response time")
    ollama_response_time: Optional[float] = Field(default=None, description="Ollama response time")
    available_models: Dict[str, List[str]] = Field(..., description="Available models")
    system_load: Dict[str, Any] = Field(..., description="System load metrics")
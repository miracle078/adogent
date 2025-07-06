"""
AI API endpoints for ADOGENT agents.
Handles chat, recommendations, voice, and visual analysis requests.
"""

from typing import Optional, Dict, Any, List
import base64

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_db
from ..services.ai_service import AIService
from ..schemas.ai_schemas import (
    AIRequest,
    AIResponse,
    ProductRecommendationRequest,
    ProductRecommendationResponse,
    VisualAnalysisRequest,
    VisualAnalysisResponse,
    AIHealthCheck,
    ConversationHistory
)
from ..utils.dependencies import optional_auth, get_current_user
from datetime import datetime
from ..agents.groq_client import GroqClient
from ..agents.ollama_client import OllamaClient
from ..logging.log import logger, log_ai_interaction, log_user_action
from ..config.config import settings


router = APIRouter(prefix="/ai", tags=["AI Agents"])


@router.post("/chat", response_model=AIResponse)
async def chat_with_agent(
    request: AIRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(optional_auth)
):
    """
    Chat with AI agents.
    
    Supports various interaction types:
    - general_chat: General conversation
    - product_search: Product-related queries
    - product_details: Specific product information
    - voice_chat: Voice-optimized responses
    - multimodal: Text + visual content
    """
    try:
        logger.info(f"AI chat request: {request.interaction_type}")
        
        # Initialize AI service
        ai_service = AIService(db)
        
        # Set user ID if authenticated - Use user_id from TokenData
        if current_user:
            request.user_id = current_user.user_id
            log_user_action(
                action="ai_chat_request",
                user_id=str(current_user.user_id),
                details={"interaction_type": request.interaction_type}
            )
        
        # Process chat request
        response = await ai_service.process_chat_request(request)
        
        # Log AI interaction
        log_ai_interaction(
            agent_name="ai_service",
            model=response.model_used or "mixed",
            input_tokens=len(request.message.split()),  # Approximate input tokens
            output_tokens=response.tokens_used or len(response.message.split()),
            duration=response.processing_time or 0,
            user_id=str(request.user_id) if request.user_id else None
        )
        
        logger.info(f"AI chat completed: {response.interaction_type}")
        return response
        
    except Exception as e:
        logger.error(f"Chat request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat request failed: {str(e)}"
        )


@router.post("/recommendations", response_model=ProductRecommendationResponse)
async def get_product_recommendations(
    request: ProductRecommendationRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(optional_auth)
):
    """
    Get AI-powered product recommendations.
    
    Analyzes user preferences and suggests relevant luxury products.
    Supports filtering by category, price range, and brand preferences.
    """
    try:
        logger.info(f"Product recommendation request")
        
        # Initialize AI service
        ai_service = AIService(db)
        
        # Set user ID if authenticated - Use user_id from TokenData
        if current_user:
            request.user_id = current_user.user_id  # Fix: Use user_id instead of id
            log_user_action(
                action="product_recommendation_request",
                user_id=str(current_user.user_id),  # Fix: Use user_id instead of id
                details={
                    "categories": request.category_preferences,
                    "price_range": request.price_range,
                    "brands": request.brand_preferences
                }
            )
        
        # Get recommendations
        response = await ai_service.get_product_recommendations(request)
        
        # Log recommendation interaction
        log_ai_interaction(
            agent_name="recommendation_agent",
            model=response.model_used or "groq+database",
            input_tokens=len(request.message.split()),
            output_tokens=response.metadata.get("groq_tokens", 0) if response.metadata else 0,
            duration=response.processing_time or 0,
            user_id=str(request.user_id) if request.user_id else None
        )
        
        logger.info(f"Generated {len(response.recommendations)} recommendations")
        return response
        
    except Exception as e:
        logger.error(f"Product recommendation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Product recommendation failed: {str(e)}"
        )


@router.post("/analyze-image", response_model=VisualAnalysisResponse)
async def analyze_image(
    request: VisualAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(optional_auth)
):
    """
    Analyze image using AI for product matching.
    
    Supports:
    - Image URL analysis
    - Base64 encoded image data
    - Product matching and visual search
    - Style and feature analysis
    """
    try:
        logger.info(f"Image analysis request")
        
        # Validate image data
        if not request.image_url and not request.image_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either image_url or image_data must be provided"
            )
        
        # Initialize AI service
        ai_service = AIService(db)
        
        # Set user ID if authenticated - Use user_id from TokenData
        if current_user:
            request.user_id = current_user.user_id  # Fix: Use user_id instead of id
            log_user_action(
                action="image_analysis_request",
                user_id=str(current_user.user_id),  # Fix: Use user_id instead of id
                details={"analysis_type": request.analysis_type}
            )
        
        # Analyze image
        response = await ai_service.analyze_image(request)
        
        # Log visual analysis interaction
        log_ai_interaction(
            agent_name="voice_agent",
            model=response.model_used or "ollama_llava",
            input_tokens=len(request.message.split()),
            output_tokens=0,  # Ollama doesn't provide token counts
            duration=response.processing_time or 0,
            user_id=str(request.user_id) if request.user_id else None
        )
        
        logger.info(f"Image analysis completed")
        return response
        
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image analysis failed: {str(e)}"
        )


@router.post("/upload-image", response_model=VisualAnalysisResponse)
async def upload_and_analyze_image(
    file: UploadFile = File(...),
    message: str = Form("Analyze this image for product matching"),
    analysis_type: str = Form("product_matching"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(optional_auth)
):
    """
    Upload and analyze image file.
    
    Accepts image files and converts to base64 for analysis.
    Supports JPEG, PNG, and WebP formats.
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Check file size
        file.file.seek(0, 2)  # Move pointer to the end of the file
        file_size = file.file.tell()  # Get the size of the file in bytes
        file.file.seek(0)  # Reset pointer to the beginning of the file
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size must be less than {settings.MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
            )
        
        # Validate file type against allowed types
        if file.content_type not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} not allowed. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
            )
        
        # Read and encode image
        image_data = await file.read()
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        
        # Create analysis request
        request = VisualAnalysisRequest(
            message=message,
            image_data=encoded_image,
            analysis_type=analysis_type,
            user_id=current_user.user_id if current_user else None  # Fix: Use user_id instead of id
        )
        
        # Log user action
        if current_user:
            log_user_action(
                action="image_upload_analysis",
                user_id=str(current_user.user_id),  # Fix: Use user_id instead of id
                details={
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "size": file.size,
                    "analysis_type": analysis_type
                }
            )
        
        # Initialize AI service
        ai_service = AIService(db)
        
        # Analyze image
        response = await ai_service.analyze_image(request)
        
        logger.info(f"Uploaded image analyzed: {file.filename}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image upload and analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image upload and analysis failed: {str(e)}"
        )


@router.post("/voice-chat", response_model=AIResponse)
async def voice_chat(
    request: AIRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(optional_auth)
):
    """
    Voice-optimized chat interface.
    
    Provides responses optimized for voice interaction with:
    - Conversational tone
    - Clear, concise responses
    - Natural language flow
    """
    try:
        logger.info(f"Voice chat request")
        
        # Set interaction type for voice optimization
        request.interaction_type = "voice_chat"
        
        # Initialize AI service
        ai_service = AIService(db)
        
        # Set user ID if authenticated - Use user_id from TokenData
        if current_user:
            request.user_id = current_user.user_id  # Fix: Use user_id instead of id
            log_user_action(
                action="voice_chat_request",
                user_id=str(current_user.user_id),  # Fix: Use user_id instead of id
                details={"message_length": len(request.message)}
            )
        
        # Process voice chat
        response = await ai_service.process_chat_request(request)
        
        # Log voice interaction
        log_ai_interaction(
            agent_name="voice_agent",
            model=response.model_used or "ollama_llava",
            input_tokens=len(request.message.split()),
            output_tokens=len(response.message.split()),
            duration=response.processing_time or 0,
            user_id=str(request.user_id) if request.user_id else None
        )
        
        logger.info(f"Voice chat completed")
        return response
        
    except Exception as e:
        logger.error(f"Voice chat failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice chat failed: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
async def clear_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(optional_auth)
):
    """
    Clear conversation history across all agents.
    
    Removes all conversation messages for the specified conversation ID.
    """
    try:
        logger.info(f"Clearing conversation: {conversation_id}")
        
        # Initialize AI service
        ai_service = AIService(db)
        
        # Clear conversation across all agents
        ai_service.groq_client.clear_conversation(conversation_id)
        if ai_service.ollama_client:
            ai_service.ollama_client.clear_conversation(conversation_id)
        ai_service.product_agent.clear_conversation(conversation_id)
        ai_service.recommendation_agent.clear_conversation(conversation_id)
        ai_service.voice_agent.clear_conversation(conversation_id)
        
        # Log user action
        if current_user:
            log_user_action(
                action="conversation_cleared",
                user_id=str(current_user.user_id),  # Fix: Use user_id instead of id
                details={"conversation_id": conversation_id}
            )
        
        logger.info(f"Conversation cleared: {conversation_id}")
        return {"message": "Conversation cleared successfully", "conversation_id": conversation_id}
        
    except Exception as e:
        logger.error(f"Clear conversation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clear conversation failed: {str(e)}"
        )


@router.get("/conversations/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    agent_type: str = "groq",
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(optional_auth)
):
    """
    Get conversation history from specified agent.
    
    Args:
        conversation_id: Unique conversation identifier
        agent_type: Agent type (groq, ollama, product, recommendation, voice)
        limit: Maximum number of messages to return
    """
    try:
        logger.info(f"Getting conversation history: {conversation_id}")
        
        # Initialize AI service
        ai_service = AIService(db)
        
        # Get conversation history based on agent type
        if agent_type == "groq":
            history = ai_service.groq_client.get_conversation_history(conversation_id)
        elif agent_type == "ollama":
            history = ai_service.ollama_client.get_conversation_history(conversation_id) if ai_service.ollama_client else []
        elif agent_type == "product":
            history = ai_service.product_agent.get_conversation_history(conversation_id)
        elif agent_type == "recommendation":
            history = ai_service.recommendation_agent.get_conversation_history(conversation_id)
        elif agent_type == "voice":
            history = ai_service.voice_agent.get_conversation_history(conversation_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid agent_type: {agent_type}. Must be one of: groq, ollama, product, recommendation, voice"
            )
        
        # Limit results
        limited_history = history[-limit:] if len(history) > limit else history
        
        # Log user action
        if current_user:
            log_user_action(
                action="conversation_history_retrieved",
                user_id=str(current_user.user_id),  # Fix: Use user_id instead of id
                details={
                    "conversation_id": conversation_id,
                    "agent_type": agent_type,
                    "message_count": len(limited_history)
                }
            )
        
        return {
            "conversation_id": conversation_id,
            "agent_type": agent_type,
            "message_count": len(limited_history),
            "messages": limited_history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get conversation history failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get conversation history failed: {str(e)}"
        )


@router.get("/health", tags=["AI Health"])
async def ai_health_check():
    """
    Check the health of all AI services.
    """
    logger.info("Performing AI health check")
    
    # Initialize results
    results = {
        "groq": {"status": "unknown", "error": None},
        "ollama": {"status": "unknown", "error": None},
        "overall_status": "unknown",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION
    }
    
    # Check Groq health
    try:
        groq_client = GroqClient()
        groq_health = await groq_client.health_check()
        results["groq"] = groq_health
        logger.info("Groq health check completed successfully")
    except Exception as e:
        logger.error(f"Groq health check failed: {str(e)}")
        results["groq"] = {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat(),
            "model": settings.GROQ_MODEL
        }
    
    # Check Ollama health (optional service)
    try:
        ollama_client = OllamaClient()
        ollama_health = await ollama_client.health_check()
        results["ollama"] = ollama_health
        logger.info("Ollama health check completed successfully")
    except ImportError:
        logger.info("Ollama client not available - treating as optional service")
        results["ollama"] = {
            "status": "not_available",
            "error": "Ollama service not configured",
            "last_check": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.warning(f"Ollama health check failed: {str(e)}")
        results["ollama"] = {
            "status": "unhealthy", 
            "error": str(e),
            "last_check": datetime.utcnow().isoformat()
        }
    
    # Determine overall status
    groq_healthy = results["groq"]["status"] == "healthy"
    ollama_available = results["ollama"]["status"] in ["healthy", "not_available"]
    
    # Overall status based on primary service (Groq)
    if groq_healthy:
        if results["ollama"]["status"] == "healthy":
            results["overall_status"] = "healthy"
        else:
            results["overall_status"] = "partial"  # Groq works, Ollama doesn't
    else:
        results["overall_status"] = "unhealthy"
    
    # Add service information
    results["services"] = {
        "primary": "groq",
        "secondary": "ollama",
        "groq_model": settings.GROQ_MODEL,
        "ollama_model": settings.OLLAMA_MODEL
    }
    
    logger.info(f"AI health check completed: Overall={results['overall_status']}, Groq={results['groq']['status']}, Ollama={results['ollama']['status']}")
    
    return results


@router.get("/statistics")
async def get_ai_statistics(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get AI agent statistics and metrics.
    
    Requires authentication. Returns:
    - Request counts per agent
    - Token usage statistics
    - Performance metrics
    - Error rates and success rates
    """
    try:
        logger.info("Getting AI statistics")
        
        # Initialize AI service
        ai_service = AIService(db)
        
        # Get comprehensive statistics
        stats = await ai_service.get_agent_statistics()
        
        # Log admin action - Use user_id from TokenData
        log_user_action(
            action="ai_statistics_retrieved",
            user_id=str(current_user.user_id),  # Fix: Use user_id instead of id
            details={"stats_type": "comprehensive"}
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Get AI statistics failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get AI statistics failed: {str(e)}"
        )


@router.get("/models")
async def get_available_models(
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of available AI models.
    
    Returns information about:
    - Groq models and capabilities
    - Ollama models and features
    - Model-specific use cases
    """
    try:
        models = {
            "groq": {
                "primary": settings.GROQ_MODEL,
                "capabilities": ["text_generation", "conversation", "product_analysis"],
                "max_tokens": settings.GROQ_MAX_TOKENS,
                "temperature_range": [0.0, 2.0],
                "status": "available"
            },
            "ollama": {
                "primary": settings.OLLAMA_MODEL,
                "capabilities": ["multimodal", "visual_analysis", "voice_chat", "image_understanding"],
                "features": ["vision", "conversation", "product_matching"],
                "status": "available"
            }
        }
        
        return {
            "models": models,
            "last_updated": "2024-01-01T00:00:00Z",
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Get available models failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get available models failed: {str(e)}"
        )


@router.post("/feedback")
async def submit_ai_feedback(
    feedback_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user = Depends(optional_auth)
):
    """
    Submit feedback about AI agent responses.
    
    Helps improve AI agent performance through user feedback.
    """
    try:
        logger.info("AI feedback submitted")
        
        # Validate feedback data
        if not feedback_data.get("conversation_id") or not feedback_data.get("rating"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="conversation_id and rating are required"
            )
        
        # Log feedback
        if current_user:
            log_user_action(
                action="ai_feedback_submitted",
                user_id=str(current_user.user_id),  # Fix: Use user_id instead of id
                details=feedback_data
            )
        
        # TODO: Store feedback in database for analysis
        
        return {"message": "Feedback submitted successfully", "feedback_id": "placeholder"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit AI feedback failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Submit AI feedback failed: {str(e)}"
        )


@router.post("/test-groq", tags=["AI Test"])
async def test_groq_connection():
    """
    Test Groq connection with a simple message.
    """
    try:
        logger.info("Testing Groq connection...")
        
        groq_client = GroqClient()
        
        # Create a simple test request
        test_request = AIRequest(
            message="Hello! Please respond with exactly: 'Groq connection successful'",
            interaction_type="general_chat",
            conversation_id=None
        )
        
        # Process the request
        response = await groq_client.process_request(test_request)
        
        logger.info(f"Groq test completed successfully: {response.message}")
        
        return {
            "status": "success",
            "message": "Groq connection test completed",
            "groq_response": response.message,
            "model_used": response.model_used,
            "processing_time": response.processing_time,
            "tokens_used": response.tokens_used,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Groq connection test failed: {str(e)}")
        return {
            "status": "error",
            "message": "Groq connection test failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/test-ollama", tags=["AI Test"])
async def test_ollama_connection():
    """
    Test Ollama connection with a simple message.
    """
    try:
        logger.info("Testing Ollama connection...")
        
        ollama_client = OllamaClient()
        
        # Create a simple test request
        test_request = AIRequest(
            message="Hello! Please respond with exactly: 'Ollama connection successful'",
            interaction_type="general_chat",
            conversation_id=None
        )
        
        # Process the request
        response = await ollama_client.process_request(test_request)
        
        logger.info(f"Ollama test completed successfully: {response.message}")
        
        return {
            "status": "success",
            "message": "Ollama connection test completed",
            "ollama_response": response.message,
            "model_used": response.model_used,
            "processing_time": response.processing_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ollama connection test failed: {str(e)}")
        return {
            "status": "error",
            "message": "Ollama connection test failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
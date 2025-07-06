"""
Product agent for ADOGENT.
Handles general product queries, search, and information retrieval.
"""

import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from .base_agent import BaseAgent
from .groq_client import GroqClient
from ..schemas.ai_schemas import AIRequest, AIResponse
from ..models.product import Product, ProductStatus
from ..services.product_service import ProductService
from ..config.config import settings


logger = logging.getLogger(__name__)


class ProductAgent(BaseAgent):
    """
    Product agent for general product queries and information.
    Handles product search, details, and general product-related questions.
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__("product_agent")
        self.db = db
        self.groq_client = GroqClient()
        self.product_service = ProductService(db)
        
        logger.info("Initialized Product Agent with Groq integration")
    
    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process product-related request."""
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
                if request.interaction_type == "product_search":
                    return await self._handle_product_search(request, conversation_id)
                elif request.interaction_type == "product_details":
                    return await self._handle_product_details(request, conversation_id)
                else:
                    return await self._handle_general_product_query(request, conversation_id)
                
            except Exception as e:
                logger.error(f"Product agent error: {e}")
                return self.create_error_response(
                    self.get_conversation_id(request),
                    f"Product query failed: {str(e)}",
                    request.interaction_type
                )
    
    async def _handle_product_search(self, request: AIRequest, conversation_id: str) -> AIResponse:
        """Handle product search requests."""
        try:
            start_time = datetime.utcnow()
            
            # Enhanced search prompt
            search_prompt = f"""Help me search for products based on: "{request.message}"
            
As a luxury e-commerce expert, analyze this search query and provide:
1. Interpreted search intent
2. Suggested search terms
3. Product categories that might match
4. Price range considerations
5. Quality and authenticity factors

Be specific and helpful in guiding the search."""
            
            # Get AI analysis
            groq_request = AIRequest(
                message=search_prompt,
                interaction_type="product_search",
                user_id=request.user_id,
                conversation_id=conversation_id
            )
            
            ai_response = await self.groq_client.process_request(groq_request)
            
            # Perform actual product search
            products = await self._search_products(request.message)
            
            # Format response with search results
            response_message = f"{ai_response.message}\n\n"
            if products:
                response_message += f"Found {len(products)} matching products:\n"
                for i, product in enumerate(products[:3], 1):
                    response_message += f"{i}. {product.name} - ${product.price}\n"
            else:
                response_message += "No products found matching your search criteria."
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AIResponse(
                message=response_message,
                interaction_type=request.interaction_type,
                conversation_id=conversation_id,
                confidence=ai_response.confidence,
                processing_time=processing_time,
                model_used="groq+database",
                metadata={
                    "products_found": len(products),
                    "search_query": request.message,
                    "groq_tokens": ai_response.tokens_used
                }
            )
            
        except Exception as e:
            logger.error(f"Product search error: {e}")
            return self.create_error_response(
                conversation_id,
                f"Product search failed: {str(e)}",
                request.interaction_type
            )
    
    async def _handle_product_details(self, request: AIRequest, conversation_id: str) -> AIResponse:
        """Handle product detail requests."""
        try:
            # Extract product ID from message if present
            product_id = self._extract_product_id(request.message)
            
            if product_id:
                product = await self.product_service.get_product_by_id(product_id)
                if product:
                    return await self._generate_product_details_response(
                        product, request, conversation_id
                    )
            
            # If no specific product ID, use AI to help
            detail_prompt = f"""Help with product details for: "{request.message}"
            
As a luxury e-commerce expert, provide guidance on:
1. What specific product information they might need
2. How to find detailed specifications
3. Questions to ask about luxury products
4. Authentication and quality factors

Be helpful and informative."""
            
            groq_request = AIRequest(
                message=detail_prompt,
                interaction_type="product_details",
                user_id=request.user_id,
                conversation_id=conversation_id
            )
            
            ai_response = await self.groq_client.process_request(groq_request)
            
            return AIResponse(
                message=ai_response.message,
                interaction_type=request.interaction_type,
                conversation_id=conversation_id,
                confidence=ai_response.confidence,
                model_used="groq",
                metadata={"groq_tokens": ai_response.tokens_used}
            )
            
        except Exception as e:
            logger.error(f"Product details error: {e}")
            return self.create_error_response(
                conversation_id,
                f"Product details failed: {str(e)}",
                request.interaction_type
            )
    
    async def _handle_general_product_query(self, request: AIRequest, conversation_id: str) -> AIResponse:
        """Handle general product queries."""
        try:
            # Build context-aware prompt
            general_prompt = f"""Answer this product-related question: "{request.message}"
            
As ADOGENT's product expert, provide helpful information about:
- Product categories and types
- Luxury brand knowledge
- Quality and authenticity guidance
- Shopping advice and tips
- General product information

Be conversational, helpful, and knowledgeable."""
            
            groq_request = AIRequest(
                message=general_prompt,
                interaction_type="general_chat",
                user_id=request.user_id,
                conversation_id=conversation_id
            )
            
            ai_response = await self.groq_client.process_request(groq_request)
            
            return AIResponse(
                message=ai_response.message,
                interaction_type=request.interaction_type,
                conversation_id=conversation_id,
                confidence=ai_response.confidence,
                model_used="groq",
                metadata={"groq_tokens": ai_response.tokens_used}
            )
            
        except Exception as e:
            logger.error(f"General product query error: {e}")
            return self.create_error_response(
                conversation_id,
                f"General product query failed: {str(e)}",
                request.interaction_type
            )
    
    async def _search_products(self, search_query: str) -> List[Product]:
        """Search products using the product service."""
        try:
            query = self.product_service.get_products_query(
                search_query=search_query,
                status=ProductStatus.ACTIVE
            )
            
            result = await self.db.execute(query.limit(10))
            products = result.scalars().all()
            
            return list(products)
            
        except Exception as e:
            logger.error(f"Product search error: {e}")
            return []
    
    async def _generate_product_details_response(
        self, 
        product: Product, 
        request: AIRequest, 
        conversation_id: str
    ) -> AIResponse:
        """Generate detailed product information response."""
        try:
            # Use Groq to generate enhanced product description
            product_data = {
                "name": product.name,
                "price": product.price,
                "category": product.category.name if product.category else None,
                "description": product.description,
                "condition": product.condition.value if product.condition else None,
                "quantity": product.quantity,
                "is_featured": product.is_featured
            }
            
            summary = await self.groq_client.generate_product_summary(product_data)
            
            return AIResponse(
                message=summary,
                interaction_type=request.interaction_type,
                conversation_id=conversation_id,
                confidence=0.9,
                model_used="groq+database",
                metadata={
                    "product_id": str(product.id),
                    "product_name": product.name,
                    "product_price": product.price
                }
            )
            
        except Exception as e:
            logger.error(f"Product details generation error: {e}")
            return self.create_error_response(
                conversation_id,
                f"Failed to generate product details: {str(e)}",
                request.interaction_type
            )
    
    def _extract_product_id(self, message: str) -> Optional[UUID]:
        """Extract product ID from message if present."""
        try:
            # Simple UUID extraction - can be enhanced
            uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
            match = re.search(uuid_pattern, message.lower())
            
            if match:
                return UUID(match.group())
            
            return None
            
        except Exception:
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the product agent."""
        try:
            groq_health = await self.groq_client.health_check()
            
            # Test database connection
            db_test = await self.db.execute(select(Product).limit(1))
            db_healthy = db_test is not None
            
            return {
                "status": "healthy" if all([
                    groq_health["status"] == "healthy",
                    db_healthy
                ]) else "unhealthy",
                "groq_status": groq_health["status"],
                "database_status": "healthy" if db_healthy else "unhealthy",
                "last_check": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Product agent health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat(),
            }
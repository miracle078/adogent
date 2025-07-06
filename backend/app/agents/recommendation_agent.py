"""
Recommendation agent for ADOGENT.
Focused specifically on intelligent product recommendations.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from .base_agent import BaseAgent
from .groq_client import GroqClient
from ..schemas.ai_schemas import (
    AIRequest, 
    ProductRecommendationRequest, 
    ProductRecommendationResponse,
    ProductRecommendation
)
from ..models.product import Product, ProductStatus
from ..services.product_service import ProductService
from ..config.config import settings


logger = logging.getLogger(__name__)


class RecommendationAgent(BaseAgent):
    """
    Specialized recommendation agent for intelligent product suggestions.
    Focuses purely on recommendation logic and AI-powered matching.
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__("recommendation_agent")
        self.db = db
        self.groq_client = GroqClient()
        self.product_service = ProductService(db)
        
        logger.info("Initialized Recommendation Agent with AI-powered matching")
    
    async def process_request(self, request: AIRequest) -> ProductRecommendationResponse:
        """Process recommendation request."""
        async with self.track_request(request):
            try:
                if not await self.validate_request(request):
                    return self._create_error_response(
                        self.get_conversation_id(request),
                        "Invalid request format"
                    )
                
                conversation_id = self.get_conversation_id(request)
                
                # Handle structured recommendation requests
                if isinstance(request, ProductRecommendationRequest):
                    return await self._process_structured_recommendation(request, conversation_id)
                
                # Convert general request to recommendation request
                else:
                    return await self._process_general_recommendation(request, conversation_id)
                
            except Exception as e:
                logger.error(f"Recommendation error: {e}")
                return self._create_error_response(
                    self.get_conversation_id(request),
                    f"Recommendation failed: {str(e)}"
                )
    
    async def _process_structured_recommendation(
        self, 
        request: ProductRecommendationRequest, 
        conversation_id: str
    ) -> ProductRecommendationResponse:
        """Process structured recommendation request."""
        try:
            start_time = datetime.utcnow()
            
            # Build AI recommendation prompt
            prompt = self._build_recommendation_prompt(request)
            
            # Get AI analysis
            groq_request = AIRequest(
                message=prompt,
                interaction_type="product_recommendation",
                user_id=request.user_id,
                conversation_id=conversation_id
            )
            
            ai_response = await self.groq_client.process_request(groq_request)
            
            # Get matching products
            products = await self._get_matching_products(request)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(products, request, ai_response.message)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProductRecommendationResponse(
                message=ai_response.message,
                interaction_type=request.interaction_type,
                conversation_id=conversation_id,
                confidence=ai_response.confidence,
                processing_time=processing_time,
                model_used="groq+database",
                recommendations=recommendations,
                total_products_considered=len(products),
                recommendation_strategy="ai_assisted_filtering",
                metadata={
                    "groq_tokens": ai_response.tokens_used,
                    "filters_applied": self._get_applied_filters(request)
                }
            )
            
        except Exception as e:
            logger.error(f"Structured recommendation error: {e}")
            return self._create_error_response(
                conversation_id,
                f"Structured recommendation failed: {str(e)}"
            )
    
    async def _process_general_recommendation(
        self, 
        request: AIRequest, 
        conversation_id: str
    ) -> ProductRecommendationResponse:
        """Process general recommendation request."""
        try:
            start_time = datetime.utcnow()
            
            # Convert to recommendation request
            recommendation_request = ProductRecommendationRequest(
                message=request.message,
                user_id=request.user_id,
                conversation_id=conversation_id,
                context=request.context
            )
            
            # Process as structured recommendation
            return await self._process_structured_recommendation(
                recommendation_request, 
                conversation_id
            )
            
        except Exception as e:
            logger.error(f"General recommendation error: {e}")
            return self._create_error_response(
                conversation_id,
                f"General recommendation failed: {str(e)}"
            )
    
    def _build_recommendation_prompt(self, request: ProductRecommendationRequest) -> str:
        """Build AI recommendation prompt."""
        prompt = f"""As ADOGENT's luxury e-commerce recommendation expert, provide personalized product suggestions for: "{request.message}"

User Context:
- Categories: {request.category_preferences or 'Open to all luxury categories'}
- Budget: {request.price_range or 'Flexible budget'}
- Brands: {request.brand_preferences or 'Open to all luxury brands'}

Provide:
1. 3-5 specific product recommendations
2. Detailed reasoning for each recommendation
3. Style compatibility analysis
4. Value and quality assessment
5. Occasion suitability

Focus on luxury, authenticity, and personalized matching."""
        
        return prompt
    
    async def _get_matching_products(self, request: ProductRecommendationRequest) -> List[Product]:
        """Get products matching recommendation criteria."""
        try:
            # Use product service for consistent querying
            query = self.product_service.get_products_query(
                category_id=None,  # We'll filter by category names if provided
                search_query=None,
                min_price=request.price_range.get("min") if request.price_range else None,
                max_price=request.price_range.get("max") if request.price_range else None,
                is_featured=None,
                status=ProductStatus.ACTIVE,
                sort_by="created_at",
                sort_order="desc"
            )
            
            # Apply additional filters
            if request.exclude_products:
                query = query.where(~Product.id.in_(request.exclude_products))
            
            # Limit results for recommendation processing
            query = query.limit(settings.PRODUCT_RECOMMENDATION_LIMIT * 3)
            
            result = await self.db.execute(query)
            products = result.scalars().all()
            
            return list(products)
            
        except Exception as e:
            logger.error(f"Product matching error: {e}")
            return []
    
    async def _generate_recommendations(
        self, 
        products: List[Product], 
        request: ProductRecommendationRequest,
        ai_analysis: str
    ) -> List[ProductRecommendation]:
        """Generate AI-powered product recommendations."""
        recommendations = []
        
        for product in products[:settings.PRODUCT_RECOMMENDATION_LIMIT]:
            try:
                # Calculate recommendation confidence
                confidence = self._calculate_recommendation_confidence(product, request)
                
                # Generate AI-powered reason
                reason = await self._generate_recommendation_reason(product, request, ai_analysis)
                
                # Extract brand information
                brand = self._extract_brand_from_product(product)
                
                recommendation = ProductRecommendation(
                    product_id=product.id,
                    product_name=product.name,
                    price=product.price,
                    confidence=confidence,
                    reason=reason,
                    category=product.category.name if product.category else None,
                    brand=brand,
                    image_url=None  # TODO: Add when image system is ready
                )
                
                recommendations.append(recommendation)
                
            except Exception as e:
                logger.error(f"Error generating recommendation for product {product.id}: {e}")
                continue
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        
        return recommendations
    
    def _calculate_recommendation_confidence(
        self, 
        product: Product, 
        request: ProductRecommendationRequest
    ) -> float:
        """Calculate recommendation confidence score."""
        confidence = 0.6  # Base confidence for recommendations
        
        # Price range matching
        if request.price_range:
            min_price = request.price_range.get("min", 0)
            max_price = request.price_range.get("max", float('inf'))
            
            if min_price <= product.price <= max_price:
                confidence += 0.2
        
        # Stock availability bonus
        if product.quantity > 0:
            confidence += 0.1
        
        # Featured product bonus
        if product.is_featured:
            confidence += 0.1
        
        # Category preference matching
        if request.category_preferences and product.category:
            if product.category.name in request.category_preferences:
                confidence += 0.15
        
        return min(confidence, 1.0)
    
    async def _generate_recommendation_reason(
        self, 
        product: Product, 
        request: ProductRecommendationRequest,
        ai_analysis: str
    ) -> str:
        """Generate AI-powered recommendation reason."""
        try:
            # Create personalized reason based on product attributes
            reasons = []
            
            if product.is_featured:
                reasons.append("Featured luxury item")
            
            if product.category:
                reasons.append(f"Premium {product.category.name.lower()}")
            
            if product.price > 1000:
                reasons.append("High-end luxury piece")
            
            if product.quantity <= 5:
                reasons.append("Limited availability")
            
            # Combine reasons or use fallback
            if reasons:
                return f"{', '.join(reasons[:2])} - {self._get_style_reason(product)}"
            else:
                return self._get_style_reason(product)
                
        except Exception as e:
            logger.error(f"Error generating recommendation reason: {e}")
            return "Recommended based on your preferences"
    
    def _get_style_reason(self, product: Product) -> str:
        """Get style-based recommendation reason."""
        style_reasons = [
            "Perfect for luxury lifestyle",
            "Matches sophisticated taste",
            "Excellent investment piece",
            "Timeless design and quality",
            "Exclusive and authentic"
        ]
        
        # Simple selection based on product attributes
        if product.is_featured:
            return style_reasons[0]
        elif product.price > 2000:
            return style_reasons[2]
        elif product.category and "bag" in product.category.name.lower():
            return style_reasons[3]
        else:
            return style_reasons[1]
    
    def _extract_brand_from_product(self, product: Product) -> Optional[str]:
        """Extract brand from product information."""
        luxury_brands = [
            "Louis Vuitton", "Chanel", "Hermès", "Gucci", "Prada", 
            "Dior", "Cartier", "Rolex", "Versace", "Armani",
            "Balenciaga", "Saint Laurent", "Bottega Veneta"
        ]
        
        product_text = f"{product.name} {product.description or ''}".lower()
        
        for brand in luxury_brands:
            if brand.lower() in product_text:
                return brand
        
        return None
    
    def _get_applied_filters(self, request: ProductRecommendationRequest) -> Dict[str, Any]:
        """Get applied filters for metadata."""
        filters = {}
        
        if request.category_preferences:
            filters["categories"] = request.category_preferences
        if request.price_range:
            filters["price_range"] = request.price_range
        if request.brand_preferences:
            filters["brands"] = request.brand_preferences
        if request.exclude_products:
            filters["excluded_products"] = len(request.exclude_products)
        
        return filters
    
    def _create_error_response(
        self, 
        conversation_id: str, 
        error_message: str
    ) -> ProductRecommendationResponse:
        """Create error response for recommendations."""
        return ProductRecommendationResponse(
            message=f"I apologize, but I encountered an error while generating recommendations: {error_message}",
            interaction_type="product_recommendation",
            conversation_id=conversation_id,
            confidence=0.0,
            recommendations=[],
            total_products_considered=0,
            recommendation_strategy="error_fallback",
            metadata={"error": True, "error_message": error_message}
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the recommendation agent."""
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
            logger.error(f"Recommendation agent health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat(),
            }
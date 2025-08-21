// Export configuration
export * from './config';

// Export client
export { apiClient, authToken, ApiError } from './client';

// Export services
export { authService } from './services/auth.service';
export { productService } from './services/product.service';
export { aiService } from './services/ai.service';

// Export types
export type {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  User,
} from './services/auth.service';

export type {
  Product,
  ProductImage,
  ProductListResponse,
  ProductFilters,
  CreateProductRequest,
} from './services/product.service';

export type {
  ChatMessage,
  ChatRequest,
  ChatResponse,
  ProductRecommendation,
  RecommendationRequest,
  RecommendationResponse,
  ImageAnalysisRequest,
  ImageAnalysisResponse,
  VoiceChatRequest,
  AIHealthStatus,
} from './services/ai.service';
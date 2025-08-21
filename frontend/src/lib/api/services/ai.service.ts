import { apiClient } from '../client';
import { API_ENDPOINTS } from '../config';

// Types
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  response?: string;  // Legacy field
  message?: string;   // New field from backend
  conversation_id: string;
  agent_type?: string;
  interaction_type?: string;
  processing_time: number;
  timestamp?: string;
  confidence?: number;
  model_used?: string;
  tokens_used?: number;
  metadata?: Record<string, any>;
}

export interface ProductRecommendation {
  product_id: string;
  name: string;
  description: string;
  price: number;
  image_url?: string;
  relevance_score: number;
  reason: string;
}

export interface RecommendationRequest {
  user_preferences?: Record<string, any>;
  category?: string;
  price_range?: {
    min: number;
    max: number;
  };
  limit?: number;
}

export interface RecommendationResponse {
  recommendations: ProductRecommendation[];
  processing_time: number;
}

export interface ImageAnalysisRequest {
  image_url?: string;
  image_file?: File;
  analysis_type?: 'product' | 'style' | 'general';
}

export interface ImageAnalysisResponse {
  analysis: string;
  detected_products?: string[];
  suggestions?: string[];
  processing_time: number;
}

export interface VoiceChatRequest {
  audio_data: Blob;
  conversation_id?: string;
}

export interface AIHealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  agents: Record<string, {
    status: string;
    last_check: string;
    response_time?: number;
  }>;
  timestamp: string;
}

// AI Service
class AIService {
  // Send chat message
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    return apiClient.post<ChatResponse>(
      API_ENDPOINTS.AI.CHAT,
      request
    );
  }

  // Get product recommendations
  async getRecommendations(request?: RecommendationRequest): Promise<RecommendationResponse> {
    return apiClient.post<RecommendationResponse>(
      API_ENDPOINTS.AI.RECOMMENDATIONS,
      request || {}
    );
  }

  // Analyze image
  async analyzeImage(request: ImageAnalysisRequest): Promise<ImageAnalysisResponse> {
    if (request.image_file) {
      const formData = new FormData();
      formData.append('file', request.image_file);
      if (request.analysis_type) {
        formData.append('analysis_type', request.analysis_type);
      }
      
      return apiClient.upload<ImageAnalysisResponse>(
        API_ENDPOINTS.AI.UPLOAD_IMAGE,
        formData
      );
    } else {
      return apiClient.post<ImageAnalysisResponse>(
        API_ENDPOINTS.AI.ANALYZE_IMAGE,
        {
          image_url: request.image_url,
          analysis_type: request.analysis_type,
        }
      );
    }
  }

  // Send voice message
  async sendVoiceMessage(audioBlob: Blob, conversationId?: string): Promise<ChatResponse> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'voice.webm');
    if (conversationId) {
      formData.append('conversation_id', conversationId);
    }
    
    return apiClient.upload<ChatResponse>(
      API_ENDPOINTS.AI.VOICE_CHAT,
      formData
    );
  }

  // Check AI health status
  async checkHealth(): Promise<AIHealthStatus> {
    return apiClient.get<AIHealthStatus>(API_ENDPOINTS.AI.HEALTH);
  }

  // Get AI statistics
  async getStatistics(): Promise<any> {
    return apiClient.get(API_ENDPOINTS.AI.STATISTICS);
  }

  // Stream chat (for future implementation with SSE)
  streamChat(request: ChatRequest, onMessage: (message: string) => void): EventSource {
    const params = new URLSearchParams({
      message: request.message,
      conversation_id: request.conversation_id || '',
    });
    
    const eventSource = new EventSource(
      `${API_ENDPOINTS.AI.CHAT}?${params.toString()}`
    );
    
    eventSource.onmessage = (event) => {
      onMessage(event.data);
    };
    
    return eventSource;
  }
}

// Export singleton instance
export const aiService = new AIService();

// Export default
export default aiService;
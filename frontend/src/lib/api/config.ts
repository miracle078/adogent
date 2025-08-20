// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8008/api/v1',
  BACKEND_URL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8008',
  TIMEOUT: 30000,
};

// API Endpoints
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    REGISTER: '/auth/register',
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
  },
  
  // Users
  USERS: {
    ME: '/users/me',
    UPDATE_ME: '/users/me',
    GET_USER: (id: string) => `/users/${id}`,
    LIST: '/users',
  },
  
  // Products
  PRODUCTS: {
    LIST: '/products',
    CREATE: '/products',
    GET: (id: string) => `/products/${id}`,
    UPDATE: (id: string) => `/products/${id}`,
    DELETE: (id: string) => `/products/${id}`,
  },
  
  // Categories
  CATEGORIES: {
    LIST: '/categories',
    CREATE: '/categories',
    GET: (id: string) => `/categories/${id}`,
  },
  
  // AI Assistant
  AI: {
    CHAT: '/ai/chat',
    RECOMMENDATIONS: '/ai/recommendations',
    ANALYZE_IMAGE: '/ai/analyze-image',
    UPLOAD_IMAGE: '/ai/upload-image',
    VOICE_CHAT: '/ai/voice-chat',
    HEALTH: '/ai/health',
    STATISTICS: '/ai/statistics',
  },
  
  // Orders
  ORDERS: {
    LIST: '/orders',
    CREATE: '/orders',
    GET: (id: string) => `/orders/${id}`,
  },
};

// Helper function to build full URL
export const buildApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};
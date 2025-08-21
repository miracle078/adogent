import { apiClient, authToken } from '../client';
import { API_ENDPOINTS } from '../config';

// Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  confirm_password: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
    full_name: string;
    role: string;
  };
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  created_at: string;
  updated_at: string;
}

// Authentication Service
class AuthService {
  // Login user
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      API_ENDPOINTS.AUTH.LOGIN,
      credentials
    );
    
    // Store tokens
    if (response.access_token) {
      authToken.set(response.access_token);
      if (response.refresh_token) {
        localStorage.setItem('refresh_token', response.refresh_token);
      }
    }
    
    return response;
  }

  // Register new user
  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      API_ENDPOINTS.AUTH.REGISTER,
      userData
    );
    
    // Store tokens
    if (response.access_token) {
      authToken.set(response.access_token);
      if (response.refresh_token) {
        localStorage.setItem('refresh_token', response.refresh_token);
      }
    }
    
    return response;
  }

  // Logout user
  async logout(): Promise<void> {
    try {
      await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear tokens regardless of API response
      authToken.remove();
      localStorage.removeItem('refresh_token');
    }
  }

  // Refresh access token
  async refreshToken(): Promise<AuthResponse> {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    
    const response = await apiClient.post<AuthResponse>(
      API_ENDPOINTS.AUTH.REFRESH,
      { refresh_token: refreshToken }
    );
    
    // Update tokens
    if (response.access_token) {
      authToken.set(response.access_token);
      if (response.refresh_token) {
        localStorage.setItem('refresh_token', response.refresh_token);
      }
    }
    
    return response;
  }

  // Get current user
  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>(API_ENDPOINTS.USERS.ME);
  }

  // Update current user
  async updateCurrentUser(userData: Partial<User>): Promise<User> {
    return apiClient.put<User>(API_ENDPOINTS.USERS.UPDATE_ME, userData);
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!authToken.get();
  }

  // Get stored user info from token (if JWT contains user info)
  getStoredUser(): User | null {
    const token = authToken.get();
    if (!token) return null;
    
    try {
      // Decode JWT payload (base64)
      const payload = JSON.parse(atob(token.split('.')[1]));
      return {
        id: payload.user_id || payload.sub,
        email: payload.email,
        full_name: payload.full_name || '',
        role: payload.role || 'user',
        created_at: '',
        updated_at: '',
      };
    } catch {
      return null;
    }
  }
}

// Export singleton instance
export const authService = new AuthService();

// Export default
export default authService;
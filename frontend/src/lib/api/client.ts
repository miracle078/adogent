import { API_CONFIG } from './config';

// API Error class
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Request options interface
interface RequestOptions extends RequestInit {
  params?: Record<string, any>;
  timeout?: number;
}

// Auth token management
export const authToken = {
  get: () => localStorage.getItem('token'),
  set: (token: string) => localStorage.setItem('token', token),
  remove: () => localStorage.removeItem('token'),
};

// Base API client class
class ApiClient {
  private baseUrl: string;
  private timeout: number;

  constructor(baseUrl: string = API_CONFIG.BASE_URL, timeout: number = API_CONFIG.TIMEOUT) {
    this.baseUrl = baseUrl;
    this.timeout = timeout;
  }

  // Build URL with query parameters
  private buildUrl(endpoint: string, params?: Record<string, any>): string {
    const url = new URL(`${this.baseUrl}${endpoint}`);
    
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== undefined && params[key] !== null) {
          url.searchParams.append(key, params[key].toString());
        }
      });
    }
    
    return url.toString();
  }

  // Build headers with authentication
  private buildHeaders(customHeaders?: HeadersInit): Headers {
    const headers = new Headers(customHeaders);
    
    // Add content type if not present
    if (!headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }
    
    // Add authentication token if available
    const token = authToken.get();
    if (token && !headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    
    return headers;
  }

  // Handle API response
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      let errorData;
      
      try {
        errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        // Response body is not JSON
      }
      
      throw new ApiError(errorMessage, response.status, errorData);
    }
    
    // Handle empty responses
    if (response.status === 204) {
      return {} as T;
    }
    
    try {
      return await response.json();
    } catch {
      // Response is not JSON
      return {} as T;
    }
  }

  // Make API request with timeout
  private async fetchWithTimeout(url: string, options: RequestInit): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error: any) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new ApiError('Request timeout', 408);
      }
      throw error;
    }
  }

  // GET request
  async get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    const url = this.buildUrl(endpoint, options?.params);
    const headers = this.buildHeaders(options?.headers);
    
    const response = await this.fetchWithTimeout(url, {
      ...options,
      method: 'GET',
      headers,
    });
    
    return this.handleResponse<T>(response);
  }

  // POST request
  async post<T>(endpoint: string, data?: any, options?: RequestOptions): Promise<T> {
    const url = this.buildUrl(endpoint, options?.params);
    const headers = this.buildHeaders(options?.headers);
    
    const response = await this.fetchWithTimeout(url, {
      ...options,
      method: 'POST',
      headers,
      body: data ? JSON.stringify(data) : undefined,
    });
    
    return this.handleResponse<T>(response);
  }

  // PUT request
  async put<T>(endpoint: string, data?: any, options?: RequestOptions): Promise<T> {
    const url = this.buildUrl(endpoint, options?.params);
    const headers = this.buildHeaders(options?.headers);
    
    const response = await this.fetchWithTimeout(url, {
      ...options,
      method: 'PUT',
      headers,
      body: data ? JSON.stringify(data) : undefined,
    });
    
    return this.handleResponse<T>(response);
  }

  // DELETE request
  async delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    const url = this.buildUrl(endpoint, options?.params);
    const headers = this.buildHeaders(options?.headers);
    
    const response = await this.fetchWithTimeout(url, {
      ...options,
      method: 'DELETE',
      headers,
    });
    
    return this.handleResponse<T>(response);
  }

  // Upload file
  async upload<T>(endpoint: string, formData: FormData, options?: RequestOptions): Promise<T> {
    const url = this.buildUrl(endpoint, options?.params);
    const headers = new Headers(options?.headers);
    
    // Remove Content-Type to let browser set it with boundary for multipart
    headers.delete('Content-Type');
    
    // Add authentication token if available
    const token = authToken.get();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    
    const response = await this.fetchWithTimeout(url, {
      ...options,
      method: 'POST',
      headers,
      body: formData,
    });
    
    return this.handleResponse<T>(response);
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export default
export default apiClient;
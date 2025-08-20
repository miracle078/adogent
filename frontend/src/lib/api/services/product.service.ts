import { apiClient } from '../client';
import { API_ENDPOINTS } from '../config';

// Types
export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  compare_at_price?: number;
  cost_price?: number;
  category_id?: string;
  brand?: string;
  sku?: string;
  barcode?: string;
  quantity: number;
  status: 'active' | 'draft' | 'archived';
  condition: 'new' | 'used' | 'refurbished';
  is_featured: boolean;
  tags?: string[];
  images?: ProductImage[];
  created_at: string;
  updated_at: string;
}

export interface ProductImage {
  id: string;
  url: string;
  alt_text?: string;
  position: number;
}

export interface ProductListResponse {
  items: Product[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface ProductFilters {
  category_id?: string;
  status?: string;
  condition?: string;
  min_price?: number;
  max_price?: number;
  search?: string;
  is_featured?: boolean;
  page?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface CreateProductRequest {
  name: string;
  description: string;
  price: number;
  compare_at_price?: number;
  cost_price?: number;
  category_id?: string;
  brand?: string;
  sku?: string;
  barcode?: string;
  quantity: number;
  status?: 'active' | 'draft' | 'archived';
  condition?: 'new' | 'used' | 'refurbished';
  is_featured?: boolean;
  tags?: string[];
}

// Product Service
class ProductService {
  // Get all products with filters
  async getProducts(filters?: ProductFilters): Promise<ProductListResponse> {
    const response = await apiClient.get<any>(
      API_ENDPOINTS.PRODUCTS.LIST,
      { params: filters }
    );
    
    // Normalize products data from backend
    const normalizeProduct = (product: any): Product => ({
      ...product,
      status: (product.status || 'active').toLowerCase() as 'active' | 'draft' | 'archived',
      condition: product.condition || 'new' as 'new' | 'used' | 'refurbished',
      quantity: product.quantity || 0,
      is_featured: product.is_featured || false,
      images: product.images || [],
      tags: product.tags || [],
      created_at: product.created_at || new Date().toISOString(),
      updated_at: product.updated_at || new Date().toISOString()
    });
    
    // Handle both direct array and object with products field
    if (Array.isArray(response)) {
      return {
        items: response.map(normalizeProduct),
        total: response.length,
        page: 1,
        limit: response.length,
        pages: 1
      };
    } else if (response.products) {
      return {
        items: response.products.map(normalizeProduct),
        total: response.total || response.products.length,
        page: response.page || 1,
        limit: response.size || response.limit || response.products.length, // Handle 'size' field from backend
        pages: response.pages || 1
      };
    }
    
    // Handle paginated response from backend
    return {
      items: (response.items || response.results || []).map(normalizeProduct),
      total: response.total || 0,
      page: response.page || 1,
      limit: response.size || response.limit || 10, // Handle 'size' field from backend
      pages: response.pages || 1
    };
  }

  // Get single product by ID
  async getProduct(id: string): Promise<Product> {
    return apiClient.get<Product>(API_ENDPOINTS.PRODUCTS.GET(id));
  }

  // Create new product
  async createProduct(productData: CreateProductRequest, images?: File[]): Promise<Product> {
    // Backend expects FormData with product_data as JSON string
    const formData = new FormData();
    formData.append('product_data', JSON.stringify(productData));
    
    // Add images if provided
    if (images && images.length > 0) {
      images.forEach((image) => {
        formData.append('images', image);
      });
    }
    
    // Use upload method which handles FormData correctly
    return apiClient.upload<Product>(
      API_ENDPOINTS.PRODUCTS.CREATE,
      formData
    );
  }

  // Update product
  async updateProduct(id: string, productData: Partial<CreateProductRequest>): Promise<Product> {
    return apiClient.put<Product>(
      API_ENDPOINTS.PRODUCTS.UPDATE(id),
      productData
    );
  }

  // Delete product
  async deleteProduct(id: string): Promise<void> {
    return apiClient.delete<void>(API_ENDPOINTS.PRODUCTS.DELETE(id));
  }

  // Search products
  async searchProducts(query: string, limit: number = 10): Promise<Product[]> {
    const response = await this.getProducts({
      search: query,
      limit,
      status: 'active',
    });
    return response.items;
  }

  // Get featured products
  async getFeaturedProducts(limit: number = 8): Promise<Product[]> {
    const response = await this.getProducts({
      is_featured: true,
      status: 'active',
      limit,
    });
    return response.items;
  }

  // Get products by category
  async getProductsByCategory(categoryId: string, filters?: ProductFilters): Promise<ProductListResponse> {
    return this.getProducts({
      ...filters,
      category_id: categoryId,
    });
  }

  // Upload product image
  async uploadProductImage(productId: string, file: File): Promise<ProductImage> {
    const formData = new FormData();
    formData.append('file', file);
    
    return apiClient.upload<ProductImage>(
      `/products/${productId}/images`,
      formData
    );
  }
}

// Export singleton instance
export const productService = new ProductService();

// Export default
export default productService;
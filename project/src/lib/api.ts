const API_BASE_URL = 'http://localhost:8000';

export interface Product {
  id: string;
  name: string;
  price: number;
  description: string;
  color: string;
  size: string;
  product_code: string;
  category: string;
  image_url: string;
  pricebook_entry_id: string;
}

export interface CartItem {
  product: Product;
  quantity: number;
}

export interface SearchFilters {
  query?: string;
  category?: string;
  price_min?: number;
  price_max?: number;
  color?: string;
  size?: string;
}

export interface OrderCustomer {
  name: string;
  email: string;
  phone: string;
}

export interface OrderItem {
  pricebook_entry_id: string;
  quantity: number;
}

export interface OrderResponse {
  success: boolean;
  order_number: string;
  order_id: string;
  total_amount: number;
  message: string;
}

export const api = {
  // Products
  async getProducts(category?: string, limit?: number): Promise<Product[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (limit) params.append('limit', limit.toString());

    const response = await fetch(`${API_BASE_URL}/api/products?${params}`);
    if (!response.ok) throw new Error('Failed to fetch products');
    return response.json();
  },

  async searchProducts(filters: SearchFilters): Promise<Product[]> {
    const response = await fetch(`${API_BASE_URL}/api/products/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(filters),
    });
    if (!response.ok) throw new Error('Failed to search products');
    return response.json();
  },

  async getProduct(productId: string): Promise<Product> {
    const response = await fetch(`${API_BASE_URL}/api/products/${productId}`);
    if (!response.ok) throw new Error('Failed to fetch product');
    return response.json();
  },

  async getCategories(): Promise<string[]> {
    const response = await fetch(`${API_BASE_URL}/api/categories`);
    if (!response.ok) throw new Error('Failed to fetch categories');
    const data = await response.json();
    return data.categories;
  },

  // Cart
  async addToCart(sessionId: string, productId: string, quantity: number) {
    const response = await fetch(`${API_BASE_URL}/api/cart/${sessionId}/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: productId, quantity }),
    });
    if (!response.ok) throw new Error('Failed to add to cart');
    return response.json();
  },

  async getCart(sessionId: string): Promise<{ cart: CartItem[]; total: number }> {
    const response = await fetch(`${API_BASE_URL}/api/cart/${sessionId}`);
    if (!response.ok) throw new Error('Failed to fetch cart');
    return response.json();
  },

  async removeFromCart(sessionId: string, productId: string) {
    const response = await fetch(`${API_BASE_URL}/api/cart/${sessionId}/item/${productId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to remove from cart');
    return response.json();
  },

  async updateCartQuantity(sessionId: string, productId: string, quantity: number) {
    const response = await fetch(`${API_BASE_URL}/api/cart/${sessionId}/item/${productId}?quantity=${quantity}`, {
      method: 'PUT',
    });
    if (!response.ok) throw new Error('Failed to update cart');
    return response.json();
  },

  async clearCart(sessionId: string) {
    const response = await fetch(`${API_BASE_URL}/api/cart/${sessionId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to clear cart');
    return response.json();
  },

  // Orders
  async placeOrder(customer: OrderCustomer, items: OrderItem[]): Promise<OrderResponse> {
    const response = await fetch(`${API_BASE_URL}/api/orders`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        customer,
        items,
        checkout_source: 'Web',
      }),
    });
    if (!response.ok) throw new Error('Failed to place order');
    return response.json();
  },

  async getOrder(orderNumber: string) {
    const response = await fetch(`${API_BASE_URL}/api/orders/${orderNumber}`);
    if (!response.ok) throw new Error('Failed to fetch order');
    return response.json();
  },

  async getCustomerOrders(email: string) {
    const response = await fetch(`${API_BASE_URL}/api/orders/customer/${email}`);
    if (!response.ok) throw new Error('Failed to fetch customer orders');
    return response.json();
  },
};

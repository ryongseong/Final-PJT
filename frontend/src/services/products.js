import axios from 'axios'

// Base API URL for products
const API_URL = 'http://localhost:8000/products/'

// Create API client with default configuration
const apiClient = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor for authentication
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default {
  // Get all financial products
  async getAllFinancialProducts() {
    return apiClient.get('financial-products/').then((response) => response.data)
  },

  // Alias for getAllFinancialProducts to maintain compatibility
  async getAllProducts(params = {}) {
    return apiClient.get('financial-products/', { params }).then((response) => response.data)
  },

  // Get specific financial product
  async getFinancialProduct(id) {
    return apiClient.get(`financial-products/${id}/`).then((response) => response.data)
  },

  // Get all deposit products
  async getDepositProducts(params = {}) {
    return apiClient.get('deposits/', { params }).then((response) => response.data)
  },

  // Get specific deposit product
  async getDepositProduct(id) {
    return apiClient.get(`deposits/${id}/`).then((response) => response.data)
  },

  // Get all saving products
  async getSavingProducts(params = {}) {
    return apiClient.get('savings/', { params }).then((response) => response.data)
  },

  // Get specific saving product
  async getSavingProduct(id) {
    return apiClient.get(`savings/${id}/`).then((response) => response.data)
  },

  // Get all loan products
  async getLoanProducts(params = {}) {
    return apiClient.get('loans/', { params }).then((response) => response.data)
  },

  // Get specific loan product
  async getLoanProduct(id) {
    return apiClient.get(`loans/${id}/`).then((response) => response.data)
  },

  // Get top rate products by type
  async getTopRateProducts(type, limit = 5) {
    return apiClient
      .get(`top-rates/${type}/`, {
        params: { limit },
      })
      .then((response) => response.data)
  },

  // Get lowest rate loan products
  async getLowestRateLoans(limit = 5) {
    return apiClient
      .get('lowest-rate-loans/', {
        params: { limit },
      })
      .then((response) => response.data)
  },

  // Search financial products
  async searchProducts(query) {
    return apiClient
      .get('search/', {
        params: { q: query },
      })
      .then((response) => response.data)
  },

  // User favorites operations
  async getUserFavorites() {
    return apiClient.get('user/favorites/').then((response) => response.data)
  },
  async addToFavorites(productId) {
    return apiClient
      .post(`user/favorites/${productId}/add/`)
      .then((response) => response.data || {})
  },

  async removeFromFavorites(productId) {
    return apiClient.delete(`user/favorites/${productId}/remove/`).then((response) => response.data)
  },

  // Admin operations - these require admin privileges
  async updateAllProducts() {
    return apiClient.post('admin/update-all/').then((response) => response.data)
  },

  async updateDepositProducts() {
    return apiClient.post('admin/update-deposits/').then((response) => response.data)
  },

  async updateSavingProducts() {
    return apiClient.post('admin/update-savings/').then((response) => response.data)
  },

  async updateMortgageProducts() {
    return apiClient.post('admin/update-mortgage-loans/').then((response) => response.data)
  },

  async updateCreditProducts() {
    return apiClient.post('admin/update-credit-loans/').then((response) => response.data)
  },
}

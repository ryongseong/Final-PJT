import axios from 'axios'

// Base API URL for admin routes
const API_URL = 'http://localhost:8000/products/admin/'

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
  // Financial Products Management
  async getFinancialProducts(params = {}) {
    return apiClient.get('financial-products/', { params }).then((response) => response.data)
  },

  async getFinancialProduct(id) {
    return apiClient.get(`financial-products/${id}/`).then((response) => response.data)
  },

  async createFinancialProduct(productData) {
    return apiClient.post('financial-products/', productData).then((response) => response.data)
  },

  async updateFinancialProduct(id, productData) {
    return apiClient.put(`financial-products/${id}/`, productData).then((response) => response.data)
  },

  async deleteFinancialProduct(id) {
    return apiClient.delete(`financial-products/${id}/`).then((response) => response.data)
  },

  async searchFinancialProducts(query, category) {
    return apiClient
      .get(`financial-products/search/?q=${query}&category=${category || ''}`)
      .then((response) => response.data)
  },

  // Deposit Products Management
  async getDepositProducts(params = {}) {
    return apiClient.get('deposits/', { params }).then((response) => response.data)
  },

  async getDepositProduct(id) {
    return apiClient.get(`deposits/${id}/`).then((response) => response.data)
  },

  async createDepositProduct(productData) {
    return apiClient.post('deposits/', productData).then((response) => response.data)
  },

  async updateDepositProduct(id, productData) {
    return apiClient.put(`deposits/${id}/`, productData).then((response) => response.data)
  },

  async deleteDepositProduct(id) {
    return apiClient.delete(`deposits/${id}/`).then((response) => response.data)
  },

  // Saving Products Management
  async getSavingProducts(params = {}) {
    return apiClient.get('savings/', { params }).then((response) => response.data)
  },

  async getSavingProduct(id) {
    return apiClient.get(`savings/${id}/`).then((response) => response.data)
  },

  async createSavingProduct(productData) {
    return apiClient.post('savings/', productData).then((response) => response.data)
  },

  async updateSavingProduct(id, productData) {
    return apiClient.put(`savings/${id}/`, productData).then((response) => response.data)
  },

  async deleteSavingProduct(id) {
    return apiClient.delete(`savings/${id}/`).then((response) => response.data)
  },

  // Loan Products Management
  async getLoanProducts(params = {}) {
    return apiClient.get('loans/', { params }).then((response) => response.data)
  },

  async getLoanProduct(id) {
    return apiClient.get(`loans/${id}/`).then((response) => response.data)
  },

  async createLoanProduct(productData) {
    return apiClient.post('loans/', productData).then((response) => response.data)
  },

  async updateLoanProduct(id, productData) {
    return apiClient.put(`loans/${id}/`, productData).then((response) => response.data)
  },

  async deleteLoanProduct(id) {
    return apiClient.delete(`loans/${id}/`).then((response) => response.data)
  },

  // Update operations from API
  async updateAllProducts() {
    return apiClient.post('../admin/update-all/').then((response) => response.data)
  },

  async batchUpdateProducts() {
    return apiClient.post('../admin/batch-update/').then((response) => response.data)
  },

  async updateDepositProductsFromAPI() {
    return apiClient.post('../admin/update-deposits/').then((response) => response.data)
  },

  async updateSavingProductsFromAPI() {
    return apiClient.post('../admin/update-savings/').then((response) => response.data)
  },

  async updateMortgageProductsFromAPI() {
    return apiClient.post('../admin/update-mortgage-loans/').then((response) => response.data)
  },

  async updateCreditProductsFromAPI() {
    return apiClient.post('../admin/update-credit-loans/').then((response) => response.data)
  },
}

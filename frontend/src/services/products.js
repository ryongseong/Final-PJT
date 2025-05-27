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
  async getGoldAndSilverPrices(params = {}) {
    console.log(params)
    return await apiClient
      .get('gold-and-silver-prices/', { params })
      .then((response) => response.data)
  },

  async getExchangeRate() {
    return await apiClient.get('exchange-rate/').then((response) => response.data)
  },

  async getKosdaqData() {
    return await apiClient.get('kosdaq-stock-market/').then((response) => response)
  },

  async getKospiData() {
    return await apiClient.get('kospi-stock-market/').then((response) => response)
  },

  // Get all financial products
  async getAllFinancialProducts() {
    return apiClient.get('financial-products/').then((response) => response.data)
  },

  // Alias for getAllFinancialProducts to maintain compatibility
  async getAllProducts(params = {}) {
    const depositProduct = await apiClient.get('deposits/', { params })
    const savingProduct = await apiClient.get('savings/', { params })
    const loanProduct = await apiClient.get('loans/', { params })

    const allProducts = depositProduct.data.concat(savingProduct.data, loanProduct.data)
    if (allProducts) {
      return allProducts
    }

    return apiClient.get('financial-products/', { params }).then((response) => response.data)
  },

  // Get specific financial product
  async getFinancialProduct(id) {
    return apiClient.get(`financial-products/${id}/`).then((response) => response.data)
  },

  // Get all deposit products with expanded parameters
  async getDepositProducts(params = {}) {
    return apiClient.get('deposits/', { params }).then((response) => response.data)
  },

  // Search deposit products with filtering options
  async searchDepositProducts({ page = 1, pageSize = 20, minRate, maxRate, bank, term, orderBy }) {
    const params = { page }

    // Add optional filters if provided
    if (pageSize) params.page_size = pageSize
    if (minRate) params.min_rate = minRate
    if (maxRate) params.max_rate = maxRate
    if (bank) params.bank = bank
    if (term) params.save_trm = term
    if (orderBy) params.ordering = orderBy // e.g. '-intr_rate2' for highest rate first

    return apiClient.get('deposits/', { params }).then((response) => response.data)
  },

  // Get specific deposit product
  async getDepositProduct(id) {
    return apiClient.get(`deposits/${id}/?include_requirements=true`).then((response) => {
      console.log('Deposit product response with requirements:', response.data)
      return response.data
    })
  },

  // Get all saving products
  async getSavingProducts(params = {}) {
    return apiClient.get('savings/', { params }).then((response) => response.data)
  },

  // Search saving products with filtering options
  async searchSavingProducts({
    page = 1,
    pageSize = 20,
    minRate,
    maxRate,
    bank,
    term,
    rsrvType,
    orderBy,
  }) {
    const params = { page }

    // Add optional filters if provided
    if (pageSize) params.page_size = pageSize
    if (minRate) params.min_rate = minRate
    if (maxRate) params.max_rate = maxRate
    if (bank) params.bank = bank
    if (term) params.save_trm = term
    if (rsrvType) params.rsrv_type = rsrvType
    if (orderBy) params.ordering = orderBy // e.g. '-intr_rate2' for highest rate first

    return apiClient.get('savings/', { params }).then((response) => response.data)
  },

  // Get specific saving product
  async getSavingProduct(id) {
    return apiClient.get(`savings/${id}/?include_requirements=true`).then((response) => {
      console.log('Saving product response with requirements:', response.data)
      return response.data
    })
  },

  // Get all loan products
  async getLoanProducts(params = {}) {
    return apiClient.get('loans/', { params }).then((response) => response.data)
  },

  // Search loan products with filtering options
  async searchLoanProducts({
    page = 1,
    pageSize = 20,
    bank,
    loanType,
    hasMortgage,
    hasCredit,
    orderBy,
  }) {
    const params = { page }

    // Add optional filters if provided
    if (pageSize) params.page_size = pageSize
    if (bank) params.bank = bank
    if (loanType) params.loan_type = loanType
    if (hasMortgage) params.has_mortgage = hasMortgage
    if (hasCredit) params.has_credit = hasCredit
    if (orderBy) params.ordering = orderBy

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

  // Admin: Update financial product data
  async updateAllProducts() {
    return apiClient.post('admin/update-all/').then((response) => response.data)
  },

  // Admin: Batch update specific types of financial products
  async batchUpdateProducts(types = []) {
    return apiClient.post('admin/batch-update/', { types }).then((response) => response.data)
  },

  // Get product statistics
  async getProductStatistics() {
    return apiClient.get('statistics/').then((response) => response.data)
  },

  // Filter products by criteria
  async filterProducts(params = {}) {
    return apiClient.get('filter/', { params }).then((response) => response.data)
  },

  // Get personalized product recommendations
  async getRecommendations() {
    return apiClient.get('recommendations/').then((response) => response.data)
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

  // Get detailed product information by ID and type
  async getProductByTypeAndId(type, id) {
    if (!type || !id) {
      throw new Error('Type and ID are required')
    }

    const typeEndpoints = {
      deposit: 'deposits',
      DEPOSIT: 'deposits',
      saving: 'savings',
      SAVINGS: 'savings',
      loan: 'loans',
      LOAN: 'loans',
    }

    const endpoint = typeEndpoints[type] || 'financial-products'

    // Include requirements=true parameter to get requirement options data
    return apiClient.get(`${endpoint}/${id}/?include_requirements=true`).then((response) => {
      // Log the structure of the response to help with debugging
      console.log(`API Response for ${type} product ${id}:`, response.data)
      return response.data
    })
  },

  // Get AI recommendations
  async getAIRecommendations(params = {}) {
    return apiClient.get('ai-recommendations/', { params })
  },
}

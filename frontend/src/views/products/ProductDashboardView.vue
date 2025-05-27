<template>
  <div class="dashboard-container">
    <h1 class="page-title">금융상품 대시보드</h1>

    <div class="dashboard-grid">
      <ProductStatistics class="dashboard-widget" />

      <div class="dashboard-widget" v-if="isLoggedIn">
        <ProductRecommendations />
      </div>

      <div class="dashboard-widget top-products-section">
        <h2 class="widget-title">최고 금리 상품</h2>
        <div class="tab-container">
          <div class="tabs">
            <button
              v-for="tab in productTabs"
              :key="tab.value"
              :class="['tab', { active: activeTab === tab.value }]"
              @click="activeTab = tab.value"
            >
              {{ tab.label }}
            </button>
          </div>

          <div v-if="topProductsLoading" class="loading-indicator">
            <p>상품을 불러오는 중...</p>
          </div>

          <div v-else-if="topProductsError" class="error-message">
            <p>{{ topProductsError }}</p>
          </div>

          <div v-else-if="topProducts.length === 0" class="empty-state">
            <p>상품 데이터가 없습니다.</p>
          </div>

          <div v-else class="top-products-grid">
            <ProductCard
              v-for="product in topProducts"
              :key="product.fin_prdt_cd"
              :product="{
                ...(product.financial_product || product.product_info || product),
                ...product,
                type: activeTab,
                product_type: activeTab,
              }"
              :isFavorite="isProductInFavorites(product.fin_prdt_cd)"
              @toggle-favorite="toggleFavorite"
            />
          </div>

          <div class="view-all">
            <router-link
              :to="{ name: 'Products', query: { tab: activeTab } }"
              class="view-all-link"
            >
              모든 {{ getTabLabel(activeTab) }} 상품 보기
              <i class="fas fa-arrow-right"></i>
            </router-link>
          </div>
        </div>
      </div>

      <div class="dashboard-widget search-section">
        <h2 class="widget-title">상품 검색</h2>
        <div class="search-wrapper">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="상품명 또는 은행명으로 검색"
            class="search-input"
            @keyup.enter="searchProducts"
          />
          <button class="search-button" @click="searchProducts">
            <i class="fas fa-search"></i> 검색
          </button>
        </div>
        <div class="popular-terms">
          <span class="popular-label">인기 검색어:</span>
          <button
            v-for="term in popularSearchTerms"
            :key="term"
            class="popular-term"
            @click="
              () => {
                searchQuery = term
                searchProducts()
              }
            "
          >
            {{ term }}
          </button>
        </div>
      </div>
    </div>

    <!-- Admin Section for Batch Updates -->
    <section v-if="isAdmin" class="dashboard-section admin-section">
      <h2>Admin: Batch Product Updates</h2>
      <button @click="triggerBatchUpdate('deposit')" :disabled="isUpdating">
        Update Deposit Products
      </button>
      <button @click="triggerBatchUpdate('saving')" :disabled="isUpdating">
        Update Saving Products
      </button>
      <button @click="triggerBatchUpdate('mortgage_loan')" :disabled="isUpdating">
        Update Mortgage Loans
      </button>
      <button @click="triggerBatchUpdate('credit_loan')" :disabled="isUpdating">
        Update Credit Loans
      </button>
      <div v-if="isUpdating" class="loading-message">Updating...</div>
      <div
        v-if="updateStatus"
        :class="{ 'success-message': updateStatus.success, 'error-message': !updateStatus.success }"
      >
        {{ updateStatus.message }}
      </div>
    </section>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import productsService from '@/services/products'
import ProductCard from '@/components/products/ProductCard.vue'
import ProductStatistics from '@/components/products/ProductStatistics.vue'
import ProductRecommendations from '@/components/products/ProductRecommendations.vue'

export default {
  name: 'ProductDashboardView',
  components: {
    ProductCard,
    ProductStatistics,
    ProductRecommendations,
  },
  setup() {
    const userStore = useUserStore()
    const router = useRouter()

    const isLoggedIn = computed(() => userStore.isLoggedIn)

    // Product tabs for the top rates section
    const productTabs = [
      { label: '예금', value: 'deposit' },
      { label: '적금', value: 'saving' },
      { label: '대출', value: 'loan' },
    ]
    const activeTab = ref('deposit')

    // Top products section
    const topProducts = ref([])
    const topProductsLoading = ref(false)
    const topProductsError = ref(null)

    const loadTopProducts = async () => {
      topProductsLoading.value = true
      topProductsError.value = null

      try {
        const response = await productsService.getTopRateProducts(activeTab.value, 6)
        topProducts.value = response
      } catch (err) {
        console.error('Failed to load top products:', err)
        topProductsError.value = '최고 금리 상품을 불러오는데 실패했습니다.'
      } finally {
        topProductsLoading.value = false
      }
    }

    // Favorites functionality
    const favorites = ref([])

    const loadFavorites = async () => {
      if (!isLoggedIn.value) return

      try {
        const favoritesData = await productsService.getUserFavorites()
        favorites.value = favoritesData
      } catch (error) {
        console.error('Failed to load favorites:', error)
      }
    }

    const isProductInFavorites = (productId) => {
      return favorites.value.some((fav) => fav.product.fin_prdt_cd === productId)
    }

    const toggleFavorite = async (product) => {
      if (!isLoggedIn.value) {
        router.push('/login')
        return
      }

      try {
        if (isProductInFavorites(product.fin_prdt_cd)) {
          await productsService.removeFromFavorites(product.fin_prdt_cd)
        } else {
          await productsService.addToFavorites(product.fin_prdt_cd)
        }
        await loadFavorites()
      } catch (error) {
        console.error('Failed to toggle favorite status:', error)
      }
    }

    // Search functionality
    const searchQuery = ref('')
    const popularSearchTerms = ref(['정기예금', '주택청약', '신용대출', '우대금리', '신한은행'])

    const searchProducts = () => {
      if (!searchQuery.value.trim()) return

      router.push({
        name: 'Products',
        query: { search: searchQuery.value },
      })
    }

    // Admin functionality
    const isAdmin = ref(true) // Placeholder for admin check, replace with actual logic
    const isUpdating = ref(false)
    const updateStatus = ref(null) // { success: boolean, message: string }

    const triggerBatchUpdate = async (productType) => {
      if (!isAdmin.value) {
        alert('You are not authorized to perform this action.')
        return
      }
      isUpdating.value = true
      updateStatus.value = null
      try {
        // The API endpoint expects a list of types.
        // For simplicity, updating one type at a time here.
        const response = await productsService.batchUpdateProducts({ types: [productType] })
        updateStatus.value = {
          success: true,
          message: response.data.message || `Successfully updated ${productType} products.`,
        }
        // Optionally, refresh statistics or other relevant data
        // For example, by emitting an event or calling a refresh method on ProductStatistics
      } catch (err) {
        console.error(`Error updating ${productType} products:`, err)
        updateStatus.value = {
          success: false,
          message: err.response?.data?.detail || `Failed to update ${productType} products.`,
        }
      } finally {
        isUpdating.value = false
      }
    }

    // Helper functions
    const getTabLabel = (tabValue) => {
      const tab = productTabs.find((t) => t.value === tabValue)
      return tab ? tab.label : ''
    }

    // Lifecycle hooks
    onMounted(() => {
      loadTopProducts()
      loadFavorites()
    })

    // Watch for tab changes to load new products
    const watchActiveTab = (newTab) => {
      activeTab.value = newTab
      loadTopProducts()
    }

    return {
      isLoggedIn,
      productTabs,
      activeTab,
      topProducts,
      topProductsLoading,
      topProductsError,
      searchQuery,
      popularSearchTerms,
      isProductInFavorites,
      toggleFavorite,
      searchProducts,
      getTabLabel,
      watchActiveTab,
      isAdmin,
      triggerBatchUpdate,
      isUpdating,
      updateStatus,
    }
  },
  watch: {
    activeTab: {
      handler: 'watchActiveTab',
      immediate: false,
    },
  },
}
</script>

<style scoped>
.dashboard-container {
  padding: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 2rem;
  color: #333;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 2rem;
}

.dashboard-widget {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.widget-title {
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #333;
  padding: 1.5rem 1.5rem 0 1.5rem;
}

.top-products-section {
  grid-column: span 2;
}

.tab-container {
  padding: 0 1.5rem 1.5rem 1.5rem;
}

.tabs {
  display: flex;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
}

.tab {
  padding: 0.8rem 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  color: #666;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.tab.active {
  color: #1976d2;
  font-weight: 600;
  border-bottom-color: #1976d2;
}

.top-products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.view-all {
  text-align: right;
  padding-top: 1rem;
}

.view-all-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #1976d2;
  text-decoration: none;
  font-weight: 500;
}

.search-section {
  padding-bottom: 1.5rem;
}

.search-wrapper {
  display: flex;
  margin: 0 1.5rem;
}

.search-input {
  flex: 1;
  padding: 0.8rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px 0 0 6px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #1976d2;
}

.search-button {
  background-color: #1976d2;
  color: white;
  border: none;
  padding: 0 1.5rem;
  border-radius: 0 6px 6px 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
}

.popular-terms {
  margin: 1.2rem 1.5rem;
}

.popular-label {
  font-size: 0.85rem;
  color: #888;
  margin-right: 0.5rem;
}

.popular-term {
  background: none;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  padding: 0.35rem 0.8rem;
  font-size: 0.85rem;
  margin: 0.3rem;
  cursor: pointer;
  transition: all 0.2s;
}

.popular-term:hover {
  background-color: #f5f5f5;
  border-color: #ccc;
}

.loading-indicator,
.error-message,
.empty-state {
  padding: 2rem;
  text-align: center;
  color: #666;
}

.error-message {
  color: #e53935;
}

.product-dashboard-view {
  padding: 20px;
}

.product-dashboard-view h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.dashboard-section {
  background-color: #fff;
  padding: 20px;
  margin-bottom: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
}

.dashboard-section h2 {
  margin-top: 0;
  color: #0056b3;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.placeholder-content {
  color: #666;
  font-style: italic;
}

.admin-section {
  border-left: 4px solid #dc3545; /* Red accent for admin section */
}

.admin-section button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 15px;
  margin-right: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.admin-section button:hover {
  background-color: #0056b3;
}

.admin-section button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.loading-message {
  margin-top: 10px;
  color: #007bff;
}

.success-message {
  margin-top: 10px;
  color: #28a745;
  background-color: #e9f7ef;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #a3e0b8;
}

.error-message {
  margin-top: 10px;
  color: #dc3545;
  background-color: #fbe LBEB;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #f5c6cb;
}

@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .top-products-section {
    grid-column: auto;
  }
}
</style>

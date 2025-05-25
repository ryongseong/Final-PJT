<template>
  <div class="comparison-container">
    <div class="page-header">
      <h1 class="page-title">상품 비교</h1>
      <div class="header-actions">
        <button @click="goBack" class="back-button">
          <i class="fas fa-arrow-left"></i> 뒤로가기
        </button>
      </div>
    </div>

    <div class="comparison-content">
      <div class="comparison-controls">
        <div class="comparison-info">
          <p>
            <i class="fas fa-info-circle"></i>
            최대 4개의 상품을 비교할 수 있습니다. (현재 {{ compareList.length }}개 선택됨)
          </p>
        </div>

        <div class="add-product-section" v-if="compareList.length < 4">
          <button @click="showAddModal = !showAddModal" class="add-product-button">
            <i class="fas fa-plus"></i> 상품 추가하기
          </button>
        </div>
      </div>

      <ProductComparison
        :products="compareList"
        :loading="loading"
        :error="error"
        :favorites="favorites"
        @view-details="viewProductDetails"
        @toggle-favorite="toggleFavorite"
        @remove-product="removeProductFromCompare"
      />

      <div v-if="compareList.length === 0" class="empty-comparison">
        <p>비교할 상품을 추가해주세요.</p>
        <button @click="showAddModal = true" class="add-product-button">
          <i class="fas fa-plus"></i> 상품 추가하기
        </button>
      </div>
    </div>

    <!-- Add Product Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click="showAddModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>비교할 상품 추가</h3>
          <button @click="showAddModal = false" class="close-button">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="modal-body">
          <ProductFilterBar
            @filter-change="handleFilterChange"
            @sort-change="handleSortChange"
            @search="handleSearch"
          />

          <div v-if="modalLoading" class="modal-loading">
            <div class="loading-spinner"></div>
            <p>상품을 불러오는 중...</p>
          </div>

          <div v-else-if="modalError" class="modal-error">
            <p>{{ modalError }}</p>
          </div>

          <div v-else-if="availableProducts.length === 0" class="modal-empty">
            <p>검색 결과가 없습니다.</p>
          </div>

          <div v-else class="product-grid">
            <div
              v-for="product in availableProducts"
              :key="product.id"
              class="product-card"
              @click="addProductToCompare(product)"
              :class="{ 'already-added': isProductInCompareList(product.id) }"
            >
              <div class="product-card-header">
                <BankLogo :bankName="product.kor_co_nm" :size="30" />
                <span class="product-type-badge">{{ getProductTypeName(product) }}</span>
              </div>
              <h3 class="product-name">{{ product.fin_prdt_nm }}</h3>
              <div class="product-bank">{{ product.kor_co_nm }}</div>
              <div class="product-rate">
                <template v-if="isDepositOrSaving(product)">
                  <span>최고금리: {{ formatRate(product.max_rate || product.intr_rate2) }}%</span>
                </template>
                <template v-else-if="isLoan(product)">
                  <span>최저금리: {{ formatRate(product.min_rate || product.intr_rate) }}%</span>
                </template>
              </div>
              <div v-if="isProductInCompareList(product.id)" class="already-added-badge">
                추가됨
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import productsService from '@/services/products'
import ProductComparison from '@/components/products/ProductComparison.vue'
import ProductFilterBar from '@/components/products/ProductFilterBar.vue'

export default {
  name: 'ProductComparisonView',
  components: {
    ProductComparison,
    ProductFilterBar,
  },
  setup() {
    const router = useRouter()

    // Main comparison state
    const compareList = ref([])
    const loading = ref(false)
    const error = ref(null)
    const favorites = ref([])

    // Modal state
    const showAddModal = ref(false)
    const availableProducts = ref([])
    const modalLoading = ref(false)
    const modalError = ref(null)
    const activeTab = ref('all')
    const searchQuery = ref('')
    const sortBy = ref('name')

    // Load user favorites
    const loadUserFavorites = async () => {
      try {
        const response = await productsService.getUserFavorites()
        favorites.value = response
      } catch (err) {
        console.error('Error loading favorites:', err)
      }
    }

    // Toggle product as favorite
    const toggleFavorite = async (product) => {
      try {
        if (isProductInFavorites(product.id)) {
          await productsService.removeFromFavorites(product.id)
          // Remove from local list
          favorites.value = favorites.value.filter(
            (fav) =>
              fav.product_id !== product.id && (!fav.product || fav.product.id !== product.id),
          )
        } else {
          console.log(product.id)
          await productsService.addToFavorites(product.id)
          // Wait for backend to process, then refresh the list
          await loadUserFavorites()
        }
      } catch (err) {
        console.error('Error toggling favorite:', err)
      }
    }

    // Check if a product is in favorites
    const isProductInFavorites = (productId) => {
      return favorites.value.some(
        (fav) => fav.product_id === productId || (fav.product && fav.product.id === productId),
      )
    }

    // Load available products for the modal
    const loadAvailableProducts = async () => {
      modalLoading.value = true
      modalError.value = null

      try {
        let response

        // Apply filters based on product type
        switch (activeTab.value) {
          case 'deposit':
            response = await productsService.getDepositProducts({
              query: searchQuery.value,
              sort: sortBy.value,
            })
            break
          case 'saving':
            response = await productsService.getSavingProducts({
              query: searchQuery.value,
              sort: sortBy.value,
            })
            break
          case 'loan':
            response = await productsService.getLoanProducts({
              query: searchQuery.value,
              sort: sortBy.value,
            })
            break
          default:
            response = await productsService.getAllProducts({
              query: searchQuery.value,
              sort: sortBy.value,
            })
            break
        }

        availableProducts.value = response
      } catch (err) {
        console.error('Error loading products:', err)
        modalError.value = '상품을 불러오는데 실패했습니다. 다시 시도해주세요.'
      } finally {
        modalLoading.value = false
      }
    }

    // Filter handlers
    const handleFilterChange = (type) => {
      activeTab.value = type
      loadAvailableProducts()
    }

    const handleSortChange = (sort) => {
      sortBy.value = sort
      loadAvailableProducts()
    }

    const handleSearch = (query) => {
      searchQuery.value = query
      loadAvailableProducts()
    }

    // Add product to compare list
    const addProductToCompare = (product) => {
      if (compareList.value.length >= 4) {
        alert('최대 4개까지 비교할 수 있습니다.')
        return
      }

      if (isProductInCompareList(product.id)) {
        alert('이미 추가된 상품입니다.')
        return
      }

      compareList.value.push(product)
    }

    // Remove product from compare list
    const removeProductFromCompare = (index) => {
      compareList.value.splice(index, 1)
    }

    // Check if product is already in compare list
    const isProductInCompareList = (productId) => {
      return compareList.value.some((product) => product.id === productId)
    }

    // Navigate to product details
    const viewProductDetails = (product) => {
      router.push({
        name: 'ProductDetail',
        params: { id: product.id },
        query: { type: product.product_type || getTypeFromCategory(product) },
      })
    }

    // Go back to products list
    const goBack = () => {
      router.push({ name: 'Products' })
    }

    // Helper functions
    const getProductTypeName = (product) => {
      const type = product.product_type || getTypeFromCategory(product)

      switch (type) {
        case 'deposit':
          return '예금'
        case 'saving':
          return '적금'
        case 'loan':
          return '대출'
        default:
          return '금융상품'
      }
    }

    const getTypeFromCategory = (product) => {
      if (product.fin_prdt_cd && product.fin_prdt_cd.startsWith('DW')) return 'deposit'
      if (product.fin_prdt_cd && product.fin_prdt_cd.startsWith('SW')) return 'saving'
      if (product.loan_type) return 'loan'
      return 'unknown'
    }

    const isDepositOrSaving = (product) => {
      const type = product.product_type || getTypeFromCategory(product)
      return type === 'deposit' || type === 'saving'
    }

    const isLoan = (product) => {
      const type = product.product_type || getTypeFromCategory(product)
      return type === 'loan'
    }

    const formatRate = (rate) => {
      if (!rate) return '0.00'
      return parseFloat(rate).toFixed(2)
    }

    // Load data on component mount
    onMounted(() => {
      loadUserFavorites()
    })

    return {
      compareList,
      loading,
      error,
      favorites,
      showAddModal,
      availableProducts,
      modalLoading,
      modalError,
      activeTab,
      searchQuery,
      sortBy,
      loadUserFavorites,
      toggleFavorite,
      isProductInFavorites,
      loadAvailableProducts,
      handleFilterChange,
      handleSortChange,
      handleSearch,
      addProductToCompare,
      removeProductFromCompare,
      isProductInCompareList,
      viewProductDetails,
      goBack,
      getProductTypeName,
      getTypeFromCategory,
      isDepositOrSaving,
      isLoan,
      formatRate,
    }
  },
}
</script>

<style scoped>
.comparison-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  color: #4b5563;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
}

.back-button:hover {
  background: #e5e7eb;
}

.comparison-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.comparison-info {
  color: #4b5563;
  font-size: 0.95rem;
}

.comparison-info i {
  color: #3b82f6;
  margin-right: 0.5rem;
}

.add-product-button {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.add-product-button:hover {
  background: #2563eb;
}

.empty-comparison {
  text-align: center;
  padding: 4rem 2rem;
  background: #f9fafb;
  border-radius: 10px;
  color: #6b7280;
}

.empty-comparison p {
  margin-bottom: 1.5rem;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #111827;
}

.close-button {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.25rem;
}

.close-button:hover {
  color: #111827;
}

.modal-body {
  padding: 1.5rem;
}

.modal-loading,
.modal-error,
.modal-empty {
  text-align: center;
  padding: 3rem 0;
}

.loading-spinner {
  display: inline-block;
  width: 40px;
  height: 40px;
  border: 4px solid rgba(75, 85, 99, 0.1);
  border-radius: 50%;
  border-top-color: #3b82f6;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.product-card {
  position: relative;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.product-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.product-card.already-added {
  opacity: 0.7;
  cursor: not-allowed;
}

.product-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.product-type-badge {
  font-size: 0.7rem;
  padding: 0.2rem 0.4rem;
  background: #e0f2fe;
  color: #0369a1;
  border-radius: 4px;
}

.product-name {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  color: #111827;
}

.product-bank {
  font-size: 0.85rem;
  color: #6b7280;
  margin-bottom: 0.75rem;
}

.product-rate {
  font-size: 0.9rem;
  color: #4b5563;
  background: #f9fafb;
  padding: 0.5rem;
  border-radius: 4px;
  text-align: center;
}

.already-added-badge {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  font-weight: 500;
  border-radius: 8px;
}
</style>

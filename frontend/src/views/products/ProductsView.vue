<template>
  <div class="products-container">
    <h1 class="products-title">금융 상품 목록</h1>

    <ProductFilterBar
      :initialProductType="activeTab"
      :initialSortOption="sortBy"
      :initialSearchQuery="searchQuery"
      @filter="handleFilterChange"
      @sort="handleSortChange"
      @search="handleSearch"
    />

    <div v-if="loading" class="loading-indicator">
      <p>상품을 불러오는 중...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>

    <div v-else-if="filteredProducts.length === 0" class="no-products">
      <p>조건에 맞는 상품이 없습니다.</p>
    </div>
    <div v-else>
      <div class="products-grid">
        <ProductCard
          v-for="product in paginatedProducts"
          :key="product.fin_prdt_cd || product.id"
          :product="{
            ...product,
            id: product.fin_prdt_cd || product.id,
            type: product.product_type || getTypeFromCategory(product),
            product_type: product.product_type || getTypeFromCategory(product),
            mortgage_options:
              product.mortgage_options ||
              (product.product_info && product.product_info.mortgage_options) ||
              [],
            credit_options:
              product.credit_options ||
              (product.product_info && product.product_info.credit_options) ||
              [],
          }"
          :isFavorite="isProductInFavorites(product.fin_prdt_cd || product.id)"
          @toggle-favorite="toggleFavorite(product)"
          @view-details="viewProductDetails"
        />
      </div>

      <!-- Pagination Controls -->
      <Pagination
        v-if="totalPages > 1"
        :currentPage="currentPage"
        :totalPages="totalPages"
        :totalItems="totalItems"
        :itemsPerPage="itemsPerPage"
        @page-change="goToPage"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import productsService from '@/services/products'
import ProductCard from '@/components/products/ProductCard.vue'
import ProductFilterBar from '@/components/products/ProductFilterBar.vue'
import Pagination from '@/components/common/Pagination.vue'

export default {
  name: 'ProductsView',
  components: {
    ProductCard,
    ProductFilterBar,
    Pagination,
  },
  setup() {
    const router = useRouter()

    // Data state
    const allProducts = ref([])
    const products = ref([])
    const favorites = ref([])
    const loading = ref(true)
    const error = ref(null)

    // Pagination state
    const currentPage = ref(1)
    const itemsPerPage = ref(12) // Show 12 products per page
    const totalItems = ref(0)
    const totalPages = ref(1)

    // Filter state
    const activeTab = ref('all')
    const searchQuery = ref('')
    const sortBy = ref('name') // Computed properties for pagination
    const filteredProducts = computed(() => {
      return products.value
    })

    const paginatedProducts = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      const end = start + itemsPerPage.value
      return filteredProducts.value.slice(start, end)
    })

    // Load products based on filters
    const loadProducts = async () => {
      loading.value = true
      error.value = null
      // Reset to first page when filters change
      currentPage.value = 1

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
        } // Make sure to include mortgage and credit options
        allProducts.value = response
        products.value = response.map((product) => {
          return product
        })
        totalItems.value = response.length
        totalPages.value = Math.ceil(totalItems.value / itemsPerPage.value)

        // Load user favorites
        await loadUserFavorites()
      } catch (err) {
        console.error('Error loading products:', err)
        error.value = '상품을 불러오는데 실패했습니다. 다시 시도해주세요.'
      } finally {
        loading.value = false
      }
    }

    // Go to a specific page
    const goToPage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        // Scroll to top of product list
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }

    // Load user's favorite products
    const loadUserFavorites = async () => {
      try {
        const response = await productsService.getUserFavorites()
        favorites.value = response
      } catch (err) {
        console.error('Error loading favorites:', err)
      }
    } // Toggle product as favorite
    const toggleFavorite = async (product) => {
      try {
        // Always prefer fin_prdt_cd as it's what the backend expects
        const productId = product.fin_prdt_cd
        if (!productId) {
          console.error('No fin_prdt_cd found:', product)
          return
        }

        if (isProductInFavorites(productId)) {
          await productsService.removeFromFavorites(productId)
          // Remove from local list
          favorites.value = favorites.value.filter((fav) => fav.product?.fin_prdt_cd !== productId)
        } else {
          console.log('Adding to favorites:', productId)
          await productsService.addToFavorites(productId)
          // Wait for the backend to process, then refresh the list
          await loadUserFavorites()
        }
      } catch (err) {
        console.error('Error toggling favorite:', err)
      }
    }

    // Check if a product is in favorites
    const isProductInFavorites = (productId) => {
      return favorites.value.some((fav) => fav.product?.fin_prdt_cd === productId)
    }

    // Helper function to determine product type
    const getTypeFromCategory = (product) => {
      if (product.fin_prdt_cd && product.fin_prdt_cd.startsWith('DW')) return 'deposit'
      if (product.fin_prdt_cd && product.fin_prdt_cd.startsWith('SW')) return 'saving'
      if (product.loan_type) return 'loan'
      return 'all'
    }

    // Set active tab/product type
    const handleFilterChange = (type) => {
      activeTab.value = type
      loadProducts()
    }

    // Set sort option
    const handleSortChange = (sort) => {
      sortBy.value = sort
      loadProducts()
    }

    // Set search query
    const handleSearch = (query) => {
      searchQuery.value = query
      loadProducts()
    }

    // Navigate to product details
    const viewProductDetails = (productInfo) => {
      router.push({
        name: 'ProductDetail',
        params: {
          id: productInfo.id || productInfo.fin_prdt_cd,
          type: productInfo.type || getTypeFromCategory(productInfo),
        },
      })
    }

    // Watch for changes that should trigger pagination recalculation
    watch([filteredProducts], () => {
      totalItems.value = filteredProducts.value.length
      totalPages.value = Math.ceil(totalItems.value / itemsPerPage.value)
      // Make sure current page is not out of bounds
      if (currentPage.value > totalPages.value) {
        currentPage.value = Math.max(1, totalPages.value)
      }
    }) // Initial data load
    onMounted(() => {
      loadProducts()
    })

    return {
      products,
      filteredProducts,
      paginatedProducts,
      favorites,
      loading,
      error,
      activeTab,
      searchQuery,
      sortBy,
      currentPage,
      itemsPerPage,
      totalItems,
      totalPages,
      toggleFavorite,
      isProductInFavorites,
      viewProductDetails,
      handleFilterChange,
      handleSortChange,
      handleSearch,
      getTypeFromCategory,
      goToPage,
    }
  },
}
</script>

<style scoped>
.products-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
  background: linear-gradient(135deg, var(--color-background-start) 0%, var(--color-background-end) 100%);
  min-height: calc(100vh - 160px);
}

.products-title {
  text-align: center;
  margin-bottom: 2.5rem;
  font-family: var(--font-heading);
  font-size: var(--font-size-3xl);
  color: var(--color-accent);
  position: relative;
  display: inline-block;
  width: 100%;
}

.products-title::after {
  content: '';
  position: absolute;
  bottom: -12px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 3px;
  background: linear-gradient(to right, var(--color-primary), var(--color-primary-dark));
  border-radius: 3px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
  position: relative;
  z-index: 1;
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 0;
  color: var(--color-text);
  font-family: var(--font-body);
}

.loading-indicator::before {
  content: '';
  display: inline-block;
  width: 50px;
  height: 50px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: var(--color-primary);
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 1.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  text-align: center;
  padding: 3rem;
  color: var(--color-error);
  background-color: rgba(214, 48, 49, 0.05);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  font-family: var(--font-body);
}

.error-message p {
  position: relative;
  padding-left: 2rem;
}

.error-message p::before {
  content: '⚠️';
  position: absolute;
  left: 0;
  font-size: 1.2rem;
}

.no-products {
  padding: 6rem 2rem;
  background: var(--color-card-background);
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  text-align: center;
  color: var(--color-text-light);
  font-family: var(--font-body);
  font-size: var(--font-size-lg);
  position: relative;
}

.no-products::before {
  content: '🔍';
  display: block;
  font-size: 3rem;
  margin-bottom: 1rem;
}

.no-products p {
  max-width: 600px;
  margin: 0 auto;
}

/* Pagination styles */
.pagination-container {
  margin-top: 3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.2rem;
  padding-bottom: 2rem;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: var(--color-card-background);
  padding: 0.8rem 1.2rem;
  border-radius: 50px;
  box-shadow: var(--shadow-md);
}

.page-numbers {
  display: flex;
  gap: 0.6rem;
}

.page-number {
  min-width: 2.8rem;
  height: 2.8rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-base);
  font-family: var(--font-body);
  font-weight: 500;
  background: var(--color-card-background);
  border: 1px solid var(--color-secondary);
  color: var(--color-text);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.page-number:hover {
  background: var(--color-secondary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.page-number.active {
  background: var(--color-primary);
  color: var(--color-white);
  border-color: var(--color-primary);
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.pagination-button {
  padding: 0.7rem 1.2rem;
  border-radius: 50px;
  background: var(--color-card-background);
  border: 1px solid var(--color-secondary);
  color: var(--color-text);
  font-family: var(--font-body);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-normal);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-button:hover:not(:disabled) {
  background: var(--color-secondary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.pagination-button:active:not(:disabled) {
  transform: translateY(-1px);
}

.pagination-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.page-info {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
  font-family: var(--font-body);
  background: var(--color-card-background);
  padding: 0.6rem 1.2rem;
  border-radius: 20px;
  box-shadow: var(--shadow-sm);
}

/* 다크 모드 스타일 */
:global(.dark-mode) .products-container {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
}

:global(.dark-mode) .pagination, 
:global(.dark-mode) .page-info, 
:global(.dark-mode) .no-products {
  background-color: #2D2D2D;
}

:global(.dark-mode) .page-number {
  background-color: #333333;
  border-color: #444444;
  color: #e0e0e0;
}

:global(.dark-mode) .page-number:hover {
  background-color: #3D3D3D;
}

:global(.dark-mode) .pagination-button {
  background-color: #333333;
  border-color: #444444;
  color: #e0e0e0;
}

:global(.dark-mode) .pagination-button:hover:not(:disabled) {
  background-color: #3D3D3D;
}

/* 반응형 스타일 */
@media (max-width: 1024px) {
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }
}

@media (max-width: 768px) {
  .products-container {
    padding: 2rem 1rem;
  }
  
  .products-title {
    font-size: var(--font-size-2xl);
    margin-bottom: 2rem;
  }
  
  .products-grid {
    grid-template-columns: 1fr;
    gap: 1.2rem;
  }

  .pagination {
    flex-direction: column;
    gap: 0.8rem;
    padding: 1rem;
    border-radius: 12px;
  }
  
  .page-number {
    min-width: 2.4rem;
    height: 2.4rem;
  }
}
</style>

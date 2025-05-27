<template>
  <div class="products-container">
    <h1 class="products-title">금융 상품 목록</h1>

    <div class="ai-recommendation-banner">
      <div class="banner-content">
        <div class="banner-icon">
          <i class="bi bi-robot"></i>
        </div>
        <div class="banner-text">
          <h3>AI 맞춤 금융상품 추천</h3>
          <p>AI가 당신의 재정 상황에 맞는 최적의 금융상품을 추천해 드립니다.</p>
        </div>
        <router-link to="/products/ai-recommendations" class="banner-button">
          맞춤 추천 받기
        </router-link>
      </div>
    </div>

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
            ...(product.financial_product || product.product_info || product),
            ...product,
            type: activeTab,
            product_type: activeTab,
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
      // // Filter products based on active tab and search query
      // let result = products.value

      // if (activeTab.value !== 'all') {
      //   // Filter by product type
      //   result = result.filter((product) => {
      //     const type =
      //       product.product_type ||
      //       (product.category === '예금'
      //         ? 'deposit'
      //         : product.category === '적금'
      //           ? 'saving'
      //           : product.category === '대출'
      //             ? 'loan'
      //             : null)
      //     return type === activeTab.value
      //   })
      // }

      // // Filter by search query if provided
      // if (searchQuery.value) {
      //   const query = searchQuery.value.toLowerCase()
      //   result = result.filter((product) => {
      //     const name = (product.fin_prdt_nm || '').toLowerCase()
      //     const bank = (product.kor_co_nm || '').toLowerCase()
      //     return name.includes(query) || bank.includes(query)
      //   })
      // }

      // return result
      return products.value
    })

    const paginatedProducts = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      const end = start + itemsPerPage.value
      const slicedProducts = filteredProducts.value.slice(start, end)
      return slicedProducts
    })

    // Load products based on filters
    const loadProducts = async () => {
      const currentActiveTab = activeTab.value
      console.log(
        `[ProductsView] loadProducts: Tab='${currentActiveTab}', Sort='${sortBy.value}', Query='${searchQuery.value}'`,
      )
      loading.value = true
      error.value = null
      currentPage.value = 1

      try {
        let response
        let serviceMethod
        let orderingValue = sortBy.value // 기본값

        // Determine orderingValue based on activeTab and sortBy
        if (currentActiveTab === 'deposit' || currentActiveTab === 'saving') {
          switch (sortBy.value) {
            case 'name':
              orderingValue = 'product__fin_prdt_nm'
              break
            case 'rate-desc':
              orderingValue = '-intr_rate2'
              break
            case 'rate-asc':
              orderingValue = 'intr_rate2'
              break
            case 'bank':
              orderingValue = 'product__kor_co_nm'
              break
            default:
              orderingValue = sortBy.value
              break
          }
        } else if (currentActiveTab === 'loan') {
          switch (sortBy.value) {
            case 'name':
              orderingValue = 'product__fin_prdt_nm'
              break
            case 'bank':
              orderingValue = 'product__kor_co_nm'
              break
            case 'rate-desc':
            case 'rate-asc':
              console.warn(
                `[ProductsView] Loan products rate sorting ('${sortBy.value}') is not yet supported by the backend. Defaulting to name sort.`,
              )
              orderingValue = 'product__fin_prdt_nm'
              break
            default:
              orderingValue = sortBy.value
              break
          }
        } else {
          // 'all'
          switch (sortBy.value) {
            case 'name':
              orderingValue = 'fin_prdt_nm'
              break
            case 'bank':
              orderingValue = 'kor_co_nm'
              break
            case 'rate-desc':
            case 'rate-asc':
              console.warn(
                `[ProductsView] Sorting by rate on 'all' products tab is complex. The ordering value '${sortBy.value}' will be passed to sub-APIs.`,
              )
              orderingValue = sortBy.value
              break
            default:
              orderingValue = sortBy.value
              break
          }
        }

        const params = { query: searchQuery.value, ordering: orderingValue }
        console.log(`[ProductsView] API call params for ${currentActiveTab}:`, params)

        switch (currentActiveTab) {
          case 'deposit':
            serviceMethod = productsService.getDepositProducts
            response = await serviceMethod(params)
            break
          case 'saving':
            serviceMethod = productsService.getSavingProducts
            response = await serviceMethod(params)
            break
          case 'loan':
            serviceMethod = productsService.getLoanProducts
            response = await serviceMethod(params)
            break
          default: // 'all'
            serviceMethod = productsService.getAllProducts
            response = await serviceMethod(params)
            break
        }

        if (!response || !Array.isArray(response)) {
          console.error(
            `[ProductsView] API response for ${currentActiveTab} is not a valid array or is undefined/null.`,
            response,
          )
          allProducts.value = []
          products.value = []
          error.value = `상품 데이터(${currentActiveTab})를 가져오는데 문제가 발생했습니다 (응답 형식 오류).`
        } else {
          allProducts.value = response
          products.value = response.map((product) => product)
          console.log(
            `[ProductsView] Products loaded for ${currentActiveTab}. Count: ${products.value.length}`,
          )
        }

        totalItems.value = products.value.length
        totalPages.value = Math.ceil(totalItems.value / itemsPerPage.value)

        await loadUserFavorites()
      } catch (err) {
        console.error(`[ProductsView] Error loading products for tab '${currentActiveTab}':`, err)
        error.value = `상품 (${currentActiveTab})을 불러오는데 실패했습니다: ${err.message}.`
        products.value = []
        allProducts.value = []
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
  padding: var(--spacing-xl, 2rem);
  max-width: 1200px;
  margin: 0 auto;
}

.products-title {
  font-size: var(--font-size-xxl, 2.5rem);
  color: var(--text-primary); /* Ensure text color is set by theme */
  text-align: center;
  margin-bottom: var(--spacing-xl, 2rem);
  font-weight: 700;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.loading-indicator,
.error-message,
.no-products {
  text-align: center;
  padding: 3rem 0;
  color: #555;
}

.error-message {
  color: #d32f2f;
}

.no-products {
  padding: 5rem 0;
  background: #f9f9fa;
  border-radius: 8px;
}

/* Pagination styles */
.pagination-container {
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding-bottom: 2rem;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.page-numbers {
  display: flex;
  gap: 0.5rem;
}

.page-number {
  min-width: 2.5rem;
  height: 2.5rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s;
}

.page-number:hover {
  background: #f3f4f6;
}

.page-number.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.pagination-button {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  background: white;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background: #f3f4f6;
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.9rem;
  color: #6b7280;
}

.ai-recommendation-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 2rem;
  box-shadow:
    0 10px 15px -3px rgba(0, 0, 0, 0.1),
    0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.banner-content {
  display: flex;
  align-items: center;
  color: white;
  padding: 1rem;
}

.banner-icon {
  font-size: 2.5rem;
  margin-right: 1.5rem;
  background: rgba(255, 255, 255, 0.2);
  width: 70px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  flex-shrink: 0;
}

.banner-text {
  flex-grow: 1;
}

.banner-text h3 {
  font-size: 1.5rem;
  margin: 0 0 0.5rem 0;
  font-weight: 700;
}

.banner-text p {
  margin: 0;
  opacity: 0.9;
  font-size: 1rem;
}

.banner-button {
  background-color: white;
  color: #764ba2;
  font-weight: bold;
  padding: 0.75rem 1.5rem;
  border-radius: 9999px;
  text-decoration: none;
  transition: all 0.2s;
  white-space: nowrap;
  margin-left: 1.5rem;
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.banner-button:hover {
  transform: translateY(-2px);
  box-shadow:
    0 10px 15px -3px rgba(0, 0, 0, 0.1),
    0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: 1fr;
  }

  .pagination {
    flex-direction: column;
    gap: 0.5rem;
  }

  .banner-content {
    flex-direction: column;
    text-align: center;
  }

  .banner-icon {
    margin-right: 0;
    margin-bottom: 1rem;
  }

  .banner-button {
    margin-left: 0;
    margin-top: 1.5rem;
  }
}
</style>

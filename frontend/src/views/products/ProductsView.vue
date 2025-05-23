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
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.products-title {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
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

@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: 1fr;
  }

  .pagination {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>

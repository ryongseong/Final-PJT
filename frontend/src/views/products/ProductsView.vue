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

    <div v-else-if="products.length === 0" class="no-products">
      <p>조건에 맞는 상품이 없습니다.</p>
    </div>    <div v-else class="products-grid">
      <ProductCard
        v-for="product in products"
        :key="product.fin_prdt_cd || product.id"
        :product="{
          ...product,
          id: product.fin_prdt_cd || product.id,
          type: product.product_type || getTypeFromCategory(product),
          product_type: product.product_type || getTypeFromCategory(product)
        }"
        :isFavorite="isProductInFavorites(product.fin_prdt_cd || product.id)"
        @toggle-favorite="toggleFavorite(product)"
        @view-details="viewProductDetails"
      />
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import productsService from '@/services/products'
import ProductCard from '@/components/products/ProductCard.vue'
import ProductFilterBar from '@/components/products/ProductFilterBar.vue'

export default {
  name: 'ProductsView',
  components: {
    ProductCard,
    ProductFilterBar,
  },
  setup() {
    const router = useRouter()

    const products = ref([])
    const favorites = ref([])
    const loading = ref(true)
    const error = ref(null)

    const activeTab = ref('all')
    const searchQuery = ref('')
    const sortBy = ref('name')

    // Load products based on filters
    const loadProducts = async () => {
      loading.value = true
      error.value = null

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

        products.value = response

        // Load user favorites
        await loadUserFavorites()
      } catch (err) {
        console.error('Error loading products:', err)
        error.value = '상품을 불러오는데 실패했습니다. 다시 시도해주세요.'
      } finally {
        loading.value = false
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
    }    // Toggle product as favorite
    const toggleFavorite = async (product) => {
      try {
        // Always prefer fin_prdt_cd as it's what the backend expects
        const productId = product.fin_prdt_cd;
        if (!productId) {
          console.error('No fin_prdt_cd found:', product);
          return;
        }

        if (isProductInFavorites(productId)) {
          await productsService.removeFromFavorites(productId);
          // Remove from local list
          favorites.value = favorites.value.filter((fav) => 
            fav.product?.fin_prdt_cd !== productId
          );
        } else {
          console.log('Adding to favorites:', productId);
          await productsService.addToFavorites(productId);
          // Wait for the backend to process, then refresh the list
          await loadUserFavorites();
        }
      } catch (err) {
        console.error('Error toggling favorite:', err);
      }
    };

    // Check if a product is in favorites
    const isProductInFavorites = (productId) => {
      return favorites.value.some((fav) => 
        fav.product?.fin_prdt_cd === productId
      );
    };

    // Helper function to determine product type
    const getTypeFromCategory = (product) => {
      if (product.fin_prdt_cd && product.fin_prdt_cd.startsWith('DW')) return 'deposit';
      if (product.fin_prdt_cd && product.fin_prdt_cd.startsWith('SW')) return 'saving';
      if (product.loan_type) return 'loan';
      return 'all';
    };

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
    }    // Navigate to product details
    const viewProductDetails = (productInfo) => {
      router.push({
        name: 'ProductDetail',
        params: {
          id: productInfo.id || productInfo.fin_prdt_cd,
          type: productInfo.type || getTypeFromCategory(productInfo),
        },
      })
    }

    // Initial data load
    onMounted(() => {
      loadProducts()
    })

    return {
      products,
      favorites,
      loading,
      error,
      activeTab,
      searchQuery,
      sortBy,
      toggleFavorite,
      isProductInFavorites,
      viewProductDetails,
      handleFilterChange,
      handleSortChange,
      handleSearch,
      getTypeFromCategory,
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

@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: 1fr;
  }
}
</style>

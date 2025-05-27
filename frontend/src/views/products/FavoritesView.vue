<template>
  <div class="favorites-container">
    <h1 class="favorites-title">즐겨찾기한 상품</h1>

    <div v-if="loading" class="loading-indicator">
      <p>즐겨찾기 목록을 불러오는 중...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>

    <div v-else-if="favorites.length === 0" class="no-favorites">
      <p>아직 즐겨찾기한 상품이 없습니다.</p>
      <button @click="goToProducts" class="browse-btn">상품 둘러보기</button>
    </div>

    <div v-else class="favorites-grid">
      <ProductCard
        v-for="favorite in favorites"
        :key="favorite.financial_product.fin_prdt_cd"
        :product="{
          ...favorite,
          id: favorite.id,
          type: favorite.product_type || getTypeFromCategory(favorite),
          product_type: favorite.product_type || getTypeFromCategory(favorite),
        }"
        :isFavorite="true"
        :showFavoriteDate="true"
        :favoriteDate="favorite.created_at"
        :showRemoveButton="true"
        @remove="removeFromFavorites(favorite)"
        @view-details="viewProductDetails(favorite)"
      />
    </div>
  </div>
</template>

<script>
import productsService from '@/services/products'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ProductCard from '@/components/products/ProductCard.vue'

export default {
  name: 'FavoritesView',
  components: {
    ProductCard,
  },
  setup() {
    const router = useRouter()

    const favorites = ref([])
    const loading = ref(true)
    const error = ref(null)

    // Load user favorites
    const loadFavorites = async () => {
      loading.value = true
      error.value = null

      try {
        const response = await productsService.getUserFavorites()
        favorites.value = response
        console.log('Loaded favorites:', favorites.value)
      } catch (err) {
        console.error('Error loading favorites:', err)
        error.value = '즐겨찾기 목록을 불러오는데 실패했습니다. 다시 시도해주세요.'
      } finally {
        loading.value = false
      }
    }

    // Remove a product from favorites
    const removeFromFavorites = async (favorite) => {
      try {
        const productId = favorite.financial_product.fin_prdt_cd
        if (!productId) {
          console.error('No product ID found:', favorite)
          return
        }

        await productsService.removeFromFavorites(productId)
        // Remove from local list
        favorites.value = favorites.value.filter((item) => item.id !== favorite.id)
      } catch (err) {
        console.error('Error removing from favorites:', err)
      }
    }

    // Navigate to product details
    const viewProductDetails = (product) => {
      console.log('Viewing product details:', product)
      const productTypeNew = getTypeFromCategory(product)
      router.push({
        name: 'ProductDetail',
        params: { id: product.product, type: productTypeNew || product.product_type },
      })
    }

    // Navigate to products page
    const goToProducts = () => {
      router.push({ name: 'Products' })
    }

    const getTypeFromCategory = (product) => {
      if (
        product.financial_product.fin_prdt_cd &&
        product.financial_product.fin_prdt_cd.startsWith('DW')
      )
        return 'deposit'
      if (
        product.financial_product.fin_prdt_cd &&
        product.financial_product.fin_prdt_cd.startsWith('SW')
      )
        return 'saving'
      if (product.financial_product.loan_type) return 'loan'
      return 'all'
    }

    // Format date for display
    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    }

    onMounted(() => {
      loadFavorites()
    })

    return {
      favorites,
      loading,
      error,
      removeFromFavorites,
      viewProductDetails,
      goToProducts,
      formatDate,
      getTypeFromCategory,
    }
  },
}
</script>

<style scoped>
.favorites-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
  background-color: var(--card-bg);
  border-radius: var(--border-radius-lg, 8px);
  box-shadow: var(--card-shadow, 0 2px 10px rgba(0, 0, 0, 0.05));
  color: var(--text-primary);
}

.favorites-title {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--text-primary);
}

#app.dark .favorites-title {
  color: #ffffff !important;
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.loading-indicator p,
.error-message p,
.no-favorites p {
  color: var(--text-secondary);
}

.error-message {
  color: #d32f2f;
}

.no-favorites {
  text-align: center;
  padding: 5rem 0;
  background: var(--card-bg);
  border-radius: 8px;
}

.browse-btn {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.6rem 1.2rem;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.browse-btn:hover {
  background: #1565c0;
}

@media (max-width: 768px) {
  .favorites-grid {
    grid-template-columns: 1fr;
  }
}
</style>

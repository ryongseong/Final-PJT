<template>
  <div class="product-recommendations">
    <h2 class="section-title">맞춤 추천 상품</h2>
    
    <div v-if="loading" class="loading-indicator">
      <p>추천 상품을 불러오는 중...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="!recommendations || (recommendations && isRecommendationsEmpty)" class="no-recommendations">
      <p>{{ message || '추천 상품이 없습니다.' }}</p>
      <p class="suggestion">관심 상품을 추가하면 더 정확한 추천을 받을 수 있습니다.</p>
    </div>
    
    <div v-else>
      <div v-if="message" class="recommendation-message">
        <p>{{ message }}</p>
      </div>
      
      <div v-if="favoriteInstitutions && favoriteInstitutions.length > 0" class="favorite-institutions">
        <h3>자주 이용하시는 금융기관</h3>
        <div class="institution-badges">
          <span 
            v-for="institution in favoriteInstitutions" 
            :key="institution" 
            class="institution-badge"
          >
            {{ institution }}
          </span>
        </div>
      </div>
      
      <div v-if="recommendations.deposits && recommendations.deposits.length > 0" class="product-section">
        <h3>추천 예금 상품</h3>
        <div class="products-slider">
          <ProductCard
            v-for="product in recommendations.deposits"
            :key="product.fin_prdt_cd"
            :product="{
              ...product.financial_product || product.product_info || product,
              ...product,
              type: 'deposit',
              product_type: 'deposit'
            }"
          />
        </div>
      </div>
      
      <div v-if="recommendations.savings && recommendations.savings.length > 0" class="product-section">
        <h3>추천 적금 상품</h3>
        <div class="products-slider">
          <ProductCard
            v-for="product in recommendations.savings"
            :key="product.fin_prdt_cd"
            :product="{
              ...product.financial_product || product.product_info || product,
              ...product,
              type: 'saving',
              product_type: 'saving'
            }"
          />
        </div>
      </div>
      
      <div v-if="recommendations.loans && recommendations.loans.length > 0" class="product-section">
        <h3>추천 대출 상품</h3>
        <div class="products-slider">
          <ProductCard
            v-for="product in recommendations.loans"
            :key="product.fin_prdt_cd"
            :product="{
              ...product.financial_product || product.product_info || product,
              ...product,
              type: 'loan',
              product_type: 'loan'
            }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import productsService from '@/services/products'
import ProductCard from '@/components/products/ProductCard.vue'

export default {
  name: 'ProductRecommendations',
  components: {
    ProductCard
  },
  setup() {
    const userStore = useUserStore()
    const recommendations = ref(null)
    const message = ref('')
    const favoriteInstitutions = ref([])
    const loading = ref(false)
    const error = ref(null)
    
    const isRecommendationsEmpty = computed(() => {
      if (!recommendations.value) return true
      
      const hasSavings = recommendations.value.savings && recommendations.value.savings.length > 0
      const hasDeposits = recommendations.value.deposits && recommendations.value.deposits.length > 0
      const hasLoans = recommendations.value.loans && recommendations.value.loans.length > 0
      
      return !hasSavings && !hasDeposits && !hasLoans
    })
    
    const loadRecommendations = async () => {
      if (!userStore.isLoggedIn) {
        message.value = '로그인 후 맞춤 상품을 추천받을 수 있습니다.'
        return
      }
      
      loading.value = true
      error.value = null
      
      try {
        const response = await productsService.getRecommendations()
        
        recommendations.value = response.recommendations || {}
        message.value = response.message || ''
        favoriteInstitutions.value = response.favorite_institutions || []
      } catch (err) {
        console.error('Failed to load recommendations:', err)
        error.value = '추천 상품을 불러오는데 실패했습니다.'
      } finally {
        loading.value = false
      }
    }
    
    onMounted(loadRecommendations)
    
    return {
      recommendations,
      message,
      favoriteInstitutions,
      loading,
      error,
      isRecommendationsEmpty
    }
  }
}
</script>

<style scoped>
.product-recommendations {
  padding: 1.5rem;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
}

.loading-indicator, .error-message, .no-recommendations {
  padding: 2rem;
  text-align: center;
  color: #666;
}

.error-message {
  color: #e53935;
}

.products-slider {
  display: flex;
  overflow-x: auto;
  gap: 1rem;
  padding: 0.5rem 0;
  scroll-behavior: smooth;
}

.product-section {
  margin: 1.5rem 0;
}

.product-section h3 {
  font-size: 1.2rem;
  margin-bottom: 0.75rem;
  color: #444;
}

.recommendation-message {
  background-color: #e3f2fd;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.95rem;
  color: #0d47a1;
}

.favorite-institutions {
  margin: 1rem 0;
  padding: 0.75rem;
  background-color: #f0f0f0;
  border-radius: 6px;
}

.institution-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.institution-badge {
  background-color: #e0e0e0;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  display: inline-block;
}

.suggestion {
  font-style: italic;
  font-size: 0.9rem;
  color: #888;
  margin-top: 0.5rem;
}
</style>

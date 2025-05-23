<!-- src/views/HomeView.vue -->
<template>
  <div class="home-container">
    <section class="welcome-section">
      <div class="welcome-content">
        <h1>환영합니다!</h1>
        <p class="subtitle">당신의 금융 인생을 관리하는 가장 스마트한 방법</p>

        <div v-if="isLoggedIn" class="user-greeting">
          <p>{{ user.nickname || user.username }}님, 오늘도 좋은 하루 되세요!</p>
          <router-link to="/profile" class="cta-button secondary"> 프로필 관리 </router-link>
        </div>

        <div v-else class="auth-buttons">
          <router-link to="/login" class="cta-button"> 로그인 </router-link>
          <router-link to="/register" class="cta-button secondary"> 회원가입 </router-link>
        </div>
      </div>
    </section>

    <section class="top-products-section">
      <h2>추천 금융 상품</h2>

      <div class="tabs">
        <button :class="{ active: activeTab === 'deposit' }" @click="activeTab = 'deposit'">
          예금 상품
        </button>
        <button :class="{ active: activeTab === 'saving' }" @click="activeTab = 'saving'">
          적금 상품
        </button>
        <button :class="{ active: activeTab === 'loan' }" @click="activeTab = 'loan'">
          대출 상품
        </button>
      </div>

      <div v-if="topProductsLoading" class="loading-indicator">
        <p>상품 정보를 불러오는 중...</p>
      </div>

      <div v-else-if="topProductsError" class="error-message">
        <p>{{ topProductsError }}</p>
      </div>

      <div v-else class="products-slider">
        <div class="product-cards">
          <div
            v-for="product in topProducts"
            :key="product.product"
            class="product-card"
            @click="viewProductDetails(product)"
          >
            <div class="product-header">
              <h3>{{ product.fin_prdt_nm }}</h3>
              <span class="bank-name" v-if="activeTab === 'deposit' || activeTab === 'saving'">{{
                product.financial_product.fin_prdt_nm
              }}</span>
              <span class="bank-name" v-if="activeTab === 'loan'">{{
                product.product_info.fin_prdt_nm
              }}</span>
            </div>

            <div class="product-rate" v-if="activeTab === 'deposit' || activeTab === 'saving'">
              <div class="rate-value">{{ formatRate(product.intr_rate2) }}%</div>
              <div class="rate-label">최고 금리</div>
            </div>

            <div class="product-rate" v-if="activeTab === 'loan'">
              <div class="rate-value">
                {{ formatRate(product.lending_options[0].lend_rate_min) }}%
              </div>
              <div class="rate-label">최저 대출금리</div>
            </div>

            <div class="product-meta">
              <div class="join-methods">
                <span v-if="hasJoinWay(product, '인터넷')" class="join-badge">인터넷</span>
                <span v-if="hasJoinWay(product, '영업점')" class="join-badge">영업점</span>
                <span v-if="hasJoinWay(product, '스마트폰')" class="join-badge">스마트폰</span>
                <span v-if="hasJoinWay(product, '전화(텔레뱅킹)')" class="join-badge"
                  >전화(텔레뱅킹)</span
                >
                <span v-if="hasJoinWay(product, '모집인')" class="join-badge">모집인</span>
              </div>
            </div>

            <button class="view-details-btn">상세 정보 보기</button>
          </div>
        </div>

        <div class="view-all">
          <router-link :to="{ name: 'Products', query: { tab: activeTab } }" class="view-all-link">
            모든 {{ getTabName(activeTab) }} 상품 보기
          </router-link>
        </div>
      </div>
    </section>

    <section class="features-section">
      <h2>주요 기능</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">💰</div>
          <h3>지출 관리</h3>
          <p>일일 지출을 편리하게 기록하고 관리하세요</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <h3>분석 리포트</h3>
          <p>지출 패턴을 분석하여 효과적인 재정 관리를 도와드립니다</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🎯</div>
          <h3>저축 목표</h3>
          <p>목표를 설정하고 진행 상황을 추적하세요</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🔔</div>
          <h3>알림 서비스</h3>
          <p>중요한 금융 일정을 놓치지 않도록 알림을 받으세요</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import productsService from '@/services/products'

const userStore = useUserStore()
const router = useRouter()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const user = computed(() => userStore.user)

// Top products section
const activeTab = ref('deposit')
const topProducts = ref([])
const topProductsLoading = ref(false)
const topProductsError = ref(null)

// Load top products based on active tab
const loadTopProducts = async () => {
  topProductsLoading.value = true
  topProductsError.value = null

  try {
    const response = await productsService.getTopRateProducts(activeTab.value, 5)
    console.log('Top products loaded:', response)
    topProducts.value = response
  } catch (err) {
    console.error('Error loading top products:', err)
    topProductsError.value = '상품 정보를 불러오는데 실패했습니다.'
  } finally {
    topProductsLoading.value = false
  }
}

// Format interest rate for display
const formatRate = (rate) => {
  return parseFloat(rate).toFixed(2)
}

// Check if product has specific join way
const hasJoinWay = (product, code) => {
  if (!product) return false

  if (activeTab.value === 'loan') {
    if (product.join_way && Array.isArray(product.join_way)) {
      return product.join_way.includes(code)
    }

    if (product.product_info && product.product_info.join_way) {
      return product.product_info.join_way.includes(code)
    }

    if (product.join_ways && Array.isArray(product.join_ways)) {
      return product.join_ways.some((item) => item.join_way === code)
    }

    return false
  }

  if (!product.financial_product || !product.financial_product.join_way) return false
  return product.financial_product.join_way.includes(code)
}

// Get tab name for display
const getTabName = (tab) => {
  const names = {
    deposit: '예금',
    saving: '적금',
    loan: '대출',
  }
  return names[tab] || ''
}

// Navigate to product details
const viewProductDetails = (product) => {
  console.log('Navigating to product details:', product)
  router.push({
    name: 'ProductDetail',
    params: {
      type: activeTab.value,
      id: product.product || product.product_info.fin_prdt_cd,
    },
  })
}

// Watch for tab changes and reload products
const watchTabChange = () => {
  loadTopProducts()
}

onMounted(async () => {
  // Check auth status when the component mounts
  await userStore.checkAuth()

  // Load top products for initial tab
  loadTopProducts()
})

// Watch for tab changes
import { watch } from 'vue'
watch(activeTab, watchTabChange)
</script>

<style scoped>
.home-container {
  min-height: 100vh;
}

.welcome-section {
  background: linear-gradient(135deg, #4f46e5 0%, #7e3af2 100%);
  color: white;
  padding: 80px 20px;
  text-align: center;
}

.welcome-content {
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  font-size: 3rem;
  margin-bottom: 20px;
}

.subtitle {
  font-size: 1.5rem;
  margin-bottom: 40px;
  opacity: 0.9;
}

.user-greeting {
  margin: 40px 0;
  font-size: 1.2rem;
}

.auth-buttons,
.user-greeting {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 30px;
}

.cta-button {
  display: inline-block;
  padding: 15px 30px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  text-decoration: none;
  text-align: center;
  transition: all 0.3s ease;
  background-color: white;
  color: #4f46e5;
}

.cta-button.secondary {
  background-color: transparent;
  color: white;
  border: 2px solid white;
}

.cta-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.features-section {
  padding: 80px 20px;
  text-align: center;
  background-color: #f9fafb;
}

h2 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 50px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  background: white;
  border-radius: 8px;
  padding: 30px 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-10px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.feature-card h3 {
  margin: 0 0 15px;
  color: #333;
  font-size: 1.5rem;
}

.feature-card p {
  color: #666;
  margin: 0;
}

/* Top Products Section */
.top-products-section {
  padding: 80px 20px;
  text-align: center;
  background-color: white;
}

.tabs {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 30px;
}

.tabs button {
  padding: 10px 20px;
  border: 1px solid #e5e7eb;
  background: #f3f4f6;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tabs button.active {
  background: #4f46e5;
  color: white;
  border-color: #4f46e5;
}

.products-slider {
  max-width: 1200px;
  margin: 0 auto;
}

.product-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.product-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  text-align: left;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  cursor: pointer;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

.product-header {
  margin-bottom: 15px;
}

.product-header h3 {
  margin: 0 0 5px 0;
  font-size: 1.1rem;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bank-name {
  font-size: 0.9rem;
  color: #6b7280;
}

.product-rate {
  background: #f3f4f6;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 15px;
  text-align: center;
}

.rate-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #4f46e5;
  line-height: 1;
  margin-bottom: 5px;
}

.rate-label {
  font-size: 0.9rem;
  color: #6b7280;
}

.product-meta {
  margin-bottom: 15px;
}

.join-methods {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.join-badge {
  font-size: 0.7rem;
  background: #f3f4f6;
  color: #6b7280;
  padding: 3px 8px;
  border-radius: 4px;
}

.view-details-btn {
  width: 100%;
  padding: 8px 0;
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.3s ease;
}

.view-details-btn:hover {
  background: #4338ca;
}

.view-all {
  margin-top: 20px;
}

.view-all-link {
  display: inline-block;
  padding: 10px 20px;
  color: #4f46e5;
  font-weight: 500;
  text-decoration: none;
  border: 1px solid #4f46e5;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.view-all-link:hover {
  background: #4f46e5;
  color: white;
}

.loading-indicator,
.error-message {
  padding: 40px 0;
  color: #6b7280;
}

.error-message {
  color: #ef4444;
}

@media (max-width: 768px) {
  h1 {
    font-size: 2.5rem;
  }

  .subtitle {
    font-size: 1.2rem;
  }

  .auth-buttons {
    flex-direction: column;
    align-items: center;
  }

  .cta-button {
    width: 100%;
    max-width: 300px;
  }
}
</style>

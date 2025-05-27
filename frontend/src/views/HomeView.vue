<!-- src/views/HomeView.vue -->
<template>
  <div class="home-container">
    <div class="hero-section">
      <div class="particles-container">
        <ParticleNetwork />
      </div>
      <div class="hero-content-wrapper">
        <div class="hero-content">
          <h1>{{ $t('hero.tagline') }}</h1>
          <p>{{ $t('hero.subtitle') }}</p>
          <div class="hero-buttons">
            <router-link to="/products/ai-recommendations" class="hero-btn primary">{{
              $t('hero.ctaButton')
            }}</router-link>
            <router-link to="/products" class="hero-btn secondary">{{
              $t('hero.learnMore')
            }}</router-link>
          </div>
        </div>
      </div>
    </div>
    <MarketSection />

    <!-- 금융 시장 동향 섹션 -->

    <!-- 주식 관련 영상 검색 섹션 (신규 추가) -->
    <!-- <section class="video-search-section">
      <h2>{{ $t('home.videoSearchTitle') }}</h2>
      <div class="search-bar-container">
        <input
          type="text"
          :placeholder="$t('home.videoSearchPlaceholder')"
          class="search-input"
          v-model="videoSearchQuery"
          @keyup.enter="searchVideos"
        />
        <button @click="searchVideos" class="search-button">{{ $t('common.search') }}</button>
      </div>
      
      <div v-if="videoSearchResults.length > 0" class="video-results">
        
      </div>
      <p v-else-if="searchedVideos && videoSearchResults.length === 0" class="no-results">
        {{ $t('home.noVideoResults') }}
      </p>
    </section> -->

    <section class="top-products-section">
      <h2>{{ $t('products.recommended') }}</h2>

      <div class="tabs">
        <button :class="{ active: activeTab === 'deposit' }" @click="activeTab = 'deposit'">
          {{ $t('products.types.deposit') }}
        </button>
        <button :class="{ active: activeTab === 'saving' }" @click="activeTab = 'saving'">
          {{ $t('products.types.saving') }}
        </button>
        <button :class="{ active: activeTab === 'loan' }" @click="activeTab = 'loan'">
          {{ $t('products.types.loan') }}
        </button>
      </div>

      <div v-if="topProductsLoading" class="loading-indicator">
        <p>{{ $t('products.loading') }}</p>
      </div>

      <div v-else-if="topProductsError" class="error-message">
        <p>{{ $t('common.error.loadFailed') }}</p>
        <button class="retry-button action-btn secondary-btn" @click="loadTopProducts">
          {{ $t('common.retry') }}
        </button>
      </div>

      <div v-else class="products-slider">
        <div class="product-cards">
          <div
            v-for="product in topProducts"
            :key="product.product?.fin_prdt_cd || product.id"
            class="product-card-home"
            @click="viewProductDetails(product)"
          >
            <div class="product-header">
              <span class="product-type-badge-home">{{ getProductTypeName(product) }}</span>
              <h3 class="product-name-home">{{ getProductName(product) }}</h3>
            </div>
            <p class="bank-name-home">{{ getBankName(product) }}</p>

            <div
              class="rate-info-home"
              v-if="product.product_type === 'deposit' || product.product_type === 'saving'"
            >
              <span class="rate-label-home">최고</span>
              <span class="rate-value-home">{{ formatRate(getMaxRate(product)) }}%</span>
            </div>
            <div class="rate-info-home" v-if="product.product_type === 'loan'">
              <span class="rate-label-home">최저</span>
              <span class="rate-value-home loan">{{ formatRate(getMinLoanRate(product)) }}%</span>
            </div>

            <div class="join-methods-home">
              <span v-if="hasJoinWay(product, '인터넷')" class="join-badge-home">인터넷</span>
              <span v-if="hasJoinWay(product, '영업점')" class="join-badge-home">영업점</span>
              <span v-if="hasJoinWay(product, '스마트폰')" class="join-badge-home">스마트폰</span>
            </div>
            <button @click.stop="viewProductDetails(product)" class="action-btn product-details-btn">
              {{ $t('자세히 보기') }}
            </button>
          </div>
        </div>

        <div class="view-all">
          <router-link :to="{ name: 'Products', query: { tab: activeTab } }" class="view-all-link">
            모든 {{ getTabName(activeTab) }} 상품 보기 <i class="bi bi-arrow-right-short"></i>
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref, onBeforeUnmount, watch } from 'vue'
// import { useUserStore } from '@/stores/user' // 주석 처리
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Chart from 'chart.js/auto'
import productsService from '@/services/products'
import { formatRate } from '@/utils/rateUtils'
import MarketSection from '@/components/market/MarketSection.vue'
import ParticleNetwork from '@/components/effects/ParticleNetwork.vue'

// const userStore = useUserStore()
const router = useRouter()
const i18n = useI18n()

// const isLoggedIn = computed(() => userStore.isLoggedIn)
// const user = computed(() => userStore.user)

// Top products section
const activeTab = ref('deposit')
const topProducts = ref([])
const topProductsLoading = ref(false)
const topProductsError = ref(null)

// pjt0의 차트 관련 ref 유지
const interestRateChart = ref(null)
const preciousMetalsChart = ref(null)
const exchangeRateChart = ref(null)
let interestRateChartInstance = null
let preciousMetalsChartInstance = null
let exchangeRateChartInstance = null

// Load top products based on active tab
const loadTopProducts = async () => {
  topProductsLoading.value = true
  topProductsError.value = null

  try {
    const response = await productsService.getTopRateProducts(activeTab.value, 5)
    if (!response || response.length === 0) {
      topProductsError.value = i18n.t('products.noProducts')
      topProducts.value = []
      return
    }
    topProducts.value = response.map((p) => ({ ...p, product_type: activeTab.value }))
  } catch (err) {
    console.error('Error loading top products:', err)
    topProductsError.value = err.response?.data?.message || i18n.t('common.error.networkError')
    topProducts.value = []
  } finally {
    topProductsLoading.value = false
  }
}

const getProductTypeName = (product) => {
  const type = product.product_type
  if (type === 'deposit') return i18n.t('products.types.deposit')
  if (type === 'saving') return i18n.t('products.types.saving')
  if (type === 'loan') return i18n.t('products.types.loan')
  return '상품'
}

const getProductName = (product) => {
  if (product.product_type === 'loan') {
    return product.product_info?.fin_prdt_nm || product.fin_prdt_nm || i18n.t('products.noName')
  }
  return product.financial_product?.fin_prdt_nm || product.fin_prdt_nm || i18n.t('products.noName')
}

const getBankName = (product) => {
  if (product.product_type === 'loan') {
    return product.product_info?.kor_co_nm || product.kor_co_nm || i18n.t('products.noBankName')
  }
  return product.financial_product?.kor_co_nm || product.kor_co_nm || i18n.t('products.noBankName')
}

const getMaxRate = (product) => {
  if (product.options && product.options.length > 0) {
    const rates = product.options.map((opt) => parseFloat(opt.intr_rate2)).filter((r) => !isNaN(r))
    if (rates.length > 0) return Math.max(...rates)
  }
  return parseFloat(product.intr_rate2) || 0
}

const getMinLoanRate = (product) => {
  if (product.lending_options && product.lending_options.length > 0) {
    const rates = product.lending_options
      .map((opt) => parseFloat(opt.lend_rate_min))
      .filter((r) => !isNaN(r))
    if (rates.length > 0) return Math.min(...rates)
  }
  return 0
}

const hasJoinWay = (product, way) => {
  const joinWayString =
    product.financial_product?.join_way || product.product_info?.join_way || product.join_way || ''
  return joinWayString.includes(way)
}

const viewProductDetails = (product) => {
  let id = product.product?.fin_prdt_cd || product.fin_prdt_cd || product.id
  let type = product.product_type

  if (!id || !type) {
    console.error('Product ID or type is missing for navigation', product)
    if (product.financial_product) {
      id = id || product.financial_product.fin_prdt_cd
      type = type || 'deposit'
    } else if (product.product_info) {
      id = id || product.product_info.fin_prdt_cd
      type = type || 'loan'
    }
    type = type || activeTab.value
  }

  if (id && type && type !== 'all') {
    router.push({ name: 'ProductDetail', params: { type: type, id: id } })
  } else {
    console.error('Cannot navigate to product details due to missing ID or type:', product)
    router.push({ name: 'Products' })
  }
}

const getTabName = (tabKey) => {
  const names = {
    deposit: i18n.t('products.types.deposit'),
    saving: i18n.t('products.types.saving'),
    loan: i18n.t('products.types.loan'),
  }
  return names[tabKey] || ''
}

// pjt0의 차트 생성 함수들 유지
const createInterestRateChart = () => {
  if (!interestRateChart.value) return

  const ctx = interestRateChart.value.getContext('2d')

  // 기준 금리 데이터 (최근 12개월)
  const data = {
    labels: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
    datasets: [
      {
        label: '한국은행 기준금리',
        data: [3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.25, 3.25, 3.0, 3.0, 2.75, 2.75],
        borderColor: '#A38D77',
        backgroundColor: 'rgba(163, 141, 119, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: '미 연준 기준금리',
        data: [4.75, 4.75, 5.0, 5.0, 5.25, 5.25, 5.25, 5.25, 5.25, 5.25, 5.0, 5.0],
        borderColor: '#6D4C3D',
        backgroundColor: 'rgba(109, 76, 61, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  }

  interestRateChartInstance = new Chart(ctx, {
    type: 'line',
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          mode: 'index',
          intersect: false,
        },
      },
      scales: {
        y: {
          min: 2.0,
          max: 6.0,
          ticks: {
            stepSize: 0.5,
          },
        },
      },
    },
  })
}

const createPreciousMetalsChart = () => {
  if (!preciousMetalsChart.value) return

  const ctx = preciousMetalsChart.value.getContext('2d')

  // 금/은 시세 데이터 (최근 6개월)
  const data = {
    labels: ['7월', '8월', '9월', '10월', '11월', '12월'],
    datasets: [
      {
        label: '금 (XAU/USD)',
        data: [1960, 1945, 1920, 1980, 2040, 2070],
        borderColor: '#FFD700',
        backgroundColor: 'rgba(255, 215, 0, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: '은 (XAG/USD)',
        data: [24.5, 24.2, 23.0, 22.8, 24.5, 25.5],
        borderColor: '#C0C0C0',
        backgroundColor: 'rgba(192, 192, 192, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  }

  preciousMetalsChartInstance = new Chart(ctx, {
    type: 'line',
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          mode: 'index',
          intersect: false,
        },
      },
      scales: {
        y: {
          beginAtZero: false,
        },
      },
    },
  })
}

const createExchangeRateChart = () => {
  if (!exchangeRateChart.value) return

  const ctx = exchangeRateChart.value.getContext('2d')

  // 원/달러 환율 데이터 (최근 30일)
  const data = {
    labels: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`),
    datasets: [
      {
        label: '원/달러 환율',
        data: [
          1320, 1325, 1315, 1330, 1328, 1335, 1340, 1338, 1345, 1350, 1348, 1355, 1360, 1358, 1365,
          1362, 1370, 1368, 1375, 1380, 1378, 1385, 1390, 1388, 1395, 1400, 1398, 1395, 1392, 1390,
        ],
        borderColor: '#008000',
        backgroundColor: 'rgba(0, 128, 0, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  }

  exchangeRateChartInstance = new Chart(ctx, {
    type: 'line',
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          mode: 'index',
          intersect: false,
        },
      },
      scales: {
        y: {
          beginAtZero: false,
        },
      },
    },
  })
}

watch(activeTab, () => {
  loadTopProducts()
})

onMounted(() => {
  loadTopProducts()
  // pjt0의 차트 생성 호출 유지
  createInterestRateChart()
  createPreciousMetalsChart()
  createExchangeRateChart()
})

onBeforeUnmount(() => {
  // pjt0의 차트 인스턴스 파괴 로직 유지
  if (interestRateChartInstance) {
    interestRateChartInstance.destroy()
  }
  if (preciousMetalsChartInstance) {
    preciousMetalsChartInstance.destroy()
  }
  if (exchangeRateChartInstance) {
    exchangeRateChartInstance.destroy()
  }
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  padding-top: 20px; /* 헤더 공간 확보 */
}

/* 히어로 섹션 스타일 - 머큐리 스타일 적용 */
.hero-section {
  position: relative;
  height: 85vh;
  min-height: 650px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  overflow: hidden;
  background: var(--background-gradient);
}

.particles-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.hero-content-wrapper {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  gap: 4rem;
}

.hero-content {
  flex: 1;
  text-align: left;
  padding: 2rem;
}

.hero-content h1 {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
  text-shadow: var(--hero-text-shadow);
  font-weight: 700;
  line-height: 1.2;
  font-family: 'Pretendard Variable', serif;
}

.hero-content p {
  font-size: 1.5rem;
  margin-bottom: 2.5rem;
  color: var(--text-secondary);
  max-width: 95%;
  line-height: 1.6;
  font-family: 'Pretendard Variable', sans-serif;
}

.hero-buttons {
  display: flex;
  gap: 1rem;
}

.hero-btn {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 500;
  border-radius: 16px;
  cursor: pointer;
  transition: all var(--transition-speed);
  font-family: 'Pretendard Variable', sans-serif;
  border: none;
}

.hero-btn.primary {
  background-color: var(--button-bg);
  color: var(--button-text);
  box-shadow: 0 4px 10px rgba(79, 70, 229, 0.2);
}

.hero-btn.primary:hover {
  background-color: var(--button-hover);
  transform: translateY(-4px);
  box-shadow: 0 8px 15px rgba(79, 70, 229, 0.3);
}

.hero-btn.secondary {
  background-color: transparent;
  color: var(--text-primary);
  border: 2px solid var(--border-color);
}

.hero-btn.secondary:hover {
  background-color: rgba(0, 0, 0, 0.03);
  transform: translateY(-4px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

/* 반응형 히어로 섹션 */
@media (max-width: 1200px) {
  .hero-content-wrapper {
    padding: 0 2rem;
  }
}

@media (max-width: 992px) {
  .hero-content-wrapper {
    flex-direction: column;
    gap: 3rem;
  }

  .hero-content {
    text-align: center;
    padding: 0;
  }

  .hero-content h1 {
    font-size: 3.5rem;
  }

  .hero-content p {
    font-size: 1.25rem;
    margin-left: auto;
    margin-right: auto;
  }

  .hero-buttons {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .hero-section {
    height: auto;
    padding: 6rem 1rem;
  }

  .hero-content h1 {
    font-size: 2.8rem;
  }

  .hero-content p {
    font-size: 1.1rem;
  }

  .hero-buttons {
    flex-direction: column;
    gap: 0.8rem;
    max-width: 300px;
    margin: 0 auto;
  }

  .hero-btn {
    width: 100%;
    padding: 0.9rem 1.5rem;
  }
}
/* 주식 관련 영상 검색 섹션 스타일 (신규 추가) */
.video-search-section {
  padding: 40px 20px;
  text-align: center;
  background-color: var(--background-secondary); /* Final-PJT 테마에 맞는 배경색 */
  margin-bottom: 40px;
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
}

.video-search-section h2 {
  font-size: 2rem;
  color: var(--text-primary);
  margin-bottom: 30px;
  font-family: var(--font-heading);
}

.search-bar-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  max-width: 600px;
  margin: 0 auto;
}

.search-input {
  flex-grow: 1;
  padding: 12px 18px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 1rem;
  background-color: var(--input-bg);
  color: var(--text-input);
  transition:
    border-color 0.3s ease,
    box-shadow 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(var(--accent-color-rgb), 0.2);
}

.search-button {
  padding: 12px 24px;
  background-color: var(--accent-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.search-button:hover {
  background-color: var(--accent-color-dark);
}

.video-results {
  margin-top: 30px;
  /* 영상 결과 카드 스타일링 추가 예정 */
}

.no-results {
  margin-top: 20px;
  color: var(--text-secondary);
}

/* Top Products Section */
.top-products-section {
  padding: 60px 20px; /* 상단 영상 검색 섹션과의 간격 조절 */
  text-align: center;
  background-color: var(--background-primary);
}

.top-products-section h2 {
  font-size: 2.2rem;
  color: var(--text-primary);
  margin-bottom: 40px;
  font-family: var(--font-heading);
}

.tabs {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 40px;
}

.tabs button {
  padding: 12px 24px;
  border: 1px solid var(--border-color);
  background: var(--button-bg); /* variables.css 에 정의된 변수 사용 */
  color: var(--button-text); /* variables.css 에 정의된 변수 사용 */
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-xs);
}

.tabs button.active {
  background: var(--accent-color);
  color: white;
  border-color: var(--accent-color);
  box-shadow: var(--shadow-sm);
}

.tabs button:hover:not(.active) {
  border-color: var(--accent-color-light);
  background: var(--button-hover-bg);
}

.products-slider {
  max-width: 1200px;
  margin: 0 auto;
}

.product-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); /* 카드 최소 너비 살짝 늘림 */
  gap: 35px; /* 카드 간 간격 늘림 */
  margin-bottom: 30px;
}

/* product-card-home 스타일 (감성적이고 정돈된 디자인으로 개선) */
.product-card-home {
  background: var(
    --card-bg-accent,
    var(--card-bg)
  ); /* 좀 더 부드러운 카드 배경색, 없으면 기본 사용 */
  border: 1px solid var(--border-color-light, var(--border-color)); /* 더 연한 테두리 색 */
  border-radius: 20px; /* 더욱 둥글게 */
  padding: 28px; /* 내부 패딩 살짝 늘림 */
  text-align: left;
  transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1); /* 부드러운 전환 효과 */
  box-shadow: var(--shadow-lg); /* 기본 그림자 강화 */
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.product-card-home:hover {
  transform: translateY(-10px); /* 호버 시 좀 더 뚜렷한 이동 */
  box-shadow: var(--shadow-xl); /* 호버 시 그림자 더욱 강조 */
  border-color: var(--accent-color-translucent, var(--accent-color)); /* 호버 시 테두리 강조 */
}

.product-header {
  margin-bottom: 20px; /* 헤더와 다음 요소 간 간격 늘림 */
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.product-type-badge-home {
  align-self: flex-start;
  background-color: var(
    --accent-color-opacity-10,
    rgba(var(--accent-color-rgb), 0.1)
  ); /* 투명도 있는 배경 */
  color: var(--accent-color); /* 강조색 텍스트 */
  padding: 8px 16px; /* 뱃지 패딩 늘림 */
  border-radius: 25px; /* 타원형 뱃지 더욱 둥글게 */
  font-size: 0.85rem; /* 폰트 크기 살짝 조정 */
  font-weight: 700; /* 폰트 굵기 강조 */
  text-transform: uppercase;
  letter-spacing: 0.5px; /* 자간 살짝 추가 */
}

.product-name-home {
  font-size: 1.45rem; /* 상품명 크기 강조 */
  font-weight: 700; /* 상품명 굵게 */
  color: var(--text-heading, var(--text-primary)); /* 제목용 텍스트 색상 */
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: calc(1.45rem * 1.35 * 2); /* 2줄 높이 정확히 확보 */
  margin-top: 5px; /* 뱃지와의 간격 */
}

.bank-name-home {
  font-size: 1rem; /* 은행명 크기 키움 */
  color: var(--text-subtle, var(--text-secondary)); /* 더 부드러운 텍스트 색 */
  margin-bottom: 18px;
  font-weight: 500; /* 은행명 폰트 두께 */
}

.rate-info-home {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--background-emphasis, rgba(var(--accent-color-rgb), 0.05)); /* 강조 배경 */
  border-radius: 12px; /* 내부 정보 박스도 둥글게 */
  padding: 16px 20px; /* 패딩 조정 */
  margin-bottom: 20px;
  border: 1px solid var(--accent-color-opacity-20, rgba(var(--accent-color-rgb), 0.2));
}

.rate-label-home {
  font-size: 0.95rem; /* 라벨 폰트 크기 */
  color: var(--text-secondary);
  font-weight: 500;
}

.rate-value-home {
  font-size: 1.8rem; /* 금리 값 더욱 강조 */
  font-weight: 700; /* 금리 값 굵게 */
  color: var(--accent-color-dark, var(--accent-color)); /* 더 진한 강조색 */
  line-height: 1;
}
.rate-value-home.loan {
  color: var(--color-loan-rate-dark, var(--color-loan-rate, var(--accent-color)));
}

.join-methods-home {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 24px;
}

.join-badge-home {
  font-size: 0.85rem;
  background: var(--tag-bg-alt, var(--tag-bg)); /* 대체 태그 배경색 */
  color: var(--tag-text-alt, var(--tag-text)); /* 대체 태그 텍스트색 */
  padding: 6px 12px; /* 뱃지 패딩 조정 */
  border-radius: 8px; /* 뱃지 모서리 살짝 둥글게 */
  font-weight: 500;
}

.view-details-btn {
  width: 100%;
  margin-top: auto;
  padding: 14px 24px; /* 버튼 패딩 늘림 */
  font-size: 1rem; /* 버튼 폰트 크기 */
  font-weight: 600; /* 버튼 폰트 굵기 */
  border-radius: 12px; /* 버튼 모서리 둥글게 */
  /* App.vue 또는 variables.css의 .action-btn.primary-btn 스타일을 따름 */
  /* 필요시 여기서 추가 스타일 오버라이드 */
}

.view-all {
  margin-top: 40px; /* 카드 목록과의 간격 */
}

.view-all-link {
  display: inline-flex; /* 아이콘과 텍스트 정렬 */
  align-items: center;
  padding: 12px 24px;
  color: var(--accent-color);
  font-weight: 600;
  text-decoration: none;
  border: 2px solid var(--accent-color);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.view-all-link:hover {
  background: var(--accent-color);
  color: white;
}

.view-all-link i {
  margin-left: 8px; /* 아이콘과 텍스트 간격 */
  font-size: 1.2em;
}

.loading-indicator,
.error-message {
  padding: 40px 0;
  color: var(--text-secondary); /* 좀 더 부드러운 색상 */
  text-align: center;
}

.error-message {
  background: var(--card-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color-error, var(--border-color)); /* 에러 시 테두리 색상 */
  margin: 2rem auto;
  padding: 2rem;
  max-width: 500px;
}

.error-message p {
  color: var(--text-error);
  margin-bottom: 1rem;
}

.retry-button {
  /* .action-btn .secondary-btn 스타일을 따르거나 여기서 재정의 */
}

/* Financial Data Section (pjt0 원본 차트) 스타일 개선 */
.financial-data-section {
  padding: 60px 20px;
  background-color: var(--background-primary); /* 일관된 배경색 */
  border-top: 1px solid var(--border-color);
}

.financial-data-section h2 {
  font-family: var(--font-heading);
  color: var(--text-primary); /* 제목 색상 통일 */
  font-size: 2.2rem; /* 다른 섹션 제목과 크기 통일 */
  margin-bottom: 40px;
  text-align: center;
}

.financial-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
  margin: 0 auto;
  max-width: 1200px; /* 최대 너비 설정 */
}

.chart-card {
  background-color: var(--card-bg);
  border-radius: 16px; /* 카드 곡률 통일 */
  padding: 24px;
  box-shadow: var(--shadow-md);
  transition: all var(--transition-normal);
}

.chart-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

.chart-card h3 {
  text-align: center;
  margin-bottom: 20px;
  color: var(--text-secondary); /* 부제목 색상 */
  font-family: var(--font-heading);
  font-size: 1.3rem; /* 부제목 크기 */
}

.chart-container {
  height: 300px;
  position: relative;
}

/* 반응형 스타일은 기존 것을 유지하되, 필요시 Final-PJT 기준으로 추가 조정 */
@media (max-width: 768px) {
  .video-search-section h2 {
    font-size: 1.8rem;
  }
  .search-bar-container {
    flex-direction: column;
    gap: 15px;
  }
  .search-input,
  .search-button {
    width: 100%;
  }

  .top-products-section h2,
  .financial-data-section h2 {
    font-size: 1.8rem; /* 모바일에서 제목 크기 조정 */
  }

  .product-cards {
    grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); /* 모바일 카드 최소 너비 조정 */
    gap: 25px; /* 모바일 카드 간격 조정 */
  }
  .financial-charts {
    grid-template-columns: 1fr;
  }

  .chart-container {
    height: 250px;
  }

  .product-name-home {
    font-size: 1.3rem;
  }
  .rate-value-home {
    font-size: 1.6rem;
  }
}

@media (max-width: 480px) {
  .product-cards {
    grid-template-columns: 1fr; /* 매우 작은 화면에서는 한 줄로 */
  }
  .product-card-home {
    padding: 20px; /* 매우 작은 화면에서 카드 패딩 조정 */
    border-radius: 16px; /* 모서리 곡률 살짝 줄임 */
  }
  .product-name-home {
    font-size: 1.2rem;
  }
  .rate-value-home {
    font-size: 1.45rem;
  }

  .tabs {
    flex-direction: column;
    align-items: stretch; /* 버튼 너비 100% */
  }

  .tabs button {
    width: 100%;
    max-width: none;
  }

  .top-products-section {
    padding: 40px 15px;
  }
  .financial-data-section {
    padding: 40px 15px;
  }
}

/* 기존 스타일 중복 제거 및 Final-PJT 스타일 우선 적용 */
/* .view-details-btn, .view-all-link 등은 위에서 상세히 재정의되었으므로 하단의 중복 스타일은 제거해도 무방 */

/* 전역 스타일을 사용하는 버튼 스타일 */
.action-btn {
  padding: 0.6rem 1.2rem; /* 기존 hero-btn과 유사한 패딩 */
  border-radius: 8px; /* 일관된 테두리 반경 */
  font-weight: 500;
  text-align: center;
  cursor: pointer;
  transition: background-color var(--transition-speed), color var(--transition-speed);
  border: 1px solid transparent; /* 기본 테두리 투명 처리 */
}

.product-details-btn {
  background-color: var(--button-bg); /* 전역 버튼 배경색 */
  color: var(--button-text); /* 전역 버튼 텍스트색 */
  border-color: var(--button-bg); /* 테두리도 버튼 배경색과 동일하게 */
  display: block; /* 카드의 전체 너비를 차지하도록 변경 */
  width: 100%; /* 카드의 전체 너비를 차지하도록 변경 */
  margin-top: 1rem; /* 위 요소와의 간격 */
}

.product-details-btn:hover {
  background-color: var(--button-hover); /* 전역 버튼 호버 배경색 */
  border-color: var(--button-hover);
}

/* 기존 hero-btn 스타일과 통일성 유지 (필요시) */
.hero-btn.primary {
  background-color: var(--button-bg);
  color: var(--button-text);
  border: 1px solid var(--button-bg);
}

.hero-btn.primary:hover {
  background-color: var(--button-hover);
  border-color: var(--button-hover);
}

.hero-btn.secondary {
  background-color: transparent;
  color: var(--button-bg); /* 텍스트 색상을 accent으로 */
  border: 1px solid var(--button-bg);
}

.hero-btn.secondary:hover {
  background-color: var(--accent-color-opacity-10, rgba(163, 184, 153, 0.1)); /* Soft Mint의 10% 투명도 */
  color: var(--button-hover);
  border-color: var(--button-hover);
}
</style>

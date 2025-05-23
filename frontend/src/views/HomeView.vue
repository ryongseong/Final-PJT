<!-- src/views/HomeView.vue -->
<template>
  <div class="home-container">
    <section class="hero-section">
      <div class="hero-content">
        <h1>
          {{
            currentLanguage === 'ko' ? '금융의 미래를 만나다' : 'Experience the Future of Finance'
          }}
        </h1>
        <p class="subtitle">
          {{
            currentLanguage === 'ko'
              ? '스마트한 금융 선택으로 당신의 자산을 효율적으로 관리하세요'
              : 'Manage your assets efficiently with smart financial choices'
          }}
        </p>

        <!-- 로그인된 사용자를 위한 인사말 제거 -->

        <div class="auth-buttons">
          <router-link to="/login" class="btn btn-primary">
            {{ currentLanguage === 'ko' ? '로그인' : 'Login' }}
          </router-link>
          <router-link to="/register" class="btn btn-outline">
            {{ currentLanguage === 'ko' ? '회원가입' : 'Register' }}
          </router-link>
        </div>
      </div>
      <div class="hero-image">
        <!-- Hero 섹션 이미지 또는 그래픽 -->
      </div>
    </section>

    <section class="top-products-section container">
      <h2>{{ currentLanguage === 'ko' ? '추천 금융 상품' : 'Recommended Financial Products' }}</h2>

      <div class="tabs">
        <button :class="{ active: activeTab === 'deposit' }" @click="activeTab = 'deposit'">
          {{ currentLanguage === 'ko' ? '예금 상품' : 'Deposit Products' }}
        </button>
        <button :class="{ active: activeTab === 'saving' }" @click="activeTab = 'saving'">
          {{ currentLanguage === 'ko' ? '적금 상품' : 'Savings Products' }}
        </button>
        <button :class="{ active: activeTab === 'loan' }" @click="activeTab = 'loan'">
          {{ currentLanguage === 'ko' ? '대출 상품' : 'Loan Products' }}
        </button>
      </div>

      <div v-if="topProductsLoading" class="loading-indicator">
        <div class="loading-spinner"></div>
        <p>
          {{
            currentLanguage === 'ko'
              ? '상품 정보를 불러오는 중...'
              : 'Loading product information...'
          }}
        </p>
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
              <div class="rate-label">
                {{ currentLanguage === 'ko' ? '최고 금리' : 'Maximum Rate' }}
              </div>
            </div>

            <div class="product-rate" v-if="activeTab === 'loan'">
              <div class="rate-value">
                {{ formatRate(product.lending_options[0].lend_rate_min) }}%
              </div>
              <div class="rate-label">
                {{ currentLanguage === 'ko' ? '최저 대출금리' : 'Minimum Loan Rate' }}
              </div>
            </div>

            <div class="product-meta">
              <div class="join-methods">
                <span v-if="hasJoinWay(product, '인터넷')" class="join-badge">
                  {{ currentLanguage === 'ko' ? '인터넷' : 'Internet' }}
                </span>
                <span v-if="hasJoinWay(product, '영업점')" class="join-badge">
                  {{ currentLanguage === 'ko' ? '영업점' : 'Branch' }}
                </span>
                <span v-if="hasJoinWay(product, '스마트폰')" class="join-badge">
                  {{ currentLanguage === 'ko' ? '스마트폰' : 'Mobile' }}
                </span>
                <span v-if="hasJoinWay(product, '전화(텔레뱅킹)')" class="join-badge">
                  {{ currentLanguage === 'ko' ? '전화' : 'Phone' }}
                </span>
                <span v-if="hasJoinWay(product, '모집인')" class="join-badge">
                  {{ currentLanguage === 'ko' ? '모집인' : 'Agent' }}
                </span>
              </div>
            </div>

            <button class="btn btn-primary view-details-btn">
              {{ currentLanguage === 'ko' ? '상세 정보 보기' : 'View Details' }}
            </button>
          </div>
        </div>

        <div class="view-all">
          <router-link :to="{ name: 'Products', query: { tab: activeTab } }" class="view-all-link">
            {{
              currentLanguage === 'ko'
                ? `모든 ${getTabName(activeTab)} 상품 보기`
                : `View All ${getTabNameEn(activeTab)} Products`
            }}
          </router-link>
        </div>
      </div>
    </section>

    <section class="features-section">
      <div class="container">
        <h2>{{ currentLanguage === 'ko' ? '주요 기능' : 'Key Features' }}</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">💰</div>
            <h3>{{ currentLanguage === 'ko' ? '지출 관리' : 'Expense Management' }}</h3>
            <p>
              {{
                currentLanguage === 'ko'
                  ? '일일 지출을 편리하게 기록하고 관리하세요'
                  : 'Conveniently record and manage your daily expenses'
              }}
            </p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>{{ currentLanguage === 'ko' ? '분석 리포트' : 'Analysis Reports' }}</h3>
            <p>
              {{
                currentLanguage === 'ko'
                  ? '지출 패턴을 분석하여 효과적인 재정 관리를 도와드립니다'
                  : 'Analyze spending patterns to help with effective financial management'
              }}
            </p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3>{{ currentLanguage === 'ko' ? '저축 목표' : 'Savings Goals' }}</h3>
            <p>
              {{
                currentLanguage === 'ko'
                  ? '목표를 설정하고 진행 상황을 추적하세요'
                  : 'Set goals and track your progress'
              }}
            </p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">🔔</div>
            <h3>{{ currentLanguage === 'ko' ? '알림 서비스' : 'Notification Service' }}</h3>
            <p>
              {{
                currentLanguage === 'ko'
                  ? '중요한 금융 일정을 놓치지 않도록 알림을 받으세요'
                  : "Receive alerts so you don't miss important financial schedules"
              }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <section class="financial-data-section">
      <div class="container">
        <h2>{{ currentLanguage === 'ko' ? '금융 시장 데이터' : 'Financial Market Data' }}</h2>
        <div class="financial-charts">
          <div class="chart-card">
            <h3>{{ currentLanguage === 'ko' ? '기준 금리 추이' : 'Base Interest Rate Trends' }}</h3>
            <div class="chart-container interest-chart">
              <canvas ref="interestRateChart"></canvas>
            </div>
          </div>

          <div class="chart-card">
            <h3>{{ currentLanguage === 'ko' ? '금/은 시세' : 'Gold/Silver Prices' }}</h3>
            <div class="chart-container precious-metals-chart">
              <canvas ref="preciousMetalsChart"></canvas>
            </div>
          </div>

          <div class="chart-card">
            <h3>{{ currentLanguage === 'ko' ? '주요 환율' : 'Major Exchange Rates' }}</h3>
            <div class="chart-container exchange-rate-chart">
              <canvas ref="exchangeRateChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Bank Branch Finder Section -->
    <section class="branch-finder-section container">
      <h2>
        {{ currentLanguage === 'ko' ? '가까운 은행 지점 찾기' : 'Find Nearby Bank Branches' }}
      </h2>
      <p class="section-description">
        {{
          currentLanguage === 'ko'
            ? '지역과 은행을 선택하여 가까운 지점을 찾아보세요'
            : 'Select a region and bank to find branches near you'
        }}
      </p>

      <div class="map-container">
        <KakaoMap
          ref="kakaoMap"
          :initial-latitude="37.5665"
          :initial-longitude="126.978"
          :initial-level="5"
          @bank-clicked="onBankClicked"
        />
      </div>

      <div class="bank-info-panel" v-if="selectedBank">
        <h3>{{ currentLanguage === 'ko' ? '선택한 지점 정보' : 'Selected Branch Info' }}</h3>
        <div class="bank-details">
          <p>
            <strong>{{ currentLanguage === 'ko' ? '은행명' : 'Bank Name' }}:</strong>
            {{ selectedBank.place_name }}
          </p>
          <p>
            <strong>{{ currentLanguage === 'ko' ? '주소' : 'Address' }}:</strong>
            {{ selectedBank.address_name }}
          </p>
          <p v-if="selectedBank.phone">
            <strong>{{ currentLanguage === 'ko' ? '전화번호' : 'Phone' }}:</strong>
            {{ selectedBank.phone }}
          </p>
          <div class="directions-link" v-if="selectedBank.road_address_name">
            <a :href="getKakaoMapUrl(selectedBank)" target="_blank" class="btn btn-directions">
              {{ currentLanguage === 'ko' ? '길찾기' : 'Get Directions' }}
            </a>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, inject, onBeforeUnmount } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import productsService from '@/services/products'
import Chart from 'chart.js/auto'
import KakaoMap from '@/components/KakaoMap.vue'

// 언어 설정이 앱 전체에서 공유될 수 있도록 주입 시도 (앱 컴포넌트에서 제공하는 경우)
const injectedLanguage = inject('currentLanguage', ref('ko'))

// 앱 수준에서 주입되지 않은 경우 기본값 사용
const currentLanguage = ref('ko')

// 컴포넌트 마운트 시 localStorage에서 언어 설정 확인
onMounted(() => {
  const savedLanguage = localStorage.getItem('language')
  if (savedLanguage) {
    currentLanguage.value = savedLanguage
  }
})

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
    topProductsError.value =
      currentLanguage.value === 'ko'
        ? '상품 정보를 불러오는데 실패했습니다.'
        : 'Failed to load product information.'
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

// Get tab name for display (Korean)
const getTabName = (tab) => {
  const names = {
    deposit: '예금',
    saving: '적금',
    loan: '대출',
  }
  return names[tab] || ''
}

// Get tab name for display (English)
const getTabNameEn = (tab) => {
  const names = {
    deposit: 'Deposit',
    saving: 'Savings',
    loan: 'Loan',
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

// 차트 관련 참조와 변수
const interestRateChart = ref(null)
const preciousMetalsChart = ref(null)
const exchangeRateChart = ref(null)
let interestRateChartInstance = null
let preciousMetalsChartInstance = null
let exchangeRateChartInstance = null

// 차트 생성 함수들
const createInterestRateChart = () => {
  if (!interestRateChart.value) return

  const ctx = interestRateChart.value.getContext('2d')

  // 기준 금리 데이터 (최근 12개월)
  const data = {
    labels: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
    datasets: [
      {
        label: currentLanguage.value === 'ko' ? '한국은행 기준금리' : 'Bank of Korea Base Rate',
        data: [3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.25, 3.25, 3.0, 3.0, 2.75, 2.75],
        borderColor: '#A38D77',
        backgroundColor: 'rgba(163, 141, 119, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: currentLanguage.value === 'ko' ? '미 연준 기준금리' : 'US Fed Rate',
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
        label: currentLanguage.value === 'ko' ? '금 시세 (USD/온스)' : 'Gold Price (USD/oz)',
        data: [1950, 1925, 2000, 2050, 2100, 2075],
        borderColor: '#D4AF37',
        backgroundColor: 'rgba(212, 175, 55, 0.1)',
        tension: 0.4,
        fill: true,
        yAxisID: 'y',
      },
      {
        label: currentLanguage.value === 'ko' ? '은 시세 (USD/온스)' : 'Silver Price (USD/oz)',
        data: [24.5, 24.0, 25.2, 26.1, 27.5, 26.8],
        borderColor: '#C0C0C0',
        backgroundColor: 'rgba(192, 192, 192, 0.1)',
        tension: 0.4,
        fill: true,
        yAxisID: 'y1',
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
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: currentLanguage.value === 'ko' ? '금 (USD)' : 'Gold (USD)',
          },
          min: 1800,
          max: 2200,
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: currentLanguage.value === 'ko' ? '은 (USD)' : 'Silver (USD)',
          },
          min: 20,
          max: 30,
          grid: {
            drawOnChartArea: false,
          },
        },
      },
    },
  })
}

const createExchangeRateChart = () => {
  if (!exchangeRateChart.value) return

  const ctx = exchangeRateChart.value.getContext('2d')

  // 환율 데이터 (최근 12개월)
  const labels = [
    '1월',
    '2월',
    '3월',
    '4월',
    '5월',
    '6월',
    '7월',
    '8월',
    '9월',
    '10월',
    '11월',
    '12월',
  ]
  const data = {
    labels: labels,
    datasets: [
      {
        type: 'line',
        label: currentLanguage.value === 'ko' ? '달러/원' : 'USD/KRW',
        data: [1270, 1290, 1310, 1320, 1330, 1320, 1300, 1290, 1280, 1275, 1270, 1260],
        borderColor: '#3772FF',
        backgroundColor: 'rgba(55, 114, 255, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        type: 'line',
        label: currentLanguage.value === 'ko' ? '유로/원' : 'EUR/KRW',
        data: [1380, 1390, 1400, 1410, 1420, 1410, 1400, 1390, 1380, 1375, 1370, 1365],
        borderColor: '#F2B705',
        backgroundColor: 'rgba(242, 183, 5, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        type: 'line',
        label: currentLanguage.value === 'ko' ? '엔/원(100엔)' : 'JPY/KRW(100)',
        data: [920, 925, 930, 940, 950, 945, 940, 935, 930, 925, 920, 915],
        borderColor: '#D95D39',
        backgroundColor: 'rgba(217, 93, 57, 0.1)',
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
          position: 'top',
        },
        tooltip: {
          mode: 'index',
          intersect: false,
        },
      },
    },
  })
}

// 차트 초기화 함수
const initCharts = () => {
  // 기존 차트 인스턴스 정리
  if (interestRateChartInstance) interestRateChartInstance.destroy()
  if (preciousMetalsChartInstance) preciousMetalsChartInstance.destroy()
  if (exchangeRateChartInstance) exchangeRateChartInstance.destroy()

  // 새 차트 생성
  createInterestRateChart()
  createPreciousMetalsChart()
  createExchangeRateChart()
}

onMounted(async () => {
  // Check auth status when the component mounts
  await userStore.checkAuth()

  // Load top products for initial tab
  loadTopProducts()

  // 차트 초기화
  setTimeout(() => {
    initCharts()
  }, 100)
})

// 컴포넌트가 언마운트되면 차트 인스턴스 정리
onBeforeUnmount(() => {
  if (interestRateChartInstance) interestRateChartInstance.destroy()
  if (preciousMetalsChartInstance) preciousMetalsChartInstance.destroy()
  if (exchangeRateChartInstance) exchangeRateChartInstance.destroy()
})

// KakaoMap 관련 변수와 메서드
const kakaoMap = ref(null)
const selectedBank = ref(null)

// 은행 클릭 이벤트 핸들러
const onBankClicked = (bank) => {
  console.log('Bank clicked:', bank)
  selectedBank.value = bank
}

// 카카오맵 URL 생성 함수
const getKakaoMapUrl = (bank) => {
  if (!bank || !bank.road_address_name) return '#'
  return `https://map.kakao.com/link/to/${bank.place_name},${bank.y},${bank.x}`
}

// Watch for tab changes
import { watch } from 'vue'
watch(activeTab, watchTabChange)

// Also watch for language changes to update error messages if needed
watch(currentLanguage, () => {
  if (topProductsError.value) {
    topProductsError.value =
      currentLanguage.value === 'ko'
        ? '상품 정보를 불러오는데 실패했습니다.'
        : 'Failed to load product information.'
  }
})
</script>

<style scoped>
/* 홈 컨테이너 */
.home-container {
  min-height: 100vh;
}

/* 영웅 섹션 */
.hero-section {
  background: linear-gradient(
    135deg,
    var(--color-background-start) 0%,
    var(--color-background-end) 100%
  );
  color: var(--color-text);
  padding: 100px 20px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.hero-section h1 {
  font-size: var(--font-size-5xl);
  margin-bottom: 20px;
  color: var(--color-accent);
  font-family: var(--font-heading);
  animation: fadeIn 1s ease-out;
}

.subtitle {
  font-size: var(--font-size-xl);
  margin-bottom: 40px;
  color: var(--color-text);
  font-family: var(--font-body);
  animation: fadeIn 1.2s ease-out;
}

.user-greeting {
  margin: 40px 0;
  font-size: var(--font-size-lg);
  animation: fadeIn 1.4s ease-out;
}

.auth-buttons,
.user-greeting {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 30px;
  animation: fadeIn 1.6s ease-out;
}

/* 추천 상품 섹션 */
.top-products-section {
  padding: 80px 20px;
  text-align: center;
  background-color: var(--color-white);
}

.top-products-section h2 {
  font-family: var(--font-heading);
  color: var(--color-accent);
  margin-bottom: 50px;
}

.tabs {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 40px;
}

.tabs button {
  padding: 12px 25px;
  border: 1px solid var(--color-secondary);
  background: var(--color-white);
  border-radius: 30px;
  font-family: var(--font-body);
  font-size: var(--font-size-base);
  cursor: pointer;
  transition: all var(--transition-normal);
  color: var(--color-text);
}

.tabs button.active {
  background: var(--color-primary);
  color: var(--color-white);
  border-color: var(--color-primary);
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.tabs button:hover:not(.active) {
  background: var(--color-secondary);
  transform: translateY(-2px);
}

.products-slider {
  max-width: 1200px;
  margin: 0 auto;
}

.product-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.product-card {
  background: var(--color-white);
  border: 1px solid var(--color-secondary);
  border-radius: 12px;
  padding: 25px;
  text-align: left;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.product-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background: linear-gradient(to right, var(--color-primary), var(--color-primary-dark));
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.product-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg);
}

.product-card:hover::before {
  opacity: 1;
}

.product-header {
  margin-bottom: 20px;
}

.product-header h3 {
  margin: 0 0 8px 0;
  font-size: var(--font-size-lg);
  color: var(--color-accent);
  font-family: var(--font-heading);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bank-name {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
}

.product-rate {
  background: linear-gradient(
    to bottom,
    var(--color-background-start),
    var(--color-background-end)
  );
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  text-align: center;
  box-shadow: var(--shadow-sm);
}

.rate-value {
  font-size: var(--font-size-3xl);
  font-weight: bold;
  color: var(--color-accent);
  font-family: var(--font-heading);
  line-height: 1.2;
  margin-bottom: 5px;
}

.rate-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
}

.product-meta {
  margin-bottom: 20px;
}

.join-methods {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.join-badge {
  font-size: var(--font-size-xs);
  background: var(--color-secondary);
  color: var(--color-text);
  padding: 4px 10px;
  border-radius: 15px;
  transition: background var(--transition-fast);
}

.join-badge:hover {
  background: var(--color-primary);
  color: var(--color-white);
}

.view-details-btn {
  width: 100%;
  padding: 12px 0;
  margin-top: 10px;
}

.view-all {
  margin-top: 30px;
}

.view-all-link {
  display: inline-block;
  padding: 12px 30px;
  color: var(--color-primary);
  font-weight: 500;
  text-decoration: none;
  border: 1px solid var(--color-primary);
  border-radius: 30px;
  transition: all var(--transition-normal);
}

.view-all-link:hover {
  background: var(--color-primary);
  color: var(--color-white);
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

/* 로딩 및 에러 메시지 */
.loading-indicator {
  padding: 60px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  color: var(--color-text-light);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-secondary);
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.error-message {
  padding: 40px 0;
  color: var(--color-error);
}

/* 기능 섹션 */
.features-section {
  padding: 80px 20px;
  text-align: center;
  background: linear-gradient(
    to bottom,
    var(--color-background-start),
    var(--color-background-end)
  );
}

.features-section h2 {
  font-size: var(--font-size-4xl);
  font-family: var(--font-heading);
  color: var(--color-accent);
  margin-bottom: 60px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  background: var(--color-white);
  border-radius: 12px;
  padding: 40px 30px;
  box-shadow: var(--shadow-md);
  transition:
    transform var(--transition-normal),
    box-shadow var(--transition-normal);
  position: relative;
  z-index: 1;
  overflow: hidden;
}

.feature-card::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background: linear-gradient(to right, var(--color-primary), var(--color-primary-dark));
  transition: height var(--transition-normal);
  z-index: -1;
}

.feature-card:hover {
  transform: translateY(-15px);
  box-shadow: var(--shadow-lg);
}

.feature-card:hover::after {
  height: 100%;
  opacity: 0.1;
}

.feature-icon {
  font-size: var(--font-size-5xl);
  margin-bottom: 25px;
  display: inline-block;
  transition: transform var(--transition-normal);
}

.feature-card:hover .feature-icon {
  transform: scale(1.2);
}

.feature-card h3 {
  margin: 0 0 15px;
  color: var(--color-accent);
  font-size: var(--font-size-xl);
  font-family: var(--font-heading);
}

.feature-card p {
  color: var(--color-text);
  margin: 0;
  font-family: var(--font-body);
}

/* 후기 섹션 */
.testimonials-section {
  padding: 80px 20px;
  background-color: var(--color-white);
  text-align: center;
}

.testimonials-section h2 {
  font-size: var(--font-size-4xl);
  font-family: var(--font-heading);
  color: var(--color-accent);
  margin-bottom: 50px;
}

.testimonials-slider {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
  justify-content: center;
  max-width: 1200px;
  margin: 0 auto;
}

.testimonial-card {
  background: linear-gradient(
    to bottom,
    var(--color-background-start),
    var(--color-background-end)
  );
  border-radius: 12px;
  padding: 30px;
  max-width: 400px;
  box-shadow: var(--shadow-md);
  text-align: left;
  transition: transform var(--transition-normal);
  position: relative;
}

.testimonial-card::before {
  content: '"';
  position: absolute;
  top: 20px;
  left: 20px;
  font-size: 60px;
  font-family: var(--font-heading);
  color: var(--color-primary);
  opacity: 0.2;
  line-height: 1;
}

.testimonial-card:hover {
  transform: translateY(-10px);
}

.testimonial-content {
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.testimonial-content p {
  font-size: var(--font-size-base);
  color: var(--color-text);
  line-height: 1.7;
  font-style: italic;
}

.testimonial-author {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.author-name {
  font-weight: 600;
  font-size: var(--font-size-base);
  margin-bottom: 5px;
  color: var(--color-accent);
}

.author-info {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
}

/* 금융 데이터 차트 섹션 */
.financial-data-section {
  padding: 80px 20px;
  background-color: var(--color-white);
  border-top: 1px solid var(--color-secondary);
}

.financial-data-section h2 {
  font-family: var(--font-heading);
  color: var(--color-accent);
  margin-bottom: 50px;
  text-align: center;
}

.financial-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
  margin: 0 auto;
}

.chart-card {
  background-color: var(--color-white);
  border-radius: 12px;
  padding: 20px;
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
  color: var(--color-accent);
  font-family: var(--font-heading);
}

.chart-container {
  height: 300px;
  position: relative;
}

/* 반응형 스타일 */
@media (max-width: 992px) {
  .hero-section h1 {
    font-size: var(--font-size-4xl);
  }

  .subtitle {
    font-size: var(--font-size-lg);
  }

  .features-section h2,
  .top-products-section h2,
  .financial-data-section h2 {
    font-size: var(--font-size-3xl);
  }

  .financial-charts {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 70px 20px;
  }

  .hero-section h1 {
    font-size: var(--font-size-3xl);
  }

  .subtitle {
    font-size: var(--font-size-base);
  }

  .chart-container {
    height: 250px;
  }

  .features-section h2,
  .top-products-section h2,
  .testimonials-section h2 {
    font-size: var(--font-size-2xl);
    margin-bottom: 40px;
  }

  .features-grid,
  .product-cards {
    gap: 20px;
  }

  .auth-buttons {
    flex-direction: column;
    align-items: center;
  }

  .tabs {
    flex-direction: column;
    align-items: center;
  }

  .tabs button {
    width: 100%;
    max-width: 300px;
  }

  .view-all-link {
    width: 100%;
    max-width: 300px;
  }
}

@media (max-width: 576px) {
  .hero-section {
    padding: 50px 15px;
  }

  .hero-section h1 {
    font-size: var(--font-size-2xl);
  }

  .subtitle {
    font-size: var(--font-size-base);
    margin-bottom: 30px;
  }

  .product-card {
    padding: 20px;
  }

  .feature-card {
    padding: 30px 20px;
  }
}
/* 지점 찾기 섹션 스타일 */
.branch-finder-section {
  padding: 80px 20px;
  margin-bottom: 50px;
}

.branch-finder-section h2 {
  text-align: center;
  margin-bottom: 20px;
  font-family: var(--font-heading);
  color: var(--color-accent);
}

.section-description {
  text-align: center;
  margin-bottom: 40px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  color: var(--color-text-light);
}

.dark .section-description {
  color: var(--color-text-dark);
}

.map-container {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  height: 500px;
  margin-bottom: 30px;
}

.bank-info-panel {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(245, 245, 245, 0.9) 100%);
  border-radius: 12px;
  padding: 25px;
  box-shadow: var(--shadow-sm);
  max-width: 800px;
  margin: 0 auto;
  transition: all var(--transition-normal);
}

.dark .bank-info-panel {
  background: linear-gradient(135deg, rgba(40, 40, 40, 0.8) 0%, rgba(30, 30, 30, 0.8) 100%);
  box-shadow: var(--shadow-dark);
}

.bank-info-panel h3 {
  margin-bottom: 20px;
  font-family: var(--font-heading);
  font-size: var(--font-size-lg);
  color: var(--color-accent);
}

.bank-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bank-details p {
  font-size: var(--font-size-base);
  color: var(--color-text);
  line-height: 1.5;
}

.directions-link {
  margin-top: 15px;
}

.btn-directions {
  display: inline-block;
  padding: 8px 16px;
  background-color: var(--color-primary);
  color: var(--color-white);
  text-decoration: none;
  border-radius: 6px;
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
}

.btn-directions:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-2px);
}
</style>

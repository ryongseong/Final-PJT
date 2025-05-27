<template>
  <div class="stock-detail-container">
    <div class="container py-4">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">주식 정보를 불러오는 중입니다...</p>
      </div>
      <div v-else-if="stockData" class="stock-data">
        <div class="card mb-4">
          <div
            class="card-header bg-gradient-light d-flex justify-content-between align-items-center py-3"
          >
            <!-- Back link -->
            <router-link
              to="/products/stocks"
              class="btn btn-outline-secondary d-flex align-items-center"
            >
              <i class="bi bi-arrow-left me-2"></i> 주식 랭킹으로 돌아가기
            </router-link>

            <div class="d-flex align-items-center">
              <span class="badge bg-info text-white me-2">실시간</span>
              <small class="text-muted">{{ stockData.date }} 기준</small>
            </div>
          </div>

          <div class="card-body p-4">
            <!-- 1. Company name with code -->
            <div class="mb-4 d-flex justify-content-between align-items-center flex-wrap">
              <div>
                <h1 class="mb-1 fw-bold d-flex align-items-center">
                  {{ stockData.name }}
                  <span class="badge bg-secondary ms-2 rounded-pill">{{ stockData.code }}</span>
                </h1>
                <div class="d-flex align-items-center text-muted">
                  <i class="bi bi-clock me-1"></i>
                  <small>매일 장 마감 후 업데이트</small>
                </div>
              </div>
            </div>

            <!-- 2 & 3. Current amount and Increase/decrease information -->
            <div
              class="price-card mb-4 px-4 py-4 rounded-3"
              :class="{
                'bg-success-subtle': stockData.price_change > 0,
                'bg-danger-subtle': stockData.price_change < 0,
                'bg-light': stockData.price_change === 0,
              }"
            >
              <div class="row">
                <div class="col-md-6">
                  <h6 class="text-muted mb-2">현재가</h6>
                  <h1
                    class="display-4 mb-2 fw-bold"
                    :class="{
                      'text-success': stockData.price_change > 0,
                      'text-danger': stockData.price_change < 0,
                    }"
                  >
                    {{ formatPrice(stockData.current_price) }}
                  </h1>
                  <div class="d-flex align-items-center">
                    <h4
                      :class="{
                        'text-success': stockData.price_change > 0,
                        'text-danger': stockData.price_change < 0,
                        'text-secondary': stockData.price_change === 0,
                      }"
                    >
                      {{ formatPriceChange(stockData.price_change) }}
                      ({{ stockData.change_rate }}%)
                      <i
                        :class="[
                          stockData.price_change > 0
                            ? 'bi bi-arrow-up-right'
                            : 'bi bi-arrow-down-right',
                          'ms-1',
                        ]"
                      ></i>
                    </h4>
                  </div>
                </div>
                <div class="col-md-6 mt-3 mt-md-0">
                  <div class="row g-2">
                    <div class="col-6">
                      <div class="p-2 rounded bg-white bg-opacity-75">
                        <div class="small text-muted mb-1">거래량</div>
                        <div class="fw-bold">1,248,900주</div>
                      </div>
                    </div>
                    <div class="col-6">
                      <div class="p-2 rounded bg-white bg-opacity-75">
                        <div class="small text-muted mb-1">시가총액</div>
                        <div class="fw-bold">32.5조원</div>
                      </div>
                    </div>
                    <div class="col-6">
                      <div class="p-2 rounded bg-white bg-opacity-75">
                        <div class="small text-muted mb-1">52주 최고</div>
                        <div class="fw-bold text-success">
                          {{ formatPrice(stockData.current_price * 1.2) }}
                        </div>
                      </div>
                    </div>
                    <div class="col-6">
                      <div class="p-2 rounded bg-white bg-opacity-75">
                        <div class="small text-muted mb-1">52주 최저</div>
                        <div class="fw-bold text-danger">
                          {{ formatPrice(stockData.current_price * 0.85) }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 4. Stock price history chart -->
            <div class="chart-section mt-4">
              <h3 class="mb-3">주가 추이</h3>
              <div v-if="stockData.candles && stockData.candles.length > 0" class="chart-container">
                <canvas ref="chartCanvas"></canvas>
              </div>
              <div v-else class="text-center py-4 bg-light rounded">
                <i class="bi bi-graph-up" style="font-size: 3rem"></i>
                <p class="mb-0">주가 차트 데이터가 없습니다</p>
              </div>
            </div>

            <!-- Price history table -->
            <div
              class="price-history mt-4"
              v-if="stockData.candles && stockData.candles.length > 0"
            >
              <h3 class="mb-3">가격 히스토리</h3>
              <div class="table-responsive">
                <table class="table table-bordered table-striped table-hover">
                  <thead class="table-dark">
                    <tr>
                      <th>날짜</th>
                      <th>시가</th>
                      <th>고가</th>
                      <th>저가</th>
                      <th>종가</th>
                      <th>전일대비</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(candle, index) in stockData.candles.slice(0, 10)" :key="index">
                      <td>{{ new Date(candle.dt).toLocaleDateString() }}</td>
                      <td>{{ formatPrice(candle.open) }}</td>
                      <td>{{ formatPrice(candle.high) }}</td>
                      <td>{{ formatPrice(candle.low) }}</td>
                      <td
                        :class="{
                          'text-success': candle.close > candle.base,
                          'text-danger': candle.close < candle.base,
                        }"
                      >
                        {{ formatPrice(candle.close) }}
                      </td>
                      <td
                        :class="{
                          'text-success': candle.close > candle.base,
                          'text-danger': candle.close < candle.base,
                        }"
                      >
                        {{ formatPriceChange(candle.close - candle.base) }}
                        ({{ calculateChangeRate(candle.close, candle.base) }}%)
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-5 mt-4">
        <div class="alert alert-warning">
          <h4>주식 정보를 불러올 수 없습니다</h4>
          <p class="mb-0">
            요청하신 종목 코드에 대한 정보를 찾을 수 없습니다. 올바른 종목 코드인지 확인해주세요.
          </p>
        </div>
        <router-link to="/products/stocks" class="btn btn-primary mt-3">
          주식 랭킹으로 돌아가기
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import Chart from 'chart.js/auto'

const router = useRouter()
const route = useRoute()
const baseUrl = 'http://localhost:8000/products'
const stockCode = computed(() => route.params.stockCode)

const stockData = ref(null)
const loading = ref(true)

// Stock name mapping (replace with actual names or API call)
// 주요 한국 상장 기업 코드-이름 매핑
const stockNameMapping = {
  // KOSPI 상위
  A005930: '삼성전자',
  A000660: 'SK하이닉스',
  A035420: 'NAVER',
  A035720: '카카오',
  A005380: '현대차',
  A051910: 'LG화학',
  A006400: '삼성SDI',
  A000270: '기아',
  A373220: 'LG에너지솔루션',
  A003550: 'LG',
  A105560: 'KB금융',
  A055550: '신한지주',
  A066570: 'LG전자',
  A096770: 'SK이노베이션',
  A000810: '삼성화재',
  A015760: '한국전력',
  A316140: '우리금융지주',
  A012330: '현대모비스',
  A017670: 'SK텔레콤',
  A090430: '아모레퍼시픽',

  // 바이오 및 제약
  A068270: '셀트리온',
  A207940: '삼성바이오로직스',
  A128940: '한미약품',
  A302440: 'SK바이오사이언스',
  A028300: 'HLB',
  A326030: 'SK바이오팜',
  A068760: '셀트리온제약',
  A145720: '덴티움',
  A096530: '씨젠',

  // 반도체 및 IT
  A042700: '한미반도체',
  A058470: '리노공업',
  A011070: 'LG이노텍',
  A000990: 'DB하이텍',
  A039030: '이오테크닉스',
  A005290: '동진쎄미켐',
  A036930: '주성엔지니어링',
  A094360: '칩스앤미디어',
  A054620: 'APS홀딩스',

  // 금융
  A086790: '하나금융지주',
  A138930: 'BNK금융지주',
  A175330: 'JB금융지주',
  A139130: 'DGB금융지주',
  A005940: 'NH투자증권',
  A016360: '삼성증권',
  A008560: '메리츠증권',
  A039490: '키움증권',
  A071050: '한국금융지주',

  // 통신 및 미디어
  A030200: 'KT',
  A032640: 'LG유플러스',
  A036570: '엔씨소프트',
  A251270: '넷마블',
  A263750: '펄어비스',
  A259960: '크래프톤',
  A112040: '위메이드',
  A095660: '네오위즈',
  A067160: '아프리카TV',
  // 자동차 및 부품
  A000240: '한국앤컴퍼니',
  A011210: '현대위아',
  A009150: '삼성전기',
  A010120: 'LS ELECTRIC',
  A010950: 'S-Oil',
  A078930: 'GS',
  A267250: 'HD현대',

  // 철강 및 소재
  A005490: 'POSCO홀딩스',
  A004020: '현대제철',
  A001230: '동국제강',
  A003670: '포스코퓨처엠',
  A008930: '한미사이언스',
  A011780: '금호석유',

  // 유통 및 소비재
  A004170: '신세계',
  A028260: '삼성물산',
  A023530: '롯데쇼핑',
  A021240: '코웨이',
  A036460: '한국가스공사',
  A003490: '대한항공',
  A180640: '한진칼',
  A047810: '한국항공우주',
  A009830: '한화솔루션',
  A079550: 'LIG넥스원',
  // 기타 추가 기업들
  A352820: '하이브',
  A241560: '두산밥캣',
  A034020: '두산에너빌리티',
  A139480: '이마트',
  A097950: 'CJ제일제당',
  A324090: '토스',
  A293490: '카카오페이',
}

// Get stock name from code
const getStockNameByCode = (code) => {
  // Check if we have a mapping for this code
  if (code && stockNameMapping[code]) {
    return stockNameMapping[code]
  }
  // If not, return a generic name with the code
  return `종목 ${code}`
}

const calculateChangeRate = (currentPrice, basePrice) => {
  if (!basePrice) return '0.00'
  const rate = ((currentPrice - basePrice) / basePrice) * 100
  return rate.toFixed(2)
}

// 주식 상세 정보 가져오기
const fetchStockDetails = async () => {
  if (!stockCode.value) {
    router.push('/products/stocks')
    return
  }
  try {
    loading.value = true
    const response = await axios.get(`${baseUrl}/stock-details/${stockCode.value}/`)
    console.log('API Response:', response.data)

    if (response.data && response.data.result) {
      // Check if it's the new candles format
      if (response.data.result.candles) {
        const candleData = response.data.result
        // Take the latest candle for current price data
        const latestCandle = candleData.candles[0]

        // Get stock name from mapping or use code as fallback
        const stockName = getStockNameByCode(candleData.code)

        // Transform the data to match the template expectations
        stockData.value = {
          code: candleData.code,
          name: stockName,
          date: new Date(latestCandle.dt).toLocaleDateString(),
          current_price: latestCandle.close,
          price_change: latestCandle.close - latestCandle.base,
          change_rate: calculateChangeRate(latestCandle.close, latestCandle.base),
          candles: candleData.candles,
        }

        console.log('Stock data with candles loaded:', stockData.value)
      } else if (response.data.result.product) {
        // Original format
        const productData = response.data.result.product

        // Transform the data to match the template expectations
        stockData.value = {
          code: productData.productCode,
          name: productData.name || getStockNameByCode(productData.productCode),
          date: new Date().toLocaleDateString(),
          current_price: productData.price?.close || 0,
          price_change: productData.price ? productData.price.close - productData.price.base : 0,
          change_rate: calculateChangeRate(productData.price?.close, productData.price?.base),
          candles: [], // This format might not include candles
        }

        console.log('Stock data without candles loaded:', stockData.value)
      }
    } else {
      stockData.value = null
      console.error('Unexpected response format:', response.data)
    }
  } catch (error) {
    console.error('Error fetching stock details:', error)
    stockData.value = null
  } finally {
    loading.value = false
  }
}

// 포맷팅 함수들
const formatNumber = (num) => {
  return new Intl.NumberFormat('ko-KR').format(num)
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('ko-KR', { style: 'currency', currency: 'KRW' }).format(price)
}

const formatPriceChange = (change) => {
  if (change > 0) {
    return `+${formatNumber(change)}`
  } else {
    return formatNumber(change)
  }
}

const chartCanvas = ref(null)
let priceChart = null

// Function to render the chart
const renderChart = async () => {
  // Wait for DOM update
  await nextTick()

  console.log('Chart canvas element:', chartCanvas.value)
  console.log('Stock data candles:', stockData.value?.candles?.length)

  if (!chartCanvas.value) {
    console.error('Chart canvas element not found')
    return
  }

  if (!stockData.value?.candles || stockData.value.candles.length === 0) {
    console.error('No candle data available for chart')
    return
  }

  console.log('Rendering chart with candles:', stockData.value.candles.length)

  // Destroy existing chart if it exists
  if (priceChart) {
    priceChart.destroy()
  }

  try {
    // Reverse candles to show oldest first
    const candles = [...stockData.value.candles].reverse()

    // Prepare data for chart
    const labels = candles.map((candle) => {
      const date = new Date(candle.dt)
      return `${date.getMonth() + 1}/${date.getDate()}`
    })

    const priceData = candles.map((candle) => candle.close) // Determine chart color based on price trend
    const firstPrice = priceData[0]
    const lastPrice = priceData[priceData.length - 1]
    const priceIncreased = lastPrice > firstPrice

    // Define gradient colors based on trend
    const gradientColor = priceIncreased
      ? { start: 'rgba(25, 135, 84, 0.1)', end: 'rgba(25, 135, 84, 0.5)' }
      : { start: 'rgba(220, 53, 69, 0.1)', end: 'rgba(220, 53, 69, 0.5)' }

    const borderColor = priceIncreased ? 'rgba(25, 135, 84, 1)' : 'rgba(220, 53, 69, 1)'

    // Create chart
    const ctx = chartCanvas.value.getContext('2d')

    // Create gradient fill
    const gradient = ctx.createLinearGradient(0, 0, 0, 300)
    gradient.addColorStop(0, gradientColor.end)
    gradient.addColorStop(1, gradientColor.start)

    priceChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: `${stockData.value.name} 주가`,
            data: priceData,
            backgroundColor: gradient,
            borderColor: borderColor,
            borderWidth: 2.5,
            tension: 0.2,
            fill: true,
            pointRadius: 3,
            pointBackgroundColor: 'white',
            pointBorderColor: borderColor,
            pointBorderWidth: 2,
            pointHoverRadius: 5,
            pointHoverBorderWidth: 3,
            pointHoverBackgroundColor: 'white',
            pointHoverBorderColor: borderColor,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: 'index',
        },
        scales: {
          y: {
            beginAtZero: false,
            grid: {
              color: 'rgba(0, 0, 0, 0.05)',
              drawBorder: false,
            },
            ticks: {
              font: {
                size: 12,
                weight: '500',
              },
              padding: 10,
              callback: function (value) {
                return value.toLocaleString() + '원'
              },
            },
          },
          x: {
            grid: {
              display: false,
              drawBorder: false,
            },
            ticks: {
              font: {
                size: 12,
                weight: '500',
              },
              maxRotation: 0,
              padding: 10,
            },
          },
        },
        plugins: {
          tooltip: {
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            titleColor: '#000',
            bodyColor: '#333',
            titleFont: {
              size: 14,
              weight: 'bold',
              family: "'Noto Sans KR', sans-serif",
            },
            bodyFont: {
              size: 13,
              family: "'Noto Sans KR', sans-serif",
            },
            borderColor: 'rgba(0, 0, 0, 0.1)',
            borderWidth: 1,
            cornerRadius: 8,
            padding: 12,
            boxPadding: 6,
            usePointStyle: true,
            callbacks: {
              title: (context) => {
                const candle = candles[context[0].dataIndex]
                return new Date(candle.dt).toLocaleDateString() + ' 거래 정보'
              },
              label: function (context) {
                const candle = candles[context.dataIndex]
                const priceChangeText =
                  candle.close > candle.base
                    ? `▲ ${(candle.close - candle.base).toLocaleString()}원 (+${calculateChangeRate(candle.close, candle.base)}%)`
                    : `▼ ${(candle.base - candle.close).toLocaleString()}원 (${calculateChangeRate(candle.close, candle.base)}%)`

                return [
                  `종가: ${candle.close.toLocaleString()}원`,
                  `시가: ${candle.open.toLocaleString()}원`,
                  `고가: ${candle.high.toLocaleString()}원`,
                  `저가: ${candle.low.toLocaleString()}원`,
                  `전일대비: ${priceChangeText}`,
                ]
              },
            },
          },
          legend: {
            display: true,
            position: 'top',
            align: 'end',
            labels: {
              boxWidth: 15,
              usePointStyle: true,
              pointStyle: 'circle',
              padding: 20,
              font: {
                size: 13,
                weight: '600',
                family: "'Noto Sans KR', sans-serif",
              },
            },
          },
        },
      },
    })
    console.log('Chart successfully rendered')
  } catch (error) {
    console.error('Error rendering chart:', error)
  }
}

// Watch for data changes to render chart
watch(
  () => stockData.value,
  async (newValue) => {
    if (newValue && newValue.candles && newValue.candles.length > 0) {
      console.log('Stock data updated, rendering chart...')
      // Use setTimeout to ensure DOM is ready
      setTimeout(renderChart, 300)
    }
  },
  { deep: true },
)

onMounted(async () => {
  await fetchStockDetails()
  if (stockData.value?.candles?.length > 0) {
    // Use setTimeout to ensure DOM is ready
    setTimeout(renderChart, 300)
  }
})
</script>

<style scoped>
.stock-detail-container {
  background-color: #f8f9fa;
  min-height: 100vh;
  padding-bottom: 3rem;
}

.card {
  box-shadow: 0 0.5rem 1.5rem rgba(0, 0, 0, 0.08) !important;
  border: none !important;
  border-radius: 0.75rem !important;
  overflow: hidden;
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 1rem 2rem rgba(0, 0, 0, 0.12) !important;
}

.chart-container {
  position: relative;
  height: 400px;
  width: 100%;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 0.25rem 0.75rem rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.chart-section,
.price-history {
  border-top: 1px solid #dee2e6;
  padding-top: 2rem;
  margin-top: 1rem;
}

.table-responsive {
  overflow-x: auto;
  border-radius: 0.75rem;
  box-shadow: 0 0.25rem 0.75rem rgba(0, 0, 0, 0.08);
}

.table-dark th {
  background: linear-gradient(45deg, #343a40, #495057);
  color: white;
  border-color: #454d55;
  font-weight: 600;
  padding: 1rem;
}

.table {
  margin-bottom: 0;
  border-collapse: separate;
  border-spacing: 0;
}

.table tbody td {
  padding: 0.75rem 1rem;
  vertical-align: middle;
}

.table-striped tbody tr:nth-of-type(odd) {
  background-color: rgba(0, 0, 0, 0.02);
}

.table-hover tbody tr:hover {
  background-color: rgba(13, 110, 253, 0.05);
}

/* Price display styling */
.display-4 {
  letter-spacing: -1px;
  font-weight: 700 !important;
}

.text-success {
  color: #198754 !important;
}

.text-danger {
  color: #dc3545 !important;
}

/* Back button styling */
.btn-outline-secondary {
  transition: all 0.2s ease;
}

.btn-outline-secondary:hover {
  background-color: #6c757d;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Custom scrollbar */
.table-responsive::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.table-responsive::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.table-responsive::-webkit-scrollbar-thumb {
  background: #0d6efd;
  border-radius: 4px;
}

.table-responsive::-webkit-scrollbar-thumb:hover {
  background: #0a58ca;
}

.bg-gradient-light {
  background: linear-gradient(to right, #f8f9fa, #e9ecef);
}

.price-card {
  box-shadow: 0 0.25rem 0.75rem rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.bg-success-subtle {
  background-color: rgba(25, 135, 84, 0.1);
}

.bg-danger-subtle {
  background-color: rgba(220, 53, 69, 0.1);
}

/* Enhanced badges */
.badge.rounded-pill {
  font-size: 0.85rem;
  padding: 0.4rem 0.8rem;
}

.badge.bg-info {
  background-color: #0dcaf0 !important;
}

/* Button hover effects */
.btn-outline-warning {
  transition: all 0.2s ease;
}

.btn-outline-warning:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(255, 193, 7, 0.2);
}

@media (max-width: 768px) {
  .table {
    font-size: 0.85rem;
  }

  .chart-container {
    height: 300px;
    padding: 1rem;
  }

  .display-4 {
    font-size: 2.5rem;
  }
}

/* Animation for price change */
@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.text-success,
.text-danger {
  animation: pulse 1s ease-in-out;
}
</style>

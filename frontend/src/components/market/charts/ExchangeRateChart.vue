<template>
  <div class="chart-wrapper">
    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>{{ $t('market.loadingData') }}</p>
    </div>
    <div v-else-if="error" class="error-state">
      <p>{{ $t('market.errorLoadingData') }}</p>
      <button @click="retryLoading" class="retry-button">
        {{ $t('market.retry') }}
      </button>
    </div>
    <div v-else class="chart-container">
      <div class="chart-header">
        <p class="chart-title">{{ locale === 'ko' ? '환율 정보' : 'Exchange Rates' }}</p>
        <p class="chart-subtitle">{{ locale === 'ko' ? '(KRW 기준)' : '(Based on KRW)' }}</p>
      </div>
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, reactive } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useI18n } from 'vue-i18n'
import Chart from 'chart.js/auto'
import productsService from '@/services/products'

const chartCanvas = ref(null)
const chart = ref(null)
const settingsStore = useSettingsStore()
const { locale } = useI18n()

const isLoading = ref(true)
const error = ref(null)
const currentDate = ref('')
const chartData = reactive({
  labels: [],
  datasets: [
    {
      label: locale.value === 'ko' ? '환율 (KRW)' : 'Exchange Rate (KRW)',
      data: [],
      backgroundColor: 'rgba(16, 185, 129, 0.15)',
      borderColor: '#10B981',
      borderWidth: 3,
      tension: 0.4,
      fill: true,
      pointRadius: 6,
      pointBackgroundColor: [
        '#10B981', // USD - 초록색
        '#3B82F6', // EUR - 파란색
        '#EC4899', // JPY - 분홍색
        '#8B5CF6', // GBP - 보라색
      ],
      pointBorderColor: '#fff',
      pointHoverRadius: 8,
      pointBorderWidth: 2,
    },
  ],
})

// 최근 6개월 데이터 가져오기
const fetchExchangeRates = async () => {
  isLoading.value = true
  error.value = null

  try {
    const response = await productsService.getExchangeRate()

    // 현재 날짜 설정
    updateCurrentDate()

    // 환율 데이터 처리
    if (Array.isArray(response) && response.length > 0) {
      // 표시할 주요 통화 선택 (USD, EUR, JPY, GBP)
      const mainCurrencies = ['USD', 'EUR', 'JPY(100)', 'GBP']
      const filteredRates = response.filter((rate) => mainCurrencies.includes(rate.cur_unit))

      // 차트 데이터 업데이트
      chartData.labels = filteredRates.map((rate) =>
        locale.value === 'ko' ? rate.cur_nm : rate.cur_unit,
      ) // 각 통화별로 데이터셋 생성
      const colors = [
        { border: '#10B981', background: 'rgba(16, 185, 129, 0.15)' }, // USD - 초록색
        { border: '#3B82F6', background: 'rgba(59, 130, 246, 0.15)' }, // EUR - 파란색
        { border: '#EC4899', background: 'rgba(236, 72, 153, 0.15)' }, // JPY - 분홍색
        { border: '#8B5CF6', background: 'rgba(139, 92, 246, 0.15)' }, // GBP - 보라색
      ]

      // 임시로 모든 통화의 데이터를 함께 표현
      const ratesData = filteredRates.map((rate) => {
        return parseFloat(rate.deal_bas_r.replace(/,/g, ''))
      })

      chartData.labels = filteredRates.map((rate) =>
        locale.value === 'ko' ? rate.cur_nm : rate.cur_unit,
      )

      chartData.datasets = [
        {
          label: locale.value === 'ko' ? '환율 (KRW)' : 'Exchange Rate (KRW)',
          data: ratesData,
          borderColor: '#10B981',
          backgroundColor: 'rgba(16, 185, 129, 0.15)',
          borderWidth: 3,
          tension: 0.4,
          fill: true,
          pointBackgroundColor: colors.map((color) => color.border),
          pointBorderColor: '#fff',
        },
      ]

      isLoading.value = false
    } else {
      // 데이터 형식이 예상과 다를 경우 기본 데이터 사용
      useDefaultData()
    }
  } catch (err) {
    console.error('환율 데이터 로딩 중 오류 발생:', err)
    error.value = err.message || '환율 데이터를 가져오는 중 오류가 발생했습니다.'
    isLoading.value = false

    // 오류 발생 시 데모 데이터 사용
    useDefaultData()
  }
}

// 현재 날짜 설정 함수
const updateCurrentDate = () => {
  const now = new Date()
  if (locale.value === 'ko') {
    currentDate.value = `${now.getFullYear()}년 ${now.getMonth() + 1}월 ${now.getDate()}일`
  } else {
    currentDate.value = now.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }
}

// 데모 데이터 (API 오류 시 사용)
const useDefaultData = () => {
  // 데모 데이터 사용 시에도 날짜 업데이트
  updateCurrentDate()
  const currencies =
    locale.value === 'ko'
      ? ['미국 달러', '유로', '일본 옌', '영국 파운드']
      : ['USD', 'EUR', 'JPY(100)', 'GBP']

  chartData.labels = currencies
  // 모의 데이터
  const ratesData = [1378.4, 1555.94, 958.59, 1850.36]
  chartData.datasets = [
    {
      label: locale.value === 'ko' ? '환율 (KRW)' : 'Exchange Rate (KRW)',
      data: ratesData,
      borderColor: '#10B981',
      backgroundColor: 'rgba(16, 185, 129, 0.15)',
      borderWidth: 3,
      tension: 0.4,
      fill: true,
      pointBackgroundColor: [
        '#10B981', // USD - 초록색
        '#3B82F6', // EUR - 파란색
        '#EC4899', // JPY - 분홍색
        '#8B5CF6', // GBP - 보라색
      ],
      pointBorderColor: '#fff',
    },
  ]
}

// 데이터 로딩 재시도
const retryLoading = async () => {
  await fetchExchangeRates()
  createChart()
}

// 차트 데이터 반환 함수
const getChartData = () => {
  return {
    labels: chartData.labels,
    datasets: chartData.datasets,
  }
}

const createChart = () => {
  if (chartCanvas.value) {
    // 이전 차트 인스턴스 제거
    if (chart.value) {
      chart.value.destroy()
    }

    const ctx = chartCanvas.value.getContext('2d')

    // 다크모드에 따른 글자색 설정
    const textColor = settingsStore.isDarkMode ? '#F0ECE6' : '#333333'
    const gridColor = settingsStore.isDarkMode ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)'

    chart.value = new Chart(ctx, {
      // type: 'line',
      type: 'bar',
      data: getChartData(),
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 1000,
          easing: 'easeOutQuart',
        },
        plugins: {
          legend: {
            position: 'top',
            align: 'center',
            labels: {
              color: textColor,
              usePointStyle: true,
              pointStyle: 'circle',
              font: {
                family: 'Inter, sans-serif',
                size: 14,
              },
              padding: 20,
              boxWidth: 10,
              boxHeight: 10,
            },
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: settingsStore.isDarkMode
              ? 'rgba(58, 58, 58, 0.95)'
              : 'rgba(255, 255, 255, 0.95)',
            titleColor: textColor,
            bodyColor: textColor,
            borderColor: gridColor,
            borderWidth: 1,
            padding: 12,
            cornerRadius: 8,
            bodyFont: {
              family: 'Inter, sans-serif',
              size: 14,
            },
            titleFont: {
              family: 'Inter, sans-serif',
              size: 16,
              weight: 'bold',
            },
            displayColors: true,
            boxPadding: 8,
            callbacks: {
              title: function (tooltipItems) {
                return tooltipItems[0].label
              },
              label: function (context) {
                let label = context.dataset.label || ''
                if (label) {
                  label += ': '
                }
                if (context.parsed.y !== null) {
                  label += new Intl.NumberFormat('ko-KR').format(context.parsed.y) + ' 원'
                }
                return label
              },
            },
            animation: {
              duration: 150,
            },
          },
          title: {
            display: false, // 이미 템플릿에서 제목을 추가했으므로 여기서는 표시하지 않음
          },
        },
        scales: {
          x: {
            grid: {
              color: gridColor,
              drawBorder: false,
              display: false,
            },
            border: {
              display: false,
            },
            ticks: {
              color: textColor,
              font: {
                family: 'Inter, sans-serif',
                size: 13,
                weight: '500',
              },
              padding: 15,
            },
            title: {
              display: false,
              text: locale.value === 'ko' ? '통화' : 'Currency',
              color: textColor,
              font: {
                family: 'Inter, sans-serif',
                size: 14,
                weight: 'bold',
              },
              // padding: { top: 15 },
            },
          },
          y: {
            grid: {
              color: gridColor,
              drawBorder: false,
              borderDash: [4, 4],
              z: -1,
            },
            border: {
              display: false,
            },
            ticks: {
              color: textColor,
              font: {
                family: 'Inter, sans-serif',
                size: 13,
                weight: '500',
              },
              padding: 12,
              callback: function (value) {
                return value.toLocaleString('ko-KR') + '원'
              },
              maxTicksLimit: 7, // 적절한 눈금 간격을 유지
            },
            title: {
              display: true,
              text: locale.value === 'ko' ? '원화 가치' : 'KRW Value',
              color: textColor,
              font: {
                family: 'Inter, sans-serif',
                size: 14,
                weight: 'bold',
              },
              padding: { bottom: 15 },
            },
            beginAtZero: false,
          },
        },
        elements: {
          line: {
            tension: 0.4,
            borderWidth: 3,
            fill: true,
          },
          point: {
            radius: 4,
            hitRadius: 10,
            hoverRadius: 6,
            borderWidth: 2,
            hoverBorderWidth: 2,
          },
        },
        layout: {
          padding: {
            top: 15,
            right: 25,
            bottom: 15,
            left: 15,
          },
        },
        interaction: {
          mode: 'index',
          intersect: false,
        },
        hover: {
          mode: 'index',
          intersect: false,
        },
      },
    })
  }
}

// 다크모드 변경 감지
watch(
  () => settingsStore.isDarkMode,
  () => {
    createChart()
  },
)

// 언어 변경 감지
window.addEventListener('languageChanged', () => {
  createChart()
})

onMounted(async () => {
  // 초기 날짜 설정
  updateCurrentDate()

  // 초기 데이터 로드
  await fetchExchangeRates()

  // 차트 생성
  createChart()

  // 창 크기 변경 시 차트 리사이징
  window.addEventListener('resize', createChart)
})

// 언어 변경 시 차트 라벨 업데이트
watch(locale, async () => {
  await fetchExchangeRates()
  createChart()
})

onBeforeUnmount(() => {
  if (chart.value) {
    chart.value.destroy()
  }
  window.removeEventListener('resize', createChart)
  window.removeEventListener('languageChanged', createChart)
})
</script>

<style scoped>
.chart-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  /* padding: 1rem 0; */
}

.chart-container {
  width: 100%;
  height: 100%;
  position: relative;
  padding: 1.5rem;
  border-radius: 12px;
  background-color: rgba(255, 255, 255, 0.8);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.04);
  margin: 0.75rem;
  max-width: calc(100% - 1.5rem);
  max-height: calc(100% - 1.5rem);
}

.dark .chart-container {
  background-color: rgba(30, 30, 30, 0.8);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.chart-header {
  margin-bottom: 1rem;
  position: relative;
}

.chart-title {
  text-align: center;
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
  margin-top: 0;
  color: #333;
  letter-spacing: -0.02em;
  position: relative;
  display: inline-block;
  left: 50%;
  transform: translateX(-50%);
}

.chart-title::after {
  content: '';
  display: block;
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, var(--accent-color), var(--accent-hover));
  border-radius: 3px;
  margin: 0.5rem auto 0;
}

.dark .chart-title {
  color: #f0ece6;
}

.chart-subtitle {
  text-align: center;
  font-size: 1rem;
  color: #666;
  margin-top: 0;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.chart-update-date {
  text-align: center;
  font-size: 0.85rem;
  font-style: italic;
  color: #777;
  margin: 0.5rem 0 1rem;
}

.dark .chart-update-date {
  color: #999;
}

.dark .chart-subtitle {
  color: #aaa;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 2rem;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: var(--accent-color);
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.dark .loading-spinner {
  border-color: rgba(255, 255, 255, 0.1);
  border-top-color: var(--accent-color);
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.retry-button {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background-color: var(--accent-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-button:hover {
  background-color: var(--accent-hover);
  transform: translateY(-2px);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15);
}

/* Animation for chart container */
@keyframes fadeIn {
  0% {
    opacity: 0;
    transform: translateY(10px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.chart-container {
  animation: fadeIn 0.6s ease-out forwards;
}
</style>

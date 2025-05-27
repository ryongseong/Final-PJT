<template>
  <div class="stock-detail-page">
    <header class="page-header">
      <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; margin-bottom: 1rem;">
        <button @click="goBack" class="back-button">
          <i class="bi bi-arrow-left"></i>
          <span>{{ $t('stockDetail.goBackToList') }}</span>
        </button>
        <button @click="toggleLanguage" class="language-toggle-button" style="padding: 0.5rem 1rem; background-color: #e9ecef; color: #495057; border: 1px solid #ced4da; border-radius: 20px; cursor: pointer; font-size: 0.9rem; font-weight: 500;">
          <i class="bi bi-translate" style="margin-right: 0.25rem;"></i> {{ $t('settings.switchLanguage') }}
        </button>
      </div>
      <div v-if="stockData" class="stock-title-main">
        <h1>{{ stockData.isNameKey ? $t(stockData.name) : stockData.name }}</h1>
        <span class="stock-code-chip">{{ stockData.code }}</span>
      </div>
      <p v-if="stockData">{{ $t('stockDetail.pageDescription') }}</p>
      <p v-else>{{ $t('stockDetail.pageDescriptionNotFound') }}</p>
    </header>

    <div v-if="loading" class="loading-indicator-container">
      <div class="spinner"></div>
      <p>{{ $t('stockDetail.loadingDetails') }}</p>
    </div>

    <div v-else-if="stockData" class="detail-content-grid">
      <!-- Section 1: Price Overview -->
      <section class="content-card price-overview-card">
        <div class="price-display">
          <span class="current-price">{{ formatPrice(stockData.current_price) }}</span>
          <div class="price-change" :class="getPriceChangeClass(stockData.current_price, stockData.base_price)">
            <i class="bi" :class="getRateIconClass(stockData.current_price, stockData.base_price)"></i>
            {{ formatPriceChange(stockData.current_price - stockData.base_price) }} ({{ calculateChangeRate(stockData.current_price, stockData.base_price) }}%)
          </div>
        </div>
        <div class="price-meta">
          <span>{{ $t('stockDetail.baseDate') }}: {{ stockData.date }}</span>
          <span>{{ $t('stockDetail.prevClosePrice') }}: {{ formatPrice(stockData.base_price) }}</span>
        </div>
      </section>

      <!-- Section 2: Key Metrics -->
      <section class="content-card key-metrics-card">
        <h2 class="card-section-title">{{ $t('stockDetail.keyMetrics') }}</h2>
        <div class="metrics-grid">
          <div class="metric-item">
            <span class="metric-label">{{ $t('stockDetail.marketCap') }}</span>
            <span class="metric-value">{{ formatMarketCap(stockData.market_cap) }}</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">{{ $t('stockDetail.high52Week') }}</span>
            <span class="metric-value text-positive">{{ formatPrice(stockData.high_52_week) }}</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">{{ $t('stockDetail.volume') }}</span>
            <span class="metric-value">{{ formatNumber(stockData.volume) }} 주</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">{{ $t('stockDetail.low52Week') }}</span>
            <span class="metric-value text-negative">{{ formatPrice(stockData.low_52_week) }}</span>
          </div>
        </div>
      </section>

      <!-- Section 3: Price Chart -->
      <section class="content-card chart-card">
        <h2 class="card-section-title">{{ $t('stockDetail.priceChart') }}</h2>
        <div v-if="stockData.candles && stockData.candles.length > 0" class="chart-wrapper">
          <canvas ref="chartCanvas"></canvas>
        </div>
        <div v-else class="no-data-placeholder">
          <i class="bi bi-bar-chart-line"></i>
          <p>{{ $t('stockDetail.noChartData') }}</p>
        </div>
      </section>

      <!-- Section 4: Price History Table -->
      <section class="content-card history-table-card">
        <h2 class="card-section-title">{{ $t('stockDetail.dailyPricesLast10Days') }}</h2>
        <div v-if="stockData.candles && stockData.candles.length > 0" class="table-wrapper">
          <table class="history-data-table">
            <thead>
              <tr>
                <th>{{ $t('stockDetail.date') }}</th>
                <th>{{ $t('stockDetail.closingPrice') }}</th>
                <th>{{ $t('stockDetail.change') }}</th>
                <th>{{ $t('stockDetail.changeRate') }}</th>
                <th>{{ $t('stockDetail.openingPrice') }}</th>
                <th>{{ $t('stockDetail.highPrice') }}</th>
                <th>{{ $t('stockDetail.lowPrice') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(candle, index) in stockData.candles.slice(0, 10)" :key="index">
                <td>{{ formatDateForTable(candle.dt) }}</td>
                <td :class="getPriceChangeClass(candle.close, candle.base)">{{ formatPrice(candle.close) }}</td>
                <td :class="getPriceChangeClass(candle.close, candle.base)">{{ formatPriceChange(candle.close - candle.base) }}</td>
                <td :class="getPriceChangeClass(candle.close, candle.base)">
                  <i class="bi" :class="getRateIconClass(candle.close, candle.base)"></i>
                  {{ calculateChangeRate(candle.close, candle.base) }}%
                </td>
                <td>{{ formatPrice(candle.open) }}</td>
                <td>{{ formatPrice(candle.high) }}</td>
                <td>{{ formatPrice(candle.low) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="no-data-placeholder">
          <i class="bi bi-table"></i>
          <p>{{ $t('stockDetail.noPriceHistory') }}</p>
        </div>
      </section>

    </div>

    <div v-else class="no-results-container">
      <i class="bi bi-emoji-frown icon-large"></i>
      <h4>{{ $t('stockDetail.notFoundTitle') }}</h4>
      <p>{{ $t('stockDetail.notFoundDescription') }}</p>
      <button @click="goBack" class="view-all-btn">
        <i class="bi bi-arrow-left"></i> {{ $t('stockDetail.goBackToList') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import Chart from 'chart.js/auto'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

const router = useRouter()
const route = useRoute()
const baseUrl = 'http://localhost:8000/products'
const stockCode = computed(() => route.params.stockCode)
const stockNameFromQuery = computed(() => route.query.stockName)

const stockData = ref(null)
const loading = ref(true)
const chartCanvas = ref(null)
let chartInstance = null

const stockNameMapping = {
  A005930: 'stockNames.samsungElectronics',
  A000660: 'stockNames.skHynix',
  A035420: 'stockNames.naver',
  A035720: 'stockNames.kakao',
  A005380: 'stockNames.hyundaiMotor',
  'US20190205001': 'stockNames.usTreasury',
  // ... (더 많은 종목 매핑)
};

const toggleLanguage = () => {
  const newLocale = locale.value === 'ko' ? 'en' : 'ko';
  locale.value = newLocale;
  localStorage.setItem('language', newLocale);
};

const goBack = () => {
  router.back(); // 또는 router.push({ name: 'stockView' });
};

const fetchStockDetail = async () => {
  if (!stockCode.value) {
    loading.value = false;
    stockData.value = null;
    console.error('Stock code is undefined');
    return;
  }
  loading.value = true;
  try {
    console.log(`Fetching details for ${stockCode.value}, Query Name: ${stockNameFromQuery.value}`);
    await new Promise(resolve => setTimeout(resolve, 700)); // Simulate network delay

    let currentPrice = Math.random() * 100000 + 50000;
    const changeRate = (Math.random() * 10 - 5) / 100; // 비율로 변경
    let basePrice = currentPrice / (1 + changeRate);

    let resolvedNameValue;
    let resolvedIsKey = false;

    if (stockNameFromQuery.value) {
      resolvedNameValue = stockNameFromQuery.value;
      resolvedIsKey = false;
    } else if (stockNameMapping[stockCode.value]) {
      resolvedNameValue = stockNameMapping[stockCode.value];
      resolvedIsKey = true;
    } else {
      resolvedNameValue = stockCode.value;
      resolvedIsKey = false;
    }

    const mockApiResponse = {
      name: resolvedNameValue,
      isNameKey: resolvedIsKey,
      code: stockCode.value,
      date: new Date().toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' }),
      current_price: currentPrice,
      base_price: basePrice, 
      price_change: currentPrice - basePrice,
      change_rate: (changeRate * 100).toFixed(2),
      volume: Math.floor(Math.random() * 10000000),
      market_cap: Math.random() * 1000000000000 + 100000000000,
      high_52_week: currentPrice * (1 + Math.random() * 0.2 + 0.1),
      low_52_week: currentPrice * (1 - (Math.random() * 0.2 + 0.1)),
      candles: [] // Placeholder, will be filled by generateMockCandles
    };
    
    // 52주 최고/최저가 현재가 범위 안에 있도록 조정
    mockApiResponse.low_52_week = Math.min(mockApiResponse.low_52_week, mockApiResponse.current_price * 0.95);
    mockApiResponse.high_52_week = Math.max(mockApiResponse.high_52_week, mockApiResponse.current_price * 1.05, mockApiResponse.low_52_week * 1.05);
    // current_price가 high/low를 벗어나지 않도록 조정
    mockApiResponse.current_price = Math.max(mockApiResponse.low_52_week, Math.min(mockApiResponse.current_price, mockApiResponse.high_52_week));
    
    mockApiResponse.base_price = mockApiResponse.current_price / (1 + changeRate); 
    mockApiResponse.price_change = mockApiResponse.current_price - mockApiResponse.base_price;

    mockApiResponse.candles = generateMockCandles(30, mockApiResponse.current_price, mockApiResponse.base_price);

    stockData.value = mockApiResponse;

    if (stockData.value.candles && stockData.value.candles.length > 0) {
      await nextTick();
      renderChart(stockData.value.candles);
    }

  } catch (error) {
    console.error('Error fetching stock detail:', error);
    stockData.value = null;
  } finally {
    loading.value = false;
  }
};

const generateMockCandles = (numCandles, currentDayClose, currentDayBase) => {
  const candles = []; // 최종 반환 배열 (최신 날짜가 맨 앞)
  let previousDayClose = currentDayBase; // 첫 번째 과거 캔들의 base는 오늘의 base(어제 종가)가 됨

  const today = new Date();

  // 오늘 캔들부터 생성 (배열의 맨 앞에 추가될 예정)
  candles.push({
    dt: today.toISOString(),
    open: currentDayBase * (1 + (Math.random() - 0.5) * 0.02), // 오늘의 시가는 어제 종가(currentDayBase) 기준
    high: Math.max(currentDayBase * (1 + (Math.random() - 0.5) * 0.02), currentDayClose) * (1 + Math.random() * 0.01),
    low: Math.min(currentDayBase * (1 + (Math.random() - 0.5) * 0.02), currentDayClose) * (1 - Math.random() * 0.01),
    close: currentDayClose,
    base: currentDayBase,
  });

  // 오늘 제외 numCandles - 1 일치 과거 데이터 생성
  for (let i = 1; i < numCandles; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);

    const newClose = previousDayClose * (1 - (Math.random() - 0.5) * 0.05); 
    const newBase = newClose / (1 + (Math.random() - 0.5) * 0.02); 
    
    candles.push({
      dt: date.toISOString(),
      open: newBase * (1 + (Math.random() - 0.5) * 0.02),
      high: Math.max(newBase, newClose) * (1 + Math.random() * 0.01),
      low: Math.min(newBase, newClose) * (1 - Math.random() * 0.01),
      close: newClose,
      base: newBase, 
    });
    previousDayClose = newClose; 
  }
  return candles; 
};

const drawChart = async () => {
  console.log('[drawChart] Attempting to draw chart.');
  if (stockData.value && stockData.value.candles && stockData.value.candles.length > 0 && chartCanvas.value) {
    console.log('[drawChart] Conditions met. Calling renderChart.');
    await nextTick(); 
    renderChart(stockData.value.candles);
  } else {
    console.warn('[drawChart] Conditions NOT met for drawing chart:', 
      {
        hasStockData: !!stockData.value,
        hasCandles: !!(stockData.value && stockData.value.candles && stockData.value.candles.length > 0),
        hasCanvas: !!chartCanvas.value
      }
    );
  }
};

let chartjsChart = null;

const renderChart = (candlesToRender) => {
  console.log('[renderChart] Called with candles:', JSON.parse(JSON.stringify(candlesToRender)));
  console.log('[renderChart] chartCanvas.value:', chartCanvas.value);

  if (chartjsChart) {
    console.log('[renderChart] Destroying existing chart instance.');
    chartjsChart.destroy();
    chartjsChart = null;
  }

  if (chartCanvas.value && candlesToRender && candlesToRender.length > 0) {
    const chartDataCandles = [...candlesToRender].reverse();
    const ctx = chartCanvas.value.getContext('2d');
    
    if (!ctx) {
      console.error('[renderChart] Failed to get 2D context from canvas.');
      return;
    }

    const labels = chartDataCandles.map(c => new Date(c.dt).toLocaleDateString('ko-KR', { month: '2-digit', day: '2-digit' }));
    const dataPoints = chartDataCandles.map(c => c.close);

    console.log('[renderChart] Labels for chart:', labels);
    console.log('[renderChart] DataPoints for chart:', dataPoints);

    try {
      chartjsChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: t('stockDetail.closingPrice'),
            data: dataPoints,
            borderColor: '#0d6efd',
            backgroundColor: 'rgba(13, 110, 253, 0.1)',
            tension: 0.2,
            fill: true,
            pointRadius: 2,
            pointBackgroundColor: '#0d6efd',
            borderWidth: 2,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: false,
              ticks: {
                callback: function(value) {
                  return formatPrice(value);
                },
                color: '#6c757d'
              },
              grid: {
                borderColor: '#e9ecef',
                color: '#e9ecef'
              }
            },
            x: {
              ticks: {
                maxRotation: 0,
                autoSkip: true,
                maxTicksLimit: 10,
                color: '#6c757d'
              },
              grid: {
                display: false,
              }
            }
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              backgroundColor: '#212529',
              titleColor: '#fff',
              bodyColor: '#f8f9fa',
              padding: 10,
              cornerRadius: 4,
              displayColors: false,
              callbacks: {
                label: function(context) {
                  return `${t('stockDetail.closingPrice')}: ${formatPrice(context.parsed.y)}`;
                }
              }
            }
          }
        }
      });
      console.log('[renderChart] Chart instance created successfully.');
    } catch (error) {
      console.error('[renderChart] Error creating chart:', error);
    }
  } else {
    console.warn('[renderChart] Canvas not ready or no candle data for chart.');
    if (!chartCanvas.value) console.warn('[renderChart] chartCanvas.value is null or undefined.');
    if (!candlesToRender || candlesToRender.length === 0) console.warn('[renderChart] candlesToRender is empty or null.');
  }
};

const formatNumber = (num) => {
  if (typeof num !== 'number' || isNaN(num)) return '-';
  return new Intl.NumberFormat(locale.value, {}).format(num);
};

const formatPrice = (price) => {
  if (typeof price !== 'number' || isNaN(price)) return '-';
  return new Intl.NumberFormat(locale.value, { style: 'currency', currency: 'KRW' }).format(price);
};

const formatPriceChange = (change) => {
  if (typeof change !== 'number' || isNaN(change)) return '-';
  const formattedNumber = new Intl.NumberFormat(locale.value, {}).format(Math.abs(change));
  if (change === 0) return '0';
  return change > 0 ? `+${formattedNumber}` : `-${formattedNumber}`;
};

const calculateChangeRate = (currentPrice, basePrice) => {
  if (typeof currentPrice !== 'number' || typeof basePrice !== 'number' || isNaN(currentPrice) || isNaN(basePrice) || basePrice === 0) return '0.00';
  const rate = ((currentPrice - basePrice) / basePrice) * 100;
  return rate.toFixed(2);
};

const formatMarketCap = (marketCap) => {
  if (typeof marketCap !== 'number' || isNaN(marketCap)) return '-';
  if (locale.value === 'ko') {
    if (marketCap >= 1000000000000) {
      return `${(marketCap / 1000000000000).toFixed(2)}조`;
    }
    if (marketCap >= 100000000) {
      return `${(marketCap / 100000000).toFixed(0)}억`;
    }
    return `${new Intl.NumberFormat('ko-KR').format(marketCap)}원`;
  } else {
    if (marketCap >= 1000000000000) {
      return `${(marketCap / 1000000000000).toFixed(2)}T`;
    }
    if (marketCap >= 1000000000) {
      return `${(marketCap / 1000000000).toFixed(2)}B`;
    }
    if (marketCap >= 1000000) {
      return `${(marketCap / 1000000).toFixed(2)}M`;
    }
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(marketCap);
  }
};

const formatDateForTable = (dateString) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString(locale.value, { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\.$/, '');
};

const getPriceChangeClass = (currentPrice, basePrice) => {
  if (typeof currentPrice !== 'number' || typeof basePrice !== 'number' || isNaN(currentPrice) || isNaN(basePrice) || basePrice === 0) return 'text-neutral';
  if (currentPrice > basePrice) return 'text-positive';
  if (currentPrice < basePrice) return 'text-negative';
  return 'text-neutral';
};

const getRateIconClass = (currentPrice, basePrice) => {
  if (typeof currentPrice !== 'number' || typeof basePrice !== 'number' || isNaN(currentPrice) || isNaN(basePrice) || basePrice === 0) return 'bi-dash-lg';
  if (currentPrice > basePrice) return 'bi-arrow-up-short';
  if (currentPrice < basePrice) return 'bi-arrow-down-short';
  return 'bi-dash-lg';
};

onMounted(() => {
  console.log('[onMounted] Component mounted. Fetching stock detail.');
  fetchStockDetail();
});

watch(stockCode, (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {
    console.log(`[watch stockCode] Stock code changed from ${oldVal} to ${newVal}. Destroying chart and fetching new data.`);
    if (chartjsChart) {
      chartjsChart.destroy();
      chartjsChart = null;
    }
    stockData.value = null;
    loading.value = true;
    fetchStockDetail();
  }
});

watch(locale, () => {
  if (stockData.value && stockData.value.candles && stockData.value.candles.length > 0) {
    drawChart();
  }
  if (stockData.value) {
    stockData.value.date = new Date().toLocaleDateString(locale.value === 'ko' ? 'ko-KR' : 'en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  }
});

watch(stockData, (newData) => {
  if (newData) {
    console.log('[watch stockData] New data received, attempting to draw chart.', JSON.parse(JSON.stringify(newData)));
    drawChart();
  }
}, { deep: true });

watch(chartCanvas, (newCanvas) => {
  console.log('[watch chartCanvas] Canvas ref changed:', newCanvas);
  if (newCanvas) {
    console.log('[watch chartCanvas] Canvas is now available. Attempting to draw chart.');
    drawChart();
  }
});

</script>

<style scoped>
/* General Page Styles */
.stock-detail-page {
  padding: 0rem 2rem 2rem 5rem; /* Top padding removed, use header's padding. Left padding for sidebar. */
  max-width: 1200px;
  margin: 0 auto;
  font-family: 'Pretendard Variable', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Pretendard Variable', 'Helvetica Neue', Arial, sans-serif;
  background-color: #f4f7f9; /* Light gray background, same as StockView */
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 1.5rem 1rem; /* Standardized padding */
  background-color: #ffffff; /* White background for header */
  border-bottom: 1px solid #e0e7ef; /* Softer border */
  margin: 0 -2rem 2rem -5rem; /* Extend to full width considering parent padding */
  padding-left: 5rem; /* Re-apply left padding */
  padding-right: 2rem; /* Re-apply right padding */
}

.back-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #e9ecef; /* Light gray, neutral */
  color: #495057; /* Dark gray text */
  border: 1px solid #ced4da;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.back-button:hover {
  background-color: #d3d9df;
  color: #212529;
}

.back-button .bi {
  font-size: 1.1rem;
}

.stock-title-main {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 0.25rem;
}

.stock-title-main h1 {
  font-size: 2.2rem;
  font-weight: 700;
  color: #1a2c42; /* Darker blue from StockView */
  margin: 0;
}

.stock-code-chip {
  background-color: #e0e7ef; /* Lighter gray for chip */
  color: #4b5563; /* Medium gray text for chip */
  padding: 0.3em 0.7em;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
}

.page-header > p {
  font-size: 1rem;
  color: #5a687b; /* Softer gray */
  margin-top: 0.25rem;
  margin-bottom: 0;
}

/* Loading and No Results States (similar to StockView) */
.loading-indicator-container,
.no-results-container {
  text-align: center;
  padding: 4rem 1rem;
  margin-top: 1rem;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  color: #5a687b;
}

.spinner {
  border: 4px solid #e0e7ef;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1.2rem auto;
}

.no-results-container .icon-large {
  font-size: 3.5rem;
  color: #a0a9b4;
  margin-bottom: 1rem;
}

.no-results-container h4 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #334155;
  margin-bottom: 0.5rem;
}

.no-results-container p {
  font-size: 1rem;
  line-height: 1.5;
  margin-bottom: 1.5rem;
  max-width: 450px;
  margin-left: auto;
  margin-right: auto;
}

.no-results-container .view-all-btn {
    padding: 0.7rem 1.5rem;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 500;
    transition: background-color 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.no-results-container .view-all-btn:hover {
  background-color: #2980b9;
}


/* Detail Content Grid */
.detail-content-grid {
  display: grid;
  gap: 1.5rem; /* Consistent gap */
}

/* General Content Card Styling */
.content-card {
  background-color: #ffffff;
  border-radius: 10px; /* Softer radius */
  padding: 1.5rem;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.06); /* Subtle shadow */
}

.card-section-title {
  font-size: 1.3rem; /* Consistent title size */
  font-weight: 600;
  color: #334155; /* Dark gray-blue for titles */
  margin-bottom: 1.2rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e8eef3;
}

/* Price Overview Card */
.price-overview-card {
  /* Specific styles if needed, otherwise uses .content-card */
}

.price-display {
  display: flex;
  align-items: baseline; 
  justify-content: space-between;
  margin-bottom: 0.75rem;
  flex-wrap: wrap; /* Allow wrapping on small screens */
  gap: 0.5rem;
}

.current-price {
  font-size: 2.8rem;
  font-weight: 700;
  color: #1e293b; /* Very dark blue, almost black for price */
}

.price-change {
  font-size: 1.3rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
}

.price-meta {
  font-size: 0.85rem;
  color: #6b7280; /* Medium gray for meta text */
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e8eef3;
}

/* Key Metrics Card */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem 1.5rem; /* row-gap column-gap */
}

.metric-item {
  background-color: #f8fafc; /* Slightly off-white background for items */
  padding: 0.8rem 1rem;
  border-radius: 6px;
}

.metric-label {
  display: block;
  font-size: 0.8rem;
  color: #6b7280; /* Medium gray for labels */
  margin-bottom: 0.25rem;
  text-transform: uppercase;
}

.metric-value {
  font-size: 1.15rem;
  font-weight: 600;
  color: #334155; /* Darker text for values */
}

/* Chart Card */
.chart-wrapper {
  height: 350px; /* Adjusted height */
  position: relative;
}

/* History Table Card */
.table-wrapper {
  overflow-x: auto; /* Allow horizontal scroll on table if needed */
}

.history-data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem; /* Slightly smaller for table data */
}

.history-data-table th,
.history-data-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e8eef3;
  white-space: nowrap; /* Prevent wrapping in table cells */
}

.history-data-table th {
  background-color: #f8fafc;
  color: #4a5568;
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.history-data-table tbody tr:hover {
  background-color: #f0f4f8;
}

.history-data-table td {
  color: #334155;
}

.history-data-table td:nth-child(2),
.history-data-table td:nth-child(3),
.history-data-table td:nth-child(4) {
  text-align: right;
  font-weight: 500;
}

/* Text Color Classes (re-using from StockView for consistency) */
.text-positive {
  color: #22c55e !important; 
}

.text-negative {
  color: #ef4444 !important; 
}

.text-neutral {
  color: #64748b !important; /* Gray for neutral */
}

/* Icon Classes (re-using from StockView for consistency) */
.price-change .bi, .history-data-table .bi {
  margin-right: 0.25rem;
  font-size: 1em; /* Relative to parent font size */
}

.price-change.text-positive, .history-data-table td.text-positive .bi {
    background-color: rgba(34, 197, 94, 0.1);
    color: #16a34a; /* Darker green for better contrast on light green bg */
}
.price-change.text-negative, .history-data-table td.text-negative .bi {
    background-color: rgba(239, 68, 68, 0.1);
    color: #dc2626; /* Darker red for better contrast on light red bg */
}
.price-change.text-neutral {
    background-color: rgba(100, 116, 139, 0.1);
    color: #475569;
}

.no-data-placeholder {
  text-align: center;
  padding: 2rem;
  color: #95a5a6;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.no-data-placeholder .bi {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
  display: block;
}

/* Responsive Adjustments */
@media (max-width: 992px) {
  .stock-detail-page {
    padding: 0rem 1.5rem 1.5rem 3rem;
  }
  .page-header {
    margin: 0 -1.5rem 1.5rem -3rem;
    padding-left: 3rem;
    padding-right: 1.5rem;
  }
  .stock-title-main h1 { font-size: 1.9rem; }
  .current-price { font-size: 2.4rem; }
  .price-change { font-size: 1.15rem; }
}

@media (max-width: 768px) {
  .stock-detail-page {
    padding: 0rem 1rem 1rem 2rem;
  }
  .page-header {
    margin: 0 -1rem 1.5rem -2rem;
    padding-left: 2rem;
    padding-right: 1rem;
  }
  .stock-title-main h1 { font-size: 1.7rem; }
  .stock-code-chip { font-size: 0.8rem; }
  .current-price { font-size: 2rem; }
  .price-change { font-size: 1rem; }
  .metrics-grid {
    grid-template-columns: 1fr 1fr; /* Two columns for metrics */
  }
  .card-section-title { font-size: 1.15rem; }
  .metric-value { font-size: 1.05rem; }
  .history-data-table {
    font-size: 0.85rem;
  }
  .history-data-table th,
  .history-data-table td {
    padding: 0.6rem 0.8rem;
  }
}

@media (max-width: 480px) {
   .stock-detail-page {
    padding: 0rem 0.5rem 1rem 1rem;
  }
  .page-header {
    margin: 0 -0.5rem 1rem -1rem;
    padding-left: 1rem;
    padding-right: 0.5rem;
  }
  .stock-title-main {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  .stock-title-main h1 { font-size: 1.5rem; }
  .back-button { margin-bottom: 0.75rem; padding: 0.4rem 0.8rem; font-size: 0.85rem; }
  .current-price { font-size: 1.8rem; }
  .price-meta { flex-direction: column; gap: 0.25rem; align-items: flex-start; }
  .metrics-grid {
    grid-template-columns: 1fr; /* Single column for metrics on very small screens */
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

</style>

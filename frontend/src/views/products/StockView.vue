<template>
  <div class="stock-view-page">
    <header class="page-header">
      <h1>주식 현재가</h1>
      <p>국내 주요 주식의 실시간 시세를 확인하고 투자 기회를 찾아보세요.</p>
    </header>

    <div class="controls-bar">
      <div class="search-container">
        <i class="bi bi-search search-icon"></i>
        <input
          type="text"
          v-model="searchQuery"
          class="search-input"
          placeholder="종목명 또는 코드로 검색하세요"
          @input="filterStocks" />
        <button v-if="searchQuery" @click="clearSearch" class="clear-search-btn">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
      <button @click="fetchStockRankings" class="refresh-button">
        <i class="bi bi-arrow-clockwise"></i>
        <span>새로고침</span>
      </button>
    </div>

    <div v-if="loading.rankings" class="loading-indicator-container">
      <div class="spinner"></div>
      <p>주식 정보를 불러오고 있습니다...</p>
    </div>

    <div v-else-if="filteredStocks.length === 0" class="no-results-container">
      <i class="bi bi-exclamation-circle icon-large"></i>
      <p>검색된 주식 정보가 없습니다.</p>
      <button @click="clearSearch" class="view-all-btn">전체 목록 보기</button>
    </div>

    <div v-else class="stock-table-container">
      <table class="stock-table">
        <thead>
          <tr>
            <th class="rank-col">순위</th>
            <th class="name-col">종목명</th>
            <th class="price-col">현재가</th>
            <th class="change-col">전일대비</th>
            <th class="rate-col">등락률</th>
            <th class="volume-col">거래량</th>
            <th class="amount-col">거래대금</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(stock, index) in filteredStocks"
            :key="stock.productCode"
            @click="goToStockDetail(stock.productCode, stock.name)"
            class="stock-row-item"
          >
            <td class="rank-col text-center">{{ index + 1 }}</td>
            <td class="name-col">
              <div class="stock-name-wrapper">
                <span class="stock-main-name">{{ stock.name }}</span>
                <span class="stock-product-code">{{ stock.productCode }}</span>
              </div>
            </td>
            <td class="price-col text-right fw-bold">{{ formatPrice(stock.price.close) }}</td>
            <td
              class="change-col text-right"
              :class="getPriceChangeClass(stock.price.close, stock.price.base)"
            >
              {{ formatPriceChange(stock.price.close - stock.price.base) }}
            </td>
            <td
              class="rate-col text-right"
              :class="getPriceChangeClass(stock.price.close, stock.price.base)"
            >
              <i class="bi" :class="getRateIconClass(stock.price.close, stock.price.base)"></i>
              {{ calculateChangeRate(stock.price.close, stock.price.base) }}%
            </td>
            <td class="volume-col text-right">{{ formatNumber(stock.price.tossSecuritiesVolume) }}</td>
            <td class="amount-col text-right">{{ formatNumber(stock.price.tossSecuritiesAmount) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Market summary card - UI 개선 적용 -->
    <section class="market-summary-section">
      <h2>시장 주요 지수</h2>
      <div class="market-summary-grid">
        <div class="summary-card kospi">
          <div class="summary-card-header">
            <h3>KOSPI</h3>
            <span class="index-value">2,648.76</span>
          </div>
          <div class="summary-card-change positive">
            <i class="bi bi-caret-up-fill"></i> +0.23%
          </div>
        </div>
        <div class="summary-card kosdaq">
          <div class="summary-card-header">
            <h3>KOSDAQ</h3>
            <span class="index-value">874.61</span>
          </div>
          <div class="summary-card-change negative">
            <i class="bi bi-caret-down-fill"></i> -0.11%
          </div>
        </div>
        <div class="summary-card exchange">
          <div class="summary-card-header">
            <h3>원/달러</h3>
            <span class="index-value">1,342.50</span>
          </div>
          <div class="summary-card-change positive">
            <i class="bi bi-caret-up-fill"></i> +0.15%
          </div>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const baseUrl = 'http://localhost:8000/products'

const stockRankings = ref([])
const searchQuery = ref('')
const loading = ref({
  rankings: true,
})

// Filter stocks based on search query
const filteredStocks = computed(() => {
  if (!searchQuery.value) return stockRankings.value

  const query = searchQuery.value.toLowerCase()
  return stockRankings.value.filter(
    (stock) =>
      stock.name.toLowerCase().includes(query) || stock.productCode.toLowerCase().includes(query),
  )
})

// Reset search when user clicks clear
const clearSearch = () => {
  searchQuery.value = ''
}

// This function is bound to @input on search, let's keep its original purpose if any side effects were intended
// or rename/remove if truly only for clearing (which is now handled by clearSearch with a button)
const filterStocks = () => {
  // The filtering is done by the computed property `filteredStocks`.
  // This function is called on @input, so it can be used for real-time feedback or other side effects if needed in the future.
  // For now, it doesn't need to do anything extra as v-model handles the searchQuery update.
}

const fetchStockRankings = async () => {
  try {
    loading.value.rankings = true
    const response = await axios.get(`${baseUrl}/stock-rankings/`)
    console.log(response)
    if (response.data && response.data.result && response.data.result.products) {
      stockRankings.value = response.data.result.products
    } else {
      console.error('Unexpected response format:', response.data)
      stockRankings.value = []
    }
  } catch (error) {
    console.error('Error fetching stock rankings:', error)
    stockRankings.value = []
  } finally {
    loading.value.rankings = false
  }
}

const calculateChangeRate = (currentPrice, basePrice) => {
  if (!basePrice) return '0.00'
  const rate = ((currentPrice - basePrice) / basePrice) * 100
  return rate.toFixed(2)
}

const goToStockDetail = (stockCode, name) => {
  router.push({ 
    name: 'stockDetail', 
    params: { stockCode },
    query: { stockName: name }
  })
}

const formatNumber = (num) => {
  if (typeof num !== 'number' || isNaN(num)) return '-';
  return new Intl.NumberFormat('ko-KR').format(num);
};

const formatPrice = (price) => {
  if (typeof price !== 'number' || isNaN(price)) return '가격 정보 없음';
  return new Intl.NumberFormat('ko-KR', { style: 'currency', currency: 'KRW' }).format(price);
};

const formatPriceChange = (change) => {
  if (typeof change !== 'number' || isNaN(change)) return '-';
  const formattedNumber = formatNumber(Math.abs(change));
  if (change > 0) {
    return `+${formattedNumber}`;
  }
  return `${formatNumber(change)}`;
};

// Helper function to determine class for price change text
const getPriceChangeClass = (currentPrice, basePrice) => {
  if (typeof currentPrice !== 'number' || typeof basePrice !== 'number' || isNaN(currentPrice) || isNaN(basePrice)) return 'text-neutral';
  if (currentPrice > basePrice) {
    return 'text-positive';
  } else if (currentPrice < basePrice) {
    return 'text-negative';
  } else {
    return 'text-neutral';
  }
};

// Helper function to determine icon for rate change
const getRateIconClass = (currentPrice, basePrice) => {
  if (typeof currentPrice !== 'number' || typeof basePrice !== 'number' || isNaN(currentPrice) || isNaN(basePrice)) return '';
  if (currentPrice > basePrice) {
    return 'bi-arrow-up-right';
  } else if (currentPrice < basePrice) {
    return 'bi-arrow-down-right';
  } else {
    return 'bi-dash-lg'; // Icon for no change
  }
};

onMounted(() => {
  fetchStockRankings()
})
</script>

<style scoped>
/* General Page Styles */
.stock-view-page {
  padding: 2rem 2rem 2rem 5rem; /* Left padding for potential sidebar/icons */
  max-width: 1400px;
  margin: 0 auto;
  font-family: 'Pretendard Variable', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Pretendard Variable', 'Helvetica Neue', Arial, sans-serif;
  background-color: #f4f7f9; /* Light gray background */
  min-height: 100vh;
}

/* Header */
.page-header {
  text-align: left;
  margin-bottom: 2.5rem;
  padding-left: 10px; /* Align with table content */
}

.page-header h1 {
  font-size: 2.5rem; /* Slightly reduced */
  font-weight: 700;
  color: #1a2c42; /* Darker, more serious blue */
  margin-bottom: 0.4rem;
}

.page-header p {
  font-size: 1.05rem; /* Slightly reduced */
  color: #5a687b; /* Softer gray */
  max-width: 600px;
}

/* Controls Bar: Search and Refresh */
.controls-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 0 10px; /* Align with table content */
}

.search-container {
  display: flex;
  align-items: center;
  background-color: #fff;
  border-radius: 25px;
  padding: 0.5rem 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  flex-grow: 1;
  max-width: 500px;
}

.search-icon {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin-right: 0.75rem;
}

.search-input {
  border: none;
  outline: none;
  font-size: 1rem;
  width: 100%;
  background-color: transparent;
}

.search-input::placeholder {
  color: #a0a9b4;
}

.clear-search-btn {
  background: none;
  border: none;
  color: #7f8c8d;
  cursor: pointer;
  padding: 0 0 0 0.5rem;
  font-size: 1.1rem;
}

.refresh-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem 1.3rem;
  background-color: #3498db; /* Primary blue */
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.refresh-button:hover {
  background-color: #2980b9; /* Darker blue */
}

.refresh-button .bi {
  font-size: 1.1rem;
}

/* Loading and No Results States */
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
  color: #a0a9b4; /* Lighter gray for icon */
  margin-bottom: 1rem;
}

.no-results-container p {
  font-size: 1.15rem;
  margin-bottom: 1.5rem;
}

.view-all-btn {
  padding: 0.6rem 1.5rem;
  background-color: #5cb85c; /* Green for positive action */
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.view-all-btn:hover {
  background-color: #4cae4c;
}

/* Stock Table */
.stock-table-container {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  overflow: hidden; /* For rounded corners on table */
}

.stock-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.stock-table th,
.stock-table td {
  padding: 1rem 1.2rem;
  text-align: left;
  border-bottom: 1px solid #e8eef3; /* Lighter border */
}

.stock-table th {
  background-color: #f8fafc; /* Very light blue-gray for header */
  color: #4a5568; /* Darker gray for header text */
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.05em;
}

.stock-row-item {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.stock-row-item:hover {
  background-color: #f0f4f8; /* Light hover effect */
}

.stock-row-item td {
  color: #334155; /* Main text color */
}

/* Specific Column Styling */
.rank-col { width: 8%; text-align: center; font-weight: 500; color: #6b7280;}
.name-col { width: 28%; }
.price-col { width: 15%; text-align: right; }
.change-col { width: 15%; text-align: right; }
.rate-col { width: 12%; text-align: right; }
.volume-col { width: 12%; text-align: right; color: #6b7280; font-size: 0.9rem;}
.amount-col { width: 10%; text-align: right; color: #6b7280; font-size: 0.9rem;}

.stock-name-wrapper {
  display: flex;
  flex-direction: column;
}

.stock-main-name {
  font-weight: 600;
  font-size: 1.05rem;
  color: #1e293b; /* Darker for name */
}

.stock-product-code {
  font-size: 0.8rem;
  color: #7f8c8d;
}

.fw-bold { font-weight: 600 !important; }

.text-positive {
  color: #22c55e !important; /* Vibrant Green */
}

.text-negative {
  color: #ef4444 !important; /* Vibrant Red */
}

.text-neutral {
  color: #64748b; /* Gray for neutral */
}

.rate-col .bi {
  margin-right: 0.25rem;
  font-size: 0.9em;
}

.rate-col .bi-arrow-up-right { color: #22c55e; }
.rate-col .bi-arrow-down-right { color: #ef4444; }
.rate-col .bi-dash-lg { color: #64748b; }


/* Market Summary Section */
.market-summary-section {
  margin-top: 3rem;
  padding: 0 10px; /* Align with table content */
}

.market-summary-section h2 {
  font-size: 1.6rem;
  font-weight: 600;
  color: #1a2c42;
  margin-bottom: 1.5rem;
}

.market-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.summary-card {
  background-color: #fff;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 3px 10px rgba(0,0,0,0.06);
  border-left: 5px solid;
}

.summary-card.kospi { border-left-color: #2563eb; } /* Blue */
.summary-card.kosdaq { border-left-color: #db2777; } /* Pink */
.summary-card.exchange { border-left-color: #f59e0b; } /* Amber */

.summary-card-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.5rem;
}

.summary-card-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #334155;
  margin: 0;
}

.summary-card-header .index-value {
  font-size: 1.7rem;
  font-weight: 700;
  color: #1e293b;
}

.summary-card-change {
  font-size: 1rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.summary-card-change.positive { color: #16a34a; }
.summary-card-change.negative { color: #dc2626; }

.summary-card-change .bi {
  font-size: 1.2em;
}

/* Responsive adjustments */
@media (max-width: 992px) {
  .page-header h1 { font-size: 2.2rem; }
  .page-header p { font-size: 1rem; }
  .controls-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  .search-container {
    max-width: none;
  }
}

@media (max-width: 768px) {
  .stock-view-page {
    padding: 1.5rem 1rem 1.5rem 2.5rem; /* Adjust left padding for smaller screens */
  }
  .stock-table {
    font-size: 0.9rem;
  }
  .stock-table th,
  .stock-table td {
    padding: 0.8rem 0.9rem;
  }
  .name-col { width: auto; }
  .price-col, .change-col, .rate-col, .volume-col, .amount-col {
    width: auto; /* Allow columns to shrink */
    min-width: 70px; /* Minimum width for readability */
  }
  .stock-main-name { font-size: 0.95rem; }
  .stock-product-code { font-size: 0.75rem; }

  .market-summary-grid {
    grid-template-columns: 1fr; /* Stack cards on smaller screens */
  }
}

@media (max-width: 480px) {
  .page-header h1 { font-size: 1.8rem; }
  .page-header p { font-size: 0.9rem; }
  .refresh-button span { display: none; } /* Hide text on very small screens */
  .refresh-button .bi { margin-right: 0; }
  .stock-table th {
    font-size: 0.7rem;
  }
   .stock-table td {
    font-size: 0.85rem;
  }
  .summary-card-header .index-value { font-size: 1.5rem; }
  .summary-card-change { font-size: 0.9rem; }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

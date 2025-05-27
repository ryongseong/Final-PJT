<template>
  <div class="stock-rankings-container">
    <div class="container py-4">
      <h1 class="text-center mb-4 fw-bold">주식 랭킹</h1>

      <div class="search-filter mb-4">
        <div class="input-group shadow-sm">
          <span class="input-group-text bg-primary text-white">
            <i class="bi bi-search"></i>
          </span>
          <input
            type="text"
            v-model="searchQuery"
            class="form-control"
            placeholder="종목명 또는 코드로 검색..."
            @input="filterStocks"
          />
          <button class="btn btn-outline-secondary" type="button" @click="searchQuery = ''">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
      </div>

      <div class="card shadow-lg rounded-3 border-0 overflow-hidden">
        <div class="card-header bg-gradient-primary text-white py-3">
          <div class="d-flex justify-content-between align-items-center">
            <h3 class="card-title mb-0 fw-bold">실시간 주식 랭킹</h3>
            <button @click="fetchStockRankings" class="btn btn-sm btn-light">
              <i class="bi bi-arrow-clockwise me-1"></i> 새로고침
            </button>
          </div>
        </div>
        <div class="card-body p-0">
          <div v-if="loading.rankings" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">실시간 주식 정보를 불러오는 중입니다...</p>
          </div>
          <div v-else-if="filteredStocks.length === 0" class="text-center py-5">
            <i class="bi bi-search display-1 text-muted"></i>
            <p class="mt-3">검색 결과가 없습니다.</p>
            <button class="btn btn-outline-primary mt-2" @click="searchQuery = ''">
              모든 주식 보기
            </button>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr>
                  <th scope="col" class="text-center">순위</th>
                  <th scope="col">종목명</th>
                  <th scope="col">현재가</th>
                  <th scope="col">전일대비</th>
                  <th scope="col">등락률</th>
                  <th scope="col">거래량</th>
                  <th scope="col">거래대금</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(stock, index) in filteredStocks"
                  :key="stock.productCode"
                  @click="goToStockDetail(stock.productCode)"
                  class="cursor-pointer stock-row"
                >
                  <td class="text-center fw-bold">{{ index + 1 }}</td>
                  <td>
                    <div class="d-flex align-items-center">
                      <span class="fw-bold">{{ stock.name }}</span>
                      <span class="badge bg-secondary ms-2 rounded-pill">{{
                        stock.productCode
                      }}</span>
                    </div>
                  </td>
                  <td class="fw-bold">{{ formatPrice(stock.price.close) }}</td>
                  <td
                    :class="{
                      'text-success fw-bold': stock.price.close > stock.price.base,
                      'text-danger fw-bold': stock.price.close < stock.price.base,
                      'text-secondary': stock.price.close === stock.price.base,
                    }"
                  >
                    {{ formatPriceChange(stock.price.close - stock.price.base) }}
                  </td>
                  <td
                    :class="{
                      'text-success fw-bold': stock.price.close > stock.price.base,
                      'text-danger fw-bold': stock.price.close < stock.price.base,
                      'text-secondary': stock.price.close === stock.price.base,
                    }"
                  >
                    <div class="d-flex align-items-center">
                      {{ calculateChangeRate(stock.price.close, stock.price.base) }}%
                      <i
                        v-if="stock.price.close !== stock.price.base"
                        :class="[
                          stock.price.close > stock.price.base
                            ? 'bi-arrow-up-right'
                            : 'bi-arrow-down-right',
                          'ms-1',
                        ]"
                      ></i>
                    </div>
                  </td>
                  <td>
                    <span class="badge bg-light text-dark">
                      {{ formatNumber(stock.price.tossSecuritiesVolume) }}
                    </span>
                  </td>
                  <td>
                    <span class="badge bg-light text-dark">
                      {{ formatNumber(stock.price.tossSecuritiesAmount) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="card-footer bg-light text-center py-3">
          <small class="text-muted">데이터는 실시간으로 업데이트됩니다</small>
        </div>
      </div>

      <!-- Market summary card -->
      <div class="card mt-4 shadow-sm rounded-3 border-0">
        <div class="card-header bg-light">
          <h4 class="mb-0">시장 요약</h4>
        </div>
        <div class="card-body">
          <div class="row g-3">
            <div class="col-md-4">
              <div class="p-3 border rounded bg-light">
                <h5>KOSPI</h5>
                <div class="h4 mb-0 text-primary">
                  2,648.76 <small class="text-success">+0.23%</small>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="p-3 border rounded bg-light">
                <h5>KOSDAQ</h5>
                <div class="h4 mb-0 text-primary">
                  874.61 <small class="text-danger">-0.11%</small>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="p-3 border rounded bg-light">
                <h5>원/달러</h5>
                <div class="h4 mb-0 text-primary">
                  1,342.50 <small class="text-success">+0.15%</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
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
const filterStocks = () => {
  // This function exists to handle the input event
  // The actual filtering is done by the computed property
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

const goToStockDetail = (stockCode) => {
  router.push({ name: 'stockDetail', params: { stockCode } })
}

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

onMounted(() => {
  fetchStockRankings()
})
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
  transition: all 0.2s ease;
}

.cursor-pointer:hover {
  background-color: rgba(13, 110, 253, 0.05);
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
}

.stock-row {
  border-left: 3px solid transparent;
}

.stock-row:hover {
  border-left: 3px solid #0d6efd;
}

.bg-gradient-primary {
  background: linear-gradient(45deg, #0d6efd, #0a58ca);
}

.table-responsive {
  max-height: 600px;
  overflow-y: auto;
}

.search-filter .form-control:focus {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}

.rounded-3 {
  border-radius: 0.5rem !important;
}

/* Custom scrollbar for table */
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

/* Animation for refresh button */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.bi-arrow-clockwise {
  transition: transform 0.3s ease;
}

button:active .bi-arrow-clockwise {
  animation: spin 0.7s linear;
}
</style>

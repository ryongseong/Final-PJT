<template>
  <div class="product-statistics">
    <h2>{{ $t('products.statistics.title') }}</h2>
    <div v-if="isLoading" class="loading">{{ $t('products.statistics.loading') }}</div>
    <div v-if="error" class="error-message">{{ error }}</div>
    <div v-if="!isLoading && !error && statistics" class="statistics-content">
      <div class="stat-item">
        <span class="stat-label">{{ $t('products.statistics.totalProducts') }}:</span>
        <span class="stat-value">{{ statistics.total_products }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">{{ $t('products.statistics.depositProducts') }}:</span>
        <span class="stat-value">{{ statistics.deposit_count }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">{{ $t('products.statistics.savingProducts') }}:</span>
        <span class="stat-value">{{ statistics.saving_count }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">{{ $t('products.statistics.mortgageLoans') }}:</span>
        <span class="stat-value">{{ statistics.mortgage_loan_count }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">{{ $t('products.statistics.creditLoans') }}:</span>
        <span class="stat-value">{{ statistics.credit_loan_count }}</span>
      </div>
      <!-- Add more stats as available and needed -->
      <div v-if="statistics.average_deposit_rate" class="stat-item">
        <span class="stat-label">{{ $t('products.statistics.avgDepositRate') }}:</span>
        <span class="stat-value"
          >{{ parseFloat(statistics.average_deposit_rate).toFixed(2) }}%</span
        >
      </div>
      <div v-if="statistics.average_saving_rate" class="stat-item">
        <span class="stat-label">{{ $t('products.statistics.avgSavingRate') }}:</span>
        <span class="stat-value">{{ parseFloat(statistics.average_saving_rate).toFixed(2) }}%</span>
      </div>
    </div>
    <div v-if="!isLoading && !error && !statistics" class="no-data">
      {{ $t('products.statistics.noData') }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import productService from '@/services/products.js'

const { t } = useI18n()
const statistics = ref(null)
const isLoading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    isLoading.value = true
    error.value = null
    const response = await productService.getProductStatistics()
    statistics.value = response.data // Adjust based on your API response structure
  } catch (err) {
    console.error('Error fetching product statistics:', err)
    error.value = 'Failed to load product statistics. Please try again later.'
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail
    }
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.product-statistics {
  padding: 20px;
  background-color: #f0f4f8;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.product-statistics h2 {
  margin-top: 0;
  color: #333;
  text-align: center;
  margin-bottom: 20px;
}

.loading,
.no-data {
  text-align: center;
  color: #666;
  padding: 20px;
}

.error-message {
  text-align: center;
  color: red;
  padding: 10px;
  border: 1px solid red;
  border-radius: 4px;
  background-color: #ffe0e0;
}

.statistics-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.stat-item {
  background-color: #fff;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.stat-label {
  font-weight: bold;
  color: #555;
  font-size: 0.9em;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 1.2em;
  color: #007bff;
}
</style>

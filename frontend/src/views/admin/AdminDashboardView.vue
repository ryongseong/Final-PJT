<template>
  <div class="admin-dashboard">
    <AdminNavbar />

    <div class="dashboard-content">
      <header class="dashboard-header">
        <h1>관리자 대시보드</h1>
        <p class="subtitle">금융 상품 데이터베이스 관리 및 업데이트</p>
      </header>

      <section class="admin-section">
        <h2>빠른 작업</h2>
        <div class="action-buttons-grid">
          <button @click="updateAllProducts" :disabled="loading" class="action-btn primary">
            <i class="icon">🔄</i> 전체 상품 업데이트
          </button>
          <button @click="updateDepositProducts" :disabled="loading" class="action-btn secondary">
            <i class="icon">💰</i> 예금 상품 업데이트
          </button>
          <button @click="updateSavingProducts" :disabled="loading" class="action-btn secondary">
            <i class="icon">🏦</i> 적금 상품 업데이트
          </button>
          <button @click="updateLoanProducts" :disabled="loading" class="action-btn secondary">
            <i class="icon">🏠</i> 대출 상품 업데이트
          </button>
        </div>
        <div v-if="loading" class="loading-indicator">
          <div class="spinner"></div>
          <p>데이터를 업데이트하는 중입니다...</p>
        </div>
        <div
          v-if="message"
          :class="['alert-message', messageType === 'error' ? 'error' : 'success']"
        >
          <i :class="['icon', messageType === 'error' ? '⚠️' : '✅']"></i>
          {{ message }}
        </div>
      </section>

      <section class="admin-section">
        <h2>데이터베이스 개요</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon-wrapper"><i class="icon">📦</i></div>
            <div class="stat-content">
              <h3>전체 금융 상품</h3>
              <p class="stat-number">{{ stats.financialProducts }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon-wrapper"><i class="icon">💰</i></div>
            <div class="stat-content">
              <h3>예금 상품</h3>
              <p class="stat-number">{{ stats.depositProducts }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon-wrapper"><i class="icon">🏦</i></div>
            <div class="stat-content">
              <h3>적금 상품</h3>
              <p class="stat-number">{{ stats.savingProducts }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon-wrapper"><i class="icon">🏠</i></div>
            <div class="stat-content">
              <h3>대출 상품</h3>
              <p class="stat-number">{{ stats.loanProducts }}</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import adminService from '@/services/admin'
import productsService from '@/services/products'
import AdminNavbar from '@/components/admin/AdminNavbar.vue'

const loading = ref(false)
const message = ref('')
const messageType = ref('success')
const stats = ref({
  financialProducts: 0,
  depositProducts: 0,
  savingProducts: 0,
  loanProducts: 0,
})

const showMessage = (msg, type = 'success') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

const fetchStats = async () => {
  try {
    loading.value = true
    const financialProductsResponse = await productsService.getAllFinancialProducts().catch(() => [])
    const depositProductsResponse = await productsService.getDepositProducts().catch(() => [])
    const savingProductsResponse = await productsService.getSavingProducts().catch(() => [])
    const loanProductsResponse = await productsService.getLoanProducts().catch(() => [])

    stats.value.financialProducts = financialProductsResponse.length
    stats.value.depositProducts = depositProductsResponse.length
    stats.value.savingProducts = savingProductsResponse.length
    stats.value.loanProducts = loanProductsResponse.length
  } catch (error) {
    showMessage('통계 로딩 실패: ' + error.message, 'error')
    console.error('Error fetching stats:', error)
  } finally {
    loading.value = false
  }
}

const updateAllProducts = async () => {
  try {
    loading.value = true
    message.value = ''
    await productsService.updateAllProducts()
    showMessage('모든 금융 상품을 성공적으로 업데이트했습니다!')
    await fetchStats()
  } catch (error) {
    showMessage('상품 업데이트 실패: ' + error.message, 'error')
    console.error('Error updating all products:', error)
  } finally {
    loading.value = false
  }
}

const updateDepositProducts = async () => {
  try {
    loading.value = true
    message.value = ''
    await productsService.updateDepositProducts()
    showMessage('예금 상품을 성공적으로 업데이트했습니다!')
    await fetchStats()
  } catch (error) {
    showMessage('예금 상품 업데이트 실패: ' + error.message, 'error')
    console.error('Error updating deposit products:', error)
  } finally {
    loading.value = false
  }
}

const updateSavingProducts = async () => {
  try {
    loading.value = true
    message.value = ''
    await productsService.updateSavingProducts()
    showMessage('적금 상품을 성공적으로 업데이트했습니다!')
    await fetchStats()
  } catch (error) {
    showMessage('적금 상품 업데이트 실패: ' + error.message, 'error')
    console.error('Error updating saving products:', error)
  } finally {
    loading.value = false
  }
}

const updateLoanProducts = async () => {
  try {
    loading.value = true
    message.value = ''
    await productsService.updateMortgageProducts()
    await productsService.updateCreditProducts()
    showMessage('대출 상품을 성공적으로 업데이트했습니다!')
    await fetchStats()
  } catch (error) {
    showMessage('대출 상품 업데이트 실패: ' + error.message, 'error')
    console.error('Error updating loan products:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.admin-dashboard {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--background-primary);
}

.dashboard-content {
  flex-grow: 1;
  padding: 2rem;
  max-width: var(--max-width-content, 1200px);
  margin: 0 auto;
  width: 100%;
}

.dashboard-header {
  margin-bottom: 2.5rem;
  text-align: left;
}

.dashboard-header h1 {
  font-size: 2.5rem;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
  font-family: 'Pretendard Variable', serif;
  font-weight: 700;
}

.dashboard-header .subtitle {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

.admin-section {
  background-color: var(--card-bg);
  padding: 2rem;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--card-shadow);
  margin-bottom: 2.5rem;
  border: 1px solid var(--card-border);
}

.admin-section h2 {
  font-size: 1.5rem;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
  font-weight: 600;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.8rem;
}

.action-buttons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.7rem 1.5rem;
  border-radius: var(--border-radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-speed);
  text-align: center;
  font-size: 0.95rem;
  border: 1px solid transparent;
}

.action-btn .icon {
  margin-right: 0.6rem;
  font-size: 1.1rem;
}

.action-btn.primary {
  background-color: var(--accent-color);
  color: var(--button-text);
  border-color: var(--accent-color);
}

.action-btn.primary:hover:not(:disabled) {
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

.action-btn.secondary {
  background-color: var(--background-primary);
  color: var(--text-secondary);
  border-color: var(--border-color);
}

.action-btn.secondary:hover:not(:disabled) {
  background-color: var(--border-color);
  color: var(--text-primary);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin: 2rem 0;
  color: var(--text-secondary);
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.alert-message {
  padding: 1rem 1.5rem;
  border-radius: var(--border-radius-md);
  margin-top: 1.5rem;
  display: flex;
  align-items: center;
  font-weight: 500;
  font-size: 0.95rem;
}

.alert-message .icon {
  margin-right: 0.75rem;
  font-size: 1.2rem;
}

.alert-message.success {
  background-color: rgba(var(--accent-color-rgb, 163, 184, 153), 0.15);
  color: var(--accent-color);
  border: 1px solid rgba(var(--accent-color-rgb, 163, 184, 153), 0.3);
}

.alert-message.error {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background-color: var(--background-primary);
  padding: 1.5rem;
  border-radius: var(--border-radius-md);
  box-shadow: var(--card-shadow-sm, 0 2px 4px rgba(0,0,0,0.05));
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid var(--border-color);
}

.stat-icon-wrapper {
  background-color: rgba(var(--accent-color-rgb, 163, 184, 153), 0.1);
  color: var(--accent-color);
  border-radius: 50%;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon-wrapper .icon {
  font-size: 1.8rem;
}

.stat-content h3 {
  font-size: 0.95rem;
  color: var(--text-secondary);
  margin-bottom: 0.3rem;
  font-weight: 500;
}

.stat-content .stat-number {
  font-size: 1.8rem;
  color: var(--text-primary);
  font-weight: 700;
}
</style>

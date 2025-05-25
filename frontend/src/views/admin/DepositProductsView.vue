<template>
  <div class="admin-products-view">
    <AdminNavbar />

    <div class="view-content">
      <header class="view-header">
        <h1>예금 상품 옵션 관리</h1>
        <p class="subtitle">등록된 예금 상품의 옵션을 확인하고 관리합니다.</p>
      </header>

      <section class="controls-section card-style">
        <div class="search-filter-bar">
          <div class="search-input-group">
            <i class="icon search-icon">🔍</i>
            <input
              type="text"
              v-model="searchQuery"
              placeholder="상품명, 금융사명 등으로 검색..."
              @keyup.enter="applyFiltersAndSearch"
              class="search-input"
            />
          </div>
          <div class="filter-input-group">
            <i class="icon filter-icon">🗓️</i>
            <select v-model="termFilter" @change="applyFiltersAndSearch" class="filter-select">
              <option value="">전체 저축 기간</option>
              <option v-for="term in availableTerms" :key="term" :value="term">
                {{ term }}개월
              </option>
            </select>
          </div>
          <div class="filter-input-group">
            <i class="icon filter-icon">📈</i>
            <select v-model="rateTypeFilter" @change="applyFiltersAndSearch" class="filter-select">
              <option value="">전체 금리 유형</option>
              <option value="S">단리</option>
              <option value="M">복리</option>
            </select>
          </div>
          <button class="action-btn primary-btn" @click="applyFiltersAndSearch" :disabled="loading">
            <i class="icon">🔎</i> 적용
          </button>
        </div>
      </section>

      <div v-if="loading" class="loading-indicator">
        <div class="spinner"></div>
        <p>예금 상품 옵션 목록을 불러오는 중...</p>
      </div>

      <div
        v-if="message"
        :class="['alert-message', messageType === 'error' ? 'error' : 'success']"
      >
        <i :class="['icon', messageType === 'error' ? '⚠️' : '✅']"></i>
        {{ message }}
      </div>

      <section class="table-section card-style">
        <div class="table-header-actions">
          <h3>예금 상품 옵션 목록</h3>
          <button @click="createNewOption" class="action-btn success-btn add-product-btn">
            <i class="icon">➕</i> 새 예금 옵션 추가
          </button>
        </div>
        <div class="products-table-responsive">
          <table class="products-table">
            <thead>
              <tr>
                <th>금융상품 코드</th>
                <th>금융회사명</th>
                <th>상품명</th>
                <th>금리유형</th>
                <th>저축 기간(개월)</th>
                <th>기본 금리(%)</th>
                <th>최고 금리(%)</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="depositOption in filteredDepositOptions" :key="depositOption.id || depositOption.fin_prdt_cd + depositOption.save_trm">
                <td data-label="금융상품 코드">{{ depositOption.product?.fin_prdt_cd || depositOption.fin_prdt_cd || '-' }}</td>
                <td data-label="금융회사명">{{ depositOption.product?.kor_co_nm || '-' }}</td>
                <td data-label="상품명">{{ depositOption.product?.fin_prdt_nm || '-' }}</td>
                <td data-label="금리유형">{{ depositOption.intr_rate_type === 'S' ? '단리' : '복리' }}</td>
                <td data-label="저축 기간(개월)">{{ depositOption.save_trm }}개월</td>
                <td data-label="기본 금리(%)">{{ depositOption.intr_rate?.toFixed(2) || '0.00' }}%</td>
                <td data-label="최고 금리(%)">{{ depositOption.intr_rate2?.toFixed(2) || '0.00' }}%</td>
                <td data-label="작업" class="actions-cell">
                  <button @click="editOption(depositOption)" class="action-btn icon-btn edit-btn" title="수정">
                    <i class="icon">✏️</i>
                  </button>
                  <button @click="confirmDelete(depositOption)" class="action-btn icon-btn delete-btn" title="삭제">
                    <i class="icon">🗑️</i>
                  </button>
                </td>
              </tr>
              <tr v-if="filteredDepositOptions.length === 0 && !loading">
                <td colspan="8" class="no-data">
                  <p>표시할 예금 상품 옵션이 없습니다.</p>
                  <p v-if="searchQuery || termFilter || rateTypeFilter">다른 검색어나 필터를 시도해보세요.</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Edit/Create Modal -->
      <div v-if="showEditModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-container card-style">
          <div class="modal-header">
            <h3>{{ editMode === 'create' ? '새 예금 옵션 추가' : '예금 옵션 정보 수정' }}</h3>
            <button class="close-modal-btn" @click="closeModal"><i class="icon">✕</i></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveOption" class="modal-form">
              <div class="form-grid">
                <div class="form-group full-width" v-if="editMode === 'create'">
                  <label for="product_fin_prdt_cd">금융상품 선택 (상품 코드)</label>
                   <input
                    type="text"
                    id="product_fin_prdt_cd"
                    v-model="editedOption.product_fin_prdt_cd"
                    required
                    placeholder="연결할 금융상품의 코드를 입력하세요."
                  />
                  <!-- <small>pjt0에서는 product_id 대신 fin_prdt_cd로 직접 연결합니다.</small> -->
                </div>
                 <div class="form-group" v-else>
                  <label>금융상품 코드</label>
                  <input type="text" :value="editedOption.product_fin_prdt_cd || editedOption.fin_prdt_cd" disabled />
                </div>

                <div class="form-group">
                  <label for="dcls_month">공시 월</label>
                  <input
                    type="text"
                    id="dcls_month"
                    v-model="editedOption.dcls_month"
                    required
                    placeholder="YYYYMM"
                  />
                </div>

                <div class="form-group">
                  <label for="intr_rate_type">금리유형</label>
                  <select id="intr_rate_type" v-model="editedOption.intr_rate_type" required>
                    <option value="S">단리</option>
                    <option value="M">복리</option>
                  </select>
                </div>
                <div class="form-group">
                  <label for="save_trm">저축 기간 (개월)</label>
                  <input
                    type="number"
                    id="save_trm"
                    v-model.number="editedOption.save_trm"
                    min="1"
                    required
                  />
                </div>
                <div class="form-group">
                  <label for="intr_rate">기본 금리 (%)</label>
                  <input
                    type="number"
                    id="intr_rate"
                    v-model.number="editedOption.intr_rate"
                    step="0.01"
                    min="0"
                    required
                  />
                </div>
                <div class="form-group">
                  <label for="intr_rate2">최고 금리 (%)</label>
                  <input
                    type="number"
                    id="intr_rate2"
                    v-model.number="editedOption.intr_rate2"
                    step="0.01"
                    min="0"
                    required
                  />
                </div>
              </div>
              <div class="modal-actions">
                <button type="button" class="action-btn secondary-btn" @click="closeModal">취소</button>
                <button type="submit" class="action-btn primary-btn" :disabled="savingChanges">
                  {{ savingChanges ? '저장 중...' : (editMode === 'create' ? '추가하기' : '변경사항 저장') }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <div v-if="showDeleteModal" class="modal-overlay" @click.self="cancelDelete">
        <div class="modal-container confirmation-modal card-style">
          <div class="modal-header">
            <h3>삭제 확인</h3>
            <button class="close-modal-btn" @click="cancelDelete"><i class="icon">✕</i></button>
          </div>
          <div class="modal-body">
            <p>정말로 이 예금 상품 옵션을 삭제하시겠습니까?</p>
            <div v-if="optionToDelete" class="product-info-delete">
              <strong>상품명:</strong> {{ optionToDelete.product?.fin_prdt_nm || optionToDelete.fin_prdt_cd || '-' }}<br />
              <strong>저축 기간:</strong> {{ optionToDelete.save_trm }} 개월
            </div>
            <p class="warning-text"><i class="icon">⚠️</i> 이 작업은 되돌릴 수 없습니다!</p>
          </div>
          <div class="modal-actions">
            <button class="action-btn secondary-btn" @click="cancelDelete">취소</button>
            <button class="action-btn danger-btn" @click="deleteOption" :disabled="deleting">
              {{ deleting ? '삭제 중...' : '삭제' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import productsService from '@/services/products' // pjt0은 productsService에 모든 API가 있음
import AdminNavbar from '@/components/admin/AdminNavbar.vue'

const allDepositProducts = ref([]) // 모든 예금 상품 (옵션들을 포함한 상품)
const allDepositOptions = ref([])  // 모든 예금 상품 옵션 (테이블에 표시될 데이터)
const filteredDepositOptions = ref([]) // 필터링된 예금 상품 옵션

const loading = ref(false)
const message = ref('')
const messageType = ref('success')
const searchQuery = ref('')
const termFilter = ref('')
const rateTypeFilter = ref('')
const availableTerms = ref([6, 12, 24, 36]) // 예시 기간, 실제 데이터에서 추출 가능

const showEditModal = ref(false)
const editMode = ref('edit') // 'create', 'edit'
const editedOption = ref({ // pjt0에서는 '상품 옵션'을 직접 수정/생성
  id: null, // 옵션의 ID (백엔드에서 자동 생성될 수 있음)
  product_fin_prdt_cd: '', // 연결될 금융상품의 코드 (DepositProduct의 fin_prdt_cd)
  dcls_month: '',
  intr_rate_type: 'S',
  save_trm: 12,
  intr_rate: null,
  intr_rate2: null,
})
const savingChanges = ref(false)

const showDeleteModal = ref(false)
const optionToDelete = ref(null) // 삭제할 '옵션'
const deleting = ref(false)

const showMessage = (msg, type = 'success') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

const fetchAllDeposits = async () => {
  try {
    loading.value = true
    message.value = ''
    const response = await productsService.getDepositProducts() // pjt0 API 호출
    allDepositProducts.value = response || [] // productsService는 배열을 직접 반환할 수 있음

    // pjt0 데이터 구조에 맞춰 옵션들을 추출하고, 각 옵션에 부모 상품 정보를 연결
    const options = []
    allDepositProducts.value.forEach(product => {
      if (product.options && product.options.length > 0) {
        product.options.forEach(option => {
          options.push({
            ...option, // 금리, 기간 등 옵션 정보
            id: option.id, // 옵션의 고유 ID가 있다면 사용
            product_fin_prdt_cd: product.fin_prdt_cd, // 부모 상품 코드
            product: { // 부모 상품의 주요 정보 (테이블 표시용)
              fin_prdt_cd: product.fin_prdt_cd,
              kor_co_nm: product.kor_co_nm,
              fin_prdt_nm: product.fin_prdt_nm,
            }
          })
        })
      }
    })
    allDepositOptions.value = options
    applyFiltersAndSearch()

    // 사용 가능한 저축 기간 업데이트 (allDepositOptions에서 추출)
    const terms = new Set(allDepositOptions.value.map(opt => opt.save_trm))
    availableTerms.value = Array.from(terms).sort((a, b) => a - b)
  } catch (error) {
    showMessage(`예금 상품 목록 로딩 실패: ${error.message}`, 'error')
    console.error('Error fetching deposits:', error)
    allDepositProducts.value = []
    allDepositOptions.value = []
    filteredDepositOptions.value = []
  } finally {
    loading.value = false
  }
}

const applyFiltersAndSearch = () => {
  let options = [...allDepositOptions.value]

  if (termFilter.value) {
    options = options.filter(opt => opt.save_trm === parseInt(termFilter.value))
  }

  if (rateTypeFilter.value) {
    options = options.filter(opt => opt.intr_rate_type === rateTypeFilter.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    options = options.filter(opt => {
      const productName = opt.product?.fin_prdt_nm?.toLowerCase() || ''
      const companyName = opt.product?.kor_co_nm?.toLowerCase() || ''
      const productCode = opt.product_fin_prdt_cd?.toLowerCase() || ''
      return productName.includes(query) || companyName.includes(query) || productCode.includes(query)
    })
  }
  filteredDepositOptions.value = options
}

const createNewOption = () => { // 실제로는 새 '옵션'을 추가하는 UI
  editMode.value = 'create'
  const currentDate = new Date()
  const year = currentDate.getFullYear()
  const month = (currentDate.getMonth() + 1).toString().padStart(2, '0')

  editedOption.value = {
    id: null,
    product_fin_prdt_cd: '', // 사용자가 입력
    dcls_month: `${year}${month}`,
    intr_rate_type: 'S',
    save_trm: 12,
    intr_rate: null,
    intr_rate2: null,
  }
  showEditModal.value = true
}

const editOption = (option) => { // '옵션' 수정
  editMode.value = 'edit'
  editedOption.value = { ...option } 
  showEditModal.value = true
}

const closeModal = () => {
  showEditModal.value = false
}

// pjt0의 productsService에는 예금 '옵션'을 직접 생성/수정/삭제하는 API가 없을 가능성이 높습니다.
// 이 로직은 UI상의 표현이며, 실제 백엔드 연동이 필요합니다.
const saveOption = async () => {
  savingChanges.value = true
  message.value = ''
  try {
    const payload = { ...editedOption.value }
    payload.save_trm = Number(payload.save_trm)
    payload.intr_rate = Number(payload.intr_rate)
    payload.intr_rate2 = Number(payload.intr_rate2)

    console.log('Saving deposit option (pjt0 - UI only):', payload)
    // TODO: pjt0 백엔드에 예금 상품 '옵션' 생성/수정 API 연동 필요
    // 예시: if (editMode.value === 'create') { await productsService.createDepositOption(payload) } 
    //      else { await productsService.updateDepositOption(payload.id, payload) }
    
    showMessage('예금 상품 정보가 (UI상에서) 저장되었습니다. 백엔드 연동 필요', 'success')
    closeModal()
    await fetchAllDeposits() // 목록 새로고침
  } catch (error) {
    showMessage(`저장 실패: ${error.message}`, 'error')
    console.error('Error saving deposit option:', error)
  } finally {
    savingChanges.value = false
  }
}

const confirmDelete = (option) => {
  optionToDelete.value = option
  showDeleteModal.value = true
}

const cancelDelete = () => {
  optionToDelete.value = null
  showDeleteModal.value = false
}

const deleteOption = async () => { // 실제로는 '옵션' 삭제
  if (!optionToDelete.value) return
  deleting.value = true
  message.value = ''
  try {
    console.log('Deleting deposit option (pjt0 - UI only):', optionToDelete.value)
    // TODO: pjt0 백엔드에 예금 상품 '옵션' 삭제 API 연동 필요
    // 예시: await productsService.deleteDepositOption(optionToDelete.value.id)
    showMessage('예금 상품 옵션이 (UI상에서) 삭제되었습니다. 백엔드 연동 필요', 'success')
    optionToDelete.value = null
    showDeleteModal.value = false
    await fetchAllDeposits() // 목록 새로고침
  } catch (error) {
    showMessage(`삭제 실패: ${error.message}`, 'error')
    console.error('Error deleting deposit option:', error)
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  fetchAllDeposits()
})
</script>

<style scoped>
/* General View Styles - Consistent with FinancialProductsView */
.admin-products-view {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--background-primary);
}

.view-content {
  flex-grow: 1;
  padding: 2rem;
  max-width: var(--max-width-content, 1400px); /* Consistent max-width */
  margin: 0 auto;
  width: 100%;
}

.view-header {
  margin-bottom: 2rem;
}

.view-header h1 {
  font-size: 2.2rem;
  color: var(--text-primary);
  margin-bottom: 0.4rem;
  font-family: 'Playfair Display', serif;
  font-weight: 700;
}

.view-header .subtitle {
  font-size: 1.05rem;
  color: var(--text-secondary);
}

.card-style {
  background-color: var(--card-bg);
  padding: 1.5rem;
  border-radius: var(--border-radius-lg); /* Larger border radius */
  box-shadow: var(--card-shadow);
  margin-bottom: 2rem;
  border: 1px solid var(--card-border);
}

/* Controls Section - Consistent with FinancialProductsView */
.controls-section .search-filter-bar {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); /* Responsive grid */
  gap: 1rem;
  align-items: center;
}

.search-input-group, .filter-input-group {
  display: flex;
  align-items: center;
  background-color: var(--background-primary);
  border-radius: var(--border-radius-md);
  padding: 0.5rem 0.8rem;
  border: 1px solid var(--border-color);
}

.search-input-group .icon, .filter-input-group .icon {
  color: var(--text-secondary);
  margin-right: 0.5rem;
  font-size: 1.1rem;
}

.search-input, .filter-select {
  border: none;
  outline: none;
  background-color: transparent;
  flex-grow: 1;
  font-size: 0.95rem;
  color: var(--text-primary);
  padding: 0.3rem;
}

.filter-select { cursor: pointer; }

/* Action Buttons - Consistent with FinancialProductsView */
.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.6rem 1.2rem;
  border-radius: var(--border-radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-speed);
  text-align: center;
  font-size: 0.9rem;
  border: 1px solid transparent;
}

.action-btn .icon {
  margin-right: 0.5rem;
}
.action-btn .icon:last-child:first-child {
    margin-right: 0; /* No margin if only icon */
}

.action-btn.primary-btn {
  background-color: var(--accent-color);
  color: var(--button-text);
  border-color: var(--accent-color);
  grid-column: span 1; /* Ensure it takes one grid cell */
}
.action-btn.primary-btn:hover:not(:disabled) {
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

.action-btn.secondary-btn {
  background-color: var(--background-primary);
  color: var(--text-secondary);
  border-color: var(--border-color);
}
.action-btn.secondary-btn:hover:not(:disabled) {
  background-color: var(--border-color);
  color: var(--text-primary);
}

.action-btn.success-btn {
  background-color: var(--accent-color); /* Using accent for success to match theme */
  color: var(--button-text);
  border-color: var(--accent-color);
}
.action-btn.success-btn:hover:not(:disabled) {
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

.action-btn.danger-btn {
  background-color: #EF4444;
  color: white;
  border-color: #EF4444;
}
.action-btn.danger-btn:hover:not(:disabled) {
  background-color: #DC2626;
  border-color: #DC2626;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-btn.icon-btn {
  padding: 0.5rem;
  background-color: transparent;
  border: none;
  color: var(--text-secondary);
}
.action-btn.icon-btn .icon {
  margin-right: 0;
  font-size: 1.2rem;
}
.action-btn.icon-btn.edit-btn:hover {
  color: var(--accent-color);
}
.action-btn.icon-btn.delete-btn:hover {
  color: #EF4444;
}

/* Loading and Alerts - Consistent with FinancialProductsView */
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
  to { transform: rotate(360deg); }
}

.alert-message {
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  font-weight: 500;
}
.alert-message .icon { margin-right: 0.75rem; font-size: 1.2rem; }
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

/* Table Section - Consistent with FinancialProductsView */
.table-section .table-header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.table-section .table-header-actions h3 {
  font-size: 1.3rem;
  color: var(--text-primary);
  font-weight: 600;
}

.products-table-responsive { overflow-x: auto; }
.products-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}
.products-table th, .products-table td {
  padding: 0.8rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
  vertical-align: middle;
}
.products-table th {
  background-color: var(--background-primary);
  font-weight: 600;
  color: var(--text-secondary);
  white-space: nowrap;
}
.products-table tbody tr:hover {
  background-color: rgba(var(--accent-color-rgb, 163, 184, 153), 0.05);
}
.actions-cell { display: flex; gap: 0.5rem; align-items: center; white-space: nowrap; }
.no-data td { text-align: center; padding: 2rem; color: var(--text-secondary); }
.no-data p { margin-bottom: 0.5rem; }

/* Modal Styles - Consistent with FinancialProductsView */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex; align-items: center; justify-content: center;
  z-index: 1050; padding: 1rem;
}
.modal-container {
  width: 100%;
  max-width: 700px; /* Slightly wider for more fields */
  max-height: 90vh;
  overflow-y: auto;
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding-bottom: 1rem; margin-bottom: 1.5rem; border-bottom: 1px solid var(--border-color);
}
.modal-header h3 { font-size: 1.4rem; color: var(--text-primary); font-weight: 600; margin: 0; }
.close-modal-btn {
  background: none; border: none; font-size: 1.5rem; line-height: 1;
  cursor: pointer; color: var(--text-secondary); padding: 0.3rem;
}
.close-modal-btn:hover { color: var(--text-primary); }

.modal-form .form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); /* Responsive grid */
  gap: 1.2rem;
}
.modal-form .form-group { margin-bottom: 0; }
.modal-form .form-group.full-width { grid-column: 1 / -1; }
.modal-form label {
  display: block; margin-bottom: 0.5rem; font-weight: 500;
  color: var(--text-secondary); font-size: 0.85rem;
}
.modal-form input[type="text"],
.modal-form input[type="number"],
.modal-form textarea,
.modal-form select {
  width: 100%; padding: 0.7rem 0.9rem; border: 1px solid var(--border-color);
  border-radius: 6px; font-size: 0.95rem; background-color: var(--background-primary);
  color: var(--text-primary);
  transition: border-color var(--transition-speed), box-shadow var(--transition-speed);
}
.modal-form input[type="text"]:focus,
.modal-form input[type="number"]:focus,
.modal-form textarea:focus,
.modal-form select:focus {
  outline: none; border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(var(--accent-color-rgb, 163, 184, 153), 0.2);
}
.modal-form textarea { resize: vertical; min-height: 80px; }

.modal-actions {
  display: flex; justify-content: flex-end; gap: 0.8rem; margin-top: 2rem;
  padding-top: 1.5rem; border-top: 1px solid var(--border-color);
}

.confirmation-modal .modal-body p { margin-bottom: 0.8rem; font-size: 1.05rem; color: var(--text-primary); }
.confirmation-modal .product-info-delete {
  background-color: var(--background-primary); padding: 0.8rem; border-radius: 6px;
  margin-bottom: 1rem; border: 1px solid var(--border-color); font-size: 0.9rem;
}
.confirmation-modal .warning-text {
  color: #D97706; font-weight: 500; display: flex; align-items: center;
}
.confirmation-modal .warning-text .icon { margin-right: 0.4rem; font-size: 1.1rem; }

/* Responsive Table - Consistent with FinancialProductsView */
@media (max-width: 992px) { /* Adjusted breakpoint for better table view */
  .products-table thead { display: none; }
  .products-table tr { display: block; margin-bottom: 1rem; border: 1px solid var(--border-color); border-radius: 8px; box-shadow: var(--card-shadow); }
  .products-table td { display: block; text-align: right; padding-left: 50%; position: relative; border-bottom: 1px solid var(--border-color); }
  .products-table td:last-child { border-bottom: none; }
  .products-table td::before {
    content: attr(data-label);
    position: absolute; left: 1rem; font-weight: 600;
    color: var(--text-secondary); text-align: left; white-space: nowrap;
  }
  .actions-cell { justify-content: flex-end; }
}

@media (max-width: 768px) {
  .view-header h1 { font-size: 1.8rem; }
  .controls-section .search-filter-bar {
    grid-template-columns: 1fr; /* Stack filters on smaller screens */
  }
  .modal-form .form-grid {
    grid-template-columns: 1fr; /* Stack form elements in modal */
  }
}
</style>

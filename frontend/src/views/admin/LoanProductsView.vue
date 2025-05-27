<template>
  <div class="admin-products-view">
    <AdminNavbar />
    <div class="view-content">
      <header class="view-header">
        <h1>대출 상품 옵션 관리</h1>
        <p class="subtitle">등록된 대출 상품의 옵션을 확인하고 관리합니다.</p>
      </header>

      <section class="controls-section card-style">
        <div class="search-filter-bar">
          <div class="search-box">
            <input
              type="text"
              v-model="searchQuery"
              placeholder="상품명, 금융사명 등으로 검색..."
              @keyup.enter="applyFiltersAndSearch"
              class="search-input-field"
            />
            <i class="icon search-icon">🔍</i>
          </div>
          <div class="filter-input-group">
            <i class="icon filter-icon">📊</i>
            <select
              v-model="loanProductTypeFilter"
              @change="applyFiltersAndSearch"
              class="filter-select"
            >
              <option value="">전체 대출 유형</option>
              <option value="mortgage">주택담보대출</option>
              <option value="credit">신용대출</option>
            </select>
          </div>
          <div class="filter-input-group">
            <i class="icon filter-icon">💼</i>
            <select
              v-model="loanOptionTypeFilter"
              @change="applyFiltersAndSearch"
              class="filter-select"
            >
              <option value="">전체 옵션 유형</option>
              <template v-if="loanProductTypeFilter === 'mortgage' || !loanProductTypeFilter">
                <option
                  v-for="type in availableMortgageTypes"
                  :key="type.value"
                  :value="type.value"
                >
                  {{ type.text }}
                </option>
              </template>
              <template v-if="loanProductTypeFilter === 'credit' || !loanProductTypeFilter">
                <option
                  v-for="type in availableCreditLoanProductTypes"
                  :key="type.value"
                  :value="type.value"
                >
                  {{ type.text }}
                </option>
              </template>
            </select>
          </div>
          <button class="action-btn primary-btn" @click="applyFiltersAndSearch" :disabled="loading">
            <i class="icon"></i> 검색
          </button>
        </div>
      </section>

      <div v-if="loading" class="loading-indicator">
        <div class="spinner"></div>
        <p>대출 상품 옵션을 불러오는 중...</p>
      </div>

      <div v-if="message" :class="['alert-message', messageType === 'error' ? 'error' : 'success']">
        <i :class="['icon', messageType === 'error' ? '⚠️' : '✅']"></i>
        {{ message }}
      </div>

      <section class="table-section card-style">
        <div class="table-header-actions">
          <h3>대출 상품 옵션 목록</h3>
          <button @click="createNewOption" class="action-btn success-btn add-product-btn">
            <i class="icon">➕</i> 새 대출 옵션 추가
          </button>
        </div>
        <div class="products-table-responsive">
          <table class="products-table">
            <thead>
              <tr>
                <th>금융상품 코드</th>
                <th>금융회사명</th>
                <th>상품명</th>
                <th>대출유형</th>
                <th>세부유형</th>
                <th>대출금리</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="option in filteredLoanOptions"
                :key="option.id || option.product_fin_prdt_cd + option.lend_rate_type"
              >
                <td data-label="금융상품 코드">
                  {{ option.product?.fin_prdt_cd || option.product_fin_prdt_cd || '-' }}
                </td>
                <td data-label="금융회사명">{{ option.product?.kor_co_nm || '-' }}</td>
                <td data-label="상품명">{{ option.product?.fin_prdt_nm || '-' }}</td>
                <td data-label="대출유형">
                  {{ option.loan_product_type === 'mortgage' ? '주택담보대출' : '신용대출' }}
                </td>
                <td data-label="세부유형">{{ getLoanOptionSpecificType(option) }}</td>
                <td data-label="대출금리">
                  {{ option.lend_rate_min }}% ~ {{ option.lend_rate_max }}% ({{
                    getLendRateType(option.lend_rate_type)
                  }})
                </td>
                <td data-label="작업" class="actions-cell">
                  <button
                    @click="editOption(option)"
                    class="action-btn icon-btn edit-btn"
                    title="수정"
                  >
                    <i class="icon">✏️</i>
                  </button>
                  <button
                    @click="confirmDeleteOption(option)"
                    class="action-btn icon-btn delete-btn"
                    title="삭제"
                  >
                    <i class="icon">🗑️</i>
                  </button>
                </td>
              </tr>
              <tr v-if="filteredLoanOptions.length === 0 && !loading">
                <td colspan="7" class="no-data">
                  <p>표시할 대출 상품 옵션이 없습니다.</p>
                  <p v-if="searchQuery || loanProductTypeFilter || loanOptionTypeFilter">
                    다른 검색어나 필터를 시도해보세요.
                  </p>
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
            <h3>{{ editMode === 'create' ? '새 대출 옵션 추가' : '대출 옵션 정보 수정' }}</h3>
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
                </div>
                <div class="form-group" v-else>
                  <label>금융상품 코드</label>
                  <div class="static-value">{{ editedOption.product_fin_prdt_cd }}</div>
                </div>
                <div class="form-group">
                  <label for="loan_product_type">대출 상품 유형</label>
                  <select
                    id="loan_product_type"
                    v-model="editedOption.loan_product_type"
                    @change="resetLoanSpecificType"
                    required
                  >
                    <option value="mortgage">주택담보대출</option>
                    <option value="credit">신용대출</option>
                  </select>
                </div>

                <div class="form-group" v-if="editedOption.loan_product_type === 'mortgage'">
                  <label for="mrtg_type">담보 유형</label>
                  <select id="mrtg_type" v-model="editedOption.mrtg_type" required>
                    <option
                      v-for="type in availableMortgageTypes"
                      :key="type.value"
                      :value="type.value"
                    >
                      {{ type.text }}
                    </option>
                  </select>
                </div>

                <div class="form-group" v-if="editedOption.loan_product_type === 'credit'">
                  <label for="crdt_prdt_type">신용대출 유형</label>
                  <select id="crdt_prdt_type" v-model="editedOption.crdt_prdt_type" required>
                    <option
                      v-for="type in availableCreditLoanProductTypes"
                      :key="type.value"
                      :value="type.value"
                    >
                      {{ type.text }}
                    </option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="lend_rate_type">금리 형태</label>
                  <select id="lend_rate_type" v-model="editedOption.lend_rate_type" required>
                    <option value="F">고정금리</option>
                    <option value="C">변동금리</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="rpay_type">상환 방식</label>
                  <select id="rpay_type" v-model="editedOption.rpay_type">
                    <option
                      v-for="type in availableRepayTypes"
                      :key="type.value"
                      :value="type.value"
                    >
                      {{ type.text }}
                    </option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="lend_rate_min">최저 금리 (%)</label>
                  <input
                    type="number"
                    id="lend_rate_min"
                    v-model="editedOption.lend_rate_min"
                    min="0"
                    max="20"
                    step="0.01"
                    required
                  />
                </div>

                <div class="form-group">
                  <label for="lend_rate_max">최고 금리 (%)</label>
                  <input
                    type="number"
                    id="lend_rate_max"
                    v-model="editedOption.lend_rate_max"
                    min="0"
                    max="20"
                    step="0.01"
                    required
                  />
                </div>

                <div class="form-group">
                  <label for="lend_rate_avg">평균 금리 (%)</label>
                  <input
                    type="number"
                    id="lend_rate_avg"
                    v-model="editedOption.lend_rate_avg"
                    min="0"
                    max="20"
                    step="0.01"
                  />
                </div>
              </div>
              <div class="modal-actions">
                <button type="button" class="action-btn secondary-btn" @click="closeModal">
                  취소
                </button>
                <button type="submit" class="action-btn primary-btn" :disabled="savingChanges">
                  {{
                    savingChanges
                      ? '저장 중...'
                      : editMode === 'create'
                        ? '추가하기'
                        : '변경사항 저장'
                  }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <div v-if="showDeleteModal" class="modal-overlay" @click.self="cancelDeleteOption">
        <div class="modal-container confirmation-modal card-style">
          <div class="modal-header">
            <h3>삭제 확인</h3>
            <button class="close-modal-btn" @click="cancelDeleteOption">
              <i class="icon">✕</i>
            </button>
          </div>
          <div class="modal-body">
            <p>정말로 이 대출 상품 옵션을 삭제하시겠습니까?</p>
            <div v-if="optionToDelete" class="product-info-delete">
              <p>
                <strong>상품:</strong> {{ optionToDelete.product?.fin_prdt_nm || '미지정' }} ({{
                  optionToDelete.product?.kor_co_nm || '미지정'
                }})
              </p>
              <p>
                <strong>대출유형:</strong>
                {{ optionToDelete.loan_product_type === 'mortgage' ? '주택담보대출' : '신용대출' }}
              </p>
              <p><strong>세부유형:</strong> {{ getLoanOptionSpecificType(optionToDelete) }}</p>
              <p>
                <strong>금리:</strong> {{ optionToDelete.lend_rate_min }}% ~
                {{ optionToDelete.lend_rate_max }}%
              </p>
            </div>
            <p class="warning-text"><i class="icon">⚠️</i> 이 작업은 되돌릴 수 없습니다!</p>
            <div class="modal-actions">
              <button class="action-btn secondary-btn" @click="cancelDeleteOption">취소</button>
              <button class="action-btn danger-btn" @click="deleteOption" :disabled="deleting">
                {{ deleting ? '삭제 중...' : '삭제' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import productsService from '@/services/products'
import AdminNavbar from '@/components/admin/AdminNavbar.vue'

const allLoanProducts = ref([])
const allLoanOptions = ref([])
const filteredLoanOptions = ref([])

const loading = ref(false)
const message = ref('')
const messageType = ref('success')

const searchQuery = ref('')
const loanProductTypeFilter = ref('')
const loanOptionTypeFilter = ref('')

const availableMortgageTypes = ref([])
const availableCreditLoanProductTypes = ref([])
const availableRepayTypes = ref([])
const availableLendRateTypes = ref([])

const showEditModal = ref(false)
const editMode = ref('edit')
const editedOption = ref({
  id: null,
  product_fin_prdt_cd: '',
  loan_product_type: 'mortgage',
  dcls_month: '',
  mrtg_type: '',
  rpay_type: '',
  crdt_prdt_type: '',
  lend_rate_type: '',
  lend_rate_min: null,
  lend_rate_max: null,
  lend_rate_avg: null,
})
const savingChanges = ref(false)

const showDeleteModal = ref(false)
const optionToDelete = ref(null)
const deleting = ref(false)

const showMessage = (msg, type = 'success') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

const mrtgTypeMap = { APT: '아파트', ETC: '기타주택' }
const repayTypeMap = { CD: '원리금분할상환', CI: '원금분할상환', CS: '만기일시상환' }
const lendRateTypeMap = { F: '고정금리', C: '변동금리' }
const crdtPrdtTypeMap = {
  G: '일반신용대출',
  M: '마이너스한도대출',
  C: '신용카드연계대출',
}

const getLoanOptionSpecificType = (option) => {
  if (option.loan_product_type === 'mortgage') {
    return mrtgTypeMap[option.mrtg_type] || option.mrtg_type
  } else if (option.loan_product_type === 'credit') {
    return crdtPrdtTypeMap[option.crdt_prdt_type] || option.crdt_prdt_type
  }
  return '-'
}

const getLendRateType = (typeCode) => {
  return lendRateTypeMap[typeCode] || typeCode
}

const populateFilterOptions = () => {
  const mortgageTypes = new Set()
  const creditTypes = new Set()
  const repayTypes = new Set()
  const lendRateTypes = new Set()

  allLoanOptions.value.forEach((opt) => {
    if (opt.loan_product_type === 'mortgage') {
      if (opt.mrtg_type) mortgageTypes.add(opt.mrtg_type)
      if (opt.rpay_type) repayTypes.add(opt.rpay_type)
    } else if (opt.loan_product_type === 'credit') {
      if (opt.crdt_prdt_type) creditTypes.add(opt.crdt_prdt_type)
    }
    if (opt.lend_rate_type) lendRateTypes.add(opt.lend_rate_type)
  })

  availableMortgageTypes.value = Array.from(mortgageTypes)
    .map((val) => ({ value: val, text: mrtgTypeMap[val] || val }))
    .sort((a, b) => a.text.localeCompare(b.text))
  availableCreditLoanProductTypes.value = Array.from(creditTypes)
    .map((val) => ({ value: val, text: crdtPrdtTypeMap[val] || val }))
    .sort((a, b) => a.text.localeCompare(b.text))
  availableRepayTypes.value = Array.from(repayTypes)
    .map((val) => ({ value: val, text: repayTypeMap[val] || val }))
    .sort((a, b) => a.text.localeCompare(b.text))
  availableLendRateTypes.value = Array.from(lendRateTypes)
    .map((val) => ({ value: val, text: lendRateTypeMap[val] || val }))
    .sort((a, b) => a.text.localeCompare(b.text))
}

const fetchAllLoanData = async () => {
  try {
    loading.value = true
    message.value = ''
    const response = await productsService.getLoanProducts()
    allLoanProducts.value = response || []

    const options = []
    allLoanProducts.value.forEach((product) => {
      if (product.mortgage_loan_options && product.mortgage_loan_options.length > 0) {
        product.mortgage_loan_options.forEach((opt) => {
          options.push({
            ...opt,
            unique_id: `M-${product.fin_prdt_cd}-${opt.id || opt.mrtg_type + opt.rpay_type}`,
            loan_product_type: 'mortgage',
            product_fin_prdt_cd: product.fin_prdt_cd,
            product: {
              fin_prdt_cd: product.fin_prdt_cd,
              kor_co_nm: product.kor_co_nm,
              fin_prdt_nm: product.fin_prdt_nm,
            },
          })
        })
      }
      if (product.credit_loan_options && product.credit_loan_options.length > 0) {
        product.credit_loan_options.forEach((opt) => {
          options.push({
            ...opt,
            unique_id: `C-${product.fin_prdt_cd}-${opt.id || opt.crdt_prdt_type}`,
            loan_product_type: 'credit',
            product_fin_prdt_cd: product.fin_prdt_cd,
            product: {
              fin_prdt_cd: product.fin_prdt_cd,
              kor_co_nm: product.kor_co_nm,
              fin_prdt_nm: product.fin_prdt_nm,
            },
          })
        })
      }
    })
    allLoanOptions.value = options
    populateFilterOptions()
    applyFiltersAndSearch()
  } catch (error) {
    showMessage('대출 상품 목록 로딩 실패: ' + error.message, 'error')
    console.error('Error fetching loan data:', error)
    allLoanProducts.value = []
    allLoanOptions.value = []
    filteredLoanOptions.value = []
  } finally {
    loading.value = false
  }
}

const applyFiltersAndSearch = () => {
  let options = [...allLoanOptions.value]

  if (loanProductTypeFilter.value) {
    options = options.filter((opt) => opt.loan_product_type === loanProductTypeFilter.value)
  }

  if (loanOptionTypeFilter.value) {
    if (loanProductTypeFilter.value === 'mortgage' || !loanProductTypeFilter.value) {
      options = options.filter(
        (opt) =>
          opt.loan_product_type === 'mortgage' && opt.mrtg_type === loanOptionTypeFilter.value,
      )
    }
    if (loanProductTypeFilter.value === 'credit' || !loanProductTypeFilter.value) {
      options = options.filter(
        (opt) =>
          opt.loan_product_type === 'credit' && opt.crdt_prdt_type === loanOptionTypeFilter.value,
      )
    }
    if (loanProductTypeFilter.value) {
      options = options.filter((opt) => {
        if (opt.loan_product_type === 'mortgage')
          return opt.mrtg_type === loanOptionTypeFilter.value
        if (opt.loan_product_type === 'credit')
          return opt.crdt_prdt_type === loanOptionTypeFilter.value
        return false
      })
    } else {
      options = options.filter((opt) => {
        return (
          (opt.loan_product_type === 'mortgage' && opt.mrtg_type === loanOptionTypeFilter.value) ||
          (opt.loan_product_type === 'credit' && opt.crdt_prdt_type === loanOptionTypeFilter.value)
        )
      })
    }
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    options = options.filter((opt) => {
      const productName = opt.product?.fin_prdt_nm?.toLowerCase() || ''
      const companyName = opt.product?.kor_co_nm?.toLowerCase() || ''
      const productCode = opt.product_fin_prdt_cd?.toLowerCase() || ''
      return (
        productName.includes(query) || companyName.includes(query) || productCode.includes(query)
      )
    })
  }
  filteredLoanOptions.value = options
}

const createNewOption = () => {
  editMode.value = 'create'
  const currentDate = new Date()
  const year = currentDate.getFullYear()
  const month = (currentDate.getMonth() + 1).toString().padStart(2, '0')

  editedOption.value = {
    id: null,
    product_fin_prdt_cd: '',
    loan_product_type: 'mortgage',
    dcls_month: `${year}${month}`,
    mrtg_type: availableMortgageTypes.value.length > 0 ? availableMortgageTypes.value[0].value : '',
    rpay_type: availableRepayTypes.value.length > 0 ? availableRepayTypes.value[0].value : '',
    crdt_prdt_type: '',
    lend_rate_type:
      availableLendRateTypes.value.length > 0 ? availableLendRateTypes.value[0].value : '',
    lend_rate_min: null,
    lend_rate_max: null,
    lend_rate_avg: null,
  }
  showEditModal.value = true
}

const editOption = (option) => {
  editMode.value = 'edit'
  editedOption.value = { ...option }
  editedOption.value.lend_rate_min = Number(option.lend_rate_min) || null
  editedOption.value.lend_rate_max = Number(option.lend_rate_max) || null
  editedOption.value.lend_rate_avg = Number(option.lend_rate_avg) || null
  showEditModal.value = true
}

const closeModal = () => {
  showEditModal.value = false
}

const resetLoanSpecificType = () => {
  if (editedOption.value.loan_product_type === 'mortgage') {
    editedOption.value.crdt_prdt_type = ''
    editedOption.value.mrtg_type =
      availableMortgageTypes.value.length > 0 ? availableMortgageTypes.value[0].value : ''
    editedOption.value.rpay_type =
      availableRepayTypes.value.length > 0 ? availableRepayTypes.value[0].value : ''
  } else if (editedOption.value.loan_product_type === 'credit') {
    editedOption.value.mrtg_type = ''
    editedOption.value.rpay_type = ''
    editedOption.value.crdt_prdt_type =
      availableCreditLoanProductTypes.value.length > 0
        ? availableCreditLoanProductTypes.value[0].value
        : ''
  }
}

const saveOption = async () => {
  savingChanges.value = true
  message.value = ''
  try {
    const payload = { ...editedOption.value }
    payload.lend_rate_min = Number(payload.lend_rate_min)
    payload.lend_rate_max = Number(payload.lend_rate_max)
    payload.lend_rate_avg = payload.lend_rate_avg ? Number(payload.lend_rate_avg) : null

    console.log('Saving loan option (pjt0 - UI only):', payload)
    showMessage('대출 옵션 정보가 (UI상에서) 저장되었습니다. 백엔드 연동 필요', 'success')
    closeModal()
    await fetchAllLoanData()
  } catch (error) {
    showMessage('옵션 저장 실패: ' + error.message, 'error')
    console.error('Error saving loan option:', error)
  } finally {
    savingChanges.value = false
  }
}

const confirmDeleteOption = (option) => {
  optionToDelete.value = option
  showDeleteModal.value = true
}

const cancelDeleteOption = () => {
  optionToDelete.value = null
  showDeleteModal.value = false
}

const deleteOption = async () => {
  if (!optionToDelete.value) return
  deleting.value = true
  message.value = ''
  try {
    console.log('Deleting loan option (pjt0 - UI only):', optionToDelete.value)
    showMessage('대출 옵션이 (UI상에서) 삭제되었습니다. 백엔드 연동 필요', 'success')
    optionToDelete.value = null
    showDeleteModal.value = false
    await fetchAllLoanData()
  } catch (error) {
    showMessage('옵션 삭제 실패: ' + error.message, 'error')
    console.error('Error deleting loan option:', error)
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  fetchAllLoanData()
})
</script>

<style scoped>
.admin-products-view {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--background-primary);
}

.view-content {
  flex-grow: 1;
  padding: 2rem;
  max-width: var(--max-width-content, 1400px);
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
  font-family: 'Pretendard Variable', serif;
  font-weight: 700;
}

.view-header .subtitle {
  font-size: 1.05rem;
  color: var(--text-secondary);
}

.card-style {
  background-color: var(--card-bg);
  padding: 1.5rem;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--card-shadow);
  margin-bottom: 2rem;
  border: 1px solid var(--card-border);
}

.controls-section .search-filter-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm, 0.5rem);
  padding: var(--spacing-md, 1rem);
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  background-color: var(--background-primary);
  border-radius: var(--input-border-radius, 8px);
  padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
  flex-grow: 1;
  min-width: 250px;
  border: 1px solid var(--border-color);
}

.search-input-field {
  border: none;
  outline: none;
  background-color: transparent;
  flex-grow: 1;
  padding: var(--spacing-sm, 0.5rem);
  font-size: var(--font-size-md, 1rem);
  color: var(--text-input, var(--text-primary));
  font-family: var(--font-body);
}

.search-input-field::placeholder {
  color: var(--text-secondary, #6c757d);
}

.search-box .search-icon {
  color: var(--text-secondary);
  font-size: 1.2rem;
  margin-left: var(--spacing-sm, 0.5rem);
}

.filter-input-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs, 0.25rem);
  background-color: var(--input-bg);
  padding: var(--spacing-sm, 0.5rem) var(--spacing-sm, 0.75rem);
  border-radius: var(--input-border-radius, 6px);
  border: 1px solid var(--border-color);
}

.filter-input-group .icon {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.filter-select {
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid var(--border-color, #ced4da);
  font-size: var(--font-size-sm, 0.9rem);
  background-color: transparent;
  color: var(--text-input);
  flex-grow: 1;
  min-width: 150px;
}

/* Add styles for select options for theme awareness */
.filter-select option {
  background-color: var(--background-primary);
  color: var(--text-primary);
}

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
  margin-right: 0;
}

.action-btn.primary-btn {
  padding: var(--input-padding-y, 0.6rem) var(--input-padding-x, 1rem);
  border-radius: var(--input-border-radius, 6px);
  border: 1px solid var(--border-color);
  font-size: var(--font-size-sm, 0.9rem);
  background-color: var(--button-bg);
  color: var(--button-text);
  border-color: var(--button-bg);
}

.action-btn.primary-btn:hover:not(:disabled) {
  background-color: var(--button-hover-bg);
  border-color: var(--button-hover-bg);
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
  background-color: var(--accent-color);
  color: var(--button-text);
  border-color: var(--accent-color);
}
.action-btn.success-btn:hover:not(:disabled) {
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

.action-btn.danger-btn {
  background-color: #ef4444;
  color: white;
  border-color: #ef4444;
}
.action-btn.danger-btn:hover:not(:disabled) {
  background-color: #dc2626;
  border-color: #dc2626;
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
  color: #ef4444;
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
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  font-weight: 500;
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

.products-table-responsive {
  overflow-x: auto;
}
.products-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}
.products-table th,
.products-table td {
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
.actions-cell {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  white-space: nowrap;
}
.no-data td {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}
.no-data p {
  margin-bottom: 0.5rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--overlay-bg, rgba(0, 0, 0, 0.7));
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  padding: 1rem;
}
.modal-container {
  background-color: var(--modal-bg, var(--card-bg));
  padding: var(--spacing-lg, 1.5rem);
  border-radius: var(--modal-border-radius, var(--card-border-radius, 12px));
  box-shadow: var(--shadow-xl, 0 10px 25px rgba(0, 0, 0, 0.2));
  border: 1px solid var(--modal-border, var(--card-border));
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
  font-family: var(--font-body);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--spacing-md, 1rem);
  margin-bottom: var(--spacing-lg, 1.5rem);
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}
.modal-header h3 {
  font-size: var(--font-size-xl, 1.4rem);
  color: var(--text-primary);
  font-weight: 700;
  margin: 0;
  font-family: var(--font-heading);
}
.close-modal-btn {
  background: none;
  border: none;
  font-size: var(--icon-size-lg, 1.5rem);
  line-height: 1;
  cursor: pointer;
  color: var(--text-secondary);
  padding: var(--spacing-xs, 0.3rem);
  transition: color var(--transition-speed);
}
.close-modal-btn:hover {
  color: var(--text-primary);
}

.modal-form .form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-lg, 1.2rem);
}
.modal-form .form-group {
  margin-bottom: 0;
}
.modal-form .form-group.full-width {
  grid-column: 1 / -1;
}
.modal-form label {
  display: block;
  margin-bottom: var(--spacing-sm, 0.5rem);
  font-weight: 600;
  color: var(--text-secondary);
  font-size: var(--font-size-sm, 0.9rem);
}
.modal-form input[type='text'],
.modal-form input[type='number'],
.modal-form textarea,
.modal-form select {
  width: 100%;
  padding: var(--input-padding-y, 0.75rem) var(--input-padding-x, 1rem);
  border: 1px solid var(--border-color, #ccc);
  border-radius: var(--input-border-radius, var(--border-radius-md, 8px));
  font-size: var(--font-size-md, 0.95rem);
  background-color: var(--input-bg, var(--background-primary));
  color: var(--text-input, var(--text-primary));
  font-family: var(--font-body);
  transition:
    border-color var(--transition-speed),
    box-shadow var(--transition-speed);
}
.modal-form input[type='text']:focus,
.modal-form input[type='number']:focus,
.modal-form textarea:focus,
.modal-form select:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px var(--accent-color-opacity-20, rgba(163, 184, 153, 0.2));
}
.modal-form textarea {
  resize: vertical;
  min-height: 100px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md, 1rem);
  margin-top: var(--spacing-xl, 2rem);
  padding-top: var(--spacing-lg, 1.5rem);
  border-top: 1px solid var(--border-color, #e0e0e0);
}

.confirmation-modal .modal-body p {
  margin-bottom: var(--spacing-md, 1rem);
  font-size: var(--font-size-lg, 1.1rem);
  color: var(--text-primary);
  line-height: 1.6;
}
.confirmation-modal .product-info-delete {
  background-color: var(--background-secondary, var(--background-primary));
  padding: var(--spacing-md, 1rem);
  border-radius: var(--border-radius-md, 8px);
  margin-bottom: var(--spacing-lg, 1.5rem);
  border: 1px solid var(--border-color, #ccc);
  font-size: var(--font-size-md, 0.95rem);
  color: var(--text-secondary);
}
.confirmation-modal .warning-text {
  color: var(--warning-color-text, #d97706);
  font-weight: 600;
  display: flex;
  align-items: center;
  font-size: var(--font-size-md, 1rem);
}
.confirmation-modal .warning-text .icon {
  margin-right: var(--spacing-sm, 0.5rem);
  font-size: var(--icon-size-md, 1.2rem);
}

@media (max-width: 992px) {
  .products-table thead {
    display: none;
  }
  .products-table tr {
    display: block;
    margin-bottom: 1rem;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-md);
    box-shadow: var(--card-shadow-sm);
  }
  .products-table td {
    display: block;
    text-align: right;
    padding-left: 50%;
    position: relative;
    border-bottom: 1px solid var(--border-color);
  }
  .products-table td:last-child {
    border-bottom: none;
  }
  .products-table td::before {
    content: attr(data-label);
    position: absolute;
    left: 1rem;
    font-weight: 600;
    color: var(--text-secondary);
    text-align: left;
    white-space: nowrap;
  }
  .actions-cell {
    justify-content: flex-end;
  }
}

@media (max-width: 768px) {
  .view-header h1 {
    font-size: 1.8rem;
  }
  .controls-section .search-filter-bar {
    grid-template-columns: 1fr;
  }
  .modal-form .form-grid {
    grid-template-columns: 1fr;
  }
}

.controls-section .action-btn .icon:only-child {
  margin-right: 0;
}
</style>

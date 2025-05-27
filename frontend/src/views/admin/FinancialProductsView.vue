<template>
  <div class="admin-products-view">
    <AdminNavbar />
    <div class="view-content">
      <header class="view-header">
        <h1>전체 금융 상품 관리</h1>
        <p class="subtitle">등록된 모든 금융 상품을 확인하고 관리합니다.</p>
      </header>

      <section class="controls-section card-style">
        <div class="search-filter-bar">
          <div class="search-box">
            <input
              type="text"
              v-model="searchQuery"
              placeholder="상품명, 금융사명 등으로 검색..."
              @keyup.enter="searchProducts"
              class="search-input-field"
            />
            <i class="icon search-icon">🔍</i>
          </div>
          <div class="filter-input-group">
            <i class="icon filter-icon">📊</i>
            <select v-model="categoryFilter" @change="fetchProducts" class="filter-select">
              <option value="">전체 카테고리</option>
              <option value="deposit">예금</option>
              <option value="saving">적금</option>
              <option value="loan">대출</option>
            </select>
          </div>
          <button class="action-btn primary-btn" @click="searchProducts" :disabled="loading">
            <i class="icon"></i> 검색
          </button>
        </div>
      </section>

      <div v-if="loading" class="loading-indicator">
        <div class="spinner"></div>
        <p>상품 목록을 불러오는 중...</p>
      </div>

      <div v-if="message" :class="['alert-message', messageType === 'error' ? 'error' : 'success']">
        <i :class="['icon', messageType === 'error' ? '⚠️' : '✅']"></i>
        {{ message }}
      </div>

      <section class="table-section card-style">
        <div class="table-header-actions">
          <h3>상품 목록</h3>
          <button @click="createNewProduct" class="action-btn success-btn add-product-btn">
            <i class="icon">➕</i> 새 상품 추가
          </button>
        </div>
        <div class="products-table-responsive">
          <table class="products-table">
            <thead>
              <tr>
                <th>금융상품 코드</th>
                <th>금융회사명</th>
                <th>상품명</th>
                <th>가입방법</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in products" :key="product.id || product.fin_prdt_cd">
                <td data-label="금융상품 코드">{{ product.fin_prdt_cd }}</td>
                <td data-label="금융회사명">{{ product.kor_co_nm }}</td>
                <td data-label="상품명">{{ product.fin_prdt_nm }}</td>
                <td data-label="가입방법">
                  {{
                    Array.isArray(product.join_way) ? product.join_way.join(', ') : product.join_way
                  }}
                </td>
                <td data-label="작업" class="actions-cell">
                  <button
                    @click="editProduct(product)"
                    class="action-btn icon-btn edit-btn"
                    title="수정"
                  >
                    <i class="icon">✏️</i>
                  </button>
                  <button
                    @click="confirmDelete(product)"
                    class="action-btn icon-btn delete-btn"
                    title="삭제"
                  >
                    <i class="icon">🗑️</i>
                  </button>
                </td>
              </tr>
              <tr v-if="products.length === 0 && !loading">
                <td colspan="5" class="no-data">
                  <p>표시할 금융 상품이 없습니다.</p>
                  <p v-if="searchQuery || categoryFilter">다른 검색어나 필터를 시도해보세요.</p>
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
            <h3>{{ editMode === 'create' ? '새 금융 상품 추가' : '금융 상품 정보 수정' }}</h3>
            <button class="close-modal-btn" @click="closeModal"><i class="icon">✕</i></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveProduct" class="modal-form">
              <div class="form-grid">
                <div class="form-group">
                  <label for="fin_prdt_cd">금융상품 코드</label>
                  <input
                    type="text"
                    id="fin_prdt_cd"
                    v-model="editedProduct.fin_prdt_cd"
                    :disabled="editMode === 'edit'"
                    required
                  />
                </div>
                <div class="form-group">
                  <label for="kor_co_nm">금융회사명</label>
                  <input type="text" id="kor_co_nm" v-model="editedProduct.kor_co_nm" required />
                </div>
                <div class="form-group full-width">
                  <label for="fin_prdt_nm">금융상품명</label>
                  <input
                    type="text"
                    id="fin_prdt_nm"
                    v-model="editedProduct.fin_prdt_nm"
                    required
                  />
                </div>
                <div class="form-group full-width">
                  <label for="join_way">가입방법 (쉼표로 구분)</label>
                  <input
                    type="text"
                    id="join_way"
                    v-model="editedProduct.join_way"
                    placeholder="예: 인터넷,스마트폰,전화(텔레뱅킹)"
                    required
                  />
                </div>
                <div class="form-group">
                  <label for="product_type">상품 유형</label>
                  <select id="product_type" v-model="editedProduct.product_type">
                    <option value="deposit">예금</option>
                    <option value="saving">적금</option>
                    <option value="loan">대출</option>
                    <option value="">기타</option>
                  </select>
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
      <div v-if="showDeleteModal" class="modal-overlay" @click.self="cancelDelete">
        <div class="modal-container confirmation-modal card-style">
          <div class="modal-header">
            <h3>삭제 확인</h3>
            <button class="close-modal-btn" @click="cancelDelete"><i class="icon">✕</i></button>
          </div>
          <div class="modal-body">
            <p>정말로 이 금융 상품을 삭제하시겠습니까?</p>
            <div v-if="productToDelete" class="product-info-delete">
              <strong>상품명:</strong> {{ productToDelete.fin_prdt_nm }}<br />
              <strong>금융사:</strong> {{ productToDelete.kor_co_nm }}
            </div>
            <p class="warning-text"><i class="icon">⚠️</i> 이 작업은 되돌릴 수 없습니다!</p>
            <div class="modal-actions">
              <button class="action-btn secondary-btn" @click="cancelDelete">취소</button>
              <button class="action-btn danger-btn" @click="deleteProduct" :disabled="deleting">
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
// pjt0의 productsService 사용 (adminService 대신)
import productsService from '@/services/products'
import AdminNavbar from '@/components/admin/AdminNavbar.vue'

const products = ref([])
const loading = ref(false)
const message = ref('')
const messageType = ref('success')
const searchQuery = ref('')
const categoryFilter = ref('') // 'deposit', 'saving', 'loan', '' for all

const showEditModal = ref(false)
const editMode = ref('edit') // 'create' or 'edit'
const editedProduct = ref({
  id: null,
  fin_prdt_cd: '',
  kor_co_nm: '',
  fin_prdt_nm: '',
  join_way: '', // 문자열로 처리 (쉼표 구분)
  loan_type: '', // pjt0에는 없는 필드, Final-PJT 참고
  join_member: '', // pjt0에 없는 필드, Final-PJT 참고
  product_type: '', // 'deposit', 'saving', 'loan' - pjt0에는 없는 필드, Final-PJT 참고. 저장 시 사용
})
const savingChanges = ref(false)

const showDeleteModal = ref(false)
const productToDelete = ref(null)
const deleting = ref(false)

const showMessage = (msg, type = 'success') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

// pjt0에는 adminService가 별도로 없으므로, productsService를 사용합니다.
// Final-PJT의 adminService.getFinancialProducts(), getDepositProducts() 등은
// pjt0의 productsService.getAllFinancialProducts(), getDepositProducts() 등으로 매칭됩니다.
const fetchProducts = async () => {
  try {
    loading.value = true
    message.value = ''
    let serviceCall
    const params = { query: searchQuery.value } // 검색어는 모든 호출에 포함 가능

    switch (categoryFilter.value) {
      case 'deposit':
        serviceCall = productsService.getDepositProducts(params)
        break
      case 'saving':
        serviceCall = productsService.getSavingProducts(params)
        break
      case 'loan':
        serviceCall = productsService.getLoanProducts(params)
        break
      default:
        // searchQuery가 있으면 searchProducts를, 없으면 getAllFinancialProducts를 사용
        if (searchQuery.value) {
          serviceCall = productsService.searchProducts(searchQuery.value)
        } else {
          serviceCall = productsService.getAllFinancialProducts()
        }
    }
    const response = await serviceCall

    // response 형식에 따라 적절히 처리
    if (
      searchQuery.value &&
      !categoryFilter.value &&
      response &&
      (response.deposits || response.savings || response.loans)
    ) {
      products.value = [
        ...(response.deposits || []).map((item) => ({
          ...(item.product || item),
          id: item.id,
          product_type: 'deposit',
        })),
        ...(response.savings || []).map((item) => ({
          ...(item.product || item),
          id: item.id,
          product_type: 'saving',
        })),
        ...(response.loans || []).map((item) => ({
          ...(item.product || item),
          id: item.id,
          product_type: 'loan',
        })),
      ]
    } else if (Array.isArray(response)) {
      products.value = response
    } else if (response.results) {
      products.value = response.results.map((item) => {
        if (item.product) {
          return {
            ...item.product,
            id: item.id,
            product_type: categoryFilter.value,
          }
        }
        return item
      })
    } else {
      products.value = []
    }
  } catch (error) {
    showMessage(`상품 목록 로딩 실패: ${error.message}`, 'error')
    console.error('Error fetching products:', error)
    products.value = []
  } finally {
    loading.value = false
  }
}

const searchProducts = async () => {
  // categoryFilter 변경 시 fetchProducts가 호출되므로, 여기서는 searchQuery에 의한 호출만 처리
  await fetchProducts()
}

const createNewProduct = () => {
  editMode.value = 'create'
  editedProduct.value = {
    id: null,
    fin_prdt_cd: '',
    kor_co_nm: '',
    fin_prdt_nm: '',
    join_way: '',
    loan_type: '',
    join_member: '',
    product_type: 'deposit', // 기본값
  }
  showEditModal.value = true
}

const editProduct = (product) => {
  editMode.value = 'edit'
  // pjt0의 상품 데이터에는 product_type이 없을 수 있으므로, 간단히 추론하거나 기본값을 사용.
  // Final-PJT의 determineProductType 로직을 참고하여 단순화
  let pType = ''
  if (product.fin_prdt_cd) {
    if (product.options && product.options.length > 0 && product.options[0].save_trm)
      pType = 'deposit' // 예금/적금 공통 옵션 save_trm
    else if (product.lending_options && product.lending_options.length > 0) pType = 'loan'
    else if (product.fin_prdt_cd.includes('D'))
      pType = 'deposit' // 임시 방편
    else if (product.fin_prdt_cd.includes('S')) pType = 'saving' // 임시 방편
  }

  editedProduct.value = {
    ...product,
    join_way: Array.isArray(product.join_way) ? product.join_way.join(',') : product.join_way || '',
    // product_type이 백엔드에서 올 수도 있고, 없을 수도 있음. 없으면 위에서 추론한 값 사용.
    product_type: product.product_type || pType || 'deposit',
  }
  showEditModal.value = true
}

const closeModal = () => {
  showEditModal.value = false
}

// pjt0의 productsService에는 상품 생성/수정/삭제 기능이 없습니다.
// 이 부분은 Final-PJT의 adminService를 모방하거나, pjt0 백엔드 API에 맞춰 새로 구현해야 합니다.
// 여기서는 UI만 구현하고 실제 동작은 백엔드 API 연동이 필요함을 명시합니다.
const saveProduct = async () => {
  savingChanges.value = true
  message.value = ''
  try {
    const payload = {
      ...editedProduct.value,
      join_way: editedProduct.value.join_way
        .split(',')
        .map((s) => s.trim())
        .filter((s) => s),
    }
    console.log('Saving product (pjt0 - UI only):', payload)
    // TODO: pjt0 백엔드 API에 맞춰 상품 생성/수정 로직 구현 필요
    // 예시: if (editMode.value === 'create') { await productsService.createProduct(payload) }
    //      else { await productsService.updateProduct(payload.id, payload) }
    showMessage('상품 정보가 (UI상에서) 저장되었습니다. 백엔드 연동 필요', 'success')
    closeModal()
    await fetchProducts()
  } catch (error) {
    showMessage(`상품 저장 실패: ${error.message}`, 'error')
    console.error('Error saving product:', error)
  } finally {
    savingChanges.value = false
  }
}

const confirmDelete = (product) => {
  productToDelete.value = product
  showDeleteModal.value = true
}

const cancelDelete = () => {
  productToDelete.value = null
  showDeleteModal.value = false
}

const deleteProduct = async () => {
  if (!productToDelete.value) return
  deleting.value = true
  message.value = ''
  try {
    console.log('Deleting product (pjt0 - UI only):', productToDelete.value)
    // TODO: pjt0 백엔드 API에 맞춰 상품 삭제 로직 구현 필요
    // 예시: await productsService.deleteProduct(productToDelete.value.id, productToDelete.value.product_type)
    showMessage(
      `상품 '${productToDelete.value.fin_prdt_nm}'이(가) (UI상에서) 삭제되었습니다. 백엔드 연동 필요`,
      'success',
    )
    productToDelete.value = null
    showDeleteModal.value = false
    await fetchProducts()
  } catch (error) {
    showMessage(`상품 삭제 실패: ${error.message}`, 'error')
    console.error('Error deleting product:', error)
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
/* General View Styles - Consistent with other admin views */
.admin-products-view {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--background-primary);
}

.view-content {
  flex-grow: 1;
  padding: 2rem;
  max-width: var(--max-width-content, 1400px); /* Wider for tables */
  margin: 0 auto;
  width: 100%;
}

.view-header {
  margin-bottom: 2rem;
}

.view-header h1 {
  font-size: 2.2rem; /* Consistent with other admin views */
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

/* Controls Section */
.controls-section .search-filter-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-md, 1rem);
  padding: var(--spacing-md, 1rem);
}

.search-box {
  display: flex;
  align-items: center;
  background-color: var(--background-primary);
  border-radius: var(--input-border-radius, 8px);
  padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
  flex-grow: 1;
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
  color: var(--text-secondary, #6c757d); /* Ensuring placeholder is visible in dark mode */
}

.search-box .search-icon {
  color: var(--text-secondary);
  font-size: 1.2rem;
  margin-left: var(--spacing-sm, 0.5rem);
}

.filter-input-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs, 0.5rem);
}

.filter-input-group .icon,
.action-btn .icon {
  color: var(--text-secondary);
}

.filter-select,
.action-btn {
  padding: 0.5rem; /* AIRecommendationsView 스타일 적용 */
  border-radius: 4px; /* AIRecommendationsView 스타일 적용 */
  border: 1px solid var(--border-color, #ced4da); /* AIRecommendationsView 스타일 적용, var fallback 추가 */
  font-size: var(--font-size-sm, 0.9rem);
  background-color: var(--input-bg);
  color: var(--text-input);
}

/* Add styles for select options for theme awareness */
.filter-select option {
  background-color: var(--background-primary);
  color: var(--text-primary);
}

.action-btn.primary-btn {
  background-color: var(--button-bg);
  color: var(--button-text);
  border-color: var(--button-bg);
}

.action-btn.primary-btn:hover:not(:disabled) {
  background-color: var(--button-hover-bg);
  border-color: var(--button-hover-bg);
}

/* Action Buttons (Shared) */
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
  background-color: var(--accent-color); /* Using accent for success too */
  color: var(--button-text);
  border-color: var(--accent-color);
}
.action-btn.success-btn:hover:not(:disabled) {
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

.action-btn.danger-btn {
  background-color: #ef4444; /* Standard Red for Danger */
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

/* Loading and Alerts */
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

/* Table Section */
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
  background-color: var(--background-primary); /* Lighter header for table */
  font-weight: 600;
  color: var(--text-secondary);
  white-space: nowrap;
}
.products-table tbody tr:hover {
  background-color: rgba(var(--accent-color-rgb, 163, 184, 153), 0.05); /* Subtle hover */
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

/* Modal Styles - 전역 변수 적용 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--overlay-bg, rgba(0, 0, 0, 0.7)); /* 오버레이 배경색 강화 */
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  padding: 1rem;
}
.modal-container {
  background-color: var(--modal-bg, var(--card-bg)); /* 모달 배경 */
  padding: var(--spacing-lg, 1.5rem); /* 내부 패딩 */
  border-radius: var(--modal-border-radius, var(--card-border-radius, 12px)); /* 모달 테두리 반경 */
  box-shadow: var(--shadow-xl, 0 10px 25px rgba(0, 0, 0, 0.2)); /* 모달 그림자 강화 */
  border: 1px solid var(--modal-border, var(--card-border)); /* 모달 테두리 */
  width: 100%;
  max-width: 600px; /* Default modal width */
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
  font-weight: 700; /* 제목 굵게 */
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
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
  font-weight: 600; /* 라벨 굵게 */
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
  gap: var(--spacing-md, 1rem); /* 버튼 간 간격 증가 */
  margin-top: var(--spacing-xl, 2rem);
  padding-top: var(--spacing-lg, 1.5rem);
  border-top: 1px solid var(--border-color, #e0e0e0);
}
/* .action-btn 스타일은 전역 또는 상위에서 이미 정의된 것을 사용 기대 */
/* 필요시 여기서 .modal-actions .action-btn 으로 특정 스타일 추가 */

/* Confirmation Modal Specifics - 전역 변수 적용 */
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
  color: var(--warning-color-text, #d97706); /* 주황색 계열 경고색 */
  font-weight: 600;
  display: flex;
  align-items: center;
  font-size: var(--font-size-md, 1rem);
}
.confirmation-modal .warning-text .icon {
  margin-right: var(--spacing-sm, 0.5rem);
  font-size: var(--icon-size-md, 1.2rem);
}

/* Responsive Table */
@media (max-width: 992px) {
  /* Adjusted breakpoint */
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
    grid-template-columns: 1fr; /* Stack filters on smaller screens */
  }
  .modal-form .form-grid {
    grid-template-columns: 1fr; /* Stack form elements in modal */
  }
}

/* Fix for search button icon */
.controls-section .action-btn .icon:not(:last-child) {
  /* if icon is not the only child */
  margin-right: 0.5rem;
}
.controls-section .action-btn .icon:empty {
  /* if icon has no content, like from a class */
  /* You might need to target specific icon classes if they are empty by default */
  /* For now, assuming it might be an empty <i> or <span> */
  display: inline-block; /* or 'none' if it should be hidden if empty */
  width: 1em; /* placeholder for an icon */
  height: 1em;
  /* background-image: url('path/to/default-search-icon.svg'); */
  /* background-repeat: no-repeat; */
  /* background-position: center; */
  /* margin-right: 0.5rem; */
}
.controls-section .action-btn i.icon:before {
  /* If using font-icon and it's not rendering */
  content: '🔎'; /* Fallback or ensure font is loaded */
  font-family: initial; /* Reset font if it's a special icon font */
}
</style>

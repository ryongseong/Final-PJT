<template>
  <div class="admin-deposits">
    <AdminNavbar />

    <div class="deposits-content">
      <h1>Deposit Products Management</h1>

      <div class="search-controls">
        <div class="search-box">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Search deposit products..."
            @keyup.enter="searchProducts"
          />
          <select v-model="termFilter" @change="filterProducts">
            <option value="">All Terms</option>
            <option v-for="term in availableTerms" :key="term" :value="term">
              {{ term }} months
            </option>
          </select>
          <select v-model="rateTypeFilter" @change="filterProducts">
            <option value="">All Rate Types</option>
            <option value="S">단리 (Simple Interest)</option>
            <option value="M">복리 (Compound Interest)</option>
          </select>
          <button class="btn btn-primary" @click="searchProducts" :disabled="loading">
            Search
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading-spinner">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <div
        v-if="message"
        :class="['alert', messageType === 'error' ? 'alert-danger' : 'alert-success']"
      >
        {{ message }}
      </div>

      <div class="products-table">
        <table>
          <thead>
            <tr>
              <th>금융상품 코드</th>
              <th>금융회사명</th>
              <th>상품명</th>
              <th>금리유형</th>
              <th>저축 기간(개월)</th>
              <th>금리(%)</th>
              <th>최고 금리(%)</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="deposit in deposits" :key="deposit.product">
              <td>{{ deposit.product }}</td>
              <td>{{ getCompanyName(deposit) }}</td>
              <td>{{ getProductName(deposit) }}</td>
              <td>{{ deposit.intr_rate_type }}</td>
              <td>{{ deposit.save_trm }}</td>
              <td>{{ deposit.intr_rate.toFixed(2) }}</td>
              <td>{{ deposit.intr_rate2.toFixed(2) }}</td>
              <td class="actions">
                <button @click="editProduct(deposit)" class="btn btn-sm btn-info">Edit</button>
                <button @click="confirmDelete(deposit)" class="btn btn-sm btn-danger">
                  Delete
                </button>
              </td>
            </tr>
            <tr v-if="deposits.length === 0 && !loading">
              <td colspan="8" class="no-data">No deposit products found</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Edit Modal -->
      <div v-if="showEditModal" class="modal-backdrop">
        <div class="modal-content">
          <div class="modal-header">
            <h2>
              {{ editMode === 'create' ? 'Create New Deposit Product' : 'Edit Deposit Product' }}
            </h2>
            <button class="close-btn" @click="closeModal">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveProduct">
              <div class="form-group" v-if="editMode === 'create'">
                <label for="product">금융상품 코드</label>
                <select id="product" v-model="editedProduct.product" required>
                  <option value="">-- Select Financial Product --</option>
                  <option
                    v-for="product in availableProducts"
                    :key="product.fin_prdt_cd"
                    :value="product.fin_prdt_cd"
                  >
                    {{ product.fin_prdt_nm }} ({{ product.kor_co_nm }})
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label for="fin_co_no">금융회사 코드</label>
                <input type="text" id="fin_co_no" v-model="editedProduct.fin_co_no" required />
              </div>
              <div class="form-group">
                <label for="dcls_month">공시 월</label>
                <input
                  type="text"
                  id="dcls_month"
                  v-model="editedProduct.dcls_month"
                  required
                  placeholder="YYYYMM"
                />
              </div>
              <div class="form-group">
                <label for="intr_rate_type">금리유형</label>
                <select id="intr_rate_type" v-model="editedProduct.intr_rate_type" required>
                  <option value="S">단리 (Simple Interest)</option>
                  <option value="M">복리 (Compound Interest)</option>
                </select>
              </div>
              <div class="form-group">
                <label for="save_trm">저축 기간 (개월)</label>
                <input
                  type="number"
                  id="save_trm"
                  v-model.number="editedProduct.save_trm"
                  min="1"
                  required
                />
              </div>
              <div class="form-group">
                <label for="intr_rate">기본 금리 (%)</label>
                <input
                  type="number"
                  id="intr_rate"
                  v-model.number="editedProduct.intr_rate"
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
                  v-model.number="editedProduct.intr_rate2"
                  step="0.01"
                  min="0"
                  required
                />
              </div>
              <div class="form-group">
                <label for="category">카테고리</label>
                <input
                  type="text"
                  id="category"
                  v-model="editedProduct.category"
                  value="예금"
                  readonly
                />
              </div>

              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="savingChanges">
                  {{ savingChanges ? 'Saving...' : 'Save Changes' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <div v-if="showDeleteModal" class="modal-backdrop">
        <div class="modal-content delete-modal">
          <div class="modal-header">
            <h2>Confirm Delete</h2>
            <button class="close-btn" @click="cancelDelete">×</button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete this deposit product?</p>
            <p>
              <strong>{{ getProductName(productToDelete) }}</strong>
            </p>
            <p class="warning">This action cannot be undone!</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="cancelDelete">Cancel</button>
            <button class="btn btn-danger" @click="deleteProduct" :disabled="deleting">
              {{ deleting ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Create Product Button -->
      <div class="create-product">
        <button @click="createNewProduct" class="btn btn-success">
          Create New Deposit Product
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import adminService from '@/services/admin'
import productsService from '@/services/products'
import AdminNavbar from '@/components/admin/AdminNavbar.vue'

export default {
  name: 'AdminDepositProducts',
  components: { AdminNavbar },
  data() {
    return {
      deposits: [],
      allDeposits: [], // For filtering
      loading: false,
      message: '',
      messageType: 'success',
      searchQuery: '',
      termFilter: '',
      rateTypeFilter: '',
      availableTerms: [],
      availableProducts: [], // For creating new deposit products

      // Edit modal
      showEditModal: false,
      editMode: 'edit', // 'edit' or 'create'
      editedProduct: {
        product: '',
        fin_co_no: '',
        dcls_month: '',
        intr_rate_type: '단리',
        save_trm: 12,
        intr_rate: 0,
        intr_rate2: 0,
        category: '예금',
      },
      savingChanges: false,

      // Delete modal
      showDeleteModal: false,
      productToDelete: null,
      deleting: false,

      // Product mapping cache for names
      productNameCache: {},
      companyNameCache: {},
    }
  },
  created() {
    this.fetchDepositProducts()
    this.fetchAvailableProducts()
  },
  methods: {
    async fetchDepositProducts() {
      try {
        this.loading = true
        this.message = ''

        const deposits = await adminService.getDepositProducts()
        this.deposits = deposits
        this.allDeposits = [...deposits]

        // Extract available terms
        const terms = new Set(deposits.map((d) => d.save_trm))
        this.availableTerms = [...terms].sort((a, b) => a - b)
      } catch (error) {
        this.showMessage('Failed to load deposit products: ' + error.message, 'error')
        console.error('Error fetching deposit products:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchAvailableProducts() {
      try {
        // Get all financial products that don't have deposit products yet
        const allProducts = await productsService.getAllFinancialProducts()
        const depositProducts = await productsService.getDepositProducts()

        // Filter out products that already have deposit products
        const depositProductIds = new Set(depositProducts.map((d) => d.product))
        this.availableProducts = allProducts.filter((p) => !depositProductIds.has(p.fin_prdt_cd))

        // Also build name cache for display
        allProducts.forEach((p) => {
          this.productNameCache[p.fin_prdt_cd] = p.fin_prdt_nm
          this.companyNameCache[p.fin_prdt_cd] = p.kor_co_nm
        })
      } catch (error) {
        console.error('Error fetching available products:', error)
      }
    },

    searchProducts() {
      if (!this.searchQuery.trim()) {
        this.deposits = [...this.allDeposits]
        this.applyFilters()
        return
      }

      const query = this.searchQuery.toLowerCase()
      this.deposits = this.allDeposits.filter((deposit) => {
        const productName = this.getProductName(deposit)?.toLowerCase() || ''
        const companyName = this.getCompanyName(deposit)?.toLowerCase() || ''

        return (
          productName.includes(query) ||
          companyName.includes(query) ||
          deposit.product.toLowerCase().includes(query)
        )
      })

      this.applyFilters()
    },

    filterProducts() {
      this.deposits = [...this.allDeposits]
      this.applyFilters()
    },

    applyFilters() {
      if (this.termFilter) {
        this.deposits = this.deposits.filter((d) => d.save_trm === parseInt(this.termFilter))
      }

      if (this.rateTypeFilter) {
        this.deposits = this.deposits.filter((d) => d.intr_rate_type === this.rateTypeFilter)
      }
    },

    getProductName(deposit) {
      if (!deposit) return ''
      return this.productNameCache[deposit.product] || deposit.product
    },

    getCompanyName(deposit) {
      if (!deposit) return ''
      return this.companyNameCache[deposit.product] || ''
    },

    createNewProduct() {
      this.editMode = 'create'
      const currentDate = new Date()
      const year = currentDate.getFullYear()
      const month = (currentDate.getMonth() + 1).toString().padStart(2, '0')

      this.editedProduct = {
        product: '',
        fin_co_no: '',
        dcls_month: `${year}${month}`,
        intr_rate_type: '단리',
        save_trm: 12,
        intr_rate: 0,
        intr_rate2: 0,
        category: '예금',
      }
      this.showEditModal = true
    },

    editProduct(deposit) {
      this.editMode = 'edit'
      this.editedProduct = { ...deposit }
      this.showEditModal = true
    },

    closeModal() {
      this.showEditModal = false
    },

    async saveProduct() {
      try {
        this.savingChanges = true

        if (this.editMode === 'create') {
          await adminService.createDepositProduct(this.editedProduct)
          this.showMessage('Deposit product created successfully!')
        } else {
          await adminService.updateDepositProduct(this.editedProduct.product, this.editedProduct)
          this.showMessage('Deposit product updated successfully!')
        }

        await this.fetchDepositProducts()
        await this.fetchAvailableProducts()
        this.closeModal()
      } catch (error) {
        this.showMessage('Failed to save deposit product: ' + error.message, 'error')
        console.error('Error saving deposit product:', error)
      } finally {
        this.savingChanges = false
      }
    },

    confirmDelete(deposit) {
      this.productToDelete = deposit
      this.showDeleteModal = true
    },

    cancelDelete() {
      this.showDeleteModal = false
      this.productToDelete = null
    },

    async deleteProduct() {
      try {
        this.deleting = true

        await adminService.deleteDepositProduct(this.productToDelete.product)
        this.showMessage('Deposit product deleted successfully!')

        await this.fetchDepositProducts()
        await this.fetchAvailableProducts()
        this.cancelDelete()
      } catch (error) {
        this.showMessage('Failed to delete deposit product: ' + error.message, 'error')
        console.error('Error deleting deposit product:', error)
      } finally {
        this.deleting = false
      }
    },

    showMessage(msg, type = 'success') {
      this.message = msg
      this.messageType = type

      // Clear message after 5 seconds
      setTimeout(() => {
        this.message = ''
      }, 5000)
    },
  },
}
</script>

<style scoped>
.admin-deposits {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 1.5rem;
  color: #333;
}

.search-controls {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.search-box {
  display: flex;
  gap: 0.5rem;
  width: 100%;
}

.search-box input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.search-box select {
  width: 150px;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.products-table {
  margin-top: 1.5rem;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 0.75rem 1rem;
  text-align: left;
  justify-content: center;
  align-items: center;
}

th {
  background-color: #f5f5f5;
  font-weight: 600;
}

td {
  height: 100px;
  border-bottom: 1px solid #eaeaea;
}

td.actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-info {
  background-color: #17a2b8;
  color: white;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn:hover {
  opacity: 0.9;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  margin: 2rem 0;
}

.alert {
  padding: 0.75rem 1rem;
  margin: 1rem 0;
  border-radius: 4px;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
}

.no-data {
  text-align: center;
  padding: 2rem 0;
  color: #666;
}

.create-product {
  margin-top: 2rem;
  display: flex;
  justify-content: flex-end;
}

/* Modal styles */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.delete-modal {
  width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #eaeaea;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  border-top: 1px solid #eaeaea;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.warning {
  color: #dc3545;
  font-weight: 500;
}

@media (max-width: 768px) {
  .search-box {
    flex-direction: column;
  }

  td.actions {
    flex-direction: column;
  }
}
</style>

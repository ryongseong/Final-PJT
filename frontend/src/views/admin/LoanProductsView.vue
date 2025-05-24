<template>
  <div class="admin-loans">
    <AdminNavbar />
    <h1>Loan Products Management</h1>

    <div class="search-controls">
      <div class="search-box">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search loan products..."
          @keyup.enter="searchProducts"
        />
        <select v-model="loanTypeFilter" @change="filterProducts">
          <option value="">All Loan Types</option>
          <option v-for="type in availableLoanTypes" :key="type" :value="type">{{ type }}</option>
        </select>
        <button class="btn btn-primary" @click="searchProducts" :disabled="loading">Search</button>
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
            <th>대출종류</th>
            <th>대출 부대비용</th>
            <th>중도상환 수수료</th>
            <th>연체 이자율</th>
            <th>대출 한도</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="loan in loans" :key="loan.product">
            <td>{{ loan.product }}</td>
            <td>{{ getCompanyName(loan) }}</td>
            <td>{{ getProductName(loan) }}</td>
            <td>{{ getLoanType(loan) }}</td>
            <td>{{ loan.loan_inci_expn || '-' }}</td>
            <td>{{ loan.erly_rpay_fee || '-' }}</td>
            <td>{{ loan.dly_rate || '-' }}</td>
            <td>{{ loan.loan_lmt || '-' }}</td>
            <td class="actions">
              <button @click="editProduct(loan)" class="btn btn-sm btn-info">Edit</button>
              <button @click="confirmDelete(loan)" class="btn btn-sm btn-danger">Delete</button>
              <button @click="viewOptions(loan)" class="btn btn-sm btn-secondary">Options</button>
            </td>
          </tr>
          <tr v-if="loans.length === 0 && !loading">
            <td colspan="9" class="no-data">No loan products found</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="modal-backdrop">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ editMode === 'create' ? 'Create New Loan Product' : 'Edit Loan Product' }}</h2>
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
              <label for="loan_inci_expn">대출 부대비용</label>
              <textarea
                id="loan_inci_expn"
                v-model="editedProduct.loan_inci_expn"
                rows="2"
              ></textarea>
            </div>
            <div class="form-group">
              <label for="erly_rpay_fee">중도상환 수수료</label>
              <textarea
                id="erly_rpay_fee"
                v-model="editedProduct.erly_rpay_fee"
                rows="2"
              ></textarea>
            </div>
            <div class="form-group">
              <label for="dly_rate">연체 이자율</label>
              <textarea id="dly_rate" v-model="editedProduct.dly_rate" rows="2"></textarea>
            </div>
            <div class="form-group">
              <label for="loan_lmt">대출 한도</label>
              <textarea id="loan_lmt" v-model="editedProduct.loan_lmt" rows="2"></textarea>
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
          <p>Are you sure you want to delete this loan product?</p>
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

    <!-- Options Modal -->
    <div v-if="showOptionsModal" class="modal-backdrop">
      <div class="modal-content options-modal">
        <div class="modal-header">
          <h2>Loan Options</h2>
          <button class="close-btn" @click="closeOptionsModal">×</button>
        </div>
        <div class="modal-body">
          <div v-if="loadingOptions" class="loading-spinner">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>

          <div v-else>
            <h3>{{ getProductName(currentProduct) }}</h3>

            <div class="tabs">
              <button
                :class="['tab-btn', activeTab === 'mortgage' ? 'active' : '']"
                @click="activeTab = 'mortgage'"
              >
                Mortgage Options
              </button>
              <button
                :class="['tab-btn', activeTab === 'credit' ? 'active' : '']"
                @click="activeTab = 'credit'"
              >
                Credit Options
              </button>
            </div>

            <div v-if="activeTab === 'mortgage'">
              <h4>Mortgage Loan Options</h4>
              <div v-if="mortgageOptions.length === 0" class="no-data">
                No mortgage options available
              </div>
              <table v-else>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>담보 유형</th>
                    <th>상환 유형</th>
                    <th>금리 유형</th>
                    <th>최저 금리(%)</th>
                    <th>최고 금리(%)</th>
                    <th>평균 금리(%)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="option in mortgageOptions" :key="option.id">
                    <td>{{ option.id }}</td>
                    <td>{{ option.mrtg_type }}</td>
                    <td>{{ option.rpay_type }}</td>
                    <td>{{ option.lend_rate_type }}</td>
                    <td>{{ option.lend_rate_min.toFixed(2) }}</td>
                    <td>{{ option.lend_rate_max.toFixed(2) }}</td>
                    <td>{{ option.lend_rate_avg ? option.lend_rate_avg.toFixed(2) : '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div v-if="activeTab === 'credit'">
              <h4>Credit Loan Options</h4>
              <div v-if="creditOptions.length === 0" class="no-data">
                No credit options available
              </div>
              <table v-else>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>신용상품 유형</th>
                    <th>금리 유형</th>
                    <th>최저 금리(%)</th>
                    <th>최고 금리(%)</th>
                    <th>평균 금리(%)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="option in creditOptions" :key="option.id">
                    <td>{{ option.id }}</td>
                    <td>{{ option.crdt_prdt_type }}</td>
                    <td>{{ option.crdt_lend_rate_type }}</td>
                    <td>{{ option.crdt_grad_1 }}</td>
                    <td>{{ option.crdt_grad_4 }}</td>
                    <td>{{ option.crdt_grad_avg ? option.crdt_grad_avg.toFixed(2) : '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Product Button -->
    <div class="create-product">
      <button @click="createNewProduct" class="btn btn-success">Create New Loan Product</button>
    </div>
  </div>
</template>

<script>
import adminService from '@/services/admin'
import productsService from '@/services/products'
import AdminNavbar from '@/components/admin/AdminNavbar.vue'

export default {
  name: 'AdminLoanProducts',
  components: { AdminNavbar },
  data() {
    return {
      loans: [],
      allLoans: [], // For filtering
      loading: false,
      message: '',
      messageType: 'success',
      searchQuery: '',
      loanTypeFilter: '',
      availableLoanTypes: [],
      availableProducts: [], // For creating new loan products

      // Edit modal
      showEditModal: false,
      editMode: 'edit', // 'edit' or 'create'
      editedProduct: {
        product: '',
        fin_co_no: '',
        dcls_month: '',
        loan_inci_expn: '',
        erly_rpay_fee: '',
        dly_rate: '',
        loan_lmt: '',
      },
      savingChanges: false,

      // Delete modal
      showDeleteModal: false,
      productToDelete: null,
      deleting: false,

      // Options modal
      showOptionsModal: false,
      currentProduct: null,
      loadingOptions: false,
      mortgageOptions: [],
      creditOptions: [],
      activeTab: 'mortgage',

      // Product mapping cache for names
      productNameCache: {},
      companyNameCache: {},
      loanTypeCache: {},
    }
  },
  created() {
    this.fetchLoanProducts()
    this.fetchAvailableProducts()
  },
  methods: {
    async fetchLoanProducts() {
      try {
        this.loading = true
        this.message = ''

        const loans = await adminService.getLoanProducts()
        this.loans = loans
        this.allLoans = [...loans]

        // Extract available loan types
        this.extractLoanTypes()
      } catch (error) {
        this.showMessage('Failed to load loan products: ' + error.message, 'error')
        console.error('Error fetching loan products:', error)
      } finally {
        this.loading = false
      }
    },

    extractLoanTypes() {
      // Get all financial products to extract loan types
      const loanTypes = new Set()

      for (const loan of this.loans) {
        const productId = loan.product
        const loanType = this.loanTypeCache[productId]
        if (loanType) {
          loanTypes.add(loanType)
        }
      }

      this.availableLoanTypes = [...loanTypes].sort()
    },

    async fetchAvailableProducts() {
      try {
        // Get all financial products that don't have loan products yet
        const allProducts = await productsService.getAllFinancialProducts()
        const loanProducts = await productsService.getLoanProducts()

        // Filter out products that already have loan products
        const loanProductIds = new Set(loanProducts.map((d) => d.product))
        this.availableProducts = allProducts.filter((p) => !loanProductIds.has(p.fin_prdt_cd))

        // Also build name cache for display
        allProducts.forEach((p) => {
          this.productNameCache[p.fin_prdt_cd] = p.fin_prdt_nm
          this.companyNameCache[p.fin_prdt_cd] = p.kor_co_nm
          this.loanTypeCache[p.fin_prdt_cd] = p.loan_type
        })

        // Update available loan types
        this.extractLoanTypes()
      } catch (error) {
        console.error('Error fetching available products:', error)
      }
    },

    searchProducts() {
      if (!this.searchQuery.trim()) {
        this.loans = [...this.allLoans]
        this.applyFilters()
        return
      }

      const query = this.searchQuery.toLowerCase()
      this.loans = this.allLoans.filter((loan) => {
        const productName = this.getProductName(loan)?.toLowerCase() || ''
        const companyName = this.getCompanyName(loan)?.toLowerCase() || ''
        const loanType = this.getLoanType(loan)?.toLowerCase() || ''

        return (
          productName.includes(query) ||
          companyName.includes(query) ||
          loanType.includes(query) ||
          loan.product.toLowerCase().includes(query)
        )
      })

      this.applyFilters()
    },

    filterProducts() {
      this.loans = [...this.allLoans]
      this.applyFilters()
    },

    applyFilters() {
      if (this.loanTypeFilter) {
        this.loans = this.loans.filter((loan) => {
          const loanType = this.getLoanType(loan)
          return loanType === this.loanTypeFilter
        })
      }
    },

    getProductName(loan) {
      if (!loan) return ''
      return this.productNameCache[loan.product] || loan.product
    },

    getCompanyName(loan) {
      if (!loan) return ''
      return this.companyNameCache[loan.product] || ''
    },

    getLoanType(loan) {
      if (!loan) return ''
      return this.loanTypeCache[loan.product] || ''
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
        loan_inci_expn: '',
        erly_rpay_fee: '',
        dly_rate: '',
        loan_lmt: '',
      }
      this.showEditModal = true
    },

    editProduct(loan) {
      this.editMode = 'edit'
      this.editedProduct = { ...loan }
      this.showEditModal = true
    },

    closeModal() {
      this.showEditModal = false
    },

    async saveProduct() {
      try {
        this.savingChanges = true

        if (this.editMode === 'create') {
          await adminService.createLoanProduct(this.editedProduct)
          this.showMessage('Loan product created successfully!')
        } else {
          await adminService.updateLoanProduct(this.editedProduct.product, this.editedProduct)
          this.showMessage('Loan product updated successfully!')
        }

        await this.fetchLoanProducts()
        await this.fetchAvailableProducts()
        this.closeModal()
      } catch (error) {
        this.showMessage('Failed to save loan product: ' + error.message, 'error')
        console.error('Error saving loan product:', error)
      } finally {
        this.savingChanges = false
      }
    },

    confirmDelete(loan) {
      this.productToDelete = loan
      this.showDeleteModal = true
    },

    cancelDelete() {
      this.showDeleteModal = false
      this.productToDelete = null
    },

    async deleteProduct() {
      try {
        this.deleting = true

        await adminService.deleteLoanProduct(this.productToDelete.product)
        this.showMessage('Loan product deleted successfully!')

        await this.fetchLoanProducts()
        await this.fetchAvailableProducts()
        this.cancelDelete()
      } catch (error) {
        this.showMessage('Failed to delete loan product: ' + error.message, 'error')
        console.error('Error deleting loan product:', error)
      } finally {
        this.deleting = false
      }
    },

    async viewOptions(loan) {
      this.currentProduct = loan
      this.showOptionsModal = true
      this.loadingOptions = true

      try {
        // Here we would fetch the mortgage and credit options for this loan
        // This is a mock implementation since we don't have the actual endpoint
        // In a real implementation, you would call API endpoints to get these options

        // Mock fetching mortgage options
        setTimeout(() => {
          this.mortgageOptions = [
            {
              id: 1,
              mrtg_type: '주택담보',
              rpay_type: '원금균등분할상환',
              lend_rate_type: '변동금리',
              lend_rate_min: 3.5,
              lend_rate_max: 5.2,
              lend_rate_avg: 4.3,
            },
            {
              id: 2,
              mrtg_type: '주택담보',
              rpay_type: '원리금균등분할상환',
              lend_rate_type: '고정금리',
              lend_rate_min: 3.8,
              lend_rate_max: 5.5,
              lend_rate_avg: 4.6,
            },
          ]

          // Mock fetching credit options
          this.creditOptions = [
            {
              id: 1,
              crdt_prdt_type: '일반신용대출',
              crdt_lend_rate_type: '변동금리',
              crdt_grad_1: 4.5,
              crdt_grad_4: 8.9,
              crdt_grad_avg: 6.7,
            },
          ]

          this.loadingOptions = false
        }, 500)
      } catch (error) {
        console.error('Error fetching loan options:', error)
        this.loadingOptions = false
      }
    },

    closeOptionsModal() {
      this.showOptionsModal = false
      this.currentProduct = null
      this.mortgageOptions = []
      this.creditOptions = []
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
.admin-loans {
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
  border-bottom: 1px solid #eaeaea;
}

th {
  background-color: #f5f5f5;
  font-weight: 600;
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

.options-modal {
  width: 800px;
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

/* Tabs */
.tabs {
  display: flex;
  margin-bottom: 1rem;
  border-bottom: 1px solid #ddd;
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  border-bottom: 3px solid transparent;
}

.tab-btn.active {
  border-bottom-color: #007bff;
  color: #007bff;
}

h3,
h4 {
  margin-top: 0;
  margin-bottom: 1rem;
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

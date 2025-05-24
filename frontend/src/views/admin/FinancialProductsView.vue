<template>
  <div class="admin-products">
    <AdminNavbar />

    <div class="products-content">
      <h1>Financial Products Management</h1>

      <div class="search-controls">
        <div class="search-box">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Search products..."
            @keyup.enter="searchProducts"
          />
          <select v-model="categoryFilter" @change="searchProducts">
            <option value="">All Categories</option>
            <option value="deposit">Deposit</option>
            <option value="saving">Saving</option>
            <option value="loan">Loan</option>
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
              <th>가입방법</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in products" :key="product.fin_prdt_cd">
              <td>{{ product.fin_prdt_cd }}</td>
              <td>{{ product.kor_co_nm }}</td>
              <td>{{ product.fin_prdt_nm }}</td>
              <td>{{ product.join_way.join(', ') }}</td>
              <td class="actions">
                <button @click="editProduct(product)" class="btn btn-sm btn-info">Edit</button>
                <button @click="confirmDelete(product)" class="btn btn-sm btn-danger">
                  Delete
                </button>
              </td>
            </tr>
            <tr v-if="products.length === 0 && !loading">
              <td colspan="6" class="no-data">No financial products found</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Edit Modal -->
      <div v-if="showEditModal" class="modal-backdrop">
        <div class="modal-content">
          <div class="modal-header">
            <h2>{{ editMode === 'create' ? 'Create New Product' : 'Edit Product' }}</h2>
            <button class="close-btn" @click="closeModal">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveProduct">
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
              <div class="form-group">
                <label for="fin_prdt_nm">금융상품명</label>
                <input type="text" id="fin_prdt_nm" v-model="editedProduct.fin_prdt_nm" required />
              </div>
              <div class="form-group">
                <label for="join_way">가입방법</label>
                <input type="text" id="join_way" v-model="editedProduct.join_way" required />
              </div>
              <div class="form-group">
                <label for="loan_type">대출종류</label>
                <input type="text" id="loan_type" v-model="editedProduct.loan_type" />
              </div>
              <div class="form-group">
                <label for="join_member">가입대상</label>
                <textarea id="join_member" v-model="editedProduct.join_member" rows="3"></textarea>
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
            <p>Are you sure you want to delete this product?</p>
            <p>
              <strong>{{ productToDelete?.fin_prdt_nm }}</strong> from
              <strong>{{ productToDelete?.kor_co_nm }}</strong>
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
        <button @click="createNewProduct" class="btn btn-success">Create New Product</button>
      </div>
    </div>
  </div>
</template>

<script>
import adminService from '@/services/admin'
import AdminNavbar from '@/components/admin/AdminNavbar.vue'

export default {
  name: 'AdminFinancialProducts',
  components: { AdminNavbar },
  data() {
    return {
      products: [],
      loading: false,
      message: '',
      messageType: 'success',
      searchQuery: '',
      categoryFilter: '',

      // Edit modal
      showEditModal: false,
      editMode: 'edit', // 'edit' or 'create'
      editedProduct: {
        fin_prdt_cd: '',
        kor_co_nm: '',
        fin_prdt_nm: '',
        join_way: '',
        loan_type: '',
        join_member: '',
      },
      savingChanges: false,

      // Delete modal
      showDeleteModal: false,
      productToDelete: null,
      deleting: false,
    }
  },
  created() {
    this.fetchProducts()
  },
  methods: {
    async fetchProducts() {
      try {
        this.loading = true
        this.message = ''

        this.products = await adminService.getFinancialProducts()
      } catch (error) {
        this.showMessage('Failed to load products: ' + error.message, 'error')
        console.error('Error fetching products:', error)
      } finally {
        this.loading = false
      }
    },

    async searchProducts() {
      try {
        this.loading = true
        this.message = ''

        // If search query is empty and no category filter, fetch all
        if (!this.searchQuery && !this.categoryFilter) {
          await this.fetchProducts()
          return
        }

        this.products = await adminService.searchFinancialProducts(
          this.searchQuery,
          this.categoryFilter,
        )
      } catch (error) {
        this.showMessage('Search failed: ' + error.message, 'error')
        console.error('Error searching products:', error)
      } finally {
        this.loading = false
      }
    },

    createNewProduct() {
      this.editMode = 'create'
      this.editedProduct = {
        fin_prdt_cd: '',
        kor_co_nm: '',
        fin_prdt_nm: '',
        join_way: '',
        loan_type: '',
        join_member: '',
      }
      this.showEditModal = true
    },

    editProduct(product) {
      this.editMode = 'edit'
      this.editedProduct = { ...product }
      this.showEditModal = true
    },

    closeModal() {
      this.showEditModal = false
    },

    async saveProduct() {
      try {
        this.savingChanges = true

        if (this.editMode === 'create') {
          await adminService.createFinancialProduct(this.editedProduct)
          this.showMessage('Product created successfully!')
        } else {
          await adminService.updateFinancialProduct(
            this.editedProduct.fin_prdt_cd,
            this.editedProduct,
          )
          this.showMessage('Product updated successfully!')
        }

        await this.fetchProducts()
        this.closeModal()
      } catch (error) {
        this.showMessage('Failed to save product: ' + error.message, 'error')
        console.error('Error saving product:', error)
      } finally {
        this.savingChanges = false
      }
    },

    confirmDelete(product) {
      this.productToDelete = product
      this.showDeleteModal = true
    },

    cancelDelete() {
      this.showDeleteModal = false
      this.productToDelete = null
    },

    async deleteProduct() {
      try {
        this.deleting = true

        await adminService.deleteFinancialProduct(this.productToDelete.fin_prdt_cd)
        this.showMessage('Product deleted successfully!')

        await this.fetchProducts()
        this.cancelDelete()
      } catch (error) {
        this.showMessage('Failed to delete product: ' + error.message, 'error')
        console.error('Error deleting product:', error)
      } finally {
        this.deleting = false
      }
    },

    getProductType(product) {
      if (product.deposit_product) return 'Deposit'
      if (product.saving_product) return 'Saving'
      if (product.loan_product) return 'Loan'
      return 'Unknown'
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
.admin-products {
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

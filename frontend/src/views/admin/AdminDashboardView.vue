<template>
  <div class="admin-dashboard">
    <AdminNavbar />

    <div class="dashboard-content">
      <h1>Admin Dashboard</h1>
      <p>Welcome to the Financial Products Management Dashboard</p>

      <div class="admin-actions">
        <h2>Quick Actions</h2>
        <div class="action-buttons">
          <button @click="updateAllProducts" :disabled="loading" class="btn btn-primary">
            Update All Products from API
          </button>
          <button @click="updateDepositProducts" :disabled="loading" class="btn btn-success">
            Update Deposit Products
          </button>
          <button @click="updateSavingProducts" :disabled="loading" class="btn btn-success">
            Update Saving Products
          </button>
          <button @click="updateLoanProducts" :disabled="loading" class="btn btn-success">
            Update Loan Products
          </button>
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
      </div>

      <div class="stats-overview">
        <h2>Database Overview</h2>
        <div class="stats-cards">
          <div class="stat-card">
            <h3>Financial Products</h3>
            <p class="stat-number">{{ stats.financialProducts }}</p>
          </div>
          <div class="stat-card">
            <h3>Deposit Products</h3>
            <p class="stat-number">{{ stats.depositProducts }}</p>
          </div>
          <div class="stat-card">
            <h3>Saving Products</h3>
            <p class="stat-number">{{ stats.savingProducts }}</p>
          </div>
          <div class="stat-card">
            <h3>Loan Products</h3>
            <p class="stat-number">{{ stats.loanProducts }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import adminService from '@/services/admin'
import productsService from '@/services/products'
import AdminNavbar from '@/components/admin/AdminNavbar.vue'

export default {
  name: 'AdminDashboard',
  components: { AdminNavbar },
  data() {
    return {
      loading: false,
      message: '',
      messageType: 'success',
      stats: {
        financialProducts: 0,
        depositProducts: 0,
        savingProducts: 0,
        loanProducts: 0,
      },
    }
  },
  mounted() {
    this.fetchStats()
  },
  methods: {
    async fetchStats() {
      try {
        this.loading = true

        const financialProducts = await productsService.getAllFinancialProducts()
        const depositProducts = await productsService.getDepositProducts()
        const savingProducts = await productsService.getSavingProducts()
        const loanProducts = await productsService.getLoanProducts()

        this.stats.financialProducts = financialProducts.length
        this.stats.depositProducts = depositProducts.length
        this.stats.savingProducts = savingProducts.length
        this.stats.loanProducts = loanProducts.length
      } catch (error) {
        this.showMessage('Failed to load statistics: ' + error.message, 'error')
        console.error('Error fetching stats:', error)
      } finally {
        this.loading = false
      }
    },
    async updateAllProducts() {
      try {
        this.loading = true
        this.message = ''

        const result = await adminService.updateAllProducts()
        this.showMessage('Successfully updated all financial products!')
        this.fetchStats()

        return result
      } catch (error) {
        this.showMessage('Failed to update products: ' + error.message, 'error')
        console.error('Error updating all products:', error)
      } finally {
        this.loading = false
      }
    },
    async updateDepositProducts() {
      try {
        this.loading = true
        this.message = ''

        const result = await adminService.updateDepositProductsFromAPI()
        this.showMessage('Successfully updated deposit products!')
        this.fetchStats()

        return result
      } catch (error) {
        this.showMessage('Failed to update deposit products: ' + error.message, 'error')
        console.error('Error updating deposit products:', error)
      } finally {
        this.loading = false
      }
    },
    async updateSavingProducts() {
      try {
        this.loading = true
        this.message = ''

        const result = await adminService.updateSavingProductsFromAPI()
        this.showMessage('Successfully updated saving products!')
        this.fetchStats()

        return result
      } catch (error) {
        this.showMessage('Failed to update saving products: ' + error.message, 'error')
        console.error('Error updating saving products:', error)
      } finally {
        this.loading = false
      }
    },
    async updateLoanProducts() {
      try {
        this.loading = true
        this.message = ''

        // Update both mortgage and credit loan products
        await adminService.updateMortgageProductsFromAPI()
        await adminService.updateCreditProductsFromAPI()

        this.showMessage('Successfully updated loan products!')
        this.fetchStats()
      } catch (error) {
        this.showMessage('Failed to update loan products: ' + error.message, 'error')
        console.error('Error updating loan products:', error)
      } finally {
        this.loading = false
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
.admin-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: #333;
}

.admin-nav {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eaeaea;
}

.nav-link {
  padding: 0.5rem 1rem;
  text-decoration: none;
  color: #333;
  font-weight: 500;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-link:hover,
.router-link-active {
  background-color: #f0f0f0;
  color: #007bff;
}

.admin-actions {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.action-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition:
    background-color 0.3s,
    transform 0.1s;
}

.btn:hover {
  transform: translateY(-2px);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

.alert {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
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

.stats-overview {
  margin-top: 2rem;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.stat-card {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #007bff;
  margin: 0.5rem 0;
}

@media (max-width: 768px) {
  .admin-nav,
  .action-buttons {
    flex-direction: column;
  }

  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>

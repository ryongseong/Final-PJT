<template>
  <div class="product-comparison">
    <h3 class="comparison-title">상품 비교</h3>
    
    <div v-if="loading" class="comparison-loading">
      <div class="loading-spinner"></div>
      <p>상품 정보를 불러오는 중...</p>
    </div>
    
    <div v-else-if="error" class="comparison-error">
      <p>{{ error }}</p>
    </div>
    
    <div v-else-if="products.length === 0" class="comparison-empty">
      <p>비교할 상품이 없습니다.</p>
    </div>
    
    <div v-else class="comparison-table-container">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>상품 정보</th>
            <template v-for="(product, index) in products" :key="product.id">
              <th>
                <div class="product-header">
                  <div class="remove-product" @click="removeProduct(index)">
                    <i class="fas fa-times"></i>
                  </div>
                  <BankLogo :bankName="product.kor_co_nm" :size="40" />
                  <div class="product-name">{{ product.fin_prdt_nm }}</div>
                  <div class="product-bank">{{ product.kor_co_nm }}</div>
                </div>
              </th>
            </template>
          </tr>
        </thead>
        <tbody>
          <!-- Interest Rate Row -->
          <tr>
            <td class="row-title">금리</td>
            <template v-for="product in products" :key="product.id">
              <td>
                <template v-if="isDepositOrSaving(product)">
                  <div class="rate-info">
                    <div class="rate-value">{{ formatRate(product.max_rate || product.intr_rate2) }}%</div>
                    <div class="rate-label">최고금리</div>
                  </div>
                </template>
                <template v-else-if="isLoan(product)">
                  <div class="rate-info">
                    <div class="rate-value loan-rate">{{ formatRate(product.min_rate || product.intr_rate) }}%</div>
                    <div class="rate-label">최저금리</div>
                  </div>
                </template>
              </td>
            </template>
          </tr>
          
          <!-- Join Methods Row -->
          <tr>
            <td class="row-title">가입 방법</td>
            <template v-for="product in products" :key="product.id">
              <td>
                <JoinMethods 
                  :joinWay="product.join_way" 
                  :showLabel="false"
                />
              </td>
            </template>
          </tr>
          
          <!-- Launch Date Row -->
          <tr>
            <td class="row-title">출시일</td>
            <template v-for="product in products" :key="product.id">
              <td>
                {{ formatDate(product.fin_prdt_launch_dt) }}
              </td>
            </template>
          </tr>
          
          <!-- Special Features Row -->
          <tr>
            <td class="row-title">특징</td>
            <template v-for="product in products" :key="product.id">
              <td>
                <div class="product-description">
                  {{ product.prdt_detail || '상세 설명이 없습니다.' }}
                </div>
              </td>
            </template>
          </tr>
          
          <!-- Actions Row -->
          <tr>
            <td class="row-title">액션</td>
            <template v-for="product in products" :key="product.id">
              <td>
                <div class="action-buttons">
                  <button 
                    class="view-details-button"
                    @click="viewProductDetails(product)"
                  >
                    상세보기
                  </button>
                  <button 
                    :class="['favorite-button', {'is-favorite': isProductInFavorites(product.id)}]"
                    @click="toggleFavorite(product)"
                  >
                    <font-awesome-icon :icon="isProductInFavorites(product.id) ? ['fas', 'heart'] : ['far', 'heart']" />
                  </button>
                </div>
              </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import BankLogo from '@/components/products/BankLogo.vue';
import JoinMethods from '@/components/products/JoinMethods.vue';

export default {
  name: 'ProductComparison',
  components: {
    BankLogo,
    JoinMethods
  },
  props: {
    products: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: null
    },
    favorites: {
      type: Array,
      default: () => []
    }
  },
  emits: ['view-details', 'toggle-favorite', 'remove-product'],
  methods: {
    isDepositOrSaving(product) {
      const type = product.product_type || this.getTypeFromCategory(product);
      return type === 'deposit' || type === 'saving';
    },
    isLoan(product) {
      const type = product.product_type || this.getTypeFromCategory(product);
      return type === 'loan';
    },
    getTypeFromCategory(product) {
      if (product.fin_prdt_cd && product.fin_prdt_cd.startsWith('DW')) return 'deposit';
      if (product.fin_prdt_cd && product.fin_prdt_cd.startsWith('SW')) return 'saving';
      if (product.loan_type) return 'loan';
      return 'unknown';
    },
    formatRate(rate) {
      if (!rate) return '0.00';
      return parseFloat(rate).toFixed(2);
    },
    formatDate(dateStr) {
      if (!dateStr || dateStr.length !== 8) return '정보 없음';
      
      return `${dateStr.substring(0, 4)}년 ${dateStr.substring(4, 6)}월 ${dateStr.substring(6, 8)}일`;
    },
    isProductInFavorites(productId) {
      return this.favorites.some(fav => 
        fav.product_id === productId || 
        (fav.product && fav.product.id === productId)
      );
    },
    viewProductDetails(product) {
      this.$emit('view-details', product);
    },
    toggleFavorite(product) {
      this.$emit('toggle-favorite', product);
    },
    removeProduct(index) {
      this.$emit('remove-product', index);
    }
  }
}
</script>

<style scoped>
.product-comparison {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.comparison-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #111827;
}

.comparison-loading, .comparison-error, .comparison-empty {
  text-align: center;
  padding: 3rem 0;
}

.loading-spinner {
  display: inline-block;
  width: 40px;
  height: 40px;
  border: 4px solid rgba(75, 85, 99, 0.1);
  border-radius: 50%;
  border-top-color: #3b82f6;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.comparison-table-container {
  overflow-x: auto;
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  font-size: 0.9rem;
}

.comparison-table th, .comparison-table td {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  text-align: center;
}

.comparison-table th {
  background: #f9fafb;
  font-weight: 500;
  color: #374151;
}

.comparison-table td {
  color: #4b5563;
}

.row-title {
  text-align: left;
  font-weight: 500;
  color: #111827;
  background: #f9fafb;
}

.product-header {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  min-width: 150px;
}

.remove-product {
  position: absolute;
  top: -0.5rem;
  right: -0.5rem;
  width: 20px;
  height: 20px;
  background: #ef4444;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  cursor: pointer;
}

.product-name {
  font-weight: 500;
  margin-top: 0.5rem;
  text-align: center;
}

.product-bank {
  font-size: 0.8rem;
  color: #6b7280;
}

.rate-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.rate-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #4caf50;
}

.rate-value.loan-rate {
  color: #2196f3;
}

.rate-label {
  font-size: 0.75rem;
  color: #6b7280;
}

.product-description {
  font-size: 0.85rem;
  max-width: 200px;
  margin: 0 auto;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-align: left;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
}

.view-details-button {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.2s;
}

.view-details-button:hover {
  background: #2563eb;
}

.favorite-button {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
}

.favorite-button.is-favorite {
  background: #fffbeb;
  border-color: #fbbf24;
  color: #d97706;
}

.favorite-button:hover {
  background: #f9fafb;
}

.favorite-button.is-favorite:hover {
  background: #fef3c7;
}
</style>

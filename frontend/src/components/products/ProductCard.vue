<template>
  <div class="product-card" @click="viewProductDetails">
    <!-- Product Header -->
    <div class="product-header">
      <div class="product-badges">
        <span class="product-type-badge">{{ getProductTypeName }}</span>
        <span v-if="isNewProduct" class="new-badge">신규</span>
      </div>
    </div>
    <!-- Product Name and Bank -->
    <h3 class="product-name">{{ getProductName }}</h3>
    <div class="product-bank">{{ getBankName }}</div>
    <!-- Interest Rate Information -->
    <div class="product-rate">
      <template v-if="isDepositOrSaving">
        <div class="rate-info">
          <span class="rate-label">금리</span>
          <span class="rate-value">{{ getInterestRate('max') }}%</span>
          <span class="rate-subtitle">최고금리</span>
        </div>
      </template>
      <template v-else-if="isLoan">
        <div class="rate-info">
          <span class="rate-label">대출금리</span>
          <span class="rate-value loan">{{ getInterestRate('min') }}%</span>
          <span class="rate-subtitle">최저금리</span>
        </div>
      </template>
    </div>

    <!-- Join Methods -->
    <div class="product-join-way">
      <span class="join-label">가입방법</span>
      <div class="join-badges">
        <span v-if="hasJoinWay('영업점')" class="join-badge"> 영업점 </span>
        <span v-if="hasJoinWay('인터넷')" class="join-badge"> 인터넷 </span>
        <span v-if="hasJoinWay('스마트폰')" class="join-badge"> 스마트폰 </span>
        <span v-if="hasJoinWay('전화(텔레뱅킹)')" class="join-badge"> 전화(텔레뱅킹) </span>
      </div>
    </div>

    <!-- Optional Favorite Date -->
    <div v-if="showFavoriteDate && favoriteDate" class="favorite-date">
      추가일: {{ formatDate(favoriteDate) }}
    </div>

    <!-- Action Buttons -->
    <div class="product-actions">
      <button class="details-btn">상세정보</button>
    </div>
  </div>
</template>

<script>
import { formatRate } from '@/utils/rateUtils.js'

export default {
  name: 'ProductCard',
  props: {
    product: {
      type: Object,
      required: true,
    },
    isFavorite: {
      type: Boolean,
      default: false,
    },
    showFavoriteButton: {
      type: Boolean,
      default: true,
    },
    showRemoveButton: {
      type: Boolean,
      default: false,
    },
    showFavoriteDate: {
      type: Boolean,
      default: false,
    },
    favoriteDate: {
      type: String,
      default: null,
    },
  },
  computed: {
    getProductName() {
      // Try to get product name from various possible locations
      return (
        this.product.fin_prdt_nm ||
        (this.product.financial_product && this.product.financial_product.fin_prdt_nm) ||
        '상품명 없음'
      )
    },
    getBankName() {
      // Try to get bank name from various possible locations
      return (
        this.product.kor_co_nm ||
        (this.product.financial_product && this.product.financial_product.kor_co_nm) ||
        '은행명 없음'
      )
    },
    isDepositOrSaving() {
      const type = this.product.product_type || this.getTypeFromCategory()
      return type === 'deposit' || type === 'saving' || type === 'all'
    },
    isLoan() {
      const type = this.product.product_type || this.getTypeFromCategory()
      return type === 'loan'
    },
    getProductTypeName() {
      const type = this.product.product_type || this.getTypeFromCategory()
      const types = {
        deposit: '예금',
        saving: '적금',
        loan: '대출',
      }
      return types[type] || '금융상품'
    },
    isNewProduct() {
      // Get launch date either directly or from nested financial_product
      const launchDate =
        this.product.fin_prdt_launch_dt ||
        (this.product.financial_product && this.product.financial_product.fin_prdt_launch_dt)

      if (!launchDate) return false

      const parsedDate = new Date(
        launchDate.substring(0, 4),
        launchDate.substring(4, 6) - 1,
        launchDate.substring(6, 8),
      )

      const threeMonthsAgo = new Date()
      threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3)

      return parsedDate >= threeMonthsAgo
    },
  },
  methods: {
    getTypeFromCategory() {
      // Try to determine type from category if product_type is not available
      if (this.product.category) {
        if (this.product.category === '예금') return 'deposit'
        if (this.product.category === '적금') return 'saving'
        if (this.product.category === '대출') return 'loan'
      }
      // If we have loan-specific fields
      if (this.product.loan_type) return 'loan'
      return 'unknown'
    },
    getInterestRate(type) {
      let rate = 0.0
      if (type === 'max') {
        rate = this.product.intr_rate2
      } else {
        console.error('Invalid rate type:', type)
        return '알 수 없음'
      }
      return formatRate(rate)
    },
    formatDate(dateString) {
      if (!dateString) return '알 수 없음'
      const date = new Date(dateString)
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    },
    hasJoinWay(code) {
      // Check if join_way is directly on the product
      if (this.product && this.product.join_way) {
        return this.product.join_way.includes(code)
      }

      // Check if join_way is in the nested financial_product
      if (
        this.product &&
        this.product.financial_product &&
        this.product.financial_product.join_way
      ) {
        return this.product.financial_product.join_way.includes(code)
      }

      return false
    },
    viewProductDetails() {
      // Get the product type and ensure we have an ID
      const type = this.product.product_type || this.getTypeFromCategory()

      // Handle nested structure or direct access
      let id
      if (this.product.financial_product) {
        id =
          this.product.financial_product.fin_prdt_cd || this.product.fin_prdt_cd || this.product.id
      } else {
        id = this.product.fin_prdt_cd || this.product.id
      }

      if (!id) {
        console.error('Missing product ID:', this.product)
        return
      }

      // Emit the event with both required parameters
      this.$emit('view-details', {
        id,
        type,
      })
    },
    toggleFavorite() {
      this.$emit('toggle-favorite', this.product)
    },
    emitRemove() {
      this.$emit('remove', this.product)
    },
  },
  setup() {
    return {
      // Add any required composables if needed
    }
  },
}
</script>

<style scoped>
.product-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.25rem;
  background: white;
  transition: all 0.2s;
  cursor: pointer;
  position: relative;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.product-header {
  margin-bottom: 0.75rem;
}

.product-badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.product-type-badge {
  font-size: 0.8rem;
  padding: 0.25rem 0.75rem;
  background: #e0f2fe;
  color: #0369a1;
  border-radius: 20px;
}

.new-badge {
  font-size: 0.8rem;
  padding: 0.25rem 0.75rem;
  background: #ecfdf5;
  color: #047857;
  border-radius: 20px;
}

.product-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
}

.product-bank {
  font-size: 0.9rem;
  color: #6b7280;
  margin-bottom: 1rem;
}

.product-rate {
  background: #f9fafb;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.rate-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.rate-label {
  font-size: 0.85rem;
  color: #6b7280;
}

.rate-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #4caf50;
}

.rate-value.loan {
  color: #2196f3;
}

.rate-subtitle {
  font-size: 0.75rem;
  color: #9ca3af;
}

.product-join-way {
  margin-bottom: 1rem;
}

.join-label {
  display: block;
  font-size: 0.85rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.join-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.join-badge {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.8rem;
  padding: 0.35rem 0.75rem;
  background: #f3f4f6;
  color: #4b5563;
  border-radius: 4px;
}

.join-badge i {
  font-size: 0.9rem;
}

.favorite-date {
  font-size: 0.85rem;
  color: #6b7280;
  font-style: italic;
  margin-bottom: 1rem;
}

.product-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1rem;
}

.favorite-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 50%;
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.2s;
}

.favorite-btn.is-favorite {
  background: #fffbeb;
  border-color: #fbbf24;
  color: #d97706;
}

.favorite-btn:hover {
  background: #f9fafb;
}

.favorite-btn.is-favorite:hover {
  background: #fef3c7;
}

.remove-btn {
  padding: 0.5rem 1rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
}

.remove-btn:hover {
  background: #dc2626;
}

.details-btn {
  flex: 1;
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
}

.details-btn:hover {
  background: #2563eb;
}
</style>

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

      try {
        if (type === 'max') {
          // For deposit/savings products
          if (this.product.intr_rate2 !== undefined) {
            rate = this.product.intr_rate2
          } else if (this.product.options && this.product.options.length) {
            // Find max rate in options
            rate = Math.max(...this.product.options.map((opt) => opt.intr_rate2 || 0))
          } else if (this.product.deposit_options && this.product.deposit_options.length) {
            rate = Math.max(...this.product.deposit_options.map((opt) => opt.intr_rate2 || 0))
          } else if (this.product.saving_options && this.product.saving_options.length) {
            rate = Math.max(...this.product.saving_options.map((opt) => opt.intr_rate2 || 0))
          } else if (this.product.deposit_info) {
            rate = this.product.deposit_info.intr_rate2 || 0
          }
        } else if (type === 'min') {
          // For loan products
          if (this.product.lend_rate_min !== undefined) {
            rate = this.product.lend_rate_min
          } else if (this.product.lending_options && this.product.lending_options.length) {
            rate = Math.min(...this.product.lending_options.map((opt) => opt.lend_rate_min || 99))
          } else if (
            this.product.mortgage_loan_options &&
            this.product.mortgage_loan_options.length
          ) {
            rate = Math.min(
              ...this.product.mortgage_loan_options.map((opt) => opt.lend_rate_min || 99),
            )
          } else if (this.product.credit_loan_options && this.product.credit_loan_options.length) {
            rate = Math.min(
              ...this.product.credit_loan_options.map((opt) => opt.lend_rate_min || 99),
            )
          } else if (this.product.loan_options && this.product.loan_options.length) {
            rate = Math.min(...this.product.loan_options.map((opt) => opt.lend_rate_min || 99))
          }
        } else {
          console.error('Invalid rate type:', type)
          return '알 수 없음'
        }
      } catch (error) {
        console.error('Error calculating interest rate:', error)
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
  background-color: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  transition: all var(--transition-speed);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%; /* Ensure cards in a row have same height if in a grid */
  box-shadow: var(--card-shadow-sm); /* Softer shadow for cards */
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--card-shadow);
  border-color: var(--accent-color-rgb, 0.5); /* Highlight border on hover */
}

.product-header {
  margin-bottom: 0.75rem;
  display: flex; /* For badge alignment */
  justify-content: space-between; /* Align badges */
  align-items: center;
}

.product-badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.product-type-badge,
.new-badge {
  padding: 0.25rem 0.6rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.product-type-badge {
  background-color: rgba(var(--accent-color-rgb, 163, 184, 153), 0.2);
  color: var(--accent-color);
}

.new-badge {
  background-color: rgba(var(--info-color-rgb, 59, 130, 246), 0.15); /* Using info color for new */
  color: var(--info-color, #3b82f6);
}

.product-name {
  font-size: 1.25rem; /* Slightly larger */
  font-weight: 700; /* Bolder */
  color: var(--text-primary);
  margin-bottom: 0.25rem;
  line-height: 1.4;
  /* Clamp to 2 lines */
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-bank {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.product-rate {
  margin-bottom: 1rem;
  background-color: var(--background-primary); /* Subtle background for rate section */
  padding: 0.8rem;
  border-radius: var(--border-radius-md);
  text-align: center; /* Center align rate info */
}

.rate-info {
  display: flex;
  flex-direction: column; /* Stack rate elements */
  align-items: center;
  gap: 0.1rem;
}

.rate-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
  margin-bottom: 0.1rem;
}

.rate-value {
  font-size: 1.6rem; /* Prominent rate */
  font-weight: 700;
  color: var(--accent-color);
}

.rate-value.loan {
  color: var(--accent-color); /* CHANGED to use --accent-color for consistency */
}

.rate-subtitle {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.product-join-way {
  margin-bottom: 1rem;
}

.join-label {
  display: block;
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 0.4rem;
  font-weight: 500;
}

.join-badges {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.join-badge {
  padding: 0.2rem 0.5rem;
  border-radius: var(--border-radius-xs);
  font-size: 0.75rem;
  background-color: var(--background-primary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.favorite-date {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: auto; /* Push to bottom if card is flex column */
  padding-top: 0.75rem;
  border-top: 1px dashed var(--border-color); /* Separator for date */
}

.product-actions {
  margin-top: auto; /* Push actions to the bottom */
  padding-top: 1rem; /* Space above buttons */
  border-top: 1px solid var(--border-color);
}

.details-btn {
  /* Apply global action-btn styles */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%; /* Full width button */
  padding: 0.7rem 1.5rem;
  border-radius: var(--border-radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-speed);
  font-size: 0.95rem;
  border: 1px solid var(--accent-color);
  background-color: var(--accent-color);
  color: var(--button-text);
}

.details-btn:hover {
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}

/* Add icons to buttons if desired, e.g., using ::before or an <i> tag in template */
/* .details-btn::before {
  content: "\f05a"; // Example: Font Awesome info icon
  font-family: "Font Awesome 5 Free";
  font-weight: 900;
  margin-right: 0.5rem;
} */
</style>

<template>
  <div class="rate-display" :class="{ highlight: highlight }">
    <div class="rate-value" :class="{ 'loan-rate': isLoan }">{{ formattedRate }}</div>
    <div class="rate-label">{{ displayLabel }}</div>
  </div>
</template>

<script>
import { useI18n } from 'vue-i18n'

export default {
  name: 'RateDisplay',
  setup() {
    const { t } = useI18n()
    return { t }
  },
  props: {
    rate: {
      type: [Number, String],
      required: true,
    },
    type: {
      type: String,
      default: 'deposit', // 'deposit', 'saving', or 'loan'
      validator: (value) => ['deposit', 'saving', 'loan'].includes(value),
    },
    rateType: {
      type: String,
      default: 'max', // 'max', 'min', 'base'
      validator: (value) => ['max', 'min', 'base'].includes(value),
    },
    highlight: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    formattedRate() {
      if (!this.rate) return '0.00%'
      return parseFloat(this.rate).toFixed(2) + '%'
    },
    isLoan() {
      return this.type === 'loan'
    },
    displayLabel() {
      if (this.type === 'loan') {
        if (this.rateType === 'min') return this.t('products.rates.minLoanRate')
        if (this.rateType === 'max') return this.t('products.rates.maxLoanRate')
        return this.t('products.rates.baseLoanRate')
      } else {
        if (this.rateType === 'max') return this.t('products.rates.maxRate')
        if (this.rateType === 'min') return this.t('products.rates.minRate')
        return this.t('products.rates.baseRate')
      }
    },
  },
}
</script>

<style scoped>
.rate-display {
  background: #f9f9f9;
  border-radius: 6px;
  padding: 15px;
  text-align: center;
  transition: all 0.3s ease;
}

.rate-display.highlight {
  background: #f3f4f6;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.rate-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #4caf50;
  line-height: 1;
  margin-bottom: 5px;
}

.rate-value.loan-rate {
  color: #2196f3;
}

.rate-label {
  font-size: 0.9rem;
  color: #6b7280;
}
</style>

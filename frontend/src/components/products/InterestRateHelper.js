import {
  extractMortgageRates,
  extractCreditRates,
  getRate,
  formatRate,
} from '../utils/rateUtils.js'

export default {
  methods: {
    getInterestRate(type) {
      // For debugging
      console.log('Product data:', this.product)

      // For loans with product_info structure (from LoanProductDetailSerializer)
      if (this.product.product_info) {
        // Check for mortgage options
        if (this.product.mortgage_options && this.product.mortgage_options.length > 0) {
          const rates = extractMortgageRates(this.product.mortgage_options)
          if (rates.length > 0) {
            return formatRate(getRate(rates, type))
          }
        }

        // Check for credit options
        if (this.product.credit_options && this.product.credit_options.length > 0) {
          const rates = extractCreditRates(this.product.credit_options)
          if (rates.length > 0) {
            return formatRate(getRate(rates, type))
          }
        }

        // Try product_info structure
        if (
          this.product.product_info.mortgage_options &&
          this.product.product_info.mortgage_options.length > 0
        ) {
          const rates = extractMortgageRates(this.product.product_info.mortgage_options)
          if (rates.length > 0) {
            return formatRate(getRate(rates, type))
          }
        }

        if (
          this.product.product_info.credit_options &&
          this.product.product_info.credit_options.length > 0
        ) {
          const rates = extractCreditRates(this.product.product_info.credit_options)
          if (rates.length > 0) {
            return formatRate(getRate(rates, type))
          }
        }
      }

      // Check for direct mortgage/credit options
      if (this.product.mortgage_options && this.product.mortgage_options.length > 0) {
        const rates = extractMortgageRates(this.product.mortgage_options)
        if (rates.length > 0) {
          return formatRate(getRate(rates, type))
        }
      }

      if (this.product.credit_options && this.product.credit_options.length > 0) {
        const rates = extractCreditRates(this.product.credit_options)
        if (rates.length > 0) {
          return formatRate(getRate(rates, type))
        }
      }

      // Check for nested financial_product structure
      if (this.product.financial_product) {
        const fp = this.product.financial_product

        // Check mortgage options
        if (fp.mortgage_options && fp.mortgage_options.length > 0) {
          const rates = extractMortgageRates(fp.mortgage_options)
          if (rates.length > 0) {
            return formatRate(getRate(rates, type))
          }
        }

        // Check credit options
        if (fp.credit_options && fp.credit_options.length > 0) {
          const rates = extractCreditRates(fp.credit_options)
          if (rates.length > 0) {
            return formatRate(getRate(rates, type))
          }
        }

        // Check regular options
        if (fp.options && fp.options.length > 0) {
          const rates = fp.options
            .map((option) => parseFloat(option.intr_rate || 0))
            .filter((rate) => !isNaN(rate) && rate > 0)
          if (rates.length > 0) {
            return formatRate(getRate(rates, type))
          }
        }

        // Try direct rate fields
        if (type === 'max') {
          const maxRate = fp.max_rate || fp.intr_rate2 || fp.intr_rate
          if (maxRate) return formatRate(maxRate)
        } else {
          const minRate = fp.min_rate || fp.intr_rate || fp.intr_rate2
          if (minRate) return formatRate(minRate)
        }
      }

      // Try direct access on the product object
      if (type === 'max') {
        const maxRate = this.product.max_rate || this.product.intr_rate2 || this.product.intr_rate
        if (maxRate) return formatRate(maxRate)
      } else {
        const minRate = this.product.min_rate || this.product.intr_rate || this.product.intr_rate2
        if (minRate) return formatRate(minRate)
      }

      // Default fallback
      return '0.00'
    },
  },
}

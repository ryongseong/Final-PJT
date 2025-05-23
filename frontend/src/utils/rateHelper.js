// RateExtractor Helper Functions

// Extract rates from mortgage options, checking both lending_rate and lend_rate_min
function extractMortgageRates(options) {
  if (!options || !options.length) return []

  return options
    .map((option) => parseFloat(option.lending_rate || option.lend_rate_min || 0))
    .filter((rate) => !isNaN(rate) && rate > 0)
}

// Extract rates from credit options, checking both lending_rate and crdt_grad_1
function extractCreditRates(options) {
  if (!options || !options.length) return []

  return options
    .map((option) => parseFloat(option.lending_rate || option.crdt_grad_1 || 0))
    .filter((rate) => !isNaN(rate) && rate > 0)
}

// Get min or max rate from an array of rates
function getRate(rates, type = 'min') {
  if (!rates.length) return 0

  if (type === 'max') {
    return Math.max(...rates)
  } else {
    return Math.min(...rates)
  }
}

// Update the getInterestRate method in ProductCard.vue to use these helpers:

/*
getInterestRate(type) {
  // For debugging
  console.log('Product data:', this.product);

  // For loans with product_info (from LoanProductDetailSerializer)
  if (this.product.product_info) {
    // Check mortgage options in product
    if (this.product.mortgage_options && this.product.mortgage_options.length > 0) {
      const rates = extractMortgageRates(this.product.mortgage_options);
      if (rates.length > 0) {
        return this.formatRate(getRate(rates, type));
      }
    }

    // Check credit options in product
    if (this.product.credit_options && this.product.credit_options.length > 0) {
      const rates = extractCreditRates(this.product.credit_options);
      if (rates.length > 0) {
        return this.formatRate(getRate(rates, type));
      }
    }

    // Try to get from product_info
    if (this.product.product_info.mortgage_options && this.product.product_info.mortgage_options.length > 0) {
      const rates = extractMortgageRates(this.product.product_info.mortgage_options);
      if (rates.length > 0) {
        return this.formatRate(getRate(rates, type));
      }
    }

    if (this.product.product_info.credit_options && this.product.product_info.credit_options.length > 0) {
      const rates = extractCreditRates(this.product.product_info.credit_options);
      if (rates.length > 0) {
        return this.formatRate(getRate(rates, type));
      }
    }
  }

  // Direct access to mortgage/credit options
  if (this.product.mortgage_options && this.product.mortgage_options.length > 0) {
    const rates = extractMortgageRates(this.product.mortgage_options);
    if (rates.length > 0) {
      return this.formatRate(getRate(rates, type));
    }
  }

  if (this.product.credit_options && this.product.credit_options.length > 0) {
    const rates = extractCreditRates(this.product.credit_options);
    if (rates.length > 0) {
      return this.formatRate(getRate(rates, type));
    }
  }

  // Check for nested financial_product structure
  if (this.product.financial_product) {
    const fp = this.product.financial_product;

    // Check mortgage options in nested structure
    if (fp.mortgage_options && fp.mortgage_options.length > 0) {
      const rates = extractMortgageRates(fp.mortgage_options);
      if (rates.length > 0) {
        return this.formatRate(getRate(rates, type));
      }
    }

    // Check credit options in nested structure
    if (fp.credit_options && fp.credit_options.length > 0) {
      const rates = extractCreditRates(fp.credit_options);
      if (rates.length > 0) {
        return this.formatRate(getRate(rates, type));
      }
    }

    // Rest of the existing fallback code...
  }

  // Original fallback code remains unchanged
}
*/

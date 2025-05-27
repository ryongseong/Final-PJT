// Utility functions for extracting and formatting interest rates from various data structures

/**
 * Extract interest rates from mortgage loan options
 * @param {Array} options - Array of mortgage loan options
 * @returns {Array} - Array of parsed interest rates
 */
export function extractMortgageRates(options) {
  if (!options || !options.length) return []

  return options
    .map((option) => parseFloat(option.lending_rate || option.lend_rate_min || 0))
    .filter((rate) => !isNaN(rate) && rate > 0)
}

/**
 * Extract interest rates from credit loan options
 * @param {Array} options - Array of credit loan options
 * @returns {Array} - Array of parsed interest rates
 */
export function extractCreditRates(options) {
  if (!options || !options.length) return []

  return options
    .map((option) => parseFloat(option.lending_rate || option.crdt_grad_1 || 0))
    .filter((rate) => !isNaN(rate) && rate > 0)
}

/**
 * Get the min or max rate from an array of rates
 * @param {Array} rates - Array of interest rates
 * @param {string} type - 'min' or 'max'
 * @returns {number} - Min or max interest rate
 */
export function getRate(rates, type = 'min') {
  if (!rates || !rates.length) return 0

  if (type === 'max') {
    return Math.max(...rates)
  } else {
    return Math.min(...rates)
  }
}

/**
 * Format a rate as a fixed 2-decimal string
 * @param {number|string} rate - The rate to format
 * @returns {string} - Formatted rate string
 */
export function formatRate(rate) {
  if (!rate) return '0.00'

  // Ensure we're working with a number and handle different formats
  let numRate
  if (typeof rate === 'string') {
    // Remove any non-numeric characters except decimal point
    numRate = parseFloat(rate.replace(/[^\d.-]/g, ''))
  } else {
    numRate = parseFloat(rate)
  }

  // Check if parsing resulted in a valid number
  if (isNaN(numRate)) return '0.00'

  return numRate.toFixed(2)
}

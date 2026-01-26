/**
 * Currency formatting utilities
 * Prices are stored and displayed in the currency specified (TND, USD, etc.)
 * No conversion is applied - prices are used as-is from the database
 */

const EXCHANGE_RATES = {
  USD: 1,
  TND: 1
};

/**
 * Format price in the specified currency
 * @param {number} amount - The price amount (already in target currency)
 * @param {string} currency - The currency code ('USD' or 'TND')
 * @param {number} decimals - Number of decimal places (default: 0)
 * @returns {string} Formatted price string
 */
export const formatPrice = (amount, currency = 'TND', decimals = null) => {
  if (!amount && amount !== 0) return '0';

  // No currency conversion - prices are already in the correct currency from the database
  const decimalPlaces = decimals !== null ? decimals : 0;

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: decimalPlaces,
    maximumFractionDigits: decimalPlaces
  }).format(amount);
};

/**
 * Convert USD amount to TND
 * @param {number} amount - The amount in USD
 * @returns {number} The amount in TND
 */
export const convertToTND = (amount) => {
  return amount * EXCHANGE_RATES.TND;
};

/**
 * Get the exchange rate for a currency
 * @param {string} currency - The currency code ('USD' or 'TND')
 * @returns {number} The exchange rate
 */
export const getExchangeRate = (currency = 'TND') => {
  return EXCHANGE_RATES[currency] || 1;
};

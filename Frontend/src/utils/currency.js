/**
 * Currency conversion and formatting utilities
 * Converts USD prices to Tunisian Dinar (TND)
 * Exchange rate: 1 USD = 2.89 TND
 */

const EXCHANGE_RATES = {
  USD: 1,
  TND: 2.89
};

/**
 * Format price in the specified currency
 * @param {number} amount - The price amount in USD
 * @param {string} currency - The target currency ('USD' or 'TND')
 * @param {number} decimals - Number of decimal places (default: 3 for TND, 0 for USD)
 * @returns {string} Formatted price string
 */
export const formatPrice = (amount, currency = 'TND', decimals = null) => {
  if (!amount && amount !== 0) return '0';
  
  const converted = amount * EXCHANGE_RATES[currency];
  const decimalPlaces = decimals !== null ? decimals : (currency === 'TND' ? 3 : 0);
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: decimalPlaces,
    maximumFractionDigits: decimalPlaces
  }).format(converted);
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

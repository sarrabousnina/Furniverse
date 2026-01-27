// API service for backend communication
const API_BASE_URL = 'http://localhost:8000';

/**
 * Fetch all products from the backend
 * @param {Object} options - Query options
 * @param {string} options.category - Filter by category
 * @param {string} options.search - Search query
 * @returns {Promise<Array>} Array of products
 */
export const fetchProducts = async (options = {}) => {
  try {
    const params = new URLSearchParams();
    
    if (options.category) {
      params.append('category', options.category);
    }
    
    if (options.search) {
      params.append('search', options.search);
    }
    
    const url = `${API_BASE_URL}/products${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch products: ${response.statusText}`);
    }
    
    const products = await response.json();
    return products;
  } catch (error) {
    console.error('Error fetching products:', error);
    throw error;
  }
};

/**
 * Fetch a single product by ID
 * @param {number} id - Product ID
 * @returns {Promise<Object>} Product object
 */
export const fetchProductById = async (id) => {
  try {
    const response = await fetch(`${API_BASE_URL}/products/${id}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        return null;
      }
      throw new Error(`Failed to fetch product: ${response.statusText}`);
    }
    
    const product = await response.json();
    return product;
  } catch (error) {
    console.error(`Error fetching product ${id}:`, error);
    throw error;
  }
};

/**
 * Fetch all available categories
 * @returns {Promise<Array>} Array of category names
 */
export const fetchCategories = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/categories`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch categories: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.categories || [];
  } catch (error) {
    console.error('Error fetching categories:', error);
    throw error;
  }
};

/**
 * Get AI-powered product recommendations
 * @param {string} query - Search query
 * @returns {Promise<Object>} Recommendation response
 */
export const getRecommendation = async (query) => {
  try {
    const response = await fetch(`${API_BASE_URL}/recommend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error(`Failed to get recommendation: ${response.statusText}`);
    }

    const recommendation = await response.json();
    return recommendation;
  } catch (error) {
    console.error('Error getting recommendation:', error);
    throw error;
  }
};

/**
 * Get AI-powered smart search with budget awareness
 * @param {string} query - Natural language search query
 * @param {string} category - Optional category filter
 * @param {number} limit - Number of results (default: 8)
 * @returns {Promise<Object>} Smart search response with AI analysis
 */
export const smartSearch = async (query, category = null, limit = 8) => {
  try {
    const response = await fetch(`${API_BASE_URL}/recommend/smart`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        category,
        limit
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to perform smart search: ${response.statusText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error performing smart search:', error);
    throw error;
  }
};

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

/**
 * Search products by uploaded image using CLIP image embeddings
 * @param {File} imageFile - Image file to search with
 * @param {string} category - Optional category filter
 * @param {number} limit - Number of results (default: 8)
 * @returns {Promise<Array>} Array of visually similar products
 */
export const searchByImage = async (imageFile, category = null, limit = 8) => {
  try {
    const formData = new FormData();
    formData.append('file', imageFile);
    if (category && category !== 'all') {
      formData.append('category', category);
    }
    formData.append('limit', limit.toString());

    const response = await fetch(`${API_BASE_URL}/recommend/image`, {
      method: 'POST',
      // Don't set Content-Type header - browser will set it with boundary
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Image search failed: ${response.statusText}`);
    }

    const results = await response.json();
    return results;
  } catch (error) {
    console.error('Error searching by image:', error);
    throw error;
  }
};

// ============================================================================
// Product → User Recommendations (User Activity)
// ============================================================================

/**
 * Find users interested in a product
 * Used by admin when creating discounts to find which users to notify
 */
export const findInterestedUsers = async (productId, productName, category, limit = 10) => {
  try {
    const params = new URLSearchParams({
      product_name: productName,
      category: category,
      limit: limit.toString()
    });

    const response = await fetch(`${API_BASE_URL}/users/interested-in/${productId}?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to find interested users: ${response.statusText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error finding interested users:', error);
    throw error;
  }
};

/**
 * Get user activity summary
 */
export const getUserActivity = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/users/${userId}/activity`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get user activity: ${response.statusText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error getting user activity:', error);
    throw error;
  }
};

/**
 * Get user statistics (total users, events tracked)
 */
export const getUserStats = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/users/stats`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get user stats: ${response.statusText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error getting user stats:', error);
    throw error;
  }
};

/**
 * Trade-off aware search with explainability
 * Returns products with trade-off analysis (what you gain vs what you lose)
 */
export const searchWithTradeoffs = async (query, category = null, limit = 10) => {
  try {
    const requestBody = {
      query: query,
      category: category,
      limit: limit
    };

    const response = await fetch(`${API_BASE_URL}/search/tradeoffs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      throw new Error(`Trade-off search failed: ${response.statusText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error searching with trade-offs:', error);
    throw error;
  }
};

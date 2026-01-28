const STORAGE_KEY = 'furniverse_user_activity';
const USER_ID_KEY = 'furniverse_user_id';
const MAX_SEARCHES = 100;
const MAX_VIEWS = 200;
const API_BASE_URL = 'http://localhost:8000';

// Get all user activity from localStorage
const getActivity = () => {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    if (!data) {
      return { searches: [], productViews: [], productClicks: [] };
    }
    return JSON.parse(data);
  } catch (error) {
    console.error('Error reading user activity:', error);
    return { searches: [], productViews: [], productClicks: [] };
  }
};

// Save activity to localStorage
const saveActivity = (activity) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(activity));
  } catch (error) {
    console.error('Error saving user activity:', error);
  }
};

// Get or create user ID
export const getUserId = () => {
  try {
    let userId = localStorage.getItem(USER_ID_KEY);
    if (!userId) {
      // Generate a unique user ID
      userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem(USER_ID_KEY, userId);
    }
    return userId;
  } catch (error) {
    console.error('Error getting user ID:', error);
    return 'user_anonymous';
  }
};

// Send event to backend for Product → User recommendations
const sendEventToBackend = async (eventData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/track`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(eventData),
    });

    if (!response.ok) {
      console.warn('Failed to send event to backend:', response.statusText);
    }
  } catch (error) {
    // Silent fail - backend tracking is optional
    console.warn('Could not connect to backend for tracking:', error.message);
  }
};

// Track a search query
export const trackSearch = (query) => {
  if (!query || typeof query !== 'string') return;

  const activity = getActivity();
  const searchEntry = {
    query: query.trim(),
    timestamp: new Date().toISOString()
  };

  // Add to beginning of array and limit size
  activity.searches.unshift(searchEntry);
  if (activity.searches.length > MAX_SEARCHES) {
    activity.searches = activity.searches.slice(0, MAX_SEARCHES);
  }

  saveActivity(activity);

  // Send to backend for Product → User recommendations
  sendEventToBackend({
    user_id: getUserId(),
    event_type: 'search',
    search_query: query.trim()
  });
};

// Track when a user views a product (opens modal/detail page)
export const trackProductView = (product) => {
  if (!product || !product.id) return;

  const activity = getActivity();
  const viewEntry = {
    productId: product.id,
    productName: product.name,
    category: product.category,
    price: product.price,
    timestamp: new Date().toISOString()
  };

  // Add to beginning of array and limit size
  activity.productViews.unshift(viewEntry);
  if (activity.productViews.length > MAX_VIEWS) {
    activity.productViews = activity.productViews.slice(0, MAX_VIEWS);
  }

  saveActivity(activity);

  // Send to backend for Product → User recommendations
  sendEventToBackend({
    user_id: getUserId(),
    event_type: 'view',
    product_id: String(product.id),
    product_name: product.name,
    category: product.category,
    price: product.price
  });
};

// Track when a user clicks on a product card
export const trackProductClick = (product) => {
  if (!product || !product.id) return;

  const activity = getActivity();
  const clickEntry = {
    productId: product.id,
    productName: product.name,
    category: product.category,
    price: product.price,
    timestamp: new Date().toISOString()
  };

  // Add to beginning of array and limit size
  activity.productClicks.unshift(clickEntry);
  if (activity.productClicks.length > MAX_VIEWS) {
    activity.productClicks = activity.productClicks.slice(0, MAX_VIEWS);
  }

  saveActivity(activity);

  // Send to backend for Product → User recommendations
  sendEventToBackend({
    user_id: getUserId(),
    event_type: 'click',
    product_id: String(product.id),
    product_name: product.name,
    category: product.category,
    price: product.price
  });
};

// Get all tracked activity
export const getUserActivity = () => {
  return getActivity();
};

// Get search history
export const getSearchHistory = () => {
  return getActivity().searches;
};

// Get product view history
export const getProductViewHistory = () => {
  return getActivity().productViews;
};

// Get product click history
export const getProductClickHistory = () => {
  return getActivity().productClicks;
};

// Clear all tracking data
export const clearUserActivity = () => {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Error clearing user activity:', error);
  }
};

// Get recently viewed products (for recommendations)
export const getRecentlyViewed = (limit = 10) => {
  const views = getActivity().productViews;
  // Remove duplicates based on productId, keeping most recent
  const uniqueViews = views.filter((view, index, self) =>
    index === self.findIndex((v) => v.productId === view.productId)
  );
  return uniqueViews.slice(0, limit);
};

// Get recent searches (for autocomplete)
export const getRecentSearches = (limit = 5) => {
  const searches = getActivity().searches;
  // Remove duplicates, keeping most recent
  const uniqueSearches = searches.filter((search, index, self) =>
    index === self.findIndex((s) => s.query.toLowerCase() === search.query.toLowerCase())
  );
  return uniqueSearches.slice(0, limit).map(s => s.query);
};

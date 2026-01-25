import { createContext, useContext, useState, useEffect } from 'react';
import { fetchProducts as fetchProductsAPI, fetchCategories } from '../services/api';

const ProductsContext = createContext();

export const useProducts = () => {
  const context = useContext(ProductsContext);
  if (!context) {
    throw new Error('useProducts must be used within ProductsProvider');
  }
  return context;
};

export const ProductsProvider = ({ children }) => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch all products on mount
  useEffect(() => {
    loadProducts();
    loadCategories();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchProductsAPI();
      setProducts(data);
    } catch (err) {
      setError(err.message);
      console.error('Failed to load products:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const data = await fetchCategories();
      setCategories(data);
    } catch (err) {
      console.error('Failed to load categories:', err);
    }
  };

  const getProductById = (id) => {
    return products.find(p => p.id === parseInt(id));
  };

  const getProductsByCategory = (category) => {
    if (category === 'all') return products;
    return products.filter(p => p.category.toLowerCase() === category.toLowerCase());
  };

  const searchProducts = (query) => {
    if (!query) return products;
    const lowerQuery = query.toLowerCase();
    return products.filter(p =>
      p.name.toLowerCase().includes(lowerQuery) ||
      p.description.toLowerCase().includes(lowerQuery) ||
      p.tags?.some(tag => tag.toLowerCase().includes(lowerQuery)) ||
      p.category.toLowerCase().includes(lowerQuery)
    );
  };

  const getTrendingProducts = () => {
    return products.filter(p => p.trending);
  };

  const getRelatedProducts = (productId, limit = 4) => {
    const product = getProductById(productId);
    if (!product) return [];

    // Find products with same category or similar styles
    const related = products.filter(p =>
      p.id !== productId &&
      (p.category === product.category || p.styles?.some(s => product.styles?.includes(s)))
    );

    return related.slice(0, limit);
  };

  const value = {
    products,
    categories,
    loading,
    error,
    getProductById,
    getProductsByCategory,
    searchProducts,
    getTrendingProducts,
    getRelatedProducts,
    refreshProducts: loadProducts,
  };

  return (
    <ProductsContext.Provider value={value}>
      {children}
    </ProductsContext.Provider>
  );
};

import React, { createContext, useContext, useState, useEffect } from 'react';

const CUSTOM_PRODUCTS_STORAGE_KEY = 'furniverse_custom_products';

const CustomProductsContext = createContext();

export const useCustomProducts = () => {
  const context = useContext(CustomProductsContext);
  if (!context) {
    throw new Error('useCustomProducts must be used within a CustomProductsProvider');
  }
  return context;
};

export const CustomProductsProvider = ({ children }) => {
  const [customProducts, setCustomProducts] = useState(() => {
    try {
      const saved = localStorage.getItem(CUSTOM_PRODUCTS_STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch (error) {
      console.error('Failed to load custom products:', error);
      return [];
    }
  });

  // Save to localStorage whenever customProducts changes
  useEffect(() => {
    try {
      localStorage.setItem(CUSTOM_PRODUCTS_STORAGE_KEY, JSON.stringify(customProducts));
    } catch (error) {
      console.error('Failed to save custom products:', error);
    }
  }, [customProducts]);

  const addCustomProduct = (productData) => {
    // Generate a unique ID (negative to distinguish from backend products)
    const newId = customProducts.length > 0
      ? Math.min(...customProducts.map(p => p.id)) - 1
      : -1;

    const newProduct = {
      id: newId,
      name: productData.name,
      category: productData.category,
      price: Number(productData.price),
      rating: Number(productData.rating) || 0,
      reviewCount: Number(productData.reviewCount) || 0,
      image: productData.image,
      images: productData.images || [productData.image],
      description: productData.description || '',
      features: productData.features || [],
      styles: productData.styles || [],
      colors: productData.colors || [],
      tags: productData.tags || [],
      dimensions: productData.dimensions || null,
      inStock: productData.inStock !== undefined ? productData.inStock : true,
      trending: productData.trending || false,
      isCustom: true, // Flag to identify custom products
      variants: [] // Custom products don't have variants initially
    };

    setCustomProducts(prev => [...prev, newProduct]);
    return newProduct;
  };

  const updateCustomProduct = (productId, updates) => {
    setCustomProducts(prev =>
      prev.map(p => p.id === productId ? { ...p, ...updates } : p)
    );
  };

  const deleteCustomProduct = (productId) => {
    setCustomProducts(prev => prev.filter(p => p.id !== productId));
  };

  const getCustomProductById = (productId) => {
    return customProducts.find(p => p.id === productId);
  };

  const isCustomProduct = (productId) => {
    return customProducts.some(p => p.id === productId);
  };

  const value = {
    customProducts,
    addCustomProduct,
    updateCustomProduct,
    deleteCustomProduct,
    getCustomProductById,
    isCustomProduct
  };

  return (
    <CustomProductsContext.Provider value={value}>
      {children}
    </CustomProductsContext.Provider>
  );
};

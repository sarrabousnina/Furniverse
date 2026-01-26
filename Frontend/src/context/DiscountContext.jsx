import React, { createContext, useContext, useState, useEffect } from 'react';

const DISCOUNT_STORAGE_KEY = 'furniverse_discounts';

const DiscountContext = createContext();

export const useDiscounts = () => {
  const context = useContext(DiscountContext);
  if (!context) {
    throw new Error('useDiscounts must be used within DiscountProvider');
  }
  return context;
};

export const DiscountProvider = ({ children }) => {
  // Load discounts from localStorage on mount
  const [discounts, setDiscounts] = useState(() => {
    try {
      const saved = localStorage.getItem(DISCOUNT_STORAGE_KEY);
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });

  // Save discounts to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem(DISCOUNT_STORAGE_KEY, JSON.stringify(discounts));
    } catch (error) {
      console.error('Failed to save discounts:', error);
    }
  }, [discounts]);

  const applyDiscount = (productId, percentage) => {
    setDiscounts(prev => ({
      ...prev,
      [productId]: percentage
    }));
  };

  const removeDiscount = (productId) => {
    setDiscounts(prev => {
      const newDiscounts = { ...prev };
      delete newDiscounts[productId];
      return newDiscounts;
    });
  };

  const getDiscount = (productId) => {
    return discounts[productId] || 0;
  };

  const clearAllDiscounts = () => {
    setDiscounts({});
  };

  const getDiscountedPrice = (price, productId) => {
    const discount = discounts[productId];
    if (!discount) return price;
    return Math.round(price * (1 - discount / 100));
  };

  const hasDiscount = (productId) => {
    return productId in discounts && discounts[productId] > 0;
  };

  const value = {
    discounts,
    applyDiscount,
    removeDiscount,
    getDiscount,
    clearAllDiscounts,
    getDiscountedPrice,
    hasDiscount
  };

  return (
    <DiscountContext.Provider value={value}>
      {children}
    </DiscountContext.Provider>
  );
};

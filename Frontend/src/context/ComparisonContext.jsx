import { createContext, useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const ComparisonContext = createContext();

export const useComparison = () => {
  const context = useContext(ComparisonContext);
  if (!context) {
    throw new Error('useComparison must be used within ComparisonProvider');
  }
  return context;
};

export const ComparisonProvider = ({ children }) => {
  const [selectedProducts, setSelectedProducts] = useState([]);
  const navigate = useNavigate();

  const addToComparison = (product) => {
    if (selectedProducts.length >= 2) {
      // If already 2 products, replace the second one
      setSelectedProducts([selectedProducts[0], product]);
    } else {
      setSelectedProducts([...selectedProducts, product]);
    }
  };

  const removeFromComparison = (productId) => {
    setSelectedProducts(selectedProducts.filter(p => p.id !== productId));
  };

  const isInComparison = (productId) => {
    return selectedProducts.some(p => p.id === productId);
  };

  const clearComparison = () => {
    setSelectedProducts([]);
  };

  const startComparison = () => {
    if (selectedProducts.length === 2) {
      navigate(`/compare?productA=${selectedProducts[0].id}&productB=${selectedProducts[1].id}`);
      // Don't clear - let them see what they compared
    }
  };

  const value = {
    selectedProducts,
    addToComparison,
    removeFromComparison,
    isInComparison,
    clearComparison,
    startComparison,
    canCompare: selectedProducts.length === 2
  };

  return (
    <ComparisonContext.Provider value={value}>
      {children}
    </ComparisonContext.Provider>
  );
};

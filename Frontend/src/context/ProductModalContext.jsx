import React, { createContext, useContext, useState } from 'react';

const ProductModalContext = createContext();

export const useProductModal = () => {
  const context = useContext(ProductModalContext);
  if (!context) {
    throw new Error('useProductModal must be used within a ProductModalProvider');
  }
  return context;
};

export const ProductModalProvider = ({ children }) => {
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const openProductModal = (product) => {
    setSelectedProduct(product);
    setIsModalOpen(true);
  };

  const closeProductModal = () => {
    setIsModalOpen(false);
    setTimeout(() => setSelectedProduct(null), 300); // Clear after animation
  };

  return (
    <ProductModalContext.Provider
      value={{
        selectedProduct,
        isModalOpen,
        openProductModal,
        closeProductModal,
      }}
    >
      {children}
    </ProductModalContext.Provider>
  );
};

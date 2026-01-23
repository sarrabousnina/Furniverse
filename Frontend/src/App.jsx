import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { CartProvider, useCart } from './context/CartContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { RoomsProvider } from './context/RoomsContext';
import { ProductModalProvider, useProductModal } from './context/ProductModalContext';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './context/ToastContext';

// Pages
import HomePage from './pages/HomePage/HomePage';
import ShopPage from './pages/ShopPage/ShopPage';
import ProductDetailPage from './pages/ProductDetailPage/ProductDetailPage';
import ProfilePage from './pages/ProfilePage/ProfilePage';
import CheckoutPage from './pages/CheckoutPage/CheckoutPage';
import RoomDetailPage from './pages/RoomDetailPage/RoomDetailPage';

// Components
import Navigation from './components/Navigation/Navigation';
import CartSidebar from './components/CartSidebar/CartSidebar';
import AuthModal from './components/AuthModal/AuthModal';
import ProductDetailModal from './components/ProductDetailModal/ProductDetailModal';
import ToastContainer from './components/Toast/Toast';
import './index.css';

// Scroll to top on route change
function ScrollToTop() {
  const location = useLocation();

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [location.pathname]);

  return null;
}

// App content with routing and modals
function AppContent() {
  const { isCartOpen } = useCart();
  const { isAuthModalOpen } = useAuth();
  const { selectedProduct, isModalOpen, closeProductModal } = useProductModal();

  return (
    <>
      <ScrollToTop />
      <Navigation />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/shop" element={<ShopPage />} />
        <Route path="/product/:id" element={<ProductDetailPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/room/:roomId" element={<RoomDetailPage />} />
        <Route path="/checkout" element={<CheckoutPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      {/* Global Modals */}
      {isCartOpen && <CartSidebar />}
      {isAuthModalOpen && <AuthModal />}
      <ProductDetailModal
        product={selectedProduct}
        isOpen={isModalOpen}
        onClose={closeProductModal}
      />
    </>
  );
}

function App() {
  return (
    <Router>
      <ThemeProvider>
        <ToastProvider>
          <AuthProvider>
            <CartProvider>
              <RoomsProvider>
                <ProductModalProvider>
                  <AppContent />
                  <ToastContainer />
                </ProductModalProvider>
              </RoomsProvider>
            </CartProvider>
          </AuthProvider>
        </ToastProvider>
      </ThemeProvider>
    </Router>
  );
}

export default App;

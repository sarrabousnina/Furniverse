import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { CartProvider, useCart } from './context/CartContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { RoomsProvider } from './context/RoomsContext';

// Pages
import HomePage from './pages/HomePage/HomePage';
import ShopPage from './pages/ShopPage/ShopPage';
import ProductDetailPage from './pages/ProductDetailPage/ProductDetailPage';
import ProfilePage from './pages/ProfilePage/ProfilePage';
import CheckoutPage from './pages/CheckoutPage/CheckoutPage';

// Components
import Navigation from './components/Navigation/Navigation';
import CartSidebar from './components/CartSidebar/CartSidebar';
import AuthModal from './components/AuthModal/AuthModal';
import './index.css';

// App content with routing and modals
function AppContent() {
  const { isCartOpen } = useCart();
  const { isAuthModalOpen } = useAuth();

  return (
    <>
      <Navigation />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/shop" element={<ShopPage />} />
        <Route path="/product/:id" element={<ProductDetailPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/checkout" element={<CheckoutPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      {/* Global Modals */}
      {isCartOpen && <CartSidebar />}
      {isAuthModalOpen && <AuthModal />}
    </>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <CartProvider>
          <RoomsProvider>
            <AppContent />
          </RoomsProvider>
        </CartProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;

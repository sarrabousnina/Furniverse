import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../../context/CartContext';
import styles from './CartSidebar.module.css';

const CartSidebar = () => {
  const navigate = useNavigate();
  const {
    cart,
    cartTotal,
    updateQuantity,
    removeFromCart,
    setIsCartOpen,
  } = useCart();

  const handleCheckout = () => {
    setIsCartOpen(false);
    navigate('/checkout');
  };

  const handleContinueShopping = () => {
    setIsCartOpen(false);
  };

  return (
    <>
      <div className={styles.overlay} onClick={handleContinueShopping} />
      <div className={styles.sidebar}>
        {/* Header */}
        <div className={styles.header}>
          <h2 className={styles.headerTitle}>Shopping Cart ({cart.length})</h2>
          <button
            className={styles.closeButton}
            onClick={handleContinueShopping}
            aria-label="Close cart"
          >
            <svg viewBox="0 0 24 24" fill="none" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 6 6 18M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className={styles.content}>
          {cart.length === 0 ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyStateIcon}>🛒</div>
              <h3 className={styles.emptyStateTitle}>Your cart is empty</h3>
              <p className={styles.emptyStateText}>
                Looks like you haven't added anything to your cart yet.
              </p>
              <button
                className={styles.emptyStateButton}
                onClick={handleContinueShopping}
              >
                Continue Shopping
              </button>
            </div>
          ) : (
            <div className={styles.cartItems}>
              {cart.map(item => (
                <div key={item.id} className={styles.cartItem}>
                  <img src={item.image} alt={item.name} className={styles.itemImage} />
                  <div className={styles.itemDetails}>
                    <div className={styles.itemName}>{item.name}</div>
                    <div className={styles.itemPrice}>
                      ${item.price.toLocaleString()} × {item.quantity}
                    </div>
                    <div className={styles.itemActions}>
                      <div className={styles.quantityControls}>
                        <button
                          className={styles.quantityButton}
                          onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          aria-label="Decrease quantity"
                        >
                          −
                        </button>
                        <span className={styles.quantity}>{item.quantity}</span>
                        <button
                          className={styles.quantityButton}
                          onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          aria-label="Increase quantity"
                        >
                          +
                        </button>
                      </div>
                      <button
                        className={styles.removeButton}
                        onClick={() => removeFromCart(item.id)}
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {cart.length > 0 && (
          <div className={styles.footer}>
            <div className={styles.subtotal}>
              <span className={styles.subtotalLabel}>Subtotal</span>
              <span className={styles.subtotalAmount}>
                ${cartTotal.toLocaleString()}
              </span>
            </div>
            <button className={styles.checkoutButton} onClick={handleCheckout}>
              Proceed to Checkout
            </button>
            <p style={{
              marginTop: '12px',
              fontSize: '0.8125rem',
              color: '#6B6B6B',
              textAlign: 'center',
            }}>
              Shipping calculated at checkout
            </p>
          </div>
        )}
      </div>
    </>
  );
};

export default CartSidebar;

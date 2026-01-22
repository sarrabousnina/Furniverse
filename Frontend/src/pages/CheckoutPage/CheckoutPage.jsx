import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../../context/CartContext';
import styles from './CheckoutPage.module.css';

const CheckoutPage = () => {
  const navigate = useNavigate();
  const { cart, cartTotal, clearCart } = useCart();

  const handlePlaceOrder = (e) => {
    e.preventDefault();
    // Simulate order processing
    alert('Order placed successfully! This is a demo - no real payment was processed.');
    clearCart();
    navigate('/');
  };

  // Calculate totals
  const subtotal = cartTotal;
  const shipping = subtotal > 500 ? 0 : 49;
  const tax = subtotal * 0.08;
  const total = subtotal + shipping + tax;

  if (cart.length === 0) {
    return (
      <div className={styles.page}>
        <div className={styles.container}>
          <div className={styles.emptyState}>
            <div className={styles.emptyStateIcon}>🛒</div>
            <h2 className={styles.emptyStateTitle}>Your cart is empty</h2>
            <p className={styles.emptyStateText}>
              Add some items to your cart before checkout
            </p>
            <Link to="/shop" className={styles.backLink}>
              ← Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        {/* Header */}
        <div className={styles.header}>
          <Link to="/shop" className={styles.backLink}>← Back to Shop</Link>
          <h1 className={styles.title}>Checkout</h1>
          <p className={styles.subtitle}>Complete your order</p>
        </div>

        <div className={styles.content}>
          {/* Checkout Form */}
          <div className={styles.formSection}>
            <form onSubmit={handlePlaceOrder}>
              {/* Contact Information */}
              <div className={styles.section}>
                <h2 className={styles.sectionTitle}>Contact Information</h2>
                <div className={styles.formGrid}>
                  <div className={`${styles.formGroup} ${styles.formGroupFull}`}>
                    <label className={styles.label}>Email Address</label>
                    <input
                      type="email"
                      className={styles.input}
                      placeholder="you@example.com"
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Shipping Address */}
              <div className={styles.section}>
                <h2 className={styles.sectionTitle}>Shipping Address</h2>
                <div className={styles.formGrid}>
                  <div className={`${styles.formGroup} ${styles.formGroupFull}`}>
                    <label className={styles.label}>Full Name</label>
                    <input
                      type="text"
                      className={styles.input}
                      placeholder="John Doe"
                      required
                    />
                  </div>
                  <div className={`${styles.formGroup} ${styles.formGroupFull}`}>
                    <label className={styles.label}>Street Address</label>
                    <input
                      type="text"
                      className={styles.input}
                      placeholder="123 Main Street"
                      required
                    />
                  </div>
                  <div className={styles.formGroup}>
                    <label className={styles.label}>City</label>
                    <input
                      type="text"
                      className={styles.input}
                      placeholder="New York"
                      required
                    />
                  </div>
                  <div className={styles.formGroup}>
                    <label className={styles.label}>State</label>
                    <input
                      type="text"
                      className={styles.input}
                      placeholder="NY"
                      required
                    />
                  </div>
                  <div className={styles.formGroup}>
                    <label className={styles.label}>ZIP Code</label>
                    <input
                      type="text"
                      className={styles.input}
                      placeholder="10001"
                      required
                    />
                  </div>
                  <div className={styles.formGroup}>
                    <label className={styles.label}>Phone</label>
                    <input
                      type="tel"
                      className={styles.input}
                      placeholder="(555) 123-4567"
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Payment Information */}
              <div className={styles.section}>
                <h2 className={styles.sectionTitle}>Payment Information</h2>
                <div className={styles.formGrid}>
                  <div className={`${styles.formGroup} ${styles.formGroupFull}`}>
                    <label className={styles.label}>Card Number</label>
                    <input
                      type="text"
                      className={styles.input}
                      placeholder="1234 5678 9012 3456"
                      required
                    />
                  </div>
                  <div className={styles.formGroup}>
                    <label className={styles.label}>Expiry Date</label>
                    <input
                      type="text"
                      className={styles.input}
                      placeholder="MM/YY"
                      required
                    />
                  </div>
                  <div className={styles.formGroup}>
                    <label className={styles.label}>CVV</label>
                    <input
                      type="text"
                      className={styles.input}
                      placeholder="123"
                      required
                    />
                  </div>
                  <div className={`${styles.formGroup} ${styles.formGroupFull}`}>
                    <label className={styles.label}>Name on Card</label>
                    <input
                      type="text"
                      className={styles.input}
                      placeholder="John Doe"
                      required
                    />
                  </div>
                </div>
              </div>

              <button type="submit" className={styles.checkoutButton}>
                Place Order • ${total.toLocaleString()}
              </button>

              <div className={styles.trustBadges}>
                <div className={styles.trustBadge}>🔒 Secure Checkout</div>
                <div className={styles.trustBadge}>✓ Free Shipping Over $500</div>
                <div className={styles.trustBadge}>↩️ 30-Day Returns</div>
              </div>
            </form>
          </div>

          {/* Order Summary */}
          <div className={styles.summaryCard}>
            <h2 className={styles.summaryTitle}>Order Summary</h2>

            <div className={styles.cartItems}>
              {cart.map(item => (
                <div key={item.id} className={styles.cartItem}>
                  <img src={item.image} alt={item.name} className={styles.itemImage} />
                  <div className={styles.itemDetails}>
                    <div className={styles.itemName}>{item.name}</div>
                    <div className={styles.itemMeta}>Qty: {item.quantity}</div>
                  </div>
                  <div className={styles.itemPrice}>
                    ${(item.price * item.quantity).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>

            <div className={styles.summaryRow}>
              <span className={styles.label}>Subtotal</span>
              <span className={styles.value}>${subtotal.toLocaleString()}</span>
            </div>
            <div className={styles.summaryRow}>
              <span className={styles.label}>Shipping</span>
              <span className={styles.value}>
                {shipping === 0 ? 'FREE' : `$${shipping.toLocaleString()}`}
              </span>
            </div>
            <div className={styles.summaryRow}>
              <span className={styles.label}>Tax (8%)</span>
              <span className={styles.value}>${tax.toFixed(2)}</span>
            </div>
            <div className={`${styles.summaryRow} ${styles.summaryRowTotal}`}>
              <span className={styles.label}>Total</span>
              <span className={styles.totalValue}>${total.toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;

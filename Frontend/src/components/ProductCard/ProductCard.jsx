import React from 'react';
import { useCart } from '../../context/CartContext';
import { useProductModal } from '../../context/ProductModalContext';
import { useToast } from '../../context/ToastContext';
import { trackProductClick } from '../../utils/userTracking';
import { formatPrice } from '../../utils/currency';
import styles from './ProductCard.module.css';


const ProductCard = ({ product, matchScore = null, matchReasons = [], hideFavorite = false, style }) => {
  const { addToCart } = useCart();
  const { openProductModal } = useProductModal();
  const { success } = useToast();

  // Validate product data
  if (!product || typeof product !== 'object' || !product.id || !product.name) {
    console.error('Invalid product data:', product);
    return null;
  }

  const handleCardClick = () => {
    trackProductClick(product);
    openProductModal(product);
  };

  const handleAddToCart = (e) => {
    e.stopPropagation();
    addToCart(product, 1);
    success(`${product.name} successfully added to cart!`);
  };

  const renderStars = (rating) => {
    // Validate rating to prevent invalid array lengths
    const validRating = typeof rating === 'number' && !isNaN(rating) && rating >= 0 && rating <= 5 ? rating : 0;
    const fullStars = Math.floor(validRating);
    const hasHalfStar = validRating % 1 >= 0.5;
    const emptyStars = Math.max(0, 5 - fullStars - (hasHalfStar ? 1 : 0));

    return (
      <>
        {Array(fullStars).fill('★').map((star, i) => (
          <span key={`full-${i}`}>{star}</span>
        ))}
        {hasHalfStar && <span key="half">½</span>}
        {Array(emptyStars).fill('☆').map((star, i) => (
          <span key={`empty-${i}`}>{star}</span>
        ))}
      </>
    );
  };

  return (
    <div className={styles.card} onClick={handleCardClick} style={style}>
      {/* Match Badge (for recommendations) */}
      {matchScore && (
        <div className={styles.matchBadge}>
          <span>✨</span>
          {matchScore}% match
        </div>
      )}

      {/* Image */}
      <div className={styles.imageWrapper}>
        <img src={product.image} alt={product.name} className={styles.image} loading="lazy" />

        {/* Wishlist Button (hide on Room page) */}
        {!hideFavorite && (
          <button
            className={styles.wishlistButton}
            onClick={e => e.stopPropagation()}
            aria-label="Add to wishlist"
          >
            <svg viewBox="0 0 24 24" strokeWidth="2">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
            </svg>
          </button>
        )}
      </div>

      {/* Content */}
      <div className={styles.content}>
        <div className={styles.category}>{product.category}</div>
        <h3 className={styles.name}>{product.name}</h3>

        {/* Rating */}
        <div className={styles.rating}>
          <div className={styles.stars}>{renderStars(product.rating)}</div>
          <span className={styles.reviewCount}>({product.reviewCount})</span>
        </div>

        {/* Styles */}
        {product.styles && product.styles.length > 0 && (
          <div className={styles.styleTags}>
            {product.styles.slice(0, 2).map((style, idx) => (
              <span key={idx} className={styles.styleTag}>{style}</span>
            ))}
          </div>
        )}

        {/* Match Reasons (for recommendations) */}
        {matchReasons.length > 0 && (
          <div className={styles.matchReasons}>
            {matchReasons.slice(0, 2).map((reason, i) => (
              <div key={i} className={styles.matchReason}>
                ✓ {reason}
              </div>
            ))}
          </div>
        )}

        {/* Footer */}
        <div className={styles.footer}>
          <div className={styles.priceSection}>
            {product.variants && product.variants.length > 1 ? (
              <>
                <div className={styles.priceLabel}>Starts from</div>
                <div className={styles.price}>{formatPrice(Math.min(...product.variants.map(v => v.price)), 'TND')}</div>
              </>
            ) : (
              <div className={styles.price}>{formatPrice(product.price, 'TND')}</div>
            )}
          </div>
          <button className={styles.addButton} onClick={handleAddToCart}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 5v14M5 12h14" />
            </svg>
            Add
          </button>
        </div>

        {/* Color Variants Indicator */}
        {product.variants && product.variants.length > 1 && (
          <div className={styles.colorIndicator}>
            <span className={styles.colorDots}>
              {product.variants.slice(0, 3).map((variant, idx) => (
                <span key={idx} className={styles.colorDot} title={variant.color}></span>
              ))}
            </span>
            <span className={styles.colorCount}>{product.variants.length} colors</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductCard;

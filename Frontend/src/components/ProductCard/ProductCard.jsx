import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../../context/CartContext';
import styles from './ProductCard.module.css';

const ProductCard = ({ product, matchScore = null, matchReasons = [] }) => {
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const [isWishlisted, setIsWishlisted] = useState(false);

  const handleCardClick = () => {
    navigate(`/product/${product.id}`);
  };

  const handleAddToCart = (e) => {
    e.stopPropagation();
    addToCart(product, 1);
  };

  const handleWishlist = (e) => {
    e.stopPropagation();
    setIsWishlisted(!isWishlisted);
  };

  const renderStars = (rating) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    return (
      <>
        {Array(fullStars).fill('★').map((star, i) => (
          <span key={`full-${i}`}>{star}</span>
        ))}
        {hasHalfStar && <span>½</span>}
        {Array(emptyStars).fill('☆').map((star, i) => (
          <span key={`empty-${i}`}>{star}</span>
        ))}
      </>
    );
  };

  return (
    <div className={styles.card} onClick={handleCardClick}>
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

        {/* Wishlist Button */}
        <button
          className={`${styles.wishlistButton} ${isWishlisted ? styles.active : ''}`}
          onClick={handleWishlist}
          aria-label="Add to wishlist"
        >
          <svg viewBox="0 0 24 24" strokeWidth="2">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
          </svg>
        </button>
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
          <div className={styles.price}>${product.price.toLocaleString()}</div>
          <button className={styles.addButton} onClick={handleAddToCart}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 5v14M5 12h14" />
            </svg>
            Add
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;

import React, { useState, useEffect } from 'react';
import { getRelatedProducts } from '../../data/products';
import { useCart } from '../../context/CartContext';
import { useRooms } from '../../context/RoomsContext';
import { getRecommendedProducts } from '../../utils/recommendations';
import { trackProductView } from '../../utils/userTracking';
import ProductCard from '../ProductCard/ProductCard';
import styles from './ProductDetailModal.module.css';

const ProductDetailModal = ({ product, isOpen, onClose }) => {
  const { addToCart } = useCart();
  const { getActiveRoom } = useRooms();
  const [quantity, setQuantity] = useState(1);
  const [selectedImage, setSelectedImage] = useState(0);
  const [isWishlisted, setIsWishlisted] = useState(false);

  const activeRoom = getActiveRoom();

  // Track product view when modal opens
  useEffect(() => {
    if (isOpen && product) {
      trackProductView(product);
    }
  }, [isOpen, product]);

  if (!product || !isOpen) return null;

  const relatedProducts = getRelatedProducts(product.id);

  // Get personalized recommendations for active room
  let recommendedProducts = [];
  if (activeRoom) {
    const recs = getRecommendedProducts(activeRoom, [product, ...relatedProducts], 5);
    recommendedProducts = recs.filter(p => p.id !== product.id).slice(0, 4);
  }

  const handleAddToCart = () => {
    addToCart(product, quantity);
  };

  const renderStars = (rating) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;

    return (
      <>
        {Array(fullStars).fill('★').map((star, i) => (
          <span key={`full-${i}`}>{star}</span>
        ))}
        {hasHalfStar && <span>½</span>}
        {Array(5 - fullStars - (hasHalfStar ? 1 : 0)).fill('☆').map((star, i) => (
          <span key={`empty-${i}`}>{star}</span>
        ))}
      </>
    );
  };

  const formatDimensions = (dimensions) => {
    if (!dimensions) return null;

    // Check for nested dimensions (e.g., nesting tables, storage sets)
    const nestedKeys = Object.keys(dimensions).filter(key =>
      typeof dimensions[key] === 'object' && !Array.isArray(dimensions[key])
    );

    if (nestedKeys.length > 0) {
      return nestedKeys.map(key => {
        const item = dimensions[key];
        const label = key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1');
        return (
          <div key={key} className={styles.nestedDimension}>
            <span className={styles.nestedLabel}>{label}:</span>
            <span className={styles.nestedValues}>
              {item.width && `${item.width}" W`}
              {item.width && (item.height || item.depth) && ' × '}
              {item.height && `${item.height}" H`}
              {(item.width || item.height) && item.depth && ' × '}
              {item.depth && `${item.depth}" D`}
              {item.diameter && !item.width && `${item.diameter}" diameter`}
              {item.diameter && (item.height || item.depth) && ' × '}
              {item.minHeight && item.maxHeight && `${item.minHeight}"-${item.maxHeight}" H`}
            </span>
          </div>
        );
      });
    }

    // Handle adjustable height items
    if (dimensions.minHeight && dimensions.maxHeight) {
      return (
        <>
          {dimensions.width && <span className={styles.dimensionItem}><strong>Width:</strong> {dimensions.width}"</span>}
          {dimensions.depth && <span className={styles.dimensionItem}><strong>Depth:</strong> {dimensions.depth}"</span>}
          {dimensions.seatHeight && <span className={styles.dimensionItem}><strong>Seat Height:</strong> {dimensions.seatHeight}"</span>}
          <span className={styles.dimensionItem}><strong>Height Range:</strong> {dimensions.minHeight}"-{dimensions.maxHeight}"</span>
        </>
      );
    }

    // Handle round items (tables, lamps)
    if (dimensions.diameter) {
      return (
        <>
          <span className={styles.dimensionItem}><strong>Diameter:</strong> {dimensions.diameter}"</span>
          {dimensions.height && <span className={styles.dimensionItem}><strong>Height:</strong> {dimensions.height}"</span>}
        </>
      );
    }

    // Handle standard dimensions (width, height, depth, seatHeight)
    return (
      <>
        {dimensions.width && <span className={styles.dimensionItem}><strong>Width:</strong> {dimensions.width}"</span>}
        {dimensions.height && <span className={styles.dimensionItem}><strong>Height:</strong> {dimensions.height}"</span>}
        {dimensions.depth && <span className={styles.dimensionItem}><strong>Depth:</strong> {dimensions.depth}"</span>}
        {dimensions.seatHeight && <span className={styles.dimensionItem}><strong>Seat Height:</strong> {dimensions.seatHeight}"</span>}
      </>
    );
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <button
          className={styles.closeButton}
          onClick={onClose}
          aria-label="Close"
        >
          <svg viewBox="0 0 24 24" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>

        <div className={styles.container}>
          {/* Breadcrumb */}
          <nav className={styles.breadcrumb}>
            <span className={styles.breadcrumbLink}>Shop</span>
            <span className={styles.breadcrumbSeparator}>/</span>
            <span>{product.category}</span>
          </nav>

          <div className={styles.contentLayout}>
            {/* Gallery */}
            <div className={styles.gallery}>
              <img
                src={product.images?.[selectedImage] || product.image}
                alt={product.name}
                className={styles.mainImage}
              />
              {product.images && product.images.length > 1 && (
                <div className={styles.thumbnails}>
                  {product.images.map((img, idx) => (
                    <img
                      key={idx}
                      src={img}
                      alt={`${product.name} view ${idx + 1}`}
                      className={`${styles.thumbnail} ${selectedImage === idx ? styles.active : ''}`}
                      onClick={() => setSelectedImage(idx)}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Details */}
            <div className={styles.details}>
              <div className={styles.category}>{product.category}</div>
              <h1 className={styles.title}>{product.name}</h1>

              <div className={styles.rating}>
                <div className={styles.stars}>{renderStars(product.rating)}</div>
                <span className={styles.ratingText}>
                  {product.rating} ({product.reviewCount} reviews)
                </span>
              </div>

              <div className={styles.price}>
                ${product.price.toLocaleString()}
              </div>

              <p className={styles.description}>
                {product.description}
              </p>

              {product.features && (
                <div className={styles.features}>
                  <h3 className={styles.featuresTitle}>Features</h3>
                  <div className={styles.featuresList}>
                    {product.features.map((feature, idx) => (
                      <div key={idx} className={styles.featureItem}>
                        {feature}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {product.dimensions && (
                <div className={styles.dimensions}>
                  <h3 className={styles.dimensionsTitle}>Dimensions</h3>
                  <div className={styles.dimensionsList}>
                    {formatDimensions(product.dimensions)}
                  </div>
                </div>
              )}

              <div className={styles.actions}>
                <div className={styles.quantitySelector}>
                  <button
                    className={styles.quantityButton}
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    aria-label="Decrease quantity"
                  >
                    −
                  </button>
                  <span className={styles.quantity}>{quantity}</span>
                  <button
                    className={styles.quantityButton}
                    onClick={() => setQuantity(quantity + 1)}
                    aria-label="Increase quantity"
                  >
                    +
                  </button>
                </div>

                <button className={styles.addToCartButton} onClick={handleAddToCart}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z" />
                    <path d="M3 6h18" />
                    <path d="M16 10a4 4 0 0 1-8 0" />
                  </svg>
                  Add to Cart
                </button>

                <button
                  className={`${styles.wishlistButton} ${isWishlisted ? styles.active : ''}`}
                  onClick={() => setIsWishlisted(!isWishlisted)}
                  aria-label="Add to wishlist"
                >
                  <svg viewBox="0 0 24 24" strokeWidth="2">
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          {/* Personalized Recommendations */}
          {recommendedProducts.length > 0 && (
            <div className={styles.recommendationsSection}>
              <h2 className={styles.sectionTitle}>
                ✨ Great for Your {activeRoom.name}
              </h2>
              <div className={styles.productsGrid}>
                {recommendedProducts.map((p) => (
                  <ProductCard
                    key={p.id}
                    product={p}
                    matchScore={p.matchScore}
                    matchReasons={p.matchReasons}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Related Products */}
          {relatedProducts.length > 0 && (
            <div className={styles.recommendationsSection}>
              <h2 className={styles.sectionTitle}>
                You Might Also Like
              </h2>
              <div className={styles.productsGrid}>
                {relatedProducts.slice(0, 4).map((p) => {
                  let matchScore = null;
                  let matchReasons = [];
                  if (activeRoom) {
                    const matchData = getRecommendedProducts(activeRoom, [p], 1)[0];
                    if (matchData && matchData.matchScore) {
                      matchScore = matchData.matchScore;
                      matchReasons = matchData.matchReasons || [];
                    }
                  }

                  return (
                    <ProductCard
                      key={p.id}
                      product={p}
                      matchScore={matchScore}
                      matchReasons={matchReasons}
                    />
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductDetailModal;

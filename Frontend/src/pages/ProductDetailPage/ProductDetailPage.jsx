import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useProducts } from '../../context/ProductsContext';
import { useCart } from '../../context/CartContext';
import { useRooms } from '../../context/RoomsContext';
import { getRecommendedProducts } from '../../utils/recommendations';
import { formatPrice } from '../../utils/currency';
import ProductCard from '../../components/ProductCard/ProductCard';
import styles from './ProductDetailPage.module.css';

const ProductDetailPage = () => {
  const { id } = useParams();
  const { addToCart } = useCart();
  const { getActiveRoom } = useRooms();
  const { getProductById, getRelatedProducts, loading, error } = useProducts();
  const [quantity, setQuantity] = useState(1);
  const [selectedImage, setSelectedImage] = useState(0);
  const [isWishlisted, setIsWishlisted] = useState(false);

  const product = getProductById(id);
  const activeRoom = getActiveRoom();

  if (loading) {
    return (
      <div className={styles.container}>
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <p>Loading product...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div style={{ textAlign: 'center', padding: '100px 0', color: 'red' }}>
          <p>Error loading product: {error}</p>
          <p>Please make sure the backend server is running at http://localhost:8000</p>
          <Link to="/shop">Back to Shop</Link>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className={styles.container}>
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <h2>Product not found</h2>
          <Link to="/shop">Back to Shop</Link>
        </div>
      </div>
    );
  }

  const relatedProducts = getRelatedProducts(product.id);

  // Get personalized recommendations for active room
  let recommendedProducts = [];
  if (activeRoom) {
    const recommendations = getRecommendedProducts(activeRoom, [product, ...relatedProducts], 5);
    recommendedProducts = recommendations.filter(p => p.id !== product.id).slice(0, 4);
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

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        {/* Breadcrumb */}
        <nav className={styles.breadcrumb}>
          <Link to="/" className={styles.breadcrumbLink}>Home</Link>
          <span className={styles.breadcrumbSeparator}>/</span>
          <Link to="/shop" className={styles.breadcrumbLink}>Shop</Link>
          <span className={styles.breadcrumbSeparator}>/</span>
          <span>{product.category}</span>
        </nav>

        <div className={styles.content}>
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
              {formatPrice(product.price, 'TND')}
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
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
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
              {recommendedProducts.map(p => (
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
              {relatedProducts.slice(0, 4).map(p => {
                // Add match data if active room exists
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
  );
};

export default ProductDetailPage;

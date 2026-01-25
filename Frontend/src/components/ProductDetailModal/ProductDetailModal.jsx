import React, { useState, useEffect } from 'react';
import { useProducts } from '../../context/ProductsContext';
import { useCart } from '../../context/CartContext';
import { useRooms } from '../../context/RoomsContext';
import { useToast } from '../../context/ToastContext';
import { getRecommendedProducts } from '../../utils/recommendations';
import { trackProductView } from '../../utils/userTracking';
import { fetchProductById } from '../../services/api';
import ProductCard from '../ProductCard/ProductCard';
import styles from './ProductDetailModal.module.css';

const ProductDetailModal = ({ product: productProp, isOpen, onClose }) => {
  const { addToCart } = useCart();
  const { rooms, getActiveRoom, addProductToRoom, removeProductFromRoom, isProductInRoom } = useRooms();
  const { success } = useToast();
  const { getRelatedProducts } = useProducts();
  const [quantity, setQuantity] = useState(1);
  const [selectedImage, setSelectedImage] = useState(0);
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [showRoomDropdown, setShowRoomDropdown] = useState(false);
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const activeRoom = getActiveRoom();

  // Fetch full product details from backend when modal opens
  useEffect(() => {
    const loadProduct = async () => {
      console.log('Modal opened with product:', productProp);
      if (!isOpen || !productProp?.id) {
        console.log('No product or modal closed');
        setProduct(null);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        console.log('Fetching product details for ID:', productProp.id);
        const productData = await fetchProductById(productProp.id);
        
        if (productData) {
          console.log('Product data loaded:', productData);
          setProduct(productData);
          trackProductView(productData);
        } else {
          console.log('Product not found');
          setError('Product not found');
        }
      } catch (err) {
        console.error('Error loading product details:', err);
        setError('Failed to load product details');
      } finally {
        setLoading(false);
      }
    };

    loadProduct();
  }, [isOpen, productProp?.id]);

  if (!isOpen) return null;

  // Show loading state
  if (loading) {
    return (
      <div className={styles.modalOverlay} onClick={onClose}>
        <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
          <button className={styles.closeButton} onClick={onClose} aria-label="Close">
            <svg viewBox="0 0 24 24" fill="none" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 6 6 18M6 6l12 12" />
            </svg>
          </button>
          <div style={{ textAlign: 'center', padding: '4rem 0' }}>
            <p>Loading product details...</p>
          </div>
        </div>
      </div>
    );
  }

  // Show error state
  if (error || !product) {
    return (
      <div className={styles.modalOverlay} onClick={onClose}>
        <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
          <button className={styles.closeButton} onClick={onClose} aria-label="Close">
            <svg viewBox="0 0 24 24" fill="none" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 6 6 18M6 6l12 12" />
            </svg>
          </button>
          <div style={{ textAlign: 'center', padding: '4rem 0' }}>
            <p>{error || 'Product not found'}</p>
          </div>
        </div>
      </div>
    );
  }

  let relatedProducts = [];
  let recommendedProducts = [];
  
  try {
    relatedProducts = getRelatedProducts(product.id) || [];

    // Get personalized recommendations for active room
    if (activeRoom) {
      const recs = getRecommendedProducts(activeRoom, [product, ...relatedProducts], 5);
      recommendedProducts = recs.filter(p => p.id !== product.id).slice(0, 4);
    }
  } catch (error) {
    console.error('Error getting recommendations:', error);
  }

  const handleAddToCart = () => {
    addToCart(product, quantity);
    success(`${quantity > 1 ? `${quantity}x ` : ''}${product.name} successfully added to cart!`);
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
      typeof dimensions[key] === 'object' && dimensions[key] !== null && !Array.isArray(dimensions[key])
    );

    if (nestedKeys.length > 0) {
      return nestedKeys.map(key => {
        const item = dimensions[key];
        if (!item) return null; // Skip null items
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
            <span>{product.category || 'All'}</span>
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
              {/* Modern, premium grouping: Add to Room at top, then title/price, then details */}
              <div className={styles.productHeaderGroup}>
                <div className={styles.category}>{product.category || 'Uncategorized'}</div>
                <h1 className={styles.title}>{product.name || 'Product'}</h1>
                <div className={styles.price}>${(product.price || 0).toLocaleString()}</div>
                <div className={styles.rating}>
                  <div className={styles.stars}>{renderStars(product.rating || 0)}</div>
                  <span className={styles.ratingText}>
                    {product.rating || 0} ({product.reviewCount || 0} reviews)
                  </span>
                </div>
              </div>
              {rooms.length > 0 && (
                <div className={styles.addToRoomSection}>
                  <div className={styles.addToRoomHeader}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                      <polyline points="9 22 9 12 15 12 15 22" />
                    </svg>
                    <span>Add to Room</span>
                  </div>
                  <div className={styles.roomDropdownWrapper}>
                    <button 
                      className={styles.roomDropdownToggle}
                      onClick={() => setShowRoomDropdown(!showRoomDropdown)}
                    >
                      <span>Select a room</span>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={showRoomDropdown ? styles.rotated : ''}>
                        <path d="M6 9l6 6 6-6" />
                      </svg>
                    </button>
                    {showRoomDropdown && (
                      <div className={styles.roomDropdown}>
                        {rooms.map(room => {
                          const isInRoom = isProductInRoom(room.id, product.id);
                          return (
                            <button
                              key={room.id}
                              className={`${styles.roomOption} ${isInRoom ? styles.roomOptionActive : ''}`}
                              onClick={() => {
                                if (isInRoom) {
                                  removeProductFromRoom(room.id, product.id);
                                } else {
                                  addProductToRoom(room.id, product.id);
                                }
                              }}
                            >
                              <span className={styles.roomOptionName}>{room.name}</span>
                              <span className={styles.roomOptionType}>{room.roomType}</span>
                              {isInRoom && (
                                <svg className={styles.checkIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                  <polyline points="20 6 9 17 4 12" />
                                </svg>
                              )}
                            </button>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </div>
              )}
              

              <div className={styles.divider} />

              <p className={styles.description}>{product.description || 'No description available.'}</p>

              {product.features && product.features.length > 0 && (
                <div className={styles.features}>
                  <h3 className={styles.featuresTitle}>Features</h3>
                  <div className={styles.featuresList}>
                    {product.features.map((feature, idx) => (
                      <div key={idx} className={styles.featureItem}>{feature}</div>
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

                {/* Wishlist button is now visually lighter and less prominent */}
                <button
                  className={`${styles.wishlistButton} ${isWishlisted ? styles.active : ''}`}
                  onClick={() => setIsWishlisted(!isWishlisted)}
                  aria-label="Add to wishlist"
                  style={{boxShadow: 'none', background: '#f5f3ef', border: '1px solid #eee', color: '#6B6B6B'}}
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

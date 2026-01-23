import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Pagination } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/pagination';
import { useRooms } from '../../context/RoomsContext';
import { PRODUCTS } from '../../data/products';
import ProductCard from '../../components/ProductCard/ProductCard';
import styles from './RoomDetailPage.module.css';

const RoomDetailPage = () => {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { getRoomById, removeProductFromRoom } = useRooms();
  const [activeCategory, setActiveCategory] = useState('all');

  const room = getRoomById(roomId);

  if (!room) {
    return (
      <motion.div
        className={styles.notFound}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className={styles.notFoundIcon}>
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
            <polyline points="9 22 9 12 15 12 15 22" />
          </svg>
        </div>
        <h2>Room Not Found</h2>
        <p>The room you're looking for doesn't exist or has been deleted.</p>
        <Link to="/profile" className={styles.primaryButton}>
          Back to Profile
        </Link>
      </motion.div>
    );
  }

  const roomProducts = PRODUCTS.filter(product => 
    room.products?.includes(product.id)
  );

  const productCategories = [...new Set(roomProducts.map(p => p.category))];

  const filteredProducts = activeCategory === 'all' 
    ? roomProducts 
    : roomProducts.filter(p => p.category === activeCategory);

  const handleRemoveProduct = (e, productId) => {
    e.stopPropagation();
    removeProductFromRoom(roomId, productId);
  };

  const formatDimensions = () => {
    if (!room.dimensions) return null;
    const { width, length, height, unit } = room.dimensions;
    const parts = [];
    if (width) parts.push(`${width}${unit}`);
    if (length) parts.push(`${length}${unit}`);
    if (height) parts.push(`${height}${unit}`);
    return parts.length > 0 ? parts.join(' × ') : null;
  };

  const totalValue = roomProducts.reduce((sum, p) => sum + p.price, 0);

  const getRoomIcon = (type) => {
    const icons = {
      'Living Room': (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M20 9V7a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v2" />
          <path d="M2 11v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6a2 2 0 0 0-4 0v2H6v-2a2 2 0 0 0-4 0z" />
          <path d="M4 19v2M20 19v2" />
        </svg>
      ),
      'Bedroom': (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M2 4v16M22 4v16M2 8h20M2 16h20" />
          <path d="M6 8v8M18 8v8" />
        </svg>
      ),
      'Office': (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="2" y="6" width="20" height="12" rx="2" />
          <path d="M12 18v4M8 22h8" />
          <path d="M6 10h.01M10 10h.01" />
        </svg>
      ),
      'Dining Room': (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M12 2v8M4.93 10.93l1.41 1.41M2 18h2M20 18h2M19.07 10.93l-1.41 1.41" />
          <path d="M6 18a6 6 0 0 1 12 0" />
          <path d="M12 18v4" />
        </svg>
      ),
    };
    return icons[type] || icons['Living Room'];
  };

  return (
    <div className={styles.page}>
      {/* Hero Section */}
      <motion.section
        className={styles.hero}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <div className={styles.heroOverlay} />
        <div className={styles.heroContent}>
          <motion.button 
            className={styles.backButton}
            onClick={() => navigate('/profile')}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Back to Profile
          </motion.button>

          <motion.div 
            className={styles.heroMain}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            <div className={styles.roomIcon}>
              {getRoomIcon(room.roomType)}
            </div>
            <h1 className={styles.roomTitle}>{room.name}</h1>
            <div className={styles.roomBadges}>
              {room.style && <span className={styles.badge}>{room.style}</span>}
              {formatDimensions() && (
                <span className={styles.badge}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                </svg>
                {formatDimensions()}
                </span>
            )}
            </div>
        </motion.div>
        </div>
    </motion.section>

      {/* Stats Bar */}
    <motion.section 
        className={styles.statsBar}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
    >
        <div className={styles.statsContainer}>
        <div className={styles.statItem}>
            <div className={styles.statIcon}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
            </svg>
            </div>
            <div className={styles.statContent}>
              <span className={styles.statValue}>{roomProducts.length}</span>
              <span className={styles.statLabel}>Items</span>
            </div>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.statItem}>
            <div className={styles.statIcon}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 6v6l4 2" />
              </svg>
            </div>
            <div className={styles.statContent}>
              <span className={styles.statValue}>{productCategories.length}</span>
              <span className={styles.statLabel}>Categories</span>
            </div>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.statItem}>
            <div className={styles.statIcon}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
              </svg>
            </div>
            <div className={styles.statContent}>
              <span className={styles.statValue}>${totalValue.toLocaleString()}</span>
              <span className={styles.statLabel}>Total Value</span>
            </div>
          </div>
        </div>
      </motion.section>

      {/* Main Content */}
      <main className={styles.mainContent}>
        {roomProducts.length === 0 ? (
          <motion.div 
            className={styles.emptyState}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5 }}
          >
            <div className={styles.emptyVisual}>
              <div className={styles.emptyIconWrapper}>
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
                </svg>
              </div>
              <div className={styles.emptyDots}>
                <span></span><span></span><span></span>
              </div>
            </div>
            <h3>Your room is empty</h3>
            <p>Start curating your perfect space by adding furniture from our collection</p>
            <Link to="/shop" className={styles.primaryButton}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="9" cy="21" r="1" />
                <circle cx="20" cy="21" r="1" />
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
              </svg>
              Browse Collection
            </Link>
          </motion.div>
        ) : (
          <>
            {/* Toolbar */}
            <motion.div 
              className={styles.toolbar}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <div className={styles.categoryFilters}>
                <button
                  className={`${styles.filterChip} ${activeCategory === 'all' ? styles.active : ''}`}
                  onClick={() => setActiveCategory('all')}
                >
                  All Items
                </button>
                {productCategories.map(cat => (
                  <button
                    key={cat}
                    className={`${styles.filterChip} ${activeCategory === cat ? styles.active : ''}`}
                    onClick={() => setActiveCategory(cat)}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </motion.div>

            {/* Products Display - Carousel */}
            <motion.div
              className={styles.carouselWrapper}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <Swiper
                modules={[Pagination]}
                spaceBetween={24}
                slidesPerView={1}
                speed={600}
                grabCursor={true}
                pagination={{ clickable: true, dynamicBullets: true }}
                breakpoints={{
                640: { slidesPerView: 2, spaceBetween: 20 },
                1024: { slidesPerView: 3, spaceBetween: 24 },
                1400: { slidesPerView: 4, spaceBetween: 24 },
                }}
                className={styles.productSwiper}
              >
                {filteredProducts.map((product) => (
                  <SwiperSlide key={product.id}>
                    <div className={styles.productCard}>
                      {/* ProductCard should not render favorite/heart button in this context */}
                      <ProductCard product={product} hideFavorite />
                      <button
                        className={styles.removeButton}
                        onClick={(e) => handleRemoveProduct(e, product.id)}
                        title="Remove from room"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M18 6L6 18M6 6l12 12"/>
                        </svg>
                      </button>
                    </div>
                  </SwiperSlide>
                ))}
              </Swiper>
            </motion.div>
          </>
        )}

        {/* Add More CTA */}
        <motion.section 
          className={styles.addMoreSection}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <div className={styles.addMoreContent}>
            <div className={styles.addMoreIcon}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 8v8M8 12h8" />
              </svg>
            </div>
            <div className={styles.addMoreText}>
              <h4>Discover More</h4>
              <p>Explore our curated collection and find the perfect pieces for your space</p>
            </div>
            <Link to="/shop" className={styles.secondaryButton}>
              Browse Shop
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </Link>
          </div>
        </motion.section>
      </main>
    </div>
  );
};

export default RoomDetailPage;

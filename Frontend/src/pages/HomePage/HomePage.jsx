import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Mousewheel, Navigation } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/navigation';
import { useRooms } from '../../context/RoomsContext';
import { useProducts } from '../../context/ProductsContext';
import { useDiscounts } from '../../context/DiscountContext';
import { CATEGORIES } from '../../data/products';
import { getRecommendedProducts } from '../../utils/recommendations';
import { getUserActivity, getRecentlyViewed } from '../../utils/userTracking';
import ProductCard from '../../components/ProductCard/ProductCard';
import styles from './HomePage.module.css';

const HomePage = () => {
  const { rooms, getActiveRoom } = useRooms();
  const { products, loading, error, getTrendingProducts } = useProducts();
  const { hasDiscount } = useDiscounts();
  const activeRoom = getActiveRoom();
  const [personalizedProducts, setPersonalizedProducts] = useState([]);

  // Get trending products
  const trendingProducts = getTrendingProducts().slice(0, 8);

  // Get discounted products
  const discountedProducts = products
    .filter(product => hasDiscount(product.id))
    .slice(0, 8);

  // Get personalized recommendations if user has rooms
  const recommendedProducts = activeRoom
    ? getRecommendedProducts(activeRoom, products, 8)
    : [];

  // Get personalized products based on browsing history
  useEffect(() => {
    const getPersonalizedProducts = () => {
      const activity = getUserActivity();
      const recentlyViewed = getRecentlyViewed(8);

      if (!recentlyViewed || recentlyViewed.length === 0) {
        return [];
      }

      // Get top categories from user activity
      const categoryCounts = {};
      [...(activity.productViews || []), ...(activity.productClicks || [])].forEach(event => {
        if (event.category) {
          categoryCounts[event.category] = (categoryCounts[event.category] || 0) + 1;
        }
      });

      // Get top 3 categories
      const topCategories = Object.entries(categoryCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3)
        .map(([cat]) => cat);

      if (topCategories.length === 0) return [];

      // Find products in those categories, excluding recently viewed
      const viewedIds = new Set(recentlyViewed.map(item => parseInt(item.productId)));
      const categoryProducts = products.filter(p =>
        topCategories.includes(p.category) &&
        !viewedIds.has(p.id)
      );

      // Return up to 8 products, shuffled for variety
      return categoryProducts
        .sort(() => Math.random() - 0.5)
        .slice(0, 8);
    };

    setPersonalizedProducts(getPersonalizedProducts());
  }, [products]);

  if (loading) {
    return (
      <div className={styles.page}>
        <div className={styles.container}>
          <div style={{ textAlign: 'center', padding: '4rem 0' }}>
            <p>Loading products...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.page}>
        <div className={styles.container}>
          <div style={{ textAlign: 'center', padding: '4rem 0', color: 'red' }}>
            <p>Error loading products: {error}</p>
            <p>Please make sure the backend server is running at http://localhost:8000</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      {/* Hero Section */}
      <motion.section
        className={styles.hero}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        <div className={styles.heroBackground} />
        <div className={styles.heroContent}>
          <motion.div
            className={styles.heroBadge}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            ✨ AI-Powered Furniture Discovery
          </motion.div>
          <motion.h1
            className={styles.heroTitle}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.8 }}
          >
            Find Your Perfect <span>Dream Space</span>
          </motion.h1>
          <motion.p
            className={styles.heroSubtitle}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.8 }}
          >
            Tell us about your style, space, and budget. Our AI will curate personalized
            furniture recommendations that match your unique aesthetic.
          </motion.p>
          <motion.div
            className={styles.heroButtons}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.6 }}
          >
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Link to="/shop" className={`${styles.heroButton} ${styles.heroButtonPrimary}`}>
                <span className={styles.buttonText}>Shop All Furniture</span>
                <svg className={styles.buttonIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </Link>
            </motion.div>
            {rooms.length === 0 && (
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Link to="/profile" className={`${styles.heroButton} ${styles.heroButtonSecondary}`}>
                  <span className={styles.buttonText}>Create Your Profile</span>
                  <svg className={styles.buttonIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </Link>
              </motion.div>
            )}
          </motion.div>
        </div>
      </motion.section>

      {/* Categories Section */}
      <section className={styles.container}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Shop by Category</h2>
          <p className={styles.sectionSubtitle}>
            Browse our curated collections
          </p>
        </div>
        <div className={styles.categoriesWrapper}>
          <Swiper
            modules={[Mousewheel, Navigation]}
            spaceBetween={20}
            slidesPerView="auto"
            freeMode={{
              enabled: true,
              momentum: true,
              momentumRatio: 0.8,
              momentumVelocityRatio: 0.8,
            }}
            speed={600}
            grabCursor={true}
            navigation={true}
            mousewheel={{
              forceToAxis: true,
              sensitivity: 1.2,
              releaseOnEdges: true,
            }}
            className={styles.categoriesSwiper}
          >
            {CATEGORIES.filter(cat => cat.id !== 'all').map((category, index) => {
              // Map category IDs to correct image filenames
              const imageMap = {
                'tv-media': 'tv_media'
              };
              const imageName = imageMap[category.id] || category.id;
              
              return (
                <SwiperSlide key={category.id} className={styles.categorySlide}>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05, duration: 0.4 }}
                  >
                    <Link
                      to={`/shop?category=${category.id}`}
                      className={styles.categoryItem}
                    >
                      <div className={styles.categoryImageWrapper}>
                        <img
                          src={`/images/categories/${imageName}.png`}
                          alt={category.name}
                          className={styles.categoryImage}
                          onError={(e) => {
                            // Fallback to a placeholder if image doesn't exist
                            e.target.style.display = 'none';
                            e.target.parentElement.innerHTML += `<div class="${styles.categoryImagePlaceholder}">${category.icon}</div>`;
                          }}
                        />
                      </div>
                      <h3 className={styles.categoryTitle}>{category.name}</h3>
                      <p className={styles.categoryItemCount}>
                        {products.filter(p => p.category.toLowerCase() === category.id).length} items
                      </p>
                    </Link>
                  </motion.div>
                </SwiperSlide>
              );
            })}
          </Swiper>
        </div>
      </section>

      {/* Personalized Recommendations */}
      {activeRoom && recommendedProducts.length > 0 && (
        <section className={styles.container}>
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>
              ✨ Recommended for Your {activeRoom.name}
            </h2>
            <p className={styles.sectionSubtitle}>
              Based on your style preferences and budget
            </p>
          </div>
          <div className={styles.productsGrid}>
            {recommendedProducts.map((product, index) => (
              <ProductCard
                key={product.id}
                product={product}
                matchScore={product.matchScore}
                matchReasons={product.matchReasons}
                style={{ animationDelay: `${index * 50}ms` }}
              />
            ))}
          </div>
          <Link to="/shop" className={styles.viewAllLink}>
            View All Recommendations →
          </Link>
        </section>
      )}

      {/* Recommended For You - Based on Browsing History */}
      {!activeRoom && personalizedProducts.length > 0 && (
        <section className={styles.container}>
          <div className={styles.sectionHeader}>
            <motion.div
              className={styles.recommendationBadge}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200, damping: 10 }}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
              </svg>
              Based on your interests
            </motion.div>
            <h2 className={styles.sectionTitle}>Recommended For You</h2>
            <p className={styles.sectionSubtitle}>
              Curated picks based on what you've been browsing
            </p>
          </div>
          <div className={styles.productsGrid}>
            {personalizedProducts.map((product, index) => (
              <ProductCard
                key={product.id}
                product={product}
                style={{ animationDelay: `${index * 50}ms` }}
              />
            ))}
          </div>
          <Link to="/shop" className={styles.viewAllLink}>
            Browse All Products →
          </Link>
        </section>
      )}

      {/* Trending Products */}
      <section className={styles.container}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Trending Now</h2>
          <p className={styles.sectionSubtitle}>
            Our most popular pieces this week
          </p>
        </div>
        <div className={styles.productsGrid}>
          {trendingProducts.map((product, index) => (
            <ProductCard
              key={product.id}
              product={product}
              style={{ animationDelay: `${index * 50}ms` }}
            />
          ))}
        </div>
        <Link to="/shop" className={styles.viewAllLink}>
          View All Products →
        </Link>
      </section>

      {/* Discounted Products */}
      {discountedProducts.length > 0 && (
        <section className={`${styles.container} ${styles.discountedSection}`}>
          <div className={styles.sectionHeader}>
            <motion.div
              className={styles.discountBadge}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200, damping: 10 }}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
                <line x1="7" y1="7" x2="7.01" y2="7" />
              </svg>
              Limited Time Offers
            </motion.div>
            <h2 className={styles.sectionTitle}>Special Discounts</h2>
            <p className={styles.sectionSubtitle}>
              Don't miss out on these amazing deals
            </p>
          </div>
          <div className={styles.productsGrid}>
            {discountedProducts.map((product, index) => (
              <ProductCard
                key={product.id}
                product={product}
                style={{ animationDelay: `${index * 50}ms` }}
              />
            ))}
          </div>
          <Link to="/shop?discount=true" className={styles.viewAllLink}>
            Shop All Discounts →
          </Link>
        </section>
      )}
    </div>
  );
};

export default HomePage;

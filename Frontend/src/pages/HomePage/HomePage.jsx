import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Pagination, Mousewheel, Navigation } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/pagination';
import 'swiper/css/navigation';
import { useRooms } from '../../context/RoomsContext';
import { PRODUCTS, CATEGORIES } from '../../data/products';
import { getRecommendedProducts, getTrendingProducts } from '../../utils/recommendations';
import ProductCard from '../../components/ProductCard/ProductCard';
import styles from './HomePage.module.css';

const HomePage = () => {
  const { rooms, getActiveRoom } = useRooms();
  const activeRoom = getActiveRoom();

  // Get trending products
  const trendingProducts = getTrendingProducts(PRODUCTS, 8);

  // Get personalized recommendations if user has rooms
  const recommendedProducts = activeRoom
    ? getRecommendedProducts(activeRoom, PRODUCTS, 8)
    : [];

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
            modules={[Pagination, Mousewheel, Navigation]}
            spaceBetween={24}
            slidesPerView={2}
            grabCursor={true}
            speed={400}
            loop={false}
            initialSlide={Math.floor(CATEGORIES.filter(cat => cat.id !== 'all').length / 2)}
            centeredSlides={true}
            slideToClickedSlide={true}
            resistanceRatio={0.85}
            navigation={true}
            mousewheel={{
              forceToAxis: true,
              sensitivity: 1,
              releaseOnEdges: false,
            }}
            breakpoints={{
              640: {
                slidesPerView: 3,
                spaceBetween: 20,
              },
              1024: {
                slidesPerView: 4,
                spaceBetween: 24,
              },
              1280: {
                slidesPerView: 5,
                spaceBetween: 24,
              },
            }}
            pagination={{ 
              clickable: true,
              dynamicBullets: true,
            }}
            className={styles.categoriesSwiper}
          >
            {CATEGORIES.filter(cat => cat.id !== 'all').map(category => (
              <SwiperSlide key={category.id}>
                <Link
                  to={`/shop?category=${category.id}`}
                  className={styles.categoryCard}
                >
                  <div className={styles.categoryIcon}>
                    {category.icon.startsWith('http') || category.icon.startsWith('/') ? (
                      <img src={category.icon} alt={category.name} />
                    ) : (
                      category.icon
                    )}
                  </div>
                  <div className={styles.categoryName}>{category.name}</div>
                  <div className={styles.categoryCount}>
                    {PRODUCTS.filter(p => p.category === category.name).length} items
                  </div>
                </Link>
              </SwiperSlide>
            ))}
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
    </div>
  );
};

export default HomePage;

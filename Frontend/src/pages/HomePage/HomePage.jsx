import React from 'react';
import { Link } from 'react-router-dom';
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
      <section className={styles.hero}>
        <div className={styles.heroBackground} />
        <div className={styles.heroContent}>
          <div className={styles.heroBadge}>✨ AI-Powered Furniture Discovery</div>
          <h1 className={styles.heroTitle}>
            Find Your Perfect <span>Dream Space</span>
          </h1>
          <p className={styles.heroSubtitle}>
            Tell us about your style, space, and budget. Our AI will curate personalized
            furniture recommendations that match your unique aesthetic.
          </p>
          <div className={styles.heroButtons}>
            <Link to="/shop" className={styles.heroButtonPrimary}>
              Shop All Furniture
            </Link>
            {rooms.length === 0 && (
              <Link to="/profile" className={styles.heroButtonSecondary}>
                Create Your Profile
              </Link>
            )}
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className={styles.container}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Shop by Category</h2>
          <p className={styles.sectionSubtitle}>
            Browse our curated collections
          </p>
        </div>
        <div className={styles.categories}>
          {CATEGORIES.filter(cat => cat.id !== 'all').map(category => (
            <Link
              key={category.id}
              to={`/shop?category=${category.id}`}
              className={styles.categoryCard}
            >
              <div className={styles.categoryIcon}>{category.icon}</div>
              <div className={styles.categoryName}>{category.name}</div>
              <div className={styles.categoryCount}>
                {PRODUCTS.filter(p => p.category === category.name).length} items
              </div>
            </Link>
          ))}
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
            {recommendedProducts.map(product => (
              <ProductCard
                key={product.id}
                product={product}
                matchScore={product.matchScore}
                matchReasons={product.matchReasons}
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
          {trendingProducts.map(product => (
            <ProductCard key={product.id} product={product} />
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

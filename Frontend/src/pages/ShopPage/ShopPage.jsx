import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { PRODUCTS, CATEGORIES } from '../../data/products';
import { getRecommendedProducts } from '../../utils/recommendations';
import { useRooms } from '../../context/RoomsContext';
import ProductCard from '../../components/ProductCard/ProductCard';
import styles from './ShopPage.module.css';

const ShopPage = () => {
  const [searchParams] = useSearchParams();
  const categoryParam = searchParams.get('category');
  const { rooms, getActiveRoom } = useRooms();
  const activeRoom = getActiveRoom();

  const [selectedCategories, setSelectedCategories] = useState([]);
  const [selectedStyles, setSelectedStyles] = useState([]);
  const [priceRange, setPriceRange] = useState({ min: '', max: '' });
  const [sortBy, setSortBy] = useState('featured');

  // Get all unique styles
  const allStyles = useMemo(() => {
    const styles = new Set();
    PRODUCTS.forEach(p => p.styles?.forEach(s => styles.add(s)));
    return Array.from(styles).sort();
  }, []);

  // Filter and sort products
  const filteredProducts = useMemo(() => {
    let products = [...PRODUCTS];

    // Filter by category
    if (categoryParam) {
      products = products.filter(
        p => p.category.toLowerCase() === categoryParam.toLowerCase()
      );
    }

    // Filter by selected categories
    if (selectedCategories.length > 0) {
      products = products.filter(p =>
        selectedCategories.includes(p.category.toLowerCase())
      );
    }

    // Filter by styles
    if (selectedStyles.length > 0) {
      products = products.filter(p =>
        p.styles?.some(s => selectedStyles.includes(s.toLowerCase()))
      );
    }

    // Filter by price range
    if (priceRange.min) {
      products = products.filter(p => p.price >= parseInt(priceRange.min));
    }
    if (priceRange.max) {
      products = products.filter(p => p.price <= parseInt(priceRange.max));
    }

    // Sort products
    switch (sortBy) {
      case 'price-low':
        products.sort((a, b) => a.price - b.price);
        break;
      case 'price-high':
        products.sort((a, b) => b.price - a.price);
        break;
      case 'rating':
        products.sort((a, b) => b.rating - a.rating);
        break;
      case 'featured':
      default:
        // Trending products first
        products.sort((a, b) => (b.trending ? 1 : 0) - (a.trending ? 1 : 0));
        break;
    }

    return products;
  }, [categoryParam, selectedCategories, selectedStyles, priceRange, sortBy]);

  // Toggle category filter
  const toggleCategory = (category) => {
    setSelectedCategories(prev =>
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  // Toggle style filter
  const toggleStyle = (style) => {
    setSelectedStyles(prev =>
      prev.includes(style)
        ? prev.filter(s => s !== style)
        : [...prev, style]
    );
  };

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        {/* Header */}
        <div className={styles.header}>
          <h1 className={styles.title}>
            {categoryParam
              ? CATEGORIES.find(c => c.id === categoryParam)?.name || 'All Products'
              : 'Shop All Furniture'}
          </h1>
          <p className={styles.subtitle}>
            {filteredProducts.length} products found
          </p>
        </div>

        <div className={styles.content}>
          {/* Sidebar Filters */}
          <aside className={styles.sidebar}>
            {/* Categories */}
            <div className={styles.filterGroup}>
              <h3 className={styles.filterTitle}>Categories</h3>
              <div className={styles.filterOptions}>
                {CATEGORIES.filter(c => c.id !== 'all').map(cat => (
                  <div
                    key={cat.id}
                    className={styles.filterOption}
                    onClick={() => toggleCategory(cat.id)}
                  >
                    <div
                      className={`${styles.filterCheckbox} ${
                        selectedCategories.includes(cat.id) ? styles.checked : ''
                      }`}
                    >
                      <svg viewBox="0 0 24 24" fill="none" strokeWidth="3">
                        <path d="M20 6 9 17l-5-5" />
                      </svg>
                    </div>
                    <span className={styles.filterLabel}>{cat.name}</span>
                    <span className={styles.filterCount}>
                      {PRODUCTS.filter(p => p.category === cat.name).length}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Styles */}
            <div className={styles.filterGroup}>
              <h3 className={styles.filterTitle}>Style</h3>
              <div className={styles.filterOptions}>
                {allStyles.map(style => (
                  <div
                    key={style}
                    className={styles.filterOption}
                    onClick={() => toggleStyle(style)}
                  >
                    <div
                      className={`${styles.filterCheckbox} ${
                        selectedStyles.includes(style.toLowerCase()) ? styles.checked : ''
                      }`}
                    >
                      <svg viewBox="0 0 24 24" fill="none" strokeWidth="3">
                        <path d="M20 6 9 17l-5-5" />
                      </svg>
                    </div>
                    <span className={styles.filterLabel}>{style}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Price Range */}
            <div className={styles.filterGroup}>
              <h3 className={styles.filterTitle}>Price Range</h3>
              <div className={styles.priceRange}>
                <input
                  type="number"
                  placeholder="Min"
                  className={styles.priceInput}
                  value={priceRange.min}
                  onChange={(e) => setPriceRange(prev => ({ ...prev, min: e.target.value }))}
                />
                <span className={styles.priceSeparator}>—</span>
                <input
                  type="number"
                  placeholder="Max"
                  className={styles.priceInput}
                  value={priceRange.max}
                  onChange={(e) => setPriceRange(prev => ({ ...prev, max: e.target.value }))}
                />
              </div>
            </div>
          </aside>

          {/* Products Grid */}
          <div>
            <div className={styles.resultsHeader}>
              <span className={styles.resultsCount}>
                Showing {filteredProducts.length} of {PRODUCTS.length} products
              </span>
              <select
                className={styles.sortSelect}
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="featured">Featured</option>
                <option value="price-low">Price: Low to High</option>
                <option value="price-high">Price: High to Low</option>
                <option value="rating">Highest Rated</option>
              </select>
            </div>

            {filteredProducts.length === 0 ? (
              <div className={styles.noResults}>
                <div className={styles.noResultsIcon}>🔍</div>
                <h3 className={styles.noResultsTitle}>No products found</h3>
                <p className={styles.noResultsText}>
                  Try adjusting your filters to see more results
                </p>
              </div>
            ) : (
              <div className={styles.productsGrid}>
                {filteredProducts.map(product => {
                  // Add match data if active room exists
                  let matchScore = null;
                  let matchReasons = [];
                  if (activeRoom) {
                    const matchData = getRecommendedProducts(activeRoom, [product], 1)[0];
                    if (matchData && matchData.matchScore) {
                      matchScore = matchData.matchScore;
                      matchReasons = matchData.matchReasons || [];
                    }
                  }

                  return (
                    <ProductCard
                      key={product.id}
                      product={product}
                      matchScore={matchScore}
                      matchReasons={matchReasons}
                    />
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShopPage;

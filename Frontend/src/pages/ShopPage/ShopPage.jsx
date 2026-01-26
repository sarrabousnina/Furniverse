import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useProducts } from '../../context/ProductsContext';
import { CATEGORIES } from '../../data/products';
import { getRecommendedProducts } from '../../utils/recommendations';
import { useRooms } from '../../context/RoomsContext';
import ProductCard from '../../components/ProductCard/ProductCard';
import styles from './ShopPage.module.css';

const ShopPage = () => {
  const [searchParams] = useSearchParams();
  const categoryParam = searchParams.get('category');
  const searchParam = searchParams.get('search');
  const { products, loading, error } = useProducts();
  const { rooms, getActiveRoom } = useRooms();
  const activeRoom = getActiveRoom();

  const [selectedCategories, setSelectedCategories] = useState([]);
  const [selectedStyles, setSelectedStyles] = useState([]);
  const [priceRange, setPriceRange] = useState({ min: '', max: '' });
  const [sortBy, setSortBy] = useState('featured');

  // Get all unique styles (split comma-separated and flatten)
  const allStyles = useMemo(() => {
    const styles = new Set();
    products.forEach(p => {
      if (p.styles && Array.isArray(p.styles)) {
        p.styles.forEach(s => {
          // Split by comma in case backend sends combined styles
          const individualStyles = s.split(',').map(style => style.trim()).filter(Boolean);
          individualStyles.forEach(style => styles.add(style));
        });
      }
    });
    return Array.from(styles).sort();
  }, [products]);

  // Filter and sort products
  const filteredProducts = useMemo(() => {
    let productsList = [...products];

    // Filter by search query
    if (searchParam) {
      const searchLower = searchParam.toLowerCase();
      productsList = productsList.filter(p =>
        p.name.toLowerCase().includes(searchLower) ||
        p.category.toLowerCase().includes(searchLower) ||
        p.description?.toLowerCase().includes(searchLower) ||
        p.tags?.some(tag => tag.toLowerCase().includes(searchLower))
      );
    }

    // Filter by category
    if (categoryParam) {
      productsList = productsList.filter(
        p => p.category.toLowerCase() === categoryParam.toLowerCase()
      );
    }

    // Filter by selected categories
    if (selectedCategories.length > 0) {
      productsList = productsList.filter(p =>
        selectedCategories.includes(p.category.toLowerCase())
      );
    }

    // Filter by styles (handle both array and comma-separated)
    if (selectedStyles.length > 0) {
      productsList = productsList.filter(p => {
        if (!p.styles || !Array.isArray(p.styles)) return false;
        // Flatten all product styles (split any comma-separated ones)
        const productStyles = p.styles.flatMap(s => 
          s.split(',').map(style => style.trim().toLowerCase())
        ).filter(Boolean);
        // Check if any selected style matches
        return selectedStyles.some(selected => productStyles.includes(selected.toLowerCase()));
      });
    }

    // Filter by price range
    const getMinPrice = (p) =>
      p.variants && p.variants.length > 0
        ? Math.min(...p.variants.map(v => v.price))
        : p.price;
    if (priceRange.min) {
      productsList = productsList.filter(p => getMinPrice(p) >= parseInt(priceRange.min));
    }
    if (priceRange.max) {
      productsList = productsList.filter(p => getMinPrice(p) <= parseInt(priceRange.max));
    }

    // Sort products
    switch (sortBy) {
      case 'price-low':
        productsList.sort((a, b) => a.price - b.price);
        break;
      case 'price-high':
        productsList.sort((a, b) => b.price - a.price);
        break;
      case 'rating':
        productsList.sort((a, b) => b.rating - a.rating);
        break;
      case 'featured':
      default:
        // Trending products first
        productsList.sort((a, b) => (b.trending ? 1 : 0) - (a.trending ? 1 : 0));
        break;
    }

    return productsList;
  }, [products, categoryParam, searchParam, selectedCategories, selectedStyles, priceRange, sortBy]);

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
    const styleLower = style.toLowerCase();
    setSelectedStyles(prev =>
      prev.includes(styleLower)
        ? prev.filter(s => s !== styleLower)
        : [...prev, styleLower]
    );
  };

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
      <div className={styles.container}>
        {/* Header */}
        <div className={styles.header}>
          <h1 className={styles.title}>
            {searchParam
              ? `Search results for "${searchParam}"`
              : categoryParam
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
                {/* All Categories Option */}
                <div
                  key="all"
                  className={styles.filterOption}
                  onClick={() => setSelectedCategories([])}
                >
                  <div
                    className={`${styles.filterCheckbox} ${selectedCategories.length === 0 ? styles.checked : ''}`}
                  >
                    <svg viewBox="0 0 24 24" fill="none" strokeWidth="3">
                      <path d="M20 6 9 17l-5-5" />
                    </svg>
                  </div>
                  <span className={styles.filterLabel}>All</span>
                  <span className={styles.filterCount}>{products.length}</span>
                </div>

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
                      {products.filter(p => p.category.toLowerCase() === cat.id).length}
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
                Showing {filteredProducts.length} of {products.length} products
              </span>
            </div>

            {filteredProducts.length === 0 ? (
              <div className={styles.noResults}>
                <div className={styles.noResultsIcon}>🔍</div>
                <h3 className={styles.noResultsTitle}>No products found</h3>
                <p className={styles.noResultsText}>
                  {searchParam
                    ? `No results found for "${searchParam}". Try different keywords or adjust your filters.`
                    : 'Try adjusting your filters to see more results'}
                </p>
              </div>
            ) : (
              <div className={styles.productsGrid}>
                {filteredProducts.map((product, index) => {
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
                      style={{ animationDelay: `${index * 50}ms` }}
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

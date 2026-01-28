import React, { useState } from 'react';
import { useProducts } from '../../context/ProductsContext';
import { useDiscounts } from '../../context/DiscountContext';
import { findInterestedUsers } from '../../services/api';
import AddProductModal from '../../components/AddProductModal/AddProductModal';
import styles from './AdminPage.module.css';

const AdminPage = () => {
  const { products, loading, error } = useProducts();
  const { applyDiscount, removeDiscount, hasDiscount, getDiscount, clearAllDiscounts } = useDiscounts();
  const [discountInput, setDiscountInput] = useState({});
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [isAddProductModalOpen, setIsAddProductModalOpen] = useState(false);
  const [interestedUsers, setInterestedUsers] = useState(null); // Product → User: users interested in current product
  const [loadingUsers, setLoadingUsers] = useState(false);

  const handleDiscountChange = (productId, value) => {
    setDiscountInput(prev => ({
      ...prev,
      [productId]: value
    }));
  };

  const handleApplyDiscount = async (productId) => {
    const discount = parseInt(discountInput[productId]);
    if (discount && discount > 0 && discount <= 100) {
      applyDiscount(productId, discount);

      // Product → User: Find users interested in this product
      const product = products.find(p => p.id === productId);
      if (product) {
        setLoadingUsers(true);
        try {
          const result = await findInterestedUsers(
            productId,
            product.name,
            product.category,
            10
          );
          setInterestedUsers({
            productId,
            productName: product.name,
            users: result.interested_users || [],
            total: result.total_count || 0
          });
        } catch (error) {
          console.error('Failed to find interested users:', error);
        } finally {
          setLoadingUsers(false);
        }
      }
    }
  };

  const handleRemoveDiscount = (productId) => {
    removeDiscount(productId);
    setDiscountInput(prev => {
      const newInput = { ...prev };
      delete newInput[productId];
      return newInput;
    });
  };

  const handleClearAll = () => {
    clearAllDiscounts();
    setShowClearConfirm(false);
    setDiscountInput({});
  };

  const handleViewInterestedUsers = async (productId) => {
    const product = products.find(p => p.id === productId);
    if (product) {
      setLoadingUsers(true);
      try {
        const result = await findInterestedUsers(
          productId,
          product.name,
          product.category,
          10
        );
        setInterestedUsers({
          productId,
          productName: product.name,
          users: result.interested_users || [],
          total: result.total_count || 0
        });
      } catch (error) {
        console.error('Failed to find interested users:', error);
      } finally {
        setLoadingUsers(false);
      }
    }
  };

  // Filter products based on search query and category
  const filteredProducts = products.filter(product => {
    const matchesSearch = searchQuery === '' ||
      product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      product.id.toString().includes(searchQuery);

    const matchesCategory = selectedCategory === 'All' ||
      product.category.toLowerCase() === selectedCategory.toLowerCase();

    return matchesSearch && matchesCategory;
  });

  // Get unique categories for filter dropdown
  const categories = ['All', ...Array.from(new Set(products.map(p => p.category))).sort()];

  if (loading) {
    return (
      <div className={styles.page}>
        <div className={styles.container}>
          <div className={styles.loading}>Loading products...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.page}>
        <div className={styles.container}>
          <div className={styles.error}>Error: {error}</div>
        </div>
      </div>
    );
  }

  const discountedCount = Object.keys(filteredProducts.reduce((acc, p) => {
    if (hasDiscount(p.id)) acc[p.id] = true;
    return acc;
  }, {})).length;

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        {/* Header */}
        <div className={styles.header}>
          <div>
            <h1 className={styles.title}>Discount Management</h1>
            <p className={styles.subtitle}>
              {searchQuery || selectedCategory !== 'All'
                ? `Showing ${filteredProducts.length} of ${products.length} products`
                : 'Manage product discounts for your store'}
            </p>
          </div>
          <div style={{ display: 'flex', gap: 'var(--spacing-md, 16px)' }}>
            <button
              className={styles.addButton}
              onClick={() => setIsAddProductModalOpen(true)}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 5v14M5 12h14" />
              </svg>
              Add Product
            </button>
            {discountedCount > 0 && (
              <button
                className={styles.clearAllButton}
                onClick={() => setShowClearConfirm(true)}
              >
                Clear All Discounts ({discountedCount})
              </button>
            )}
          </div>
        </div>

        {/* Clear Confirmation Modal */}
        {showClearConfirm && (
          <div className={styles.modalOverlay} onClick={() => setShowClearConfirm(false)}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
              <h2 className={styles.modalTitle}>Clear All Discounts?</h2>
              <p className={styles.modalText}>
                This will remove all {discountedCount} active discounts. This action cannot be undone.
              </p>
              <div className={styles.modalActions}>
                <button
                  className={styles.modalCancel}
                  onClick={() => setShowClearConfirm(false)}
                >
                  Cancel
                </button>
                <button
                  className={styles.modalConfirm}
                  onClick={handleClearAll}
                >
                  Clear All
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Interested Users Modal - Product → User Recommendation */}
        {interestedUsers && (
          <div className={styles.modalOverlay} onClick={() => setInterestedUsers(null)}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()} style={{ maxWidth: '600px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2 className={styles.modalTitle}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ width: '24px', height: '24px', verticalAlign: 'middle', marginRight: '8px' }}>
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                    <circle cx="9" cy="7" r="4" />
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                  </svg>
                  Users Interested in "{interestedUsers.productName}"
                </h2>
                <button
                  onClick={() => setInterestedUsers(null)}
                  style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', color: '#666' }}
                >
                  ✕
                </button>
              </div>

              <div className={styles.modalText} style={{ marginBottom: '20px' }}>
                Found <strong>{interestedUsers.total}</strong> users who might be interested in this discount based on their browsing history.
              </div>

              {loadingUsers ? (
                <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                  Finding interested users...
                </div>
              ) : interestedUsers.users.length > 0 ? (
                <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ borderBottom: '2px solid #eee' }}>
                        <th style={{ padding: '12px', textAlign: 'left' }}>User ID</th>
                        <th style={{ padding: '12px', textAlign: 'left' }}>Interest Score</th>
                        <th style={{ padding: '12px', textAlign: 'left' }}>Activity</th>
                        <th style={{ padding: '12px', textAlign: 'left' }}>Last Active</th>
                      </tr>
                    </thead>
                    <tbody>
                      {interestedUsers.users.map((user, index) => (
                        <tr key={index} style={{ borderBottom: '1px solid #f5f5f5' }}>
                          <td style={{ padding: '12px', fontFamily: 'monospace', fontSize: '0.9em' }}>
                            {user.user_id.substring(0, 20)}...
                          </td>
                          <td style={{ padding: '12px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <div style={{
                                width: '60px',
                                height: '8px',
                                background: '#e0e0e0',
                                borderRadius: '4px',
                                overflow: 'hidden'
                              }}>
                                <div style={{
                                  width: `${Math.round(user.similarity_score * 100)}%`,
                                  height: '100%',
                                  background: `linear-gradient(90deg, #1a9e9e 0%, #7dd3d3 100%)`
                                }} />
                              </div>
                              <span style={{ fontSize: '0.9em', fontWeight: 'bold' }}>
                                {Math.round(user.similarity_score * 100)}%
                              </span>
                            </div>
                          </td>
                          <td style={{ padding: '12px', fontSize: '0.9em' }}>
                            {user.activity_count} events
                          </td>
                          <td style={{ padding: '12px', fontSize: '0.85em', color: '#666' }}>
                            {user.last_active ? new Date(user.last_active).toLocaleDateString() : 'Unknown'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ width: '48px', height: '48px', marginBottom: '16px', opacity: 0.5 }}>
                    <circle cx="11" cy="11" r="8" />
                    <path d="m21 21-4.35-4.35" />
                  </svg>
                  <p>No users found yet. Start tracking user activity to see recommendations!</p>
                </div>
              )}

              <div className={styles.modalActions} style={{ marginTop: '20px', borderTop: '1px solid #eee', paddingTop: '20px' }}>
                <button
                  className={styles.modalCancel}
                  onClick={() => setInterestedUsers(null)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Search and Filter */}
        <div className={styles.searchFilterSection}>
          <div className={styles.searchBox}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
            </svg>
            <input
              type="text"
              placeholder="Search products by name or ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={styles.searchInput}
            />
            {searchQuery && (
              <button
                className={styles.clearSearch}
                onClick={() => setSearchQuery('')}
                aria-label="Clear search"
              >
                ✕
              </button>
            )}
          </div>
          <div className={styles.categoryFilter}>
            <label htmlFor="category-select">Category:</label>
            <select
              id="category-select"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className={styles.categorySelect}
            >
              {categories.map(category => (
                <option key={category} value={category}>
                  {category} ({category === 'All' ? products.length : products.filter(p => p.category === category).length})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Stats */}
        <div className={styles.stats}>
          <div className={styles.statCard}>
            <div className={styles.statLabel}>
              {searchQuery || selectedCategory !== 'All' ? 'Filtered Products' : 'Total Products'}
            </div>
            <div className={styles.statValue}>{filteredProducts.length}</div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statLabel}>Discounted Items</div>
            <div className={styles.statValue}>{discountedCount}</div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statLabel}>Regular Price</div>
            <div className={styles.statValue}>{filteredProducts.length - discountedCount}</div>
          </div>
        </div>

        {/* Products Table */}
        <div className={styles.tableContainer}>
          {filteredProducts.length === 0 ? (
            <div className={styles.noResults}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.35-4.35" />
              </svg>
              <h3>No products found</h3>
              <p>Try adjusting your search or category filter</p>
              {(searchQuery || selectedCategory !== 'All') && (
                <button
                  className={styles.resetFilters}
                  onClick={() => {
                    setSearchQuery('');
                    setSelectedCategory('All');
                  }}
                >
                  Clear Filters
                </button>
              )}
            </div>
          ) : (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Category</th>
                  <th>Original Price</th>
                  <th>Discount Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredProducts.map((product) => {
                  const discount = getDiscount(product.id);
                  const hasActiveDiscount = hasDiscount(product.id);

                  return (
                  <tr
                    key={product.id}
                    className={`${hasActiveDiscount ? styles.discountedRow : ''}`}
                  >
                    <td className={styles.productCell}>
                      <div className={styles.productInfo}>
                        <img
                          src={product.image}
                          alt={product.name}
                          className={styles.productImage}
                        />
                        <div className={styles.productDetails}>
                          <div className={styles.productName}>{product.name}</div>
                          <div className={styles.productId}>ID: {product.id}</div>
                        </div>
                      </div>
                    </td>
                    <td className={styles.categoryCell}>
                      <span className={styles.categoryBadge}>{product.category}</span>
                    </td>
                    <td className={styles.priceCell}>
                      <div className={styles.originalPrice}>
                        {product.price.toLocaleString()} TND
                      </div>
                      {hasActiveDiscount && (
                        <div className={styles.discountedPrice}>
                          {Math.round(product.price * (1 - discount / 100)).toLocaleString()} TND
                        </div>
                      )}
                    </td>
                    <td className={styles.statusCell}>
                      {hasActiveDiscount ? (
                        <span className={`${styles.badge} ${styles.activeBadge}`}>
                          -{discount}% OFF
                        </span>
                      ) : (
                        <span className={`${styles.badge} ${styles.inactiveBadge}`}>
                          No Discount
                        </span>
                      )}
                    </td>
                    <td className={styles.actionsCell}>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        {hasActiveDiscount ? (
                          <button
                            className={`${styles.actionButton} ${styles.removeButton}`}
                            onClick={() => handleRemoveDiscount(product.id)}
                          >
                            Remove Discount
                          </button>
                        ) : (
                          <div className={styles.discountControls}>
                            <input
                              type="number"
                              min="1"
                              max="100"
                              placeholder="%"
                              value={discountInput[product.id] || ''}
                              onChange={(e) => handleDiscountChange(product.id, e.target.value)}
                              className={styles.discountInput}
                            />
                            <button
                              className={`${styles.actionButton} ${styles.applyButton}`}
                              onClick={() => handleApplyDiscount(product.id)}
                              disabled={!discountInput[product.id]}
                            >
                              Apply
                            </button>
                          </div>
                        )}
                        <button
                          className={styles.viewUsersIconButton}
                          onClick={() => handleViewInterestedUsers(product.id)}
                          disabled={loadingUsers}
                          title="View Interested Users"
                          aria-label="View interested users"
                        >
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                            <circle cx="9" cy="7" r="4" />
                            <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          )}
        </div>

        {/* Info */}
        <div className={styles.info}>
          <p>💡 <strong>Note:</strong> Discounts are automatically saved and will persist after page refresh.</p>
        </div>

        {/* Add Product Modal */}
        <AddProductModal
          isOpen={isAddProductModalOpen}
          onClose={() => setIsAddProductModalOpen(false)}
        />
      </div>
    </div>
  );
};

export default AdminPage;

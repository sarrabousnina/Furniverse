import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProducts } from '../../context/ProductsContext';
import { useToast } from '../../context/ToastContext';
import { useCart } from '../../context/CartContext';
import styles from './RoomPlannerPage.module.css';

const RoomPlannerPage = () => {
  const navigate = useNavigate();
  const { products } = useProducts();
  const { success } = useToast();
  const { addToCart } = useCart();
  
  const [selectedTemplate, setSelectedTemplate] = useState('living-room');
  const [placedItems, setPlacedItems] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isDragging, setIsDragging] = useState(false);
  const [draggedProduct, setDraggedProduct] = useState(null);
  const canvasRef = useRef(null);

  // Room templates
  const templates = [
    { id: 'living-room', name: 'Living Room', icon: '🛋️', bg: '#F5E6D3' },
    { id: 'bedroom', name: 'Bedroom', icon: '🛏️', bg: '#E6F3F5' },
    { id: 'dining', name: 'Dining Room', icon: '🍽️', bg: '#F5E6E6' },
    { id: 'office', name: 'Home Office', icon: '💼', bg: '#E6F5E6' },
  ];

  const categories = [
    { id: 'all', name: 'All Products', icon: '📦' },
    { id: 'sofa', name: 'Sofas', icon: '🛋️' },
    { id: 'table', name: 'Tables', icon: '🍽️' },
    { id: 'chair', name: 'Chairs', icon: '🪑' },
    { id: 'bed', name: 'Beds', icon: '🛏️' },
    { id: 'storage', name: 'Storage', icon: '📦' },
    { id: 'lamp', name: 'Lamps', icon: '💡' },
  ];

  // Filter products by category
  const filteredProducts = selectedCategory === 'all' 
    ? products.slice(0, 50) 
    : products.filter(p => p.category.toLowerCase().includes(selectedCategory)).slice(0, 20);

  // Calculate total price
  const totalPrice = placedItems.reduce((sum, item) => sum + item.product.price, 0);

  // Handle drag start
  const handleDragStart = (e, product) => {
    setDraggedProduct(product);
    setIsDragging(true);
    e.dataTransfer.effectAllowed = 'copy';
  };

  // Handle drag over canvas
  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  };

  // Handle drop on canvas
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    if (!draggedProduct || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Add product to canvas
    const newItem = {
      id: Date.now(),
      product: draggedProduct,
      x: Math.max(0, Math.min(x - 50, rect.width - 100)),
      y: Math.max(0, Math.min(y - 50, rect.height - 100)),
      rotation: 0,
    };

    setPlacedItems([...placedItems, newItem]);
    setDraggedProduct(null);
    success(`${draggedProduct.name} added to your room!`);
  };

  // Remove item from canvas
  const removeItem = (id) => {
    setPlacedItems(placedItems.filter(item => item.id !== id));
  };

  // Clear all items
  const clearRoom = () => {
    setPlacedItems([]);
    success('Room cleared!');
  };

  // Save room design
  const saveRoom = () => {
    const roomData = {
      template: selectedTemplate,
      items: placedItems,
      totalPrice,
      createdAt: new Date().toISOString(),
    };
    
    // Save to localStorage
    const savedRooms = JSON.parse(localStorage.getItem('savedRooms') || '[]');
    savedRooms.push(roomData);
    localStorage.setItem('savedRooms', JSON.stringify(savedRooms));
    
    success('Room design saved! 🎉');
  };

  // Share room
  const shareRoom = () => {
    const shareText = `Check out my room design! 🏠\n${placedItems.length} items for ${totalPrice} TND`;
    
    if (navigator.share) {
      navigator.share({
        title: 'My Room Design',
        text: shareText,
      });
    } else {
      navigator.clipboard.writeText(shareText);
      success('Room details copied to clipboard! 📋');
    }
  };

  // Checkout with all room items
  const handleCheckout = () => {
    placedItems.forEach(item => {
      addToCart(item.product);
    });
    success(`Added ${placedItems.length} items to cart! 🛒`);
    navigate('/checkout');
  };

  const currentTemplate = templates.find(t => t.id === selectedTemplate);

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <button onClick={() => navigate(-1)} className={styles.backBtn}>
          ← Back
        </button>
        <h1 className={styles.title}>
          Virtual Room Planner
        </h1>
        <div className={styles.headerActions}>
          <button onClick={shareRoom} className={styles.shareBtn}>
            📤 Share
          </button>
          <button onClick={saveRoom} className={styles.saveBtn}>
            💾 Save Design
          </button>
        </div>
      </div>

      <div className={styles.mainContent}>
        {/* Sidebar - Product Palette */}
        <div className={styles.sidebar}>
          <div className={styles.sidebarHeader}>
            <h3>Product Palette</h3>
            <p>{filteredProducts.length} items</p>
          </div>

          {/* Category Filter */}
          <div className={styles.categoryFilter}>
            {categories.map(cat => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`${styles.categoryBtn} ${selectedCategory === cat.id ? styles.active : ''}`}
              >
                <span>{cat.icon}</span>
                <span>{cat.name}</span>
              </button>
            ))}
          </div>

          {/* Draggable Products */}
          <div className={styles.productList}>
            {filteredProducts.map(product => (
              <div
                key={product.id}
                draggable
                onDragStart={(e) => handleDragStart(e, product)}
                className={styles.productItem}
              >
                <img src={product.image} alt={product.name} />
                <div className={styles.productInfo}>
                  <h4>{product.name}</h4>
                  <p>{product.price} TND</p>
                </div>
                <div className={styles.dragHint}>⋮⋮</div>
              </div>
            ))}
          </div>
        </div>

        {/* Canvas Area */}
        <div className={styles.canvasArea}>
          {/* Room Template Selector */}
          <div className={styles.templateSelector}>
            {templates.map(template => (
              <button
                key={template.id}
                onClick={() => setSelectedTemplate(template.id)}
                className={`${styles.templateBtn} ${selectedTemplate === template.id ? styles.active : ''}`}
              >
                <span className={styles.templateIcon}>{template.icon}</span>
                <span>{template.name}</span>
              </button>
            ))}
          </div>

          {/* Canvas */}
          <div
            ref={canvasRef}
            className={styles.canvas}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            style={{ background: currentTemplate.bg }}
          >
            {placedItems.length === 0 && (
              <div className={styles.emptyState}>
                <div className={styles.emptyIcon}>🏠</div>
                <h3>Start Designing Your {currentTemplate.name}</h3>
                <p>Drag & drop products from the left to build your dream space</p>
              </div>
            )}

            {/* Placed Items */}
            {placedItems.map(item => (
              <div
                key={item.id}
                className={styles.placedItem}
                style={{
                  left: `${item.x}px`,
                  top: `${item.y}px`,
                  transform: `rotate(${item.rotation}deg)`,
                }}
              >
                <img src={item.product.image} alt={item.product.name} />
                <button
                  onClick={() => removeItem(item.id)}
                  className={styles.removeBtn}
                >
                  ✕
                </button>
                <div className={styles.itemLabel}>
                  {item.product.name.split(' ').slice(0, 2).join(' ')}
                </div>
              </div>
            ))}

            {/* Drag Overlay */}
            {isDragging && (
              <div className={styles.dragOverlay}>
                Drop here to add to your room
              </div>
            )}
          </div>

          {/* Room Summary */}
          <div className={styles.roomSummary}>
            <div className={styles.summarySection}>
              <h4>Room Summary</h4>
              <div className={styles.stats}>
                <div className={styles.stat}>
                  <span className={styles.statIcon}>🛋️</span>
                  <div>
                    <p className={styles.statValue}>{placedItems.length}</p>
                    <p className={styles.statLabel}>Items</p>
                  </div>
                </div>
                <div className={styles.stat}>
                  <span className={styles.statIcon}>💰</span>
                  <div>
                    <p className={styles.statValue}>{totalPrice} TND</p>
                    <p className={styles.statLabel}>Total Price</p>
                  </div>
                </div>
                <div className={styles.stat}>
                  <span className={styles.statIcon}>🏠</span>
                  <div>
                    <p className={styles.statValue}>{currentTemplate.name}</p>
                    <p className={styles.statLabel}>Template</p>
                  </div>
                </div>
              </div>
            </div>

            <div className={styles.actions}>
              <button onClick={clearRoom} className={styles.clearBtn} disabled={placedItems.length === 0}>
                🗑️ Clear Room
              </button>
              <button onClick={handleCheckout} className={styles.checkoutBtn} disabled={placedItems.length === 0}>
                🛒 Checkout ({totalPrice} TND)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RoomPlannerPage;

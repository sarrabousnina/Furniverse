import { useState, useCallback } from 'react';
import { useProducts } from '../../context/ProductsContext';
import styles from './RoomVisualizerModal.module.css';

const placementOptions = [
  "in the center of the room",
  "against the main wall",
  "near the window",
  "in the corner",
  "facing the entrance",
  "next to the existing furniture",
];

const RoomVisualizerModal = ({ isOpen, onClose }) => {
  const { products: allProducts } = useProducts();
  const [step, setStep] = useState('select-products'); // select-products, upload-room, place-items, generating, result
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [roomImage, setRoomImage] = useState(null);
  const [roomFile, setRoomFile] = useState(null);
  const [placementIndex, setPlacementIndex] = useState(0);
  const [placements, setPlacements] = useState({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [resultImage, setResultImage] = useState(null);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);
  const productsPerPage = 8;
  
  const totalPages = Math.ceil(allProducts.length / productsPerPage);
  const startIndex = currentPage * productsPerPage;
  const endIndex = startIndex + productsPerPage;
  const currentProducts = allProducts.slice(startIndex, endIndex);

  const resetState = useCallback(() => {
    setStep('select-products');
    setSelectedProducts([]);
    setRoomImage(null);
    setRoomFile(null);
    setPlacementIndex(0);
    setPlacements({});
    setIsGenerating(false);
    setResultImage(null);
    setError(null);
    setCurrentPage(0);
  }, []);

  const handleClose = () => {
    resetState();
    onClose();
  };

  const toggleProductSelection = (product) => {
    setSelectedProducts((prev) => {
      if (prev.find((p) => p.id === product.id)) {
        return prev.filter((p) => p.id !== product.id);
      }
      if (prev.length >= 4) {
        alert('You can select up to 4 products');
        return prev;
      }
      return [...prev, product];
    });
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      alert('Image must be less than 10MB');
      return;
    }

    setRoomFile(file);
    const reader = new FileReader();
    reader.onload = (event) => {
      setRoomImage(event.target?.result);
    };
    reader.readAsDataURL(file);
  };

  const handlePlacementSelect = (placement) => {
    const currentProduct = selectedProducts[placementIndex];
    setPlacements((prev) => ({
      ...prev,
      [currentProduct.id]: placement,
    }));

    if (placementIndex < selectedProducts.length - 1) {
      setPlacementIndex((prev) => prev + 1);
    } else {
      // All placements done, start generating
      generateVisualization();
    }
  };

  const generateVisualization = async () => {
    setStep('generating');
    setIsGenerating(true);
    setError(null);

    try {
      const apiUrl = window.location.hostname === 'localhost' 
        ? 'http://localhost:8000' 
        : `http://${window.location.hostname}:8000`;

      // First, upload the base64 room image to get a URL
      console.log('📤 Uploading room image...');
      const uploadResponse = await fetch(`${apiUrl}/upload-temp-image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: roomImage }),
      });

      if (!uploadResponse.ok) {
        throw new Error('Failed to upload room image');
      }

      const uploadData = await uploadResponse.json();
      const roomImageUrl = uploadData.url;
      console.log('✅ Room image uploaded:', roomImageUrl);
      
      // Prepare products with placements
      const productsWithPlacements = selectedProducts.map((p) => ({
        id: p.id,
        name: p.name,
        image: p.image,
        placement: placements[p.id] || 'in the room',
      }));

      console.log('🎨 Generating visualization...');
      const response = await fetch(`${apiUrl}/room-visualizer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          room_image_url: roomImageUrl,
          products: productsWithPlacements,
          aspect_ratio: 'auto',
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate visualization');
      }

      const data = await response.json();

      if (data.result_url) {
        setResultImage(data.result_url);
        setStep('result');
      } else if (data.error) {
        throw new Error(data.error);
      } else {
        throw new Error('No result received');
      }
    } catch (err) {
      console.error('Visualization error:', err);
      setError(err.message || 'Failed to generate visualization');
      setStep('place-items');
    } finally {
      setIsGenerating(false);
    }
  };

  if (!isOpen) return null;

  const renderStep = () => {
    switch (step) {
      case 'select-products':
        return (
          <div className={styles.stepContent}>
            <p className={styles.stepDescription}>
              Select up to 4 products you want to visualize in your room
            </p>
            <div className={styles.productGrid}>
              {currentProducts.map((product) => {
                const isSelected = selectedProducts.find((p) => p.id === product.id);
                return (
                  <button
                    key={product.id}
                    onClick={() => toggleProductSelection(product)}
                    className={`${styles.productCard} ${isSelected ? styles.selected : ''}`}
                  >
                    <div className={styles.productImage}>
                      <img src={product.image} alt={product.name} />
                    </div>
                    <div className={styles.productOverlay}>
                      <p className={styles.productName}>{product.name}</p>
                    </div>
                    {isSelected && (
                      <div className={styles.checkmark}>✓</div>
                    )}
                  </button>
                );
              })}
            </div>
            
            {/* Pagination */}
            {totalPages > 1 && (
              <div className={styles.pagination}>
                <button
                  onClick={() => setCurrentPage(prev => Math.max(0, prev - 1))}
                  disabled={currentPage === 0}
                  className={styles.paginationBtn}
                >
                  ← Previous
                </button>
                <span className={styles.pageInfo}>
                  Page {currentPage + 1} of {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(prev => Math.min(totalPages - 1, prev + 1))}
                  disabled={currentPage === totalPages - 1}
                  className={styles.paginationBtn}
                >
                  Next →
                </button>
              </div>
            )}
            
            <div className={styles.stepFooter}>
              <span className={styles.selectionCount}>
                {selectedProducts.length} of 4 products selected
              </span>
              <button
                onClick={() => setStep('upload-room')}
                disabled={selectedProducts.length === 0}
                className={styles.continueBtn}
              >
                Continue →
              </button>
            </div>
          </div>
        );

      case 'upload-room':
        return (
          <div className={styles.stepContent}>
            <p className={styles.stepDescription}>
              Upload a photo of your room where you want to place the furniture
            </p>
            {roomImage ? (
              <div className={styles.uploadedImage}>
                <img src={roomImage} alt="Your room" />
                <button
                  className={styles.removeImageBtn}
                  onClick={() => {
                    setRoomImage(null);
                    setRoomFile(null);
                  }}
                >
                  ✕
                </button>
              </div>
            ) : (
              <label className={styles.uploadArea}>
                <input
                  type="file"
                  accept="image/*"
                  capture="environment"
                  className={styles.fileInput}
                  onChange={handleFileUpload}
                />
                <div className={styles.uploadIcon}>📷</div>
                <span className={styles.uploadText}>
                  Tap to upload or take a photo
                </span>
                <span className={styles.uploadSubtext}>
                  JPEG, PNG, WebP up to 10MB
                </span>
              </label>
            )}
            <div className={styles.stepFooter}>
              <button
                className={styles.backBtn}
                onClick={() => setStep('select-products')}
              >
                ← Back
              </button>
              <button
                onClick={() => setStep('place-items')}
                disabled={!roomImage}
                className={styles.continueBtn}
              >
                Continue →
              </button>
            </div>
          </div>
        );

      case 'place-items':
        const currentProduct = selectedProducts[placementIndex];
        return (
          <div className={styles.stepContent}>
            <div className={styles.placementHeader}>
              <span className={styles.placementCounter}>
                📍 Placing item {placementIndex + 1} of {selectedProducts.length}
              </span>
            </div>
            <div className={styles.currentProduct}>
              <div className={styles.currentProductImage}>
                <img src={currentProduct.image} alt={currentProduct.name} />
              </div>
              <div>
                <h3>{currentProduct.name}</h3>
                <p>Where would you like to place this item?</p>
              </div>
            </div>
            <div className={styles.placementGrid}>
              {placementOptions.map((option) => (
                <button
                  key={option}
                  className={styles.placementOption}
                  onClick={() => handlePlacementSelect(option)}
                >
                  {option}
                </button>
              ))}
            </div>
            <div className={styles.stepFooter}>
              <button
                className={styles.backBtn}
                onClick={() => {
                  if (placementIndex > 0) {
                    setPlacementIndex((prev) => prev - 1);
                  } else {
                    setStep('upload-room');
                  }
                }}
              >
                ← Back
              </button>
            </div>
          </div>
        );

      case 'generating':
        return (
          <div className={styles.generatingContent}>
            <div className={styles.spinner}>
              <div className={styles.spinnerRing}></div>
              <div className={styles.spinnerIcon}>🪄</div>
            </div>
            <h3>Creating Your Vision</h3>
            <p>AI is placing furniture in your room...</p>
            <p className={styles.timeEstimate}>This usually takes 1-2 minutes</p>
          </div>
        );

      case 'result':
        return (
          <div className={styles.stepContent}>
            <div className={styles.resultHeader}>
              <span className={styles.resultTitle}>✨ Your Room Visualization</span>
            </div>
            {resultImage && (
              <div className={styles.resultImage}>
                <img src={resultImage} alt="Room visualization result" />
              </div>
            )}
            {error && (
              <div className={styles.errorMessage}>{error}</div>
            )}
            <div className={styles.resultFooter}>
              <button className={styles.tryAgainBtn} onClick={resetState}>
                Try Again
              </button>
              {resultImage && (
                <button
                  className={styles.downloadBtn}
                  onClick={() => window.open(resultImage, '_blank')}
                >
                  🖼️ Download
                </button>
              )}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className={styles.overlay} onClick={handleClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2>🪄 AI Room Visualizer</h2>
          <button className={styles.closeBtn} onClick={handleClose}>
            ✕
          </button>
        </div>
        <div className={styles.modalBody}>{renderStep()}</div>
      </div>
    </div>
  );
};

export default RoomVisualizerModal;

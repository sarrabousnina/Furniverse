import { useEffect, useState, useRef } from 'react';
import styles from './ARViewer.module.css';

const ARViewer = ({ product, onClose, customModelUrl }) => {
  const [isMobile, setIsMobile] = useState(false);
  const [scriptLoaded, setScriptLoaded] = useState(false);
  const [modelLoaded, setModelLoaded] = useState(false);
  const modelViewerRef = useRef(null);

  useEffect(() => {
    // Check if script already exists
    const existingScript = document.querySelector('script[src*="model-viewer"]');
    if (existingScript) {
      setScriptLoaded(true);
      return;
    }

    const script = document.createElement('script');
    script.type = 'module';
    script.src = 'https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js';
    script.onload = () => {
      console.log('✅ Model-viewer script loaded');
      setScriptLoaded(true);
    };
    document.head.appendChild(script);

    // Detect if device is mobile
    const checkMobile = () => {
      return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    };
    setIsMobile(checkMobile());

    return () => {
      // Don't remove script - keep it for reuse
    };
  }, []);

  // Convert localhost to network IP ONLY if current page is already on network IP
  let modelUrl = customModelUrl;
  const isOnNetworkIP = window.location.hostname !== 'localhost';
  
  if (modelUrl && modelUrl.includes('localhost') && isOnNetworkIP) {
    // Only convert if we're accessing the frontend via network IP
    modelUrl = modelUrl.replace('localhost', window.location.hostname);
    console.log('🔧 Converted localhost to network IP:', modelUrl);
  }

  console.log('🎨 ARViewer - customModelUrl:', customModelUrl);
  console.log('🎨 ARViewer - Final modelUrl:', modelUrl);
  console.log('🎨 Script loaded:', scriptLoaded);
  console.log('🎨 Current hostname:', window.location.hostname);

  // Monitor model loading
  useEffect(() => {
    const viewer = modelViewerRef.current;
    if (!viewer || !scriptLoaded) return;

    const handleLoad = () => {
      console.log('✅ Model loaded successfully!');
      setModelLoaded(true);
    };

    const handleError = (e) => {
      console.error('❌ Model loading error:', e);
      setModelLoaded(false);
    };

    const handleProgress = (e) => {
      if (e.detail && e.detail.totalProgress !== undefined) {
        console.log('📊 Loading progress:', Math.round(e.detail.totalProgress * 100) + '%');
      }
    };

    viewer.addEventListener('load', handleLoad);
    viewer.addEventListener('error', handleError);
    viewer.addEventListener('progress', handleProgress);

    // Timeout check
    const timeout = setTimeout(() => {
      if (!modelLoaded) {
        console.warn('⚠️ Model loading timeout after 30 seconds');
      }
    }, 30000);

    return () => {
      viewer.removeEventListener('load', handleLoad);
      viewer.removeEventListener('error', handleError);
      viewer.removeEventListener('progress', handleProgress);
      clearTimeout(timeout);
    };
  }, [scriptLoaded, modelUrl]);

  // Test if file is accessible
  useEffect(() => {
    if (modelUrl) {
      console.log('🧪 Testing file access:', modelUrl);
      fetch(modelUrl, { method: 'HEAD' })
        .then(res => {
          console.log('🧪 File test response:', res.status, res.statusText);
          console.log('🧪 Content-Type:', res.headers.get('content-type'));
          console.log('🧪 Content-Length:', res.headers.get('content-length'));
        })
        .catch(err => console.error('🧪 File test error:', err));
    }
  }, [modelUrl]);

  if (!customModelUrl) {
    return (
      <div className={styles.overlay} onClick={onClose}>
        <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
          <button className={styles.closeBtn} onClick={onClose}>✕</button>
          <div style={{ padding: '4rem', textAlign: 'center' }}>
            <h3 style={{ marginBottom: '1rem' }}>No 3D Model Available</h3>
            <p>Generate a 3D model first to view it in AR</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeBtn} onClick={onClose}>✕</button>
        
        <div className={styles.header}>
          <h2>{product.name}</h2>
          <p className={styles.price}>{product.price} TND</p>
        </div>

        <div className={styles.viewerContainer}>
          {!scriptLoaded && (
            <div style={{ 
              position: 'absolute', 
              inset: 0, 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              background: '#f5f5f5'
            }}>
              <p>Loading 3D viewer...</p>
            </div>
          )}
          
          {scriptLoaded && !modelLoaded && (
            <div style={{ 
              position: 'absolute', 
              inset: 0, 
              display: 'flex', 
              flexDirection: 'column',
              alignItems: 'center', 
              justifyContent: 'center',
              background: '#f5f5f5',
              zIndex: 10
            }}>
              <div className={styles.spinner}></div>
              <p style={{ marginTop: '1rem' }}>Loading 3D model...</p>
              <p style={{ fontSize: '0.875rem', color: '#666', marginTop: '0.5rem' }}>
                {(12 / 1024).toFixed(1)}MB - This may take a few seconds
              </p>
            </div>
          )}

          <model-viewer
            ref={modelViewerRef}
            key={modelUrl}
            src={modelUrl}
            alt={product.name}
            ar
            ar-modes="webxr scene-viewer quick-look"
            camera-controls
            touch-action="pan-y"
            auto-rotate
            shadow-intensity="1"
            environment-image="neutral"
            exposure="1"
            className={styles.modelViewer}
            style={{ width: '100%', height: '100%' }}
            onLoad={() => {
              console.log('✅ Model loaded successfully!');
              setModelLoaded(true);
            }}
            onError={(e) => {
              console.error('❌ Model loading error:', e);
              alert('Failed to load 3D model. Please try refreshing.');
            }}
          >
            <div className={styles.arPrompt}>
              <div className={styles.arIcon}>{isMobile ? '📱' : '🖥️'}</div>
              <h3>{isMobile ? 'View in Your Space' : '3D Model Viewer'}</h3>
              <p>{isMobile ? 'Tap the AR button to see this furniture in your room using your camera' : 'Rotate and zoom with your mouse. Use AR on mobile for real-world placement'}</p>
              
              <button 
                slot="ar-button" 
                className={styles.arButton}
              >
                📷 View in AR
              </button>
            </div>

            <div className={styles.controls}>
              <div className={styles.hint}>
                <span>💡</span>
                <p>Drag to rotate • Pinch to zoom • On mobile: tap AR button</p>
              </div>
            </div>

            <div className={styles.loading} slot="poster">
              <div className={styles.spinner}></div>
              <p>Loading 3D model...</p>
            </div>
          </model-viewer>
        </div>

        <div className={styles.info}>
          <div className={styles.feature}>
            <span className={styles.featureIcon}>✨</span>
            <div>
              <h4>Augmented Reality</h4>
              <p>See how this furniture looks in your actual room</p>
            </div>
          </div>
          <div className={styles.feature}>
            <span className={styles.featureIcon}>📏</span>
            <div>
              <h4>True to Scale</h4>
              <p>View actual size: {product.dimensions?.width}"W × {product.dimensions?.depth}"D × {product.dimensions?.height}"H</p>
            </div>
          </div>
          <div className={styles.feature}>
            <span className={styles.featureIcon}>🔄</span>
            <div>
              <h4>360° View</h4>
              <p>Rotate and zoom to see every angle</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ARViewer;

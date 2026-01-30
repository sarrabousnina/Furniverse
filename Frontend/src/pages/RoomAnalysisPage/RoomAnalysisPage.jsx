import React, { useState } from 'react';
import styles from './RoomAnalysisPage.module.css';

const RoomAnalysisPage = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleImageSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = (e) => setImagePreview(e.target.result);
      reader.readAsDataURL(file);
      setAnalysis(null);
      setError(null);
    }
  };

  const analyzeRoom = async () => {
    if (!selectedImage) return;

    setLoading(true);
    setError(null);

    try {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const base64Image = e.target.result;
        
        const response = await fetch('http://localhost:8000/analyze/room', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            image: base64Image
          })
        });

        if (!response.ok) {
          throw new Error('Analysis failed');
        }

        const result = await response.json();
        setAnalysis(result);
      };
      reader.readAsDataURL(selectedImage);
    } catch (err) {
      setError('Failed to analyze room. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>🏠 Room Analysis</h1>
        <p>Upload a photo of your room to discover its style and detected furniture</p>
      </div>

      <div className={styles.uploadSection}>
        <input
          type="file"
          accept="image/*"
          onChange={handleImageSelect}
          className={styles.fileInput}
          id="room-image"
        />
        <label htmlFor="room-image" className={styles.uploadButton}>
          📷 Choose Room Photo
        </label>
      </div>

      {imagePreview && (
        <div className={styles.previewSection}>
          <img src={imagePreview} alt="Room preview" className={styles.preview} />
          <button 
            onClick={analyzeRoom} 
            disabled={loading}
            className={styles.analyzeButton}
          >
            {loading ? '🔍 Analyzing...' : '✨ Analyze Room'}
          </button>
        </div>
      )}

      {error && (
        <div className={styles.error}>
          ❌ {error}
        </div>
      )}

      {analysis && (
        <div className={styles.results}>
          <div className={styles.styleResult}>
            <h2>🎨 Room Style</h2>
            <div className={styles.styleCard}>
              <span className={styles.styleName}>{analysis.room_style}</span>
              <span className={styles.confidence}>
                {Math.round(analysis.style_confidence * 100)}% confidence
              </span>
            </div>
          </div>

          <div className={styles.furnitureResult}>
            <h2>🪑 Detected Furniture</h2>
            <div className={styles.furnitureGrid}>
              {analysis.detected_furniture.map((item, index) => (
                <div key={index} className={styles.furnitureCard}>
                  <div className={styles.furnitureType}>{item.class}</div>
                  <div className={styles.furnitureDetails}>
                    <span>Confidence: {Math.round(item.confidence * 100)}%</span>
                    {item.matched_product && (
                      <span>Similar to: {item.matched_product}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoomAnalysisPage;
import React, { useState, useEffect } from 'react';
import styles from './RoomForm.module.css';

const STYLE_OPTIONS = [
  'Modern',
  'Scandinavian',
  'Industrial',
  'Bohemian',
  'Minimalist',
  'Mid-Century',
  'Rustic',
  'Glam'
];

const ROOM_TYPES = [
  'Living Room',
  'Bedroom',
  'Dining Room',
  'Office',
  'Kitchen',
  'Bathroom'
];

const RoomForm = ({ onSubmit, onCancel, initialData = null }) => {
  const [formData, setFormData] = useState({
    name: '',
    budgetMin: '',
    budgetMax: '',
    dimensions: {
      width: '',
      length: '',
      height: '',
      unit: 'cm'
    },
    styles: [],
    image: null
  });
  const [imagePreview, setImagePreview] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
      if (initialData.image) {
        setImagePreview(initialData.image);
      }
    }
  }, [initialData]);

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please upload an image file');
        return;
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('Image size must be less than 5MB');
        return;
      }

      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
        setFormData(prev => ({
          ...prev,
          image: reader.result
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveImage = () => {
    setImagePreview(null);
    setFormData(prev => ({
      ...prev,
      image: null
    }));
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleDimensionChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      dimensions: {
        ...prev.dimensions,
        [name]: value
      }
    }));
  };

  const handleUnitToggle = (unit) => {
    setFormData(prev => ({
      ...prev,
      dimensions: {
        ...prev.dimensions,
        unit
      }
    }));
  };

  const toggleStyle = (style) => {
    setFormData(prev => ({
      ...prev,
      styles: prev.styles.includes(style)
        ? prev.styles.filter(s => s !== style)
        : [...prev.styles, style]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate required fields
    if (!formData.name.trim()) {
      alert('Please select a room type');
      return;
    }

    // Build room data
    let roomData = {
      ...formData,
      budgetMin: formData.budgetMin ? parseInt(formData.budgetMin) : null,
      budgetMax: formData.budgetMax ? parseInt(formData.budgetMax) : null,
      dimensions: {
        width: formData.dimensions.width ? parseFloat(formData.dimensions.width) : null,
        length: formData.dimensions.length ? parseFloat(formData.dimensions.length) : null,
        height: formData.dimensions.height ? parseFloat(formData.dimensions.height) : null,
        unit: formData.dimensions.unit
      }
    };

    // If image exists, analyze room first before submitting
    if (imagePreview) {
      setIsAnalyzing(true);
      try {
        const response = await fetch('http://localhost:8000/analyze/room', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            image: imagePreview,
            room_type: formData.name,
            budget_min: formData.budgetMin ? parseInt(formData.budgetMin) : null,
            budget_max: formData.budgetMax ? parseInt(formData.budgetMax) : null,
            existing_furniture: ""
          })
        });

        if (response.ok) {
          const analysisResults = await response.json();
          console.log('Analysis Results:', analysisResults);
          
          // Merge analysis results with room data
          roomData = {
            ...roomData,
            analysisResults: analysisResults,
            detectedFurniture: analysisResults.detected_furniture,
            detectedStyle: analysisResults.room_style,
            styleConfidence: analysisResults.style_confidence,
            roomType: analysisResults.room_type,
            missingFurniture: analysisResults.missing_furniture,
            recommendations: analysisResults.recommendations,
            analysisSummary: analysisResults.analysis_summary
          };
        } else {
          console.error('Analysis response not ok:', response.status, response.statusText);
          const errorText = await response.text();
          console.error('Error details:', errorText);
        }
      } catch (error) {
        console.error('Room analysis failed:', error);
        // Continue with submission even if analysis fails
      } finally {
        setIsAnalyzing(false);
      }
    }

    onSubmit(roomData);
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className={styles.formHeader}>
        <h2 className={styles.formTitle}>
          {initialData ? 'Edit Room' : 'Create New Room'}
        </h2>
        <p className={styles.formSubtitle}>
          {initialData
            ? 'Update your room preferences'
            : 'Tell us about your space and style preferences'}
        </p>
      </div>

      {/* Room Type */}
      <div className={styles.formGroup}>
        <label className={styles.label}>
          Room Type
        </label>
        <select
          name="name"
          value={formData.name}
          onChange={handleChange}
          className={styles.input}
          required
        >
          <option value="">Select room type</option>
          {ROOM_TYPES.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>

      {/* Room Image */}
      <div className={styles.formGroup}>
        <label className={styles.label}>
          <span className={styles.labelText}>
            Room Image
            <span className={styles.labelHint}>Optional - Upload to get AI recommendations</span>
          </span>
        </label>
        <div className={styles.imageUpload}>
          {imagePreview ? (
            <div className={styles.imagePreview}>
              <img src={imagePreview} alt="Room preview" className={styles.previewImage} />
              <button
                type="button"
                className={styles.removeImageButton}
                onClick={handleRemoveImage}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M6 18L18 6M6 6l12 12" />
                </svg>
                Remove
              </button>
            </div>
          ) : (
            <div className={styles.uploadArea}>
              <input
                type="file"
                id="roomImage"
                accept="image/*"
                onChange={handleImageUpload}
                className={styles.fileInput}
              />
              <label htmlFor="roomImage" className={styles.uploadLabel}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <path d="M21 15l-5-5L5 21" />
                </svg>
                <span>Click to upload room image</span>
                <span className={styles.uploadHint}>JPG, PNG or GIF (max 5MB)</span>
              </label>
            </div>
          )}
        </div>
      </div>

      {/* Budget Range */}
      <div className={styles.formGroup}>
        <label className={styles.label}>
          <span className={styles.labelText}>
            Budget Range (per item)
            <span className={styles.labelHint}>Optional</span>
          </span>
        </label>
        <div className={styles.budgetContainer}>
          <div className={styles.budgetInput}>
            <input
              type="number"
              name="budgetMin"
              value={formData.budgetMin}
              onChange={handleChange}
              className={styles.input}
              placeholder="Min"
              min="0"
            />
          </div>
          <span className={styles.budgetSeparator}>to</span>
          <div className={styles.budgetInput}>
            <input
              type="number"
              name="budgetMax"
              value={formData.budgetMax}
              onChange={handleChange}
              className={styles.input}
              placeholder="Max"
              min="0"
            />
          </div>
        </div>
      </div>

      {/* Room Dimensions */}
      <div className={styles.formGroup}>
        <label className={styles.label}>
          <span className={styles.labelText}>
            Room Dimensions
          </span>
        </label>
        
        {/* Unit Toggle */}
        <div className={styles.unitToggle}>
          <button
            type="button"
            className={`${styles.unitButton} ${formData.dimensions.unit === 'cm' ? styles.active : ''}`}
            onClick={() => handleUnitToggle('cm')}
          >
            cm
          </button>
          <button
            type="button"
            className={`${styles.unitButton} ${formData.dimensions.unit === 'inches' ? styles.active : ''}`}
            onClick={() => handleUnitToggle('inches')}
          >
            inches
          </button>
        </div>

        {/* Dimension Inputs */}
        <div className={styles.dimensionsContainer}>
          <div className={styles.dimensionInput}>
            <label className={styles.dimensionLabel}>Width</label>
            <input
              type="number"
              name="width"
              value={formData.dimensions.width}
              onChange={handleDimensionChange}
              className={styles.input}
              placeholder="0"
              min="0"
              step="0.1"
            />
            <span className={styles.dimensionUnit}>{formData.dimensions.unit}</span>
          </div>
          
          <div className={styles.dimensionInput}>
            <label className={styles.dimensionLabel}>Length</label>
            <input
              type="number"
              name="length"
              value={formData.dimensions.length}
              onChange={handleDimensionChange}
              className={styles.input}
              placeholder="0"
              min="0"
              step="0.1"
            />
            <span className={styles.dimensionUnit}>{formData.dimensions.unit}</span>
          </div>
          
          <div className={styles.dimensionInput}>
            <label className={styles.dimensionLabel}>Height</label>
            <input
              type="number"
              name="height"
              value={formData.dimensions.height}
              onChange={handleDimensionChange}
              className={styles.input}
              placeholder="0"
              min="0"
              step="0.1"
            />
            <span className={styles.dimensionUnit}>{formData.dimensions.unit}</span>
          </div>
        </div>
      </div>

      {/* Style Tags */}
      <div className={styles.formGroup}>
        <label className={styles.label}>
          <span className={styles.labelText}>
            Style Preferences
            <span className={styles.labelHint}>Select all that apply</span>
          </span>
        </label>
        <div className={styles.styleTags}>
          {STYLE_OPTIONS.map(style => (
            <button
              key={style}
              type="button"
              className={`${styles.styleTag} ${
                formData.styles.includes(style) ? styles.active : ''
              }`}
              onClick={() => toggleStyle(style)}
            >
              {style}
            </button>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className={styles.formActions}>
        <button
          type="button"
          className={`${styles.button} ${styles.buttonSecondary}`}
          onClick={onCancel}
        >
          Cancel
        </button>
        <button
          type="submit"
          className={`${styles.button} ${styles.buttonPrimary}`}
          disabled={isAnalyzing}
        >
          {isAnalyzing ? '🔍 Analyzing & Adding Room...' : (initialData ? 'Save Changes' : 'Add Room')}
        </button>
      </div>
    </form>
  );
};

export default RoomForm;

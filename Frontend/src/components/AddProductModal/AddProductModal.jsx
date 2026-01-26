import React, { useState } from 'react';
import { useCustomProducts } from '../../context/CustomProductsContext';
import { useToast } from '../../context/ToastContext';
import styles from './AddProductModal.module.css';

const AddProductModal = ({ isOpen, onClose }) => {
  const { addCustomProduct } = useCustomProducts();
  const { success } = useToast();

  const [formData, setFormData] = useState({
    name: '',
    category: 'sofas',
    price: '',
    rating: '4.5',
    reviewCount: '10',
    image: '',
    description: '',
    features: '',
    styles: '',
    colors: '',
    tags: 'luxury',
    inStock: true,
    trending: false
  });

  const [errors, setErrors] = useState({});
  const [imageInputMode, setImageInputMode] = useState('url'); // 'url' or 'upload'
  const [uploadedFile, setUploadedFile] = useState(null);

  const categories = [
    'sofas', 'beds', 'tables', 'chairs', 'storage',
    'lighting', 'rugs', 'decor', 'outdoor', 'office'
  ];

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setErrors(prev => ({ ...prev, image: 'Please select an image file' }));
        return;
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setErrors(prev => ({ ...prev, image: 'Image must be less than 5MB' }));
        return;
      }

      setUploadedFile(file);

      // Convert to base64
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData(prev => ({ ...prev, image: reader.result }));
        setErrors(prev => ({ ...prev, image: '' }));
      };
      reader.readAsDataURL(file);
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) newErrors.name = 'Product name is required';
    if (!formData.price || Number(formData.price) <= 0) newErrors.price = 'Valid price is required';
    if (!formData.image.trim()) {
      newErrors.image = imageInputMode === 'url' ? 'Image URL is required' : 'Please upload an image';
    }

    return newErrors;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const validationErrors = validateForm();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    // Parse array fields
    const parseArray = (str) => str.split(',').map(s => s.trim()).filter(s => s);

    const newProduct = {
      ...formData,
      features: parseArray(formData.features),
      styles: parseArray(formData.styles),
      colors: parseArray(formData.colors),
      tags: parseArray(formData.tags)
    };

    try {
      addCustomProduct(newProduct);
      success(`${newProduct.name} has been added successfully!`);
      handleClose();
    } catch (error) {
      console.error('Failed to add product:', error);
    }
  };

  const handleClose = () => {
    setFormData({
      name: '',
      category: 'sofas',
      price: '',
      rating: '4.5',
      reviewCount: '10',
      image: '',
      description: '',
      features: '',
      styles: '',
      colors: '',
      tags: 'luxury',
      inStock: true,
      trending: false
    });
    setErrors({});
    setImageInputMode('url');
    setUploadedFile(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className={styles.modalOverlay} onClick={handleClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={handleClose} aria-label="Close">
          <svg viewBox="0 0 24 24" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>

        <h2 className={styles.title}>Add New Product</h2>

        <form onSubmit={handleSubmit} className={styles.form}>
          {/* Product Name */}
          <div className={styles.formGroup}>
            <label htmlFor="name" className={styles.label}>Product Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className={`${styles.input} ${errors.name ? styles.inputError : ''}`}
              placeholder="e.g., Modern Leather Sofa"
            />
            {errors.name && <span className={styles.error}>{errors.name}</span>}
          </div>

          {/* Category & Price */}
          <div className={styles.row}>
            <div className={styles.formGroup}>
              <label htmlFor="category" className={styles.label}>Category *</label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleChange}
                className={styles.select}
              >
                {categories.map(cat => (
                  <option key={cat} value={cat}>
                    {cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="price" className={styles.label}>Price (TND) *</label>
              <input
                type="number"
                id="price"
                name="price"
                value={formData.price}
                onChange={handleChange}
                className={`${styles.input} ${errors.price ? styles.inputError : ''}`}
                placeholder="999"
                min="0"
                step="1"
              />
              {errors.price && <span className={styles.error}>{errors.price}</span>}
            </div>
          </div>

          {/* Rating & Reviews */}
          <div className={styles.row}>
            <div className={styles.formGroup}>
              <label htmlFor="rating" className={styles.label}>Rating</label>
              <input
                type="number"
                id="rating"
                name="rating"
                value={formData.rating}
                onChange={handleChange}
                className={styles.input}
                min="0"
                max="5"
                step="0.1"
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="reviewCount" className={styles.label}>Review Count</label>
              <input
                type="number"
                id="reviewCount"
                name="reviewCount"
                value={formData.reviewCount}
                onChange={handleChange}
                className={styles.input}
                min="0"
                step="1"
              />
            </div>
          </div>

          {/* Image */}
          <div className={styles.formGroup}>
            <label className={styles.label}>Product Image *</label>

            {/* Toggle Buttons */}
            <div className={styles.imageToggle}>
              <button
                type="button"
                className={`${styles.toggleButton} ${imageInputMode === 'url' ? styles.active : ''}`}
                onClick={() => setImageInputMode('url')}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                  <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
                </svg>
                Image URL
              </button>
              <button
                type="button"
                className={`${styles.toggleButton} ${imageInputMode === 'upload' ? styles.active : ''}`}
                onClick={() => setImageInputMode('upload')}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                Upload File
              </button>
            </div>

            {/* URL Input */}
            {imageInputMode === 'url' && (
              <input
                type="url"
                name="image"
                value={formData.image}
                onChange={handleChange}
                className={`${styles.input} ${errors.image ? styles.inputError : ''}`}
                placeholder="https://example.com/image.jpg"
              />
            )}

            {/* File Upload */}
            {imageInputMode === 'upload' && (
              <div className={styles.fileUpload}>
                <input
                  type="file"
                  id="imageUpload"
                  name="imageUpload"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className={styles.fileInput}
                />
                <label htmlFor="imageUpload" className={styles.fileLabel}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                    <circle cx="8.5" cy="8.5" r="1.5" />
                    <polyline points="21 15 16 10 5 21" />
                  </svg>
                  <span>{uploadedFile ? uploadedFile.name : 'Click to upload or drag and drop'}</span>
                  <span className={styles.fileHint}>PNG, JPG, GIF up to 5MB</span>
                </label>
              </div>
            )}

            {errors.image && <span className={styles.error}>{errors.image}</span>}

            {/* Image Preview */}
            {formData.image && (
              <div className={styles.imagePreview}>
                <img src={formData.image} alt="Preview" />
                <button
                  type="button"
                  className={styles.removeImage}
                  onClick={() => {
                    setFormData(prev => ({ ...prev, image: '' }));
                    setUploadedFile(null);
                  }}
                >
                  ✕
                </button>
              </div>
            )}
          </div>

          {/* Description */}
          <div className={styles.formGroup}>
            <label htmlFor="description" className={styles.label}>Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              className={styles.textarea}
              rows="3"
              placeholder="Product description..."
            />
          </div>

          {/* Features */}
          <div className={styles.formGroup}>
            <label htmlFor="features" className={styles.label}>Features (comma-separated)</label>
            <input
              type="text"
              id="features"
              name="features"
              value={formData.features}
              onChange={handleChange}
              className={styles.input}
              placeholder="Feature 1, Feature 2, Feature 3"
            />
          </div>

          {/* Styles */}
          <div className={styles.formGroup}>
            <label htmlFor="styles" className={styles.label}>Styles (comma-separated)</label>
            <input
              type="text"
              id="styles"
              name="styles"
              value={formData.styles}
              onChange={handleChange}
              className={styles.input}
              placeholder="Modern, Rustic, Minimalist"
            />
          </div>

          {/* Colors */}
          <div className={styles.formGroup}>
            <label htmlFor="colors" className={styles.label}>Available Colors (comma-separated)</label>
            <input
              type="text"
              id="colors"
              name="colors"
              value={formData.colors}
              onChange={handleChange}
              className={styles.input}
              placeholder="White, Black, Gray"
            />
          </div>

          {/* Tags */}
          <div className={styles.formGroup}>
            <label htmlFor="tags" className={styles.label}>Tags (comma-separated)</label>
            <input
              type="text"
              id="tags"
              name="tags"
              value={formData.tags}
              onChange={handleChange}
              className={styles.input}
              placeholder="luxury, comfortable, durable"
            />
          </div>

          {/* Checkboxes */}
          <div className={styles.checkboxGroup}>
            <label className={styles.checkboxLabel}>
              <input
                type="checkbox"
                name="inStock"
                checked={formData.inStock}
                onChange={handleChange}
              />
              <span>In Stock</span>
            </label>

            <label className={styles.checkboxLabel}>
              <input
                type="checkbox"
                name="trending"
                checked={formData.trending}
                onChange={handleChange}
              />
              <span>Trending Product</span>
            </label>
          </div>

          {/* Actions */}
          <div className={styles.actions}>
            <button type="button" className={styles.cancelButton} onClick={handleClose}>
              Cancel
            </button>
            <button type="submit" className={styles.submitButton}>
              Add Product
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddProductModal;

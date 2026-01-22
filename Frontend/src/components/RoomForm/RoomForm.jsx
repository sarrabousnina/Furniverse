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

const RoomForm = ({ onSubmit, onCancel, initialData = null }) => {
  const [formData, setFormData] = useState({
    name: '',
    budgetMin: '',
    budgetMax: '',
    size: '',
    styles: [],
    existingFurniture: ''
  });

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
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

  const handleSubmit = (e) => {
    e.preventDefault();

    // Validate required fields
    if (!formData.name.trim()) {
      alert('Please enter a room name');
      return;
    }

    if (!formData.budgetMin || !formData.budgetMax) {
      alert('Please enter both minimum and maximum budget');
      return;
    }

    if (parseInt(formData.budgetMin) > parseInt(formData.budgetMax)) {
      alert('Minimum budget cannot be greater than maximum budget');
      return;
    }

    onSubmit({
      ...formData,
      budgetMin: parseInt(formData.budgetMin),
      budgetMax: parseInt(formData.budgetMax),
      size: formData.size ? parseInt(formData.size) : null
    });
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

      {/* Room Name */}
      <div className={styles.formGroup}>
        <label className={styles.label}>
          Room Name
        </label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          className={styles.input}
          placeholder="e.g., Living Room, Master Bedroom"
          required
        />
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

      {/* Room Size */}
      <div className={styles.formGroup}>
        <label className={styles.label}>
          <span className={styles.labelText}>
            Room Size
            <span className={styles.labelHint}>Optional</span>
          </span>
        </label>
        <input
          type="number"
          name="size"
          value={formData.size}
          onChange={handleChange}
          className={styles.input}
          placeholder="e.g., 250"
          min="0"
        />
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

      {/* Existing Furniture */}
      <div className={styles.formGroup}>
        <label className={styles.label}>
          <span className={styles.labelText}>
            Existing Furniture
            <span className={styles.labelHint}>Optional</span>
          </span>
        </label>
        <textarea
          name="existingFurniture"
          value={formData.existingFurniture}
          onChange={handleChange}
          className={`${styles.input} ${styles.textarea}`}
          placeholder="e.g., Navy velvet sofa, walnut coffee table, brass floor lamp"
        />
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
        >
          {initialData ? 'Save Changes' : 'Add Room'}
        </button>
      </div>
    </form>
  );
};

export default RoomForm;

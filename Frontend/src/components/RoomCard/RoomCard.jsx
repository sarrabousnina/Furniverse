import React from 'react';
import { formatPrice } from '../../utils/currency';
import styles from './RoomCard.module.css';

const RoomCard = ({ room, onEdit, onDelete }) => {
  const formatBudget = (amount) => {
    if (!amount) return 'Not specified';
    return formatPrice(amount, 'TND', 0);
  };

  const formatSize = (size) => {
    if (!size) return '';
    return `${size.toLocaleString()} sq ft`;
  };

  return (
    <div className={styles.card} onClick={() => onEdit(room)}>
      {/* Room Image */}
      {room.image && (
        <div className={styles.cardImage}>
          <img src={room.image} alt={room.name} className={styles.roomImage} />
        </div>
      )}

      <div className={styles.cardHeader}>
        <div>
          <h3 className={styles.cardTitle}>{room.name}</h3>
          {room.size && (
            <div className={styles.cardSize}>{formatSize(room.size)}</div>
          )}
        </div>
        <div className={styles.cardActions}>
          <button
            className={`${styles.iconButton} ${styles.edit}`}
            onClick={(e) => {
              e.stopPropagation();
              onEdit(room);
            }}
            aria-label="Edit room"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
            </svg>
          </button>
          <button
            className={`${styles.iconButton} ${styles.delete}`}
            onClick={(e) => {
              e.stopPropagation();
              if (window.confirm(`Delete "${room.name}"?`)) {
                onDelete(room.id);
              }
            }}
            aria-label="Delete room"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M3 6h18" />
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
            </svg>
          </button>
        </div>
      </div>

      {/* Budget */}
      <div className={styles.cardSection}>
        <svg
          className={styles.icon}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
        </svg>
        <span className={styles.sectionLabel}>Budget:</span>
        <span className={`${styles.sectionValue} ${styles.budget}`}>
          {formatBudget(room.budgetMin)} – {formatBudget(room.budgetMax)}
        </span>
      </div>

      {/* Style Tags */}
      {room.styles && room.styles.length > 0 && (
        <div className={styles.styles}>
          {room.styles.map((style, index) => (
            <span key={index} className={styles.styleBadge}>
              {style}
            </span>
          ))}
        </div>
      )}

      {/* Existing Furniture */}
      {room.existingFurniture && (
        <div className={styles.furniture}>
          <span className={styles.furnitureIcon}>✨</span>
          {room.existingFurniture}
        </div>
      )}
    </div>
  );
};

export default RoomCard;

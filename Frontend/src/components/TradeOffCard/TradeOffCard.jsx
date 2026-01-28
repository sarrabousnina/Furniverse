import React from 'react';
import styles from './TradeOffCard.module.css';

const TradeOffCard = ({ product, onAddToCart }) => {
  const { name, price, image, tradeoff_analysis } = product;
  const { gains, loses } = tradeoff_analysis;

  return (
    <div className={styles.tradeOffCard}>
      {/* Header with icon */}
      <div className={styles.header}>
        <div className={styles.headerIcon}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <div>
          <h3 className={styles.title}>Smart Alternative</h3>
          <p className={styles.subtitle}>We analyzed the trade-offs for you</p>
        </div>
      </div>

      {/* Product preview */}
      <div className={styles.productPreview}>
        <div className={styles.productImage}>
          <img src={image} alt={name} />
        </div>
        <div className={styles.productInfo}>
          <h4 className={styles.productName}>{name}</h4>
          <p className={styles.productPrice}>${price}</p>
        </div>
      </div>

      {/* Trade-off analysis */}
      <div className={styles.analysis}>
        {/* What you GAIN */}
        {gains && gains.length > 0 && (
          <div className={styles.gains}>
            <div className={styles.analysisHeader}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20 6L9 17l-5-5" />
              </svg>
              <h4>What You Gain</h4>
            </div>
            <ul className={styles.gainsList}>
              {gains.map((gain, idx) => (
                <li key={idx} className={styles.gainItem}>{gain}</li>
              ))}
            </ul>
          </div>
        )}

        {/* What you LOSE */}
        {loses && loses.length > 0 && (
          <div className={styles.loses}>
            <div className={styles.analysisHeader}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
              <h4>What You Lose</h4>
            </div>
            <ul className={styles.losesList}>
              {loses.map((loss, idx) => (
                <li key={idx} className={styles.lossItem}>{loss}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Action button */}
      <div className={styles.actions}>
        <button
          className={styles.addToCartButton}
          onClick={() => onAddToCart && onAddToCart(product)}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="9" cy="21" r="1" />
            <circle cx="20" cy="21" r="1" />
            <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
          </svg>
          Add to Cart
        </button>
      </div>
    </div>
  );
};

export default TradeOffCard;

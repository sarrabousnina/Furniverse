import React from 'react';
import styles from './Header.module.css';

const Header = ({ roomCount = 0 }) => {
  return (
    <header className={styles.header}>
      <div className={styles.headerContent}>
        <div className={styles.logo}>
          <div className={styles.logoIcon}>F</div>
          <div className={styles.logoText}>
            <span className={styles.logoTitle}>Furniverse</span>
            <span className={styles.logoTagline}>AI-Powered Discovery</span>
          </div>
        </div>
        {roomCount > 0 && (
          <div className={styles.roomCount}>
            <span className={styles.roomCountNumber}>{roomCount}</span> Room
            {roomCount !== 1 ? 's' : ''}
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;

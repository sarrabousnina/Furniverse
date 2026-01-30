import { useComparison } from '../../context/ComparisonContext';
import styles from './ComparisonBar.module.css';

const ComparisonBar = () => {
  const { selectedProducts, removeFromComparison, clearComparison, startComparison, canCompare } = useComparison();

  if (selectedProducts.length === 0) return null;

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <div className={styles.header}>
          <h3>🤖 AI Product Comparison</h3>
          <button onClick={clearComparison} className={styles.clearBtn}>
            Clear All
          </button>
        </div>

        <div className={styles.products}>
          {selectedProducts.map((product, index) => (
            <div key={product.id} className={styles.productItem}>
              <img src={product.image} alt={product.name} />
              <div className={styles.productInfo}>
                <h4>{product.name}</h4>
                <p>${product.price}</p>
              </div>
              <button 
                onClick={() => removeFromComparison(product.id)}
                className={styles.removeBtn}
                aria-label="Remove product"
              >
                ✕
              </button>
            </div>
          ))}

          {selectedProducts.length === 1 && (
            <div className={styles.placeholder}>
              <div className={styles.placeholderIcon}>+</div>
              <p>Select one more product to compare</p>
            </div>
          )}
        </div>

        <button 
          onClick={startComparison}
          disabled={!canCompare}
          className={`${styles.compareBtn} ${canCompare ? styles.active : ''}`}
        >
          {canCompare ? (
            <>
              ✨ Compare with AI
              <span className={styles.badge}>Ready!</span>
            </>
          ) : (
            <>Select 2 products</>
          )}
        </button>
      </div>
    </div>
  );
};

export default ComparisonBar;

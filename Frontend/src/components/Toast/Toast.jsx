import React from 'react';
import { useToast } from '../../context/ToastContext';
import styles from './Toast.module.css';

const Toast = ({ toast }) => {
  const { removeToast } = useToast();

  return (
    <div className={`${styles.toast} ${styles[toast.type]}`}>
      <div className={styles.toastContent}>
        {toast.type === 'success' && (
          <svg className={styles.icon} viewBox="0 0 24 24" fill="none" strokeWidth="2">
            <path d="M20 6 9 17l-5-5" />
          </svg>
        )}
        {toast.type === 'error' && (
          <svg className={styles.icon} viewBox="0 0 24 24" fill="none" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 8v4M12 16h.01" />
          </svg>
        )}
        {toast.type === 'info' && (
          <svg className={styles.icon} viewBox="0 0 24 24" fill="none" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 16v-4M12 8h.01" />
          </svg>
        )}
        <span className={styles.message}>{toast.message}</span>
      </div>
      <button
        className={styles.closeButton}
        onClick={() => removeToast(toast.id)}
        aria-label="Close toast"
      >
        <svg viewBox="0 0 24 24" fill="none" strokeWidth="2">
          <path d="M18 6 6 18M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
};

const ToastContainer = () => {
  const { toasts } = useToast();

  return (
    <div className={styles.container}>
      {toasts.map(toast => (
        <Toast key={toast.id} toast={toast} />
      ))}
    </div>
  );
};

export default ToastContainer;

import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import styles from './AuthModal.module.css';

const AuthModal = () => {
  const { login, signup, isAuthModalOpen, setIsAuthModalOpen } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Allow any username/password combination
    const username = formData.email || 'user';
    const displayName = formData.name || username;

    if (isLogin) {
      login(username, displayName);
    } else {
      signup(username, displayName);
    }
  };

  const switchMode = () => {
    setIsLogin(!isLogin);
  };

  if (!isAuthModalOpen) return null;

  return (
    <div className={styles.modal} onClick={() => setIsAuthModalOpen(false)}>
      <div className={styles.content} onClick={(e) => e.stopPropagation()}>
        <button
          className={styles.closeButton}
          onClick={() => setIsAuthModalOpen(false)}
          aria-label="Close"
        >
          <svg viewBox="0 0 24 24" fill="none" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>

        <div className={styles.header}>
          <div className={styles.logoIcon}>F</div>
          <h2 className={styles.title}>
            {isLogin ? 'Welcome Back' : 'Join Furniverse'}
          </h2>
          <p className={styles.subtitle}>
            {isLogin
              ? 'Sign in to access your profile and recommendations'
              : 'Create an account to get personalized recommendations'}
          </p>
        </div>

        {/* Tabs */}
        <div className={styles.tabs}>
          <button
            className={`${styles.tab} ${isLogin ? styles.tabActive : ''}`}
            onClick={() => setIsLogin(true)}
          >
            Sign In
          </button>
          <button
            className={`${styles.tab} ${!isLogin ? styles.tabActive : ''}`}
            onClick={() => setIsLogin(false)}
          >
            Sign Up
          </button>
        </div>

        {/* Form */}
        <form className={styles.form} onSubmit={handleSubmit}>
          {!isLogin && (
            <div className={styles.formGroup}>
              <label className={styles.label}>Full Name</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className={styles.input}
                placeholder="Enter your name"
              />
            </div>
          )}

          <div className={styles.formGroup}>
            <label className={styles.label}>Username</label>
            <input
              type="text"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={styles.input}
              placeholder="Enter any username"
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label}>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={styles.input}
              placeholder="Enter any password"
            />
          </div>

          <button type="submit" className={styles.submitButton}>
            {isLogin ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        {isLogin && (
          <div className={styles.forgotPassword}>
            <a href="#forgot">Forgot your password?</a>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuthModal;

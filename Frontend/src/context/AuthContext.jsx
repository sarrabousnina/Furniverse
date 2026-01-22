import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('furniverse_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  useEffect(() => {
    if (user) {
      localStorage.setItem('furniverse_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('furniverse_user');
    }
  }, [user]);

  const login = (email, name) => {
    const newUser = {
      id: Date.now().toString(),
      email,
      name,
    };
    setUser(newUser);
    setIsAuthModalOpen(false);
    return newUser;
  };

  const logout = () => {
    setUser(null);
  };

  const signup = (email, name) => {
    return login(email, name);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        signup,
        isAuthModalOpen,
        setIsAuthModalOpen,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

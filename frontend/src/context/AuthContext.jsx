import React, {
  createContext,
  useContext,
  useMemo,
  useState,
} from 'react';

import {
  apiService,
  authStorage,
} from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => authStorage.getToken());

  const login = async (username, password) => {
    const data = await apiService.login(username, password);

    if (!data?.access_token) {
      throw new Error('Authentication token was not returned.');
    }

    authStorage.setToken(data.access_token);
    setToken(data.access_token);

    return data;
  };

  const logout = () => {
    authStorage.clearToken();
    setToken(null);
  };

  const value = useMemo(
    () => ({
      token,
      isAuthenticated: Boolean(token),
      login,
      logout,
    }),
    [token]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider.');
  }

  return context;
};
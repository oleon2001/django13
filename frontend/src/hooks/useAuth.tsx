import React, { createContext, useContext, useState, useEffect, startTransition } from 'react';
import authService from '../services/auth';

interface User {
  id: number;
  username: string;
  email: string;
  is_staff: boolean;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const initializeAuth = async () => {
    try {
      if (authService.isAuthenticated()) {
        const userData = await authService.getCurrentUser();
        startTransition(() => {
          setUser(userData);
          setIsAuthenticated(true);
        });
      }
    } catch (error) {
      console.error('Error initializing auth:', error);
      await authService.logout();
      startTransition(() => {
        setUser(null);
        setIsAuthenticated(false);
      });
    } finally {
      startTransition(() => {
        setLoading(false);
      });
    }
  };

  useEffect(() => {
    initializeAuth();
  }, []);

  const login = async (username: string, password: string) => {
    startTransition(() => {
      setLoading(true);
      setError(null);
    });
    
    try {
      const response = await authService.login({ username, password });
      startTransition(() => {
        setUser(response.user);
        setIsAuthenticated(true);
      });
    } catch (error: any) {
      startTransition(() => {
        setError(error.message || 'Error al iniciar sesión');
        setIsAuthenticated(false);
      });
      throw error;
    } finally {
      startTransition(() => {
        setLoading(false);
      });
    }
  };

  const logout = async () => {
    startTransition(() => {
      setLoading(true);
    });
    
    try {
      await authService.logout();
      startTransition(() => {
        setUser(null);
        setIsAuthenticated(false);
      });
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
      startTransition(() => {
        setLoading(false);
      });
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, error, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 
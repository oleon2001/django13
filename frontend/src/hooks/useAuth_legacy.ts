import React, { useState, useEffect, createContext, useContext } from 'react';

interface User {
  username: string;
  isStaff: boolean;
  hasFences: boolean;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const checkSession = async () => {
      const accessToken = localStorage.getItem('accessToken');
      if (accessToken) {
        try {
          const response = await fetch('/api/auth/session', {
            headers: {
              'Authorization': `Bearer ${accessToken}`,
            },
          });
          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
          } else {
            const refreshToken = localStorage.getItem('refreshToken');
            if (refreshToken) {
              try {
                const refreshResponse = await fetch('/api/token/refresh/', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify({ refresh: refreshToken }),
                });
                if (refreshResponse.ok) {
                  const data = await refreshResponse.json();
                  localStorage.setItem('accessToken', data.access);
                  const newSessionResponse = await fetch('/api/auth/session', {
                    headers: {
                      'Authorization': `Bearer ${data.access}`,
                    },
                  });
                  if (newSessionResponse.ok) {
                    const userData = await newSessionResponse.json();
                    setUser(userData);
                  } else {
                    console.error('Error fetching user data after token refresh');
                    logout();
                  }
                } else {
                  console.error('Error refreshing token');
                  logout();
                }
              } catch (refreshError) {
                console.error('Network error during token refresh:', refreshError);
                logout();
              }
            } else {
              logout();
            }
          }
        } catch (error) {
          console.error('Network error checking session:', error);
          logout();
        }
      } else {
        logout();
      }
    };

    checkSession();
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const response = await fetch('/api/token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Invalid credentials');
      }

      const data = await response.json();
      localStorage.setItem('accessToken', data.access);
      localStorage.setItem('refreshToken', data.refresh);

      const userResponse = await fetch('/api/auth/session', {
        headers: {
          'Authorization': `Bearer ${data.access}`,
        },
      });

      if (!userResponse.ok) {
        throw new Error('Failed to fetch user data after login');
      }
      const userData = await userResponse.json();
      setUser(userData);

    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setUser(null);
  };

  return React.createElement(
    AuthContext.Provider,
    { value: { user, login, logout } },
    children
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
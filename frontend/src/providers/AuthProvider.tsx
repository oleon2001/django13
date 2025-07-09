import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types/unified';

// ============================================================================
// AUTH CONTEXT - Contexto para autenticación
// ============================================================================

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (userData: any) => Promise<void>;
  updateProfile: (profileData: any) => Promise<void>;
  refreshToken: () => Promise<void>;
  forgotPassword: (email: string) => Promise<void>;
  resetPassword: (token: string, password: string) => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ============================================================================
// AUTH PROVIDER - Provider para autenticación
// ============================================================================

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Verificar si el usuario está autenticado al cargar la aplicación
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Verificar si hay un token en localStorage
      const token = localStorage.getItem('authToken');
      
      if (token) {
        // Validar el token con el backend
        // const response = await authService.validateToken(token);
        // setUser(response.data.user);
        
        // Por ahora, simular un usuario
        setUser({
          id: 1,
          username: 'admin',
          email: 'admin@skyguard.com',
          first_name: 'Admin',
          last_name: 'User',
          full_name: 'Admin User',
          is_active: true,
          is_staff: true,
          is_superuser: true,
          date_joined: new Date().toISOString(),
          groups: ['admin'],
          permissions: ['all'],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      localStorage.removeItem('authToken');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      
      // Llamar al servicio de autenticación
      // const response = await authService.login(email, password);
      // const { token, user } = response.data;
      
      // Simular respuesta
      const token = 'mock-token';
      const mockUser: User = {
        id: 1,
        username: 'admin',
        email: email,
        first_name: 'Admin',
        last_name: 'User',
        full_name: 'Admin User',
        is_active: true,
        is_staff: true,
        is_superuser: true,
        date_joined: new Date().toISOString(),
        groups: ['admin'],
        permissions: ['all'],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      
      // Guardar token en localStorage
      localStorage.setItem('authToken', token);
      
      // Actualizar estado
      setUser(mockUser);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      // Llamar al servicio de autenticación para logout
      // await authService.logout();
      
      // Limpiar localStorage
      localStorage.removeItem('authToken');
      
      // Limpiar estado
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  };

  const register = async (userData: any) => {
    try {
      setIsLoading(true);
      
      // Llamar al servicio de autenticación
      // const response = await authService.register(userData);
      // const { token, user } = response.data;
      
      // Simular respuesta
      const token = 'mock-token';
      const mockUser: User = {
        id: 2,
        username: userData.username,
        email: userData.email,
        first_name: userData.first_name,
        last_name: userData.last_name,
        full_name: `${userData.first_name} ${userData.last_name}`,
        is_active: true,
        is_staff: false,
        is_superuser: false,
        date_joined: new Date().toISOString(),
        groups: ['user'],
        permissions: ['basic'],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      
      // Guardar token en localStorage
      localStorage.setItem('authToken', token);
      
      // Actualizar estado
      setUser(mockUser);
    } catch (error) {
      console.error('Register error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const updateProfile = async (profileData: any) => {
    try {
      setIsLoading(true);
      
      // Llamar al servicio de autenticación
      // const response = await authService.updateProfile(profileData);
      // const { user } = response.data;
      
      // Simular respuesta
      const updatedUser: User = {
        ...user!,
        ...profileData,
        full_name: `${profileData.first_name} ${profileData.last_name}`,
        updated_at: new Date().toISOString(),
      };
      
      // Actualizar estado
      setUser(updatedUser);
    } catch (error) {
      console.error('Update profile error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const refreshToken = async () => {
    try {
      // Llamar al servicio de autenticación
      // const response = await authService.refreshToken();
      // const { token } = response.data;
      
      // Simular respuesta
      const token = 'new-mock-token';
      
      // Actualizar token en localStorage
      localStorage.setItem('authToken', token);
    } catch (error) {
      console.error('Refresh token error:', error);
      throw error;
    }
  };

  const forgotPassword = async (email: string) => {
    try {
      // Llamar al servicio de autenticación
      // await authService.forgotPassword(email);
      
      // Simular respuesta
      console.log('Password reset email sent to:', email);
    } catch (error) {
      console.error('Forgot password error:', error);
      throw error;
    }
  };

  const resetPassword = async (token: string, password: string) => {
    try {
      // Llamar al servicio de autenticación
      // await authService.resetPassword(token, password);
      
      // Simular respuesta
      console.log('Password reset successful');
    } catch (error) {
      console.error('Reset password error:', error);
      throw error;
    }
  };

  const changePassword = async (currentPassword: string, newPassword: string) => {
    try {
      // Llamar al servicio de autenticación
      // await authService.changePassword(currentPassword, newPassword);
      
      // Simular respuesta
      console.log('Password changed successfully');
    } catch (error) {
      console.error('Change password error:', error);
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    register,
    updateProfile,
    refreshToken,
    forgotPassword,
    resetPassword,
    changePassword,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// ============================================================================
// AUTH HOOK - Hook para usar el contexto de autenticación
// ============================================================================

export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}; 
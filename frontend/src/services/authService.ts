import axios from 'axios';
import api from './api';

const API_URL = 'http://127.0.0.1:8000/api';

// Configuración global de axios
axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

interface LoginCredentials {
  username: string;
  password: string;
}

interface AuthResponse {
  access: string;
  refresh: string;
  user: {
    id: number;
    username: string;
    email: string;
    is_staff: boolean;
  };
}

interface ProfileData {
  username: string;
  email: string;
}

interface PasswordChangeData {
  old_password: string;
  new_password: string;
}

export const authService = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    try {
      console.log('Attempting login to:', `${API_URL}/auth/login/`);
      console.log('With credentials:', { username: credentials.username });
      
      const response = await api.post<AuthResponse>('/auth/login/', credentials);
      console.log('Login response:', response.data);
      
      const { access, refresh, user } = response.data;
      
      // Guardar tokens en localStorage
      localStorage.setItem('token', access);
      localStorage.setItem('refreshToken', refresh);
      localStorage.setItem('user', JSON.stringify(user));
      
      return response.data;
    } catch (error: any) {
      console.error('Login error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        headers: error.response?.headers,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          headers: error.config?.headers,
        }
      });
      throw new Error(error.response?.data?.error || 'Error al iniciar sesión');
    }
  },

  logout: () => {
    console.log('Logging out user');
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  },

  refreshToken: async (): Promise<AuthResponse> => {
    try {
      const refresh = localStorage.getItem('refreshToken');
      if (!refresh) throw new Error('No refresh token available');

      console.log('Attempting to refresh token');
      const response = await api.post<AuthResponse>('/auth/token/refresh/', { refresh });
      console.log('Token refresh response:', response.data);
      
      const { access } = response.data;
      localStorage.setItem('token', access);
      return response.data;
    } catch (error: any) {
      console.error('Token refresh error:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      throw new Error('Error al renovar la sesión');
    }
  },

  getCurrentUser: async () => {
    try {
      console.log('Fetching current user');
      const response = await api.get('/gps/users/me/');
      console.log('Current user response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Get current user error:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      throw new Error('Error al obtener información del usuario');
    }
  },

  updateProfile: async (data: ProfileData) => {
    try {
      console.log('Updating profile with:', data);
      const response = await api.patch('/users/me/', data);
      console.log('Profile update response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Update profile error:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      throw new Error('Error al actualizar el perfil');
    }
  },

  changePassword: async (data: PasswordChangeData) => {
    try {
      console.log('Changing password');
      const response = await api.post('/users/change-password/', data);
      console.log('Password change response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Change password error:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      throw new Error('Error al cambiar la contraseña');
    }
  },
}; 
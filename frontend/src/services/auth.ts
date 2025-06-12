import api from './api';

interface LoginCredentials {
  username: string;
  password: string;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name: string;
  last_name: string;
}

const authService = {
  async login(credentials: LoginCredentials) {
    try {
      const response = await api.post('/api/auth/login/', credentials);
      const { access, refresh, user } = response.data;
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user', JSON.stringify(user));
      return response.data;
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data.error || 'Error de autenticación');
      }
      throw new Error('Error de conexión');
    }
  },

  async register(data: RegisterData) {
    try {
      const response = await api.post('/api/auth/register/', data);
      const { access, refresh, user } = response.data;
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user', JSON.stringify(user));
      return response.data;
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data.error || 'Error en el registro');
      }
      throw new Error('Error de conexión');
    }
  },

  async logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  async getCurrentUser() {
    try {
      const response = await api.get('/api/auth/profile/');
      return response.data;
    } catch (error: any) {
      if (error.response && error.response.status === 401) {
        this.logout();
      }
      throw error;
    }
  },

  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  },

  getToken() {
    return localStorage.getItem('access_token');
  }
};

export default authService; 
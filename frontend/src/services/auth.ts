import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface LoginCredentials {
  username: string;
  password: string;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  password2: string;
}

interface User {
  id: number;
  username: string;
  email: string;
  is_staff: boolean;
}

interface LoginResponse {
  access: string;
  refresh: string;
  user: {
    id: number;
    username: string;
    email: string;
    is_staff: boolean;
  };
}

interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

class AuthService {
  private token: string | null = null;
  private user: User | null = null;

  constructor() {
    try {
      this.token = localStorage.getItem('token');
      const userStr = localStorage.getItem('user');
      this.user = userStr ? JSON.parse(userStr) : null;
      
      // Configurar el token en axios si existe
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
      }
    } catch (error) {
      console.error('Error initializing auth state:', error);
      this.clearAuth();
    }
  }

  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      const response = await axios.post(`${API_URL}/api/auth/token/`, credentials);
      const { access, refresh, user } = response.data;
      
      this.token = access;
      this.user = user;
      
      localStorage.setItem('token', access);
      localStorage.setItem('refresh', refresh);
      localStorage.setItem('user', JSON.stringify(user));
      
      // Configurar el token en axios para futuras peticiones
      axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error al iniciar sesión');
    }
  }

  async logout(): Promise<void> {
    try {
      if (this.token) {
        await axios.post(`${API_URL}/api/auth/logout/`, {}, {
          headers: { Authorization: `Bearer ${this.token}` }
        });
      }
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
      this.clearAuth();
    }
  }

  private clearAuth(): void {
    this.token = null;
    this.user = null;
    localStorage.removeItem('token');
    localStorage.removeItem('refresh');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  getToken(): string | null {
    return this.token;
  }

  async getCurrentUser(): Promise<User> {
    if (!this.token) {
      throw new Error('No authenticated user');
    }

    try {
      const response = await axios.get(`${API_URL}/api/auth/user/`, {
        headers: { Authorization: `Bearer ${this.token}` }
      });
      this.user = response.data;
      localStorage.setItem('user', JSON.stringify(response.data));
      return response.data;
    } catch (error) {
      this.clearAuth();
      throw new Error('Error getting user data');
    }
  }

  async refreshToken(): Promise<string> {
    const refresh = localStorage.getItem('refresh');
    if (!refresh) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await axios.post(`${API_URL}/api/auth/token/refresh/`, {
        refresh
      });
      
      const { access } = response.data;
      this.token = access;
      localStorage.setItem('token', access);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      return access;
    } catch (error) {
      this.clearAuth();
      throw new Error('Error refreshing token');
    }
  }

  async register(data: RegisterData): Promise<AuthResponse> {
    try {
      const response = await axios.post(`${API_URL}/api/auth/register/`, data);
      const { access, refresh, user } = response.data;
      
      localStorage.setItem('token', access);
      localStorage.setItem('refresh', refresh);
      localStorage.setItem('user', JSON.stringify(user));
      
      this.token = access;
      this.user = user;
      
      axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error en el registro');
    }
  }

  getUser(): User | null {
    return this.user;
  }
}

export default new AuthService(); 
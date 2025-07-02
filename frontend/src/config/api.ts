import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import toast from 'react-hot-toast';

// Configuración base de la API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(process.env.REACT_APP_API_TIMEOUT || '30000');

// Crear instancia de axios
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para requests
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Obtener token del localStorage
    const authData = localStorage.getItem(process.env.REACT_APP_AUTH_STORAGE_KEY || 'skyguard_auth');
    
    if (authData) {
      try {
        const { access } = JSON.parse(authData);
        if (access) {
          config.headers.Authorization = `Bearer ${access}`;
        }
      } catch (error) {
        console.error('Error parsing auth data:', error);
      }
    }

    // Log request en desarrollo
    if (process.env.NODE_ENV === 'development') {
      console.log('API Request:', {
        method: config.method?.toUpperCase(),
        url: config.url,
        data: config.data,
        params: config.params,
      });
    }

    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Interceptor para responses
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response en desarrollo
    if (process.env.NODE_ENV === 'development') {
      console.log('API Response:', {
        status: response.status,
        url: response.config.url,
        data: response.data,
      });
    }

    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Log error en desarrollo
    if (process.env.NODE_ENV === 'development') {
      console.error('API Error:', {
        status: error.response?.status,
        url: error.config?.url,
        message: error.message,
        data: error.response?.data,
      });
    }

    // Manejar error 401 (Unauthorized)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Intentar refrescar el token
        const authData = localStorage.getItem(process.env.REACT_APP_AUTH_STORAGE_KEY || 'skyguard_auth');
        
        if (authData) {
          const { refresh } = JSON.parse(authData);
          
          if (refresh) {
            const refreshResponse = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
              refresh,
            });

            const { access } = refreshResponse.data;
            
            // Actualizar token en localStorage
            localStorage.setItem(
              process.env.REACT_APP_AUTH_STORAGE_KEY || 'skyguard_auth',
              JSON.stringify({ access, refresh })
            );

            // Reintentar request original con nuevo token
            originalRequest.headers.Authorization = `Bearer ${access}`;
            return apiClient(originalRequest);
          }
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        
        // Limpiar datos de autenticación
        localStorage.removeItem(process.env.REACT_APP_AUTH_STORAGE_KEY || 'skyguard_auth');
        
        // Redirigir a login
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // Manejar otros errores
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.detail || 
                        error.message || 
                        'An error occurred';

    // Mostrar toast de error
    toast.error(errorMessage);

    return Promise.reject(error);
  }
);

// Funciones de utilidad para manejo de errores
export const handleApiError = (error: any): string => {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  
  if (error.message) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
};

// Función para validar respuesta
export const validateResponse = (response: AxiosResponse): boolean => {
  return response.status >= 200 && response.status < 300;
};

// Función para extraer datos de respuesta
export const extractData = <T>(response: AxiosResponse): T => {
  return response.data;
};

// Función para crear query params
export const createQueryParams = (params: Record<string, any>): string => {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      if (Array.isArray(value)) {
        value.forEach(item => searchParams.append(key, item.toString()));
      } else {
        searchParams.append(key, value.toString());
      }
    }
  });
  
  return searchParams.toString();
};

// Función para crear headers personalizados
export const createHeaders = (headers: Record<string, string> = {}): Record<string, string> => {
  return {
    'Content-Type': 'application/json',
    ...headers,
  };
};

// Configuración para diferentes tipos de requests
export const requestConfigs = {
  // Configuración para uploads
  upload: {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  },
  
  // Configuración para downloads
  download: {
    responseType: 'blob',
  },
  
  // Configuración para requests que no necesitan cache
  noCache: {
    headers: {
      'Cache-Control': 'no-cache',
      'Pragma': 'no-cache',
    },
  },
};

export default apiClient; 
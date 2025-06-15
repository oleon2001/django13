import axios, { AxiosError, AxiosRequestConfig } from 'axios';
import authService from './auth';

interface ErrorResponse {
    detail?: string;
    message?: string;
    [key: string]: any;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,
});

// Interceptor para agregar el token JWT a las peticiones
api.interceptors.request.use(
    (config) => {
        const token = authService.getToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Interceptor para manejar errores y refresh token
api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError<ErrorResponse>) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        // Si el error es 401 y no hemos intentado refrescar el token
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                // Intentar refrescar el token
                const newToken = await authService.refreshToken();
                
                // Actualizar el token en la petición original
                if (originalRequest.headers) {
                    originalRequest.headers.Authorization = `Bearer ${newToken}`;
                }
                
                // Reintentar la petición original
                return api(originalRequest);
            } catch (refreshError) {
                // Si falla el refresh, hacer logout
                await authService.logout();
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        // Manejar otros errores
        if (error.response) {
            // Error de respuesta del servidor
            const errorMessage = error.response.data?.detail || error.response.data?.message || 'Error del servidor';
            return Promise.reject(new Error(errorMessage));
        } else if (error.request) {
            // Error de red
            return Promise.reject(new Error('Error de conexión'));
        } else {
            // Error en la configuración de la petición
            return Promise.reject(new Error('Error en la petición'));
        }
    }
);

export default api; 
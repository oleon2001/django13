import axios from 'axios';
import { Device } from '../types';
import authService from './auth';

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

// Interceptor para manejar errores de respuesta
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Si el error es 401 y no hemos intentado refrescar el token
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                if (!refreshToken) {
                    throw new Error('No refresh token available');
                }

                const response = await axios.post(`${API_URL}/api/auth/token/refresh/`, {
                    refresh: refreshToken
                });

                const { access } = response.data;
                localStorage.setItem('access_token', access);

                // Actualizar el token en la petición original
                originalRequest.headers.Authorization = `Bearer ${access}`;
                return api(originalRequest);
            } catch (refreshError) {
                // Si falla el refresh, hacer logout
                authService.logout();
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export const deviceService = {
    getDevices: async () => {
        const response = await api.get('/gps/devices/');
        return response.data as Device[];
    },
    getDevice: async (id: string) => {
        const response = await api.get(`/gps/devices/${id}/`);
        return response.data as Device;
    },
    updateDevice: async (id: string, data: Partial<Device>) => {
        const response = await api.patch(`/gps/devices/${id}/`, data);
        return response.data as Device;
    },
};

export default api; 
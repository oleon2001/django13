import axios from 'axios';
import { Device } from '../types';
import { authService } from './authService';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add token to requests if it exists
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Interceptor para manejar errores y renovación de tokens
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Si el error es 401 y no es una solicitud de renovación de token
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                // Intentar renovar el token
                const { access } = await authService.refreshToken();
                
                // Actualizar el token en la solicitud original
                localStorage.setItem('token', access);
                originalRequest.headers.Authorization = `Bearer ${access}`;
                
                // Reintentar la solicitud original
                return api(originalRequest);
            } catch (refreshError) {
                // Si falla la renovación, cerrar sesión
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
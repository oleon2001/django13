import api from './api';

export interface Vehicle {
  id: number;
  plate: string;
  model: string;
  status: 'active' | 'inactive' | 'maintenance';
  lastUpdate: string;
}

export const vehicleService = {
  getAll: async () => {
    const response = await api.get('/vehicles/');
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get(`/vehicles/${id}/`);
    return response.data;
  },

  create: async (data: Omit<Vehicle, 'id' | 'lastUpdate'>) => {
    const response = await api.post('/vehicles/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<Vehicle>) => {
    const response = await api.put(`/vehicles/${id}/`, data);
    return response.data;
  },

  delete: async (id: number) => {
    await api.delete(`/vehicles/${id}/`);
  },

  getStatus: async (id: number) => {
    const response = await api.get(`/vehicles/${id}/status/`);
    return response.data;
  },
}; 
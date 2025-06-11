import api from './api';

export interface Report {
  id: number;
  date: string;
  type: string;
  description: string;
  status: 'pending' | 'completed' | 'failed';
}

export const reportService = {
  getAll: async () => {
    const response = await api.get('/reports/');
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get(`/reports/${id}/`);
    return response.data;
  },

  create: async (data: Omit<Report, 'id'>) => {
    const response = await api.post('/reports/', data);
    return response.data;
  },

  delete: async (id: number) => {
    await api.delete(`/reports/${id}/`);
  },

  getByDate: async (date: string) => {
    const response = await api.get(`/reports/date/${date}/`);
    return response.data;
  },

  generateReport: async (type: string, params: Record<string, any>) => {
    const response = await api.post('/reports/generate/', { type, params });
    return response.data;
  },
}; 
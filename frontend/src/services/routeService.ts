import api from './api';

export interface Route {
  id: number;
  name: string;
  description: string;
  startPoint: string;
  endPoint: string;
  distance: number;
  estimatedTime: number;
  active: boolean;
}

class RouteService {
  async getAll(): Promise<Route[]> {
    try {
      const response = await api.get('/routes/');
      return response.data;
    } catch (error) {
      console.error('Error fetching routes:', error);
      return [];
    }
  }

  async getById(id: number): Promise<Route | null> {
    try {
      const response = await api.get(`/routes/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching route:', error);
      return null;
    }
  }

  async create(data: Partial<Route>): Promise<Route | null> {
    try {
      const response = await api.post('/routes/', data);
      return response.data;
    } catch (error) {
      console.error('Error creating route:', error);
      return null;
    }
  }

  async update(id: number, data: Partial<Route>): Promise<Route | null> {
    try {
      const response = await api.put(`/routes/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error('Error updating route:', error);
      return null;
    }
  }

  async delete(id: number): Promise<boolean> {
    try {
      await api.delete(`/routes/${id}/`);
      return true;
    } catch (error) {
      console.error('Error deleting route:', error);
      return false;
    }
  }
}

export const routeService = new RouteService(); 
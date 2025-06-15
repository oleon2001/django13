import api from './api';

export interface Vehicle {
  id: number;
  name: string;
  plate: string;
  model: string;
  brand: string;
  year: number;
  status: string;
  lastUpdate: string;
  device_id?: number;
}

class VehicleService {
  async getAll(): Promise<Vehicle[]> {
    try {
      const response = await api.get('/vehicles/');
      return response.data;
    } catch (error) {
      console.error('Error fetching vehicles:', error);
      return [];
    }
  }

  async getById(id: number): Promise<Vehicle | null> {
    try {
      const response = await api.get(`/vehicles/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching vehicle:', error);
      return null;
    }
  }

  async create(data: Partial<Vehicle>): Promise<Vehicle | null> {
    try {
      const response = await api.post('/vehicles/', data);
      return response.data;
    } catch (error) {
      console.error('Error creating vehicle:', error);
      return null;
    }
  }

  async update(id: number, data: Partial<Vehicle>): Promise<Vehicle | null> {
    try {
      const response = await api.put(`/vehicles/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error('Error updating vehicle:', error);
      return null;
    }
  }

  async delete(id: number): Promise<boolean> {
    try {
      await api.delete(`/vehicles/${id}/`);
      return true;
    } catch (error) {
      console.error('Error deleting vehicle:', error);
      return false;
    }
  }

  async assignDevice(vehicleId: number, deviceId: number): Promise<boolean> {
    try {
      await api.post(`/vehicles/${vehicleId}/assign-device/`, { device_id: deviceId });
      return true;
    } catch (error) {
      console.error('Error assigning device to vehicle:', error);
      return false;
    }
  }
}

export const vehicleService = new VehicleService(); 
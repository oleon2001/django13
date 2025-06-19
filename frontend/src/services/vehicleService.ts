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
  device?: any; // Referencia al dispositivo GPS vinculado
  driver_id?: number;
  driver?: any; // Referencia al conductor asignado
}

class VehicleService {
  async getAll(): Promise<Vehicle[]> {
    try {
      const response = await api.get('/api/gps/vehicles/');
      return response.data;
    } catch (error) {
      console.error('Error fetching vehicles:', error);
      return [];
    }
  }

  async getById(id: number): Promise<Vehicle | null> {
    try {
      const response = await api.get(`/api/gps/vehicles/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching vehicle:', error);
      return null;
    }
  }

  async create(data: Partial<Vehicle>): Promise<Vehicle | null> {
    try {
      const response = await api.post('/api/gps/vehicles/', data);
      return response.data;
    } catch (error) {
      console.error('Error creating vehicle:', error);
      return null;
    }
  }

  async update(id: number, data: Partial<Vehicle>): Promise<Vehicle | null> {
    try {
      const response = await api.put(`/api/gps/vehicles/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error('Error updating vehicle:', error);
      return null;
    }
  }

  async delete(id: number): Promise<boolean> {
    try {
      await api.delete(`/api/gps/vehicles/${id}/`);
      return true;
    } catch (error) {
      console.error('Error deleting vehicle:', error);
      return false;
    }
  }

  async assignDevice(vehicleId: number, deviceId: number): Promise<boolean> {
    try {
      await api.post(`/api/gps/vehicles/${vehicleId}/assign-device/`, { device_id: deviceId });
      return true;
    } catch (error) {
      console.error('Error assigning device to vehicle:', error);
      return false;
    }
  }

  async assignDriver(vehicleId: number, driverId: number): Promise<boolean> {
    try {
      await api.post(`/api/gps/vehicles/${vehicleId}/assign-driver/`, { driver_id: driverId });
      return true;
    } catch (error) {
      console.error('Error assigning driver to vehicle:', error);
      return false;
    }
  }

  async getAvailableDevices(): Promise<any[]> {
    try {
      const response = await api.get('/api/gps/devices/?available=true');
      return response.data.devices || [];
    } catch (error) {
      console.error('Error fetching available devices:', error);
      return [];
    }
  }

  async getAvailableDrivers(): Promise<any[]> {
    try {
      const response = await api.get('/api/gps/drivers/?available=true');
      return response.data || [];
    } catch (error) {
      console.error('Error fetching available drivers:', error);
      return [];
    }
  }
}

export const vehicleService = new VehicleService(); 
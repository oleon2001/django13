import api from './api';
import { Driver, TicketLog, TicketDetail } from '../types';

export const driverService = {
  // Driver CRUD operations
  getDrivers: async (): Promise<Driver[]> => {
    const response = await api.get('/api/gps/drivers/');
    return response.data;
  },

  getDriver: async (id: number): Promise<Driver> => {
    const response = await api.get(`/api/gps/drivers/${id}/`);
    return response.data;
  },

  createDriver: async (driver: Partial<Driver>): Promise<Driver> => {
    const response = await api.post('/api/gps/drivers/', driver);
    return response.data;
  },

  updateDriver: async (id: number, driver: Partial<Driver>): Promise<Driver> => {
    const response = await api.patch(`/api/gps/drivers/${id}/`, driver);
    return response.data;
  },

  deleteDriver: async (id: number): Promise<void> => {
    await api.delete(`/api/gps/drivers/${id}/`);
  },

  // Ticket management
  getTicketLogs: async (): Promise<TicketLog[]> => {
    const response = await api.get('/api/gps/ticket-logs/');
    return response.data;
  },

  getTicketDetails: async (
    deviceId?: number,
    startDate?: string,
    endDate?: string
  ): Promise<TicketDetail[]> => {
    const params = new URLSearchParams();
    if (deviceId) params.append('device', deviceId.toString());
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get(`/api/gps/ticket-details/?${params.toString()}`);
    return response.data;
  },

  createTicketDetail: async (ticket: Partial<TicketDetail>): Promise<TicketDetail> => {
    const response = await api.post('/api/gps/ticket-details/', ticket);
    return response.data;
  },

  // Driver statistics
  getDriverStats: async (driverId?: number) => {
    const url = driverId ? `/api/gps/drivers/${driverId}/stats/` : '/api/gps/drivers/stats/';
    const response = await api.get(url);
    return response.data;
  },

  // License validation
  validateLicense: async (license: string): Promise<{ valid: boolean; expires?: string }> => {
    const response = await api.post('/api/gps/drivers/validate-license/', { license });
    return response.data;
  },

  // Device and Vehicle assignment
  assignDevice: async (driverId: number, deviceId: number): Promise<Driver> => {
    const response = await api.post(`/api/gps/drivers/${driverId}/assign-device/`, { device_id: deviceId });
    return response.data;
  },

  assignVehicle: async (driverId: number, vehicleId: number): Promise<Driver> => {
    const response = await api.post(`/api/gps/drivers/${driverId}/assign-vehicle/`, { vehicle_id: vehicleId });
    return response.data;
  },

  getAvailableDevices: async (): Promise<any[]> => {
    const response = await api.get('/api/gps/devices/?available=true');
    return response.data.devices || [];
  },

  getAvailableVehicles: async (): Promise<any[]> => {
    const response = await api.get('/api/gps/vehicles/?available=true');
    return response.data || [];
  },
}; 
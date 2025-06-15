import api from './api';
import { Driver, TicketLog, TicketDetail } from '../types';

export const driverService = {
  // Driver CRUD operations
  getDrivers: async (): Promise<Driver[]> => {
    const response = await api.get('/gps/drivers/');
    return response.data;
  },

  getDriver: async (id: number): Promise<Driver> => {
    const response = await api.get(`/gps/drivers/${id}/`);
    return response.data;
  },

  createDriver: async (driver: Partial<Driver>): Promise<Driver> => {
    const response = await api.post('/gps/drivers/', driver);
    return response.data;
  },

  updateDriver: async (id: number, driver: Partial<Driver>): Promise<Driver> => {
    const response = await api.patch(`/gps/drivers/${id}/`, driver);
    return response.data;
  },

  deleteDriver: async (id: number): Promise<void> => {
    await api.delete(`/gps/drivers/${id}/`);
  },

  // Ticket management
  getTicketLogs: async (): Promise<TicketLog[]> => {
    const response = await api.get('/gps/ticket-logs/');
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
    
    const response = await api.get(`/gps/ticket-details/?${params.toString()}`);
    return response.data;
  },

  createTicketDetail: async (ticket: Partial<TicketDetail>): Promise<TicketDetail> => {
    const response = await api.post('/gps/ticket-details/', ticket);
    return response.data;
  },

  // Driver statistics
  getDriverStats: async (driverId?: number) => {
    const url = driverId ? `/gps/drivers/${driverId}/stats/` : '/gps/drivers/stats/';
    const response = await api.get(url);
    return response.data;
  },

  // License validation
  validateLicense: async (license: string): Promise<{ valid: boolean; expires?: string }> => {
    const response = await api.post('/gps/drivers/validate-license/', { license });
    return response.data;
  },
}; 
import api from './api';
import { Device } from '../types';

export const deviceService = {
  getAll: async (): Promise<Device[]> => {
    const response = await api.get('/gps/devices/');
    return response.data;
  },

  getById: async (imei: number): Promise<Device> => {
    const response = await api.get(`/gps/devices/${imei}/`);
    return response.data;
  },

  getHistory: async (
    imei: number,
    startTime?: string,
    endTime?: string
  ): Promise<any> => {
    const params = { startTime, endTime };
    const response = await api.get(`/gps/devices/${imei}/history/`, { params });
    return response.data;
  },

  getEvents: async (imei: number, type?: string): Promise<any> => {
    const params = { type };
    const response = await api.get(`/gps/devices/${imei}/events/`, { params });
    return response.data;
  },

  sendCommand: async (
    imei: number,
    command: string,
    params?: Record<string, any>
  ): Promise<any> => {
    const response = await api.post(`/gps/devices/${imei}/command/`, {
      command,
      params,
    });
    return response.data;
  },
}; 
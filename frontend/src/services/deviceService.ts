import api from './api';
import { Device, DeviceEvent, DeviceData, NetworkEvent } from '../types';

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
  ): Promise<DeviceEvent[]> => {
    const params = { startTime, endTime };
    const response = await api.get(`/gps/devices/${imei}/history/`, { params });
    return response.data;
  },

  getEvents: async (imei: number, type?: string): Promise<DeviceEvent[]> => {
    const params = { type };
    const response = await api.get(`/gps/devices/${imei}/events/`, { params });
    return response.data;
  },

  getDeviceData: async (
    imei: number,
    dataType?: string,
    startTime?: string,
    endTime?: string
  ): Promise<DeviceData[]> => {
    const params = { dataType, startTime, endTime };
    const response = await api.get(`/gps/devices/${imei}/data/`, { params });
    return response.data;
  },

  getNetworkEvents: async (
    imei: number,
    eventType?: string,
    startTime?: string,
    endTime?: string
  ): Promise<NetworkEvent[]> => {
    const params = { eventType, startTime, endTime };
    const response = await api.get(`/gps/devices/${imei}/network-events/`, { params });
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

  updateDevice: async (imei: number, data: Partial<Device>): Promise<Device> => {
    const response = await api.patch(`/gps/devices/${imei}/`, data);
    return response.data;
  },

  createDevice: async (data: Partial<Device>): Promise<Device> => {
    const response = await api.post('/gps/devices/', data);
    return response.data;
  },

  deleteDevice: async (imei: number): Promise<void> => {
    await api.delete(`/gps/devices/${imei}/`);
  }
}; 
import api from './api';
import { Device, DeviceEvent, DeviceData, NetworkEvent, DeviceStats, ServerSMS, GPRSSession, UDPSession } from '../types';

export const deviceService = {
  getAll: async (): Promise<Device[]> => {
    const response = await api.get('/api/gps/devices/');
    // Extract the devices array from the response object
    return response.data.devices || [];
  },

  getById: async (imei: number): Promise<Device> => {
    const response = await api.get(`/api/gps/devices/${imei}/`);
    return response.data;
  },

  getHistory: async (
    imei: number,
    startTime?: string,
    endTime?: string
  ): Promise<DeviceEvent[]> => {
    const params = { startTime, endTime };
    const response = await api.get(`/api/gps/devices/${imei}/history/`, { params });
    return response.data;
  },

  getEvents: async (imei: number, type?: string): Promise<DeviceEvent[]> => {
    const params = { type };
    const response = await api.get(`/api/gps/devices/${imei}/events/`, { params });
    return response.data;
  },

  getDeviceData: async (
    imei: number,
    dataType?: string,
    startTime?: string,
    endTime?: string
  ): Promise<DeviceData[]> => {
    const params = { dataType, startTime, endTime };
    const response = await api.get(`/api/gps/devices/${imei}/data/`, { params });
    return response.data;
  },

  getNetworkEvents: async (
    imei: number,
    eventType?: string,
    startTime?: string,
    endTime?: string
  ): Promise<NetworkEvent[]> => {
    const params = { eventType, startTime, endTime };
    const response = await api.get(`/api/gps/devices/${imei}/network-events/`, { params });
    return response.data;
  },

  sendCommand: async (
    imei: number,
    command: string,
    params?: Record<string, any>
  ): Promise<any> => {
    const response = await api.post(`/api/gps/devices/${imei}/command/`, {
      command,
      params,
    });
    return response.data;
  },

  updateDevice: async (imei: number, data: Partial<Device>): Promise<Device> => {
    const response = await api.patch(`/api/gps/devices/${imei}/`, data);
    return response.data;
  },

  createDevice: async (data: Partial<Device>): Promise<Device> => {
    // Asegurarse de que el protocolo esté configurado
    const deviceData = {
      ...data,
      protocol: data.protocol || 'concox' // Default to concox if not specified
    };
    const response = await api.post('/api/gps/devices/', deviceData);
    return response.data;
  },

  deleteDevice: async (imei: number): Promise<void> => {
    await api.delete(`/api/gps/devices/${imei}/`);
  },

  getConnections: async (imei: number, startTime?: string, endTime?: string) => {
    const params = new URLSearchParams();
    if (startTime) params.append('start_time', startTime);
    if (endTime) params.append('end_time', endTime);
    
    const response = await api.get(`/api/gps/devices/${imei}/connections/?${params.toString()}`);
    return response.data;
  },

  getConnectionStats: async (imei: number) => {
    const response = await api.get(`/api/gps/devices/${imei}/connection-stats/`);
    return response.data;
  },

  getCurrentStatus: async (imei: number) => {
    const response = await api.get(`/api/gps/devices/${imei}/status/`);
    return response.data;
  },

  getActiveSessions: async () => {
    const response = await api.get('/api/gps/sessions/active/');
    return response.data;
  },

  cleanupSessions: async (days: number = 30) => {
    const response = await api.post('/api/gps/sessions/cleanup/', { days });
    return response.data;
  },

  getDeviceStats: async (imei?: number): Promise<DeviceStats[]> => {
    const url = imei ? `/api/gps/device-stats/?device=${imei}` : '/api/gps/device-stats/';
    const response = await api.get(url);
    return response.data;
  },

  createDeviceStats: async (stats: Partial<DeviceStats>): Promise<DeviceStats> => {
    const response = await api.post('/api/gps/device-stats/', stats);
    return response.data;
  },

  getSMSCommands: async (imei: number): Promise<ServerSMS[]> => {
    const response = await api.get(`/api/gps/devices/${imei}/sms-commands/`);
    return response.data;
  },

  sendSMS: async (imei: number, message: string, command: number = 1): Promise<ServerSMS> => {
    const response = await api.post(`/api/gps/devices/${imei}/send-sms/`, {
      message,
      command,
      direction: 0
    });
    return response.data;
  },

  assignRoute: async (imei: number, route: number, economico?: number): Promise<Device> => {
    const response = await api.patch(`/api/gps/devices/${imei}/assign-route/`, {
      route,
      economico
    });
    return response.data;
  },

  getDevicesByRoute: async (route: number): Promise<Device[]> => {
    const response = await api.get(`/api/gps/devices/?route=${route}`);
    // Extract the devices array from the response object
    return response.data.devices || [];
  },

  getGPRSSessions: async (imei: number): Promise<GPRSSession[]> => {
    const response = await api.get(`/api/gps/devices/${imei}/gprs-sessions/`);
    return response.data;
  },

  getUDPSession: async (imei: number): Promise<UDPSession | null> => {
    const response = await api.get(`/api/gps/devices/${imei}/udp-session/`);
    return response.data;
  },

  createUDPSession: async (imei: number, host: string, port: number): Promise<UDPSession> => {
    const response = await api.post(`/api/gps/devices/${imei}/create-udp-session/`, {
      host,
      port
    });
    return response.data;
  },

  getDeviceHarnesses: async () => {
    const response = await api.get('/api/gps/device-harnesses/');
    return response.data;
  },

  assignHarness: async (imei: number, harnessId: number): Promise<Device> => {
    const response = await api.patch(`/api/gps/devices/${imei}/assign-harness/`, {
      harness: harnessId
    });
    return response.data;
  },

  getDeviceHealth: async (imei: number) => {
    const response = await api.get(`/api/gps/devices/${imei}/health/`);
    return response.data;
  },

  resetDevice: async (imei: number): Promise<{ status: string }> => {
    const response = await api.post(`/api/gps/devices/${imei}/reset/`);
    return response.data;
  },

  updateFirmware: async (imei: number, firmwareFile: string): Promise<{ status: string }> => {
    const response = await api.post(`/api/gps/devices/${imei}/update-firmware/`, {
      firmware_file: firmwareFile
    });
    return response.data;
  },

  getFirmwareHistory: async (imei: number) => {
    const response = await api.get(`/api/gps/devices/${imei}/firmware-history/`);
    return response.data;
  },

  bulkUpdateDevices: async (devices: Array<{ imei: number; data: Partial<Device> }>) => {
    const response = await api.patch('/api/gps/devices/bulk-update/', { devices });
    return response.data;
  },

  exportDeviceData: async (
    imei: number,
    startDate: string,
    endDate: string,
    format: 'csv' | 'json' = 'csv'
  ): Promise<Blob> => {
    const response = await api.get(`/api/gps/devices/${imei}/export/`, {
      params: { start_date: startDate, end_date: endDate, format },
      responseType: 'blob'
    });
    return response.data;
  },

  testConnection: async (imei: number): Promise<any> => {
    const response = await api.post(`/api/gps/devices/${imei}/test-connection/`);
    return response.data;
  },

  checkAllDevicesStatus: async (timeout: number = 60): Promise<any> => {
    const response = await api.post('/api/gps/devices/check-status/', { timeout });
    return response.data;
  },

  // Real-time position methods
  getRealTimePositions: async () => {
    const response = await api.get('/api/gps/positions/real-time/');
    return response.data;
  },

  getDeviceTrail: async (imei: number, hours: number = 24) => {
    const response = await api.get(`/api/gps/devices/${imei}/trail/?hours=${hours}`);
    return response.data;
  },

  // Polling method for real-time updates
  startRealTimePolling: (callback: (positions: any[]) => void, interval: number = 5000) => {
    let isActive = true;
    let timeoutId: NodeJS.Timeout | null = null;
    
    const poll = async () => {
      if (!isActive) return;
      
      try {
        const data = await deviceService.getRealTimePositions();
        if (isActive && data && data.positions) {
          // Use a small timeout to prevent synchronous updates that could cause suspense
          timeoutId = setTimeout(() => {
            if (isActive) {
              callback(data.positions || []);
            }
          }, 50); // Small delay to allow React to process the update
        }
      } catch (error) {
        console.error('Error polling real-time positions:', error);
        // Don't callback with error data to avoid state inconsistencies
        // Add exponential backoff on errors
        if (isActive) {
          const backoffDelay = Math.min(interval * 2, 30000); // Max 30 seconds
          timeoutId = setTimeout(() => {
            if (isActive) poll();
          }, backoffDelay);
          return;
        }
      }
      
      // Schedule next poll
      if (isActive) {
        timeoutId = setTimeout(poll, interval);
      }
    };

    // Initial call with delay to avoid immediate suspense
    timeoutId = setTimeout(poll, 200);
    
    // Return cleanup function
    return () => {
      isActive = false;
      if (timeoutId) {
        clearTimeout(timeoutId);
        timeoutId = null;
      }
    };
  },
}; 
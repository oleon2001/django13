import api from './api';
import { PressureSensor, PressureReading, AlarmLog } from '../types';

export const sensorService = {
  // Pressure Sensors
  getPressureSensors: async (deviceId?: number): Promise<PressureSensor[]> => {
    const url = deviceId ? `/api/gps/pressure-sensors/?device=${deviceId}` : '/api/gps/pressure-sensors/';
    const response = await api.get(url);
    return response.data;
  },

  getPressureSensor: async (id: number): Promise<PressureSensor> => {
    const response = await api.get(`/api/gps/pressure-sensors/${id}/`);
    return response.data;
  },

  createPressureSensor: async (data: Partial<PressureSensor>): Promise<PressureSensor> => {
    const response = await api.post('/api/gps/pressure-sensors/', data);
    return response.data;
  },

  updatePressureSensor: async (id: number, data: Partial<PressureSensor>): Promise<PressureSensor> => {
    const response = await api.patch(`/api/gps/pressure-sensors/${id}/`, data);
    return response.data;
  },

  deletePressureSensor: async (id: number): Promise<void> => {
    await api.delete(`/api/gps/pressure-sensors/${id}/`);
  },

  // Pressure Readings
  getPressureReadings: async (
    sensorId?: number,
    startDate?: string,
    endDate?: string
  ): Promise<PressureReading[]> => {
    const params = new URLSearchParams();
    if (sensorId) params.append('sensor', sensorId.toString());
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get(`/api/gps/pressure-readings/?${params.toString()}`);
    return response.data;
  },

  // Alarm Logs
  getAlarmLogs: async (
    deviceId?: number,
    startDate?: string,
    endDate?: string
  ): Promise<AlarmLog[]> => {
    const params = new URLSearchParams();
    if (deviceId) params.append('device', deviceId.toString());
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get(`/api/gps/alarm-logs/?${params.toString()}`);
    return response.data;
  },

  getActiveAlarms: async (): Promise<AlarmLog[]> => {
    const response = await api.get('/api/gps/alarm-logs/active/');
    return response.data;
  },

  // Sensor Statistics
  getSensorStats: async (deviceId?: number) => {
    const url = deviceId ? `/api/gps/sensors/${deviceId}/stats/` : '/api/gps/sensors/stats/';
    const response = await api.get(url);
    return response.data;
  },

  // Real-time monitoring
  getSensorHealth: async (deviceId: number) => {
    const response = await api.get(`/api/gps/devices/${deviceId}/sensor-health/`);
    return response.data;
  },

  // Calibration
  calibrateSensor: async (sensorId: number, calibrationData: any) => {
    const response = await api.post(`/api/gps/pressure-sensors/${sensorId}/calibrate/`, calibrationData);
    return response.data;
  },

  // Export sensor data
  exportSensorData: async (
    deviceId: number,
    startDate: string,
    endDate: string,
    format: 'csv' | 'json' = 'csv'
  ): Promise<Blob> => {
    const response = await api.get(`/api/gps/devices/${deviceId}/sensor-data/export/`, {
      params: { start_date: startDate, end_date: endDate, format },
      responseType: 'blob'
    });
    return response.data;
  },

  // Sensor alerts configuration
  getSensorAlertConfig: async (sensorId: number) => {
    const response = await api.get(`/api/gps/pressure-sensors/${sensorId}/alert-config/`);
    return response.data;
  },

  updateSensorAlertConfig: async (sensorId: number, config: any) => {
    const response = await api.patch(`/api/gps/pressure-sensors/${sensorId}/alert-config/`, config);
    return response.data;
  },
}; 
import api from './api';
import { PressureSensor, PressureReading, AlarmLog } from '../types';

export const sensorService = {
  // Pressure Sensor operations
  getPressureSensors: async (deviceId?: number): Promise<PressureSensor[]> => {
    const url = deviceId ? `/gps/pressure-sensors/?device=${deviceId}` : '/gps/pressure-sensors/';
    const response = await api.get(url);
    return response.data;
  },

  getPressureSensor: async (id: number): Promise<PressureSensor> => {
    const response = await api.get(`/gps/pressure-sensors/${id}/`);
    return response.data;
  },

  createPressureSensor: async (sensor: Partial<PressureSensor>): Promise<PressureSensor> => {
    const response = await api.post('/gps/pressure-sensors/', sensor);
    return response.data;
  },

  updatePressureSensor: async (id: number, sensor: Partial<PressureSensor>): Promise<PressureSensor> => {
    const response = await api.patch(`/gps/pressure-sensors/${id}/`, sensor);
    return response.data;
  },

  deletePressureSensor: async (id: number): Promise<void> => {
    await api.delete(`/gps/pressure-sensors/${id}/`);
  },

  // Pressure Readings
  getPressureReadings: async (
    deviceId?: number,
    sensorSerial?: string,
    startDate?: string,
    endDate?: string
  ): Promise<PressureReading[]> => {
    const params = new URLSearchParams();
    if (deviceId) params.append('device', deviceId.toString());
    if (sensorSerial) params.append('sensor', sensorSerial);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get(`/gps/pressure-readings/?${params.toString()}`);
    return response.data;
  },

  getLatestReading: async (deviceId: number, sensorSerial: string): Promise<PressureReading> => {
    const response = await api.get(`/gps/pressure-readings/latest/?device=${deviceId}&sensor=${sensorSerial}`);
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
    
    const response = await api.get(`/gps/alarm-logs/?${params.toString()}`);
    return response.data;
  },

  getActiveAlarms: async (): Promise<AlarmLog[]> => {
    const response = await api.get('/gps/alarm-logs/active/');
    return response.data;
  },

  // Sensor Statistics
  getSensorStats: async (deviceId?: number) => {
    const url = deviceId ? `/gps/sensors/${deviceId}/stats/` : '/gps/sensors/stats/';
    const response = await api.get(url);
    return response.data;
  },

  // Real-time monitoring
  getSensorHealth: async (deviceId: number) => {
    const response = await api.get(`/gps/devices/${deviceId}/sensor-health/`);
    return response.data;
  },

  // Calibration
  calibrateSensor: async (sensorId: number, calibrationData: any) => {
    const response = await api.post(`/gps/pressure-sensors/${sensorId}/calibrate/`, calibrationData);
    return response.data;
  },

  // Export sensor data
  exportSensorData: async (
    deviceId: number,
    startDate: string,
    endDate: string,
    format: 'csv' | 'json' = 'csv'
  ): Promise<Blob> => {
    const response = await api.get(`/gps/devices/${deviceId}/sensor-data/export/`, {
      params: { start_date: startDate, end_date: endDate, format },
      responseType: 'blob'
    });
    return response.data;
  },

  // Sensor alerts configuration
  getSensorAlertConfig: async (sensorId: number) => {
    const response = await api.get(`/gps/pressure-sensors/${sensorId}/alert-config/`);
    return response.data;
  },

  updateSensorAlertConfig: async (sensorId: number, config: any) => {
    const response = await api.patch(`/gps/pressure-sensors/${sensorId}/alert-config/`, config);
    return response.data;
  },
}; 
import { useState, useEffect, useCallback } from 'react';
import { Device } from '../types';
import { deviceService } from '../services/deviceService';

interface DeviceStatusOptions {
  checkInterval?: number; // Intervalo en ms para verificar el estado
  heartbeatTimeout?: number; // Tiempo en ms para considerar un dispositivo offline
  autoRefresh?: boolean; // Si debe refrescar automáticamente
}

export const useDeviceStatus = (options: DeviceStatusOptions = {}) => {
  const {
    checkInterval = 30000, // 30 segundos por defecto
    heartbeatTimeout = 60000, // 1 minuto por defecto
    autoRefresh = true
  } = options;

  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Función para verificar si un dispositivo está offline basado en su último heartbeat
  const isDeviceOffline = useCallback((device: Device): boolean => {
    if (!device.last_heartbeat) return true;
    
    const lastHeartbeat = new Date(device.last_heartbeat);
    const now = new Date();
    const timeDiff = now.getTime() - lastHeartbeat.getTime();
    
    return timeDiff > heartbeatTimeout;
  }, [heartbeatTimeout]);

  // Función para actualizar el estado de un dispositivo basado en su heartbeat
  const updateDeviceStatus = useCallback(async (device: Device): Promise<Device> => {
    const shouldBeOffline = isDeviceOffline(device);
    const currentStatus = device.connection_status?.toUpperCase();
    
    // Si el dispositivo debería estar offline pero está marcado como online
    if (shouldBeOffline && currentStatus === 'ONLINE') {
      try {
        // Actualizar el estado en el backend
        await deviceService.updateDevice(device.imei, { connection_status: 'OFFLINE' });
        return { ...device, connection_status: 'OFFLINE' };
      } catch (error) {
        console.error(`Error updating device ${device.imei} status:`, error);
        return device;
      }
    }
    
    return device;
  }, [isDeviceOffline]);

  // Función para cargar todos los dispositivos
  const fetchDevices = useCallback(async (): Promise<Device[]> => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await deviceService.getAll();
      
      if (!Array.isArray(data)) {
        throw new Error('Formato de datos inválido recibido del servidor');
      }

      // Filtrar dispositivos con IMEI válidos (números no nulos)
      const validDevices = data.filter(device => 
        device && 
        device.imei && 
        typeof device.imei === 'number' && 
        !isNaN(device.imei) &&
        device.imei > 0
      );

      // Verificar y actualizar el estado de cada dispositivo válido
      const updatedDevices = await Promise.all(
        validDevices.map(device => updateDeviceStatus(device))
      );

      setDevices(updatedDevices);
      return updatedDevices;
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || 'Error al cargar los dispositivos';
      setError(errorMessage);
      console.error('Error loading devices:', err);
      return [];
    } finally {
      setLoading(false);
    }
  }, [updateDeviceStatus]);

  // Función para probar la conexión de un dispositivo
  const testDeviceConnection = useCallback(async (imei: number): Promise<{
    success: boolean;
    message: string;
    status: string;
    device?: Device;
  }> => {
    try {
      const result = await deviceService.testConnection(imei);
      
      // Actualizar el dispositivo en la lista local
      setDevices(prevDevices => 
        prevDevices.map(device => 
          device.imei === imei 
            ? { ...device, connection_status: result.status }
            : device
        )
      );

      return {
        success: result.success,
        message: result.message,
        status: result.status,
        device: devices.find(d => d.imei === imei)
      };
      
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || error.message || 'Error desconocido';
      
      // Marcar el dispositivo como offline en caso de error
      setDevices(prevDevices => 
        prevDevices.map(device => 
          device.imei === imei 
            ? { ...device, connection_status: 'OFFLINE' }
            : device
        )
      );

      return {
        success: false,
        message: errorMessage,
        status: 'OFFLINE'
      };
    }
  }, [devices]);

  // Función para actualizar un dispositivo específico
  const updateDevice = useCallback(async (imei: number, updates: Partial<Device>): Promise<Device | null> => {
    try {
      const updatedDevice = await deviceService.updateDevice(imei, updates);
      
      setDevices(prevDevices => 
        prevDevices.map(device => 
          device.imei === imei ? { ...device, ...updatedDevice } : device
        )
      );
      
      return updatedDevice;
    } catch (error: any) {
      setError(error.response?.data?.error || error.message || 'Error al actualizar dispositivo');
      return null;
    }
  }, []);

  // Función para crear un nuevo dispositivo
  const createDevice = useCallback(async (deviceData: Partial<Device>): Promise<Device | null> => {
    try {
      const newDevice = await deviceService.createDevice(deviceData);
      setDevices(prevDevices => [...prevDevices, newDevice]);
      return newDevice;
    } catch (error: any) {
      setError(error.response?.data?.error || error.message || 'Error al crear dispositivo');
      return null;
    }
  }, []);

  // Función para eliminar un dispositivo
  const deleteDevice = useCallback(async (imei: number): Promise<boolean> => {
    try {
      // Verificar si el dispositivo existe en la lista local antes de intentar eliminarlo
      const deviceExists = devices.some(device => device.imei === imei);
      if (!deviceExists) {
        setError(`Dispositivo con IMEI ${imei} no encontrado en la lista actual`);
        return false;
      }

      await deviceService.deleteDevice(imei);
      setDevices(prevDevices => prevDevices.filter(device => device.imei !== imei));
      return true;
    } catch (error: any) {
      // Si es un error 404, el dispositivo ya no existe, removerlo de la lista local
      if (error.response?.status === 404) {
        setDevices(prevDevices => prevDevices.filter(device => device.imei !== imei));
        setError(`Dispositivo con IMEI ${imei} ya no existe en el servidor`);
        return true; // Retornar true porque el objetivo (eliminar) se cumplió
      }
      
      setError(error.response?.data?.error || error.message || 'Error al eliminar dispositivo');
      return false;
    }
  }, [devices]);

  // Función para verificar el estado de todos los dispositivos
      const checkAllDevicesStatus = useCallback(async (timeout: number = 60): Promise<{
    success: boolean;
    message: string;
    devicesUpdated: number;
    stats: any;
  }> => {
    try {
      const result = await deviceService.checkAllDevicesStatus(timeout);
      
      // Recargar los dispositivos después de la verificación
      await fetchDevices();
      
      return {
        success: true,
        message: result.message,
        devicesUpdated: result.devices_updated_to_offline,
        stats: result.current_stats
      };
    } catch (error: any) {
      setError(error.response?.data?.error || error.message || 'Error al verificar estado de dispositivos');
      return {
        success: false,
        message: error.message || 'Error desconocido',
        devicesUpdated: 0,
        stats: null
      };
    }
  }, [fetchDevices]);

  // Efecto para cargar dispositivos inicialmente
  useEffect(() => {
    fetchDevices();
  }, [fetchDevices]);

  // Efecto para refrescar automáticamente
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchDevices();
    }, checkInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, checkInterval, fetchDevices]);

  // Estadísticas calculadas
  const stats = {
    total: devices.length,
    online: devices.filter(d => d.connection_status?.toUpperCase() === 'ONLINE').length,
    offline: devices.filter(d => d.connection_status?.toUpperCase() === 'OFFLINE').length,
    unknown: devices.filter(d => !d.connection_status || d.connection_status.toUpperCase() === 'UNKNOWN').length
  };

  return {
    devices,
    loading,
    error,
    stats,
    fetchDevices,
    testDeviceConnection,
    updateDevice,
    createDevice,
    deleteDevice,
    checkAllDevicesStatus,
    isDeviceOffline,
    setError
  };
}; 
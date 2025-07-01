import { useCrudOperations, useApiQuery, useApiMutation, useRealtimeQuery } from './useApi';
import { Device, DeviceStatus, FirmwareHistory, DeviceData } from '../types/unified';
import { deviceService } from '../services/deviceService';

// ============================================================================
// DEVICE HOOKS - Hooks específicos para dispositivos
// ============================================================================

/**
 * Hook para operaciones CRUD de dispositivos
 */
export const useDeviceCrud = () => {
  return useCrudOperations<Device>('devices', {
    getAll: deviceService.getAllDevices,
    getById: deviceService.getDevice,
    create: deviceService.createDevice,
    update: deviceService.updateDevice,
    delete: deviceService.deleteDevice,
  });
};

/**
 * Hook para obtener el historial de firmware de un dispositivo
 */
export const useDeviceFirmwareHistory = (deviceId: number) => {
  return useApiQuery(
    ['devices', 'firmware-history', deviceId.toString()],
    () => deviceService.getFirmwareHistory(deviceId),
    {
      enabled: !!deviceId,
    }
  );
};

/**
 * Hook para actualización masiva de dispositivos
 */
export const useBulkUpdateDevices = () => {
  return useApiMutation(
    deviceService.bulkUpdateDevices,
    {
      successMessage: 'Devices updated successfully',
      errorMessage: 'Failed to update devices',
      invalidateQueries: ['devices'],
    }
  );
};

/**
 * Hook para exportar datos de dispositivos
 */
export const useExportDeviceData = () => {
  return useApiMutation(
    deviceService.exportDeviceData,
    {
      successMessage: 'Device data exported successfully',
      errorMessage: 'Failed to export device data',
    }
  );
};

/**
 * Hook para probar conexión de dispositivo
 */
export const useTestDeviceConnection = () => {
  return useApiMutation(
    deviceService.testConnection,
    {
      successMessage: 'Connection test successful',
      errorMessage: 'Connection test failed',
    }
  );
};

/**
 * Hook para verificar estado de todos los dispositivos
 */
export const useCheckAllDevicesStatus = () => {
  return useApiMutation(
    deviceService.checkAllDevicesStatus,
    {
      successMessage: 'Device status check completed',
      errorMessage: 'Failed to check device status',
      invalidateQueries: ['devices'],
    }
  );
};

/**
 * Hook para seguimiento en tiempo real de posición
 */
export const useRealTimePosition = (deviceId: number, interval: number = 5000) => {
  return useRealtimeQuery(
    ['devices', 'position', deviceId.toString()],
    () => deviceService.getRealTimePosition(deviceId),
    interval,
    {
      enabled: !!deviceId,
    }
  );
};

/**
 * Hook para polling de actualizaciones de dispositivo
 */
export const useDevicePolling = (deviceId: number, interval: number = 10000) => {
  return useRealtimeQuery(
    ['devices', 'polling', deviceId.toString()],
    () => deviceService.pollDeviceUpdates(deviceId),
    interval,
    {
      enabled: !!deviceId,
    }
  );
};

/**
 * Hook para obtener dispositivos por estado
 */
export const useDevicesByStatus = (status: DeviceStatus) => {
  return useApiQuery(
    ['devices', 'status', status],
    () => deviceService.getDevicesByStatus(status),
    {
      enabled: !!status,
    }
  );
};

/**
 * Hook para obtener dispositivos por tipo
 */
export const useDevicesByType = (type: string) => {
  return useApiQuery(
    ['devices', 'type', type],
    () => deviceService.getDevicesByType(type),
    {
      enabled: !!type,
    }
  );
};

/**
 * Hook para obtener dispositivos por ubicación
 */
export const useDevicesByLocation = (latitude: number, longitude: number, radius: number = 10) => {
  return useApiQuery(
    ['devices', 'location', latitude.toString(), longitude.toString(), radius.toString()],
    () => deviceService.getDevicesByLocation(latitude, longitude, radius),
    {
      enabled: !!(latitude && longitude),
    }
  );
};

/**
 * Hook para obtener estadísticas de dispositivos
 */
export const useDeviceStatistics = () => {
  return useApiQuery(
    ['devices', 'statistics'],
    deviceService.getDeviceStatistics,
    {
      refetchInterval: 30000, // Actualizar cada 30 segundos
    }
  );
};

/**
 * Hook para obtener dispositivos con alertas
 */
export const useDevicesWithAlerts = () => {
  return useApiQuery(
    ['devices', 'alerts'],
    deviceService.getDevicesWithAlerts,
    {
      refetchInterval: 15000, // Actualizar cada 15 segundos
    }
  );
};

/**
 * Hook para obtener dispositivos offline
 */
export const useOfflineDevices = () => {
  return useApiQuery(
    ['devices', 'offline'],
    deviceService.getOfflineDevices,
    {
      refetchInterval: 20000, // Actualizar cada 20 segundos
    }
  );
};

/**
 * Hook para obtener dispositivos con batería baja
 */
export const useLowBatteryDevices = () => {
  return useApiQuery(
    ['devices', 'low-battery'],
    deviceService.getLowBatteryDevices,
    {
      refetchInterval: 25000, // Actualizar cada 25 segundos
    }
  );
};

/**
 * Hook para obtener dispositivos con señal débil
 */
export const useWeakSignalDevices = () => {
  return useApiQuery(
    ['devices', 'weak-signal'],
    deviceService.getWeakSignalDevices,
    {
      refetchInterval: 30000, // Actualizar cada 30 segundos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de GPS
 */
export const useGpsIssueDevices = () => {
  return useApiQuery(
    ['devices', 'gps-issues'],
    deviceService.getGpsIssueDevices,
    {
      refetchInterval: 45000, // Actualizar cada 45 segundos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de conectividad
 */
export const useConnectivityIssueDevices = () => {
  return useApiQuery(
    ['devices', 'connectivity-issues'],
    deviceService.getConnectivityIssueDevices,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de temperatura
 */
export const useTemperatureIssueDevices = () => {
  return useApiQuery(
    ['devices', 'temperature-issues'],
    deviceService.getTemperatureIssueDevices,
    {
      refetchInterval: 30000, // Actualizar cada 30 segundos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de memoria
 */
export const useMemoryIssueDevices = () => {
  return useApiQuery(
    ['devices', 'memory-issues'],
    deviceService.getMemoryIssueDevices,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de alimentación
 */
export const usePowerIssueDevices = () => {
  return useApiQuery(
    ['devices', 'power-issues'],
    deviceService.getPowerIssueDevices,
    {
      refetchInterval: 30000, // Actualizar cada 30 segundos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de sensores
 */
export const useSensorIssueDevices = () => {
  return useApiQuery(
    ['devices', 'sensor-issues'],
    deviceService.getSensorIssueDevices,
    {
      refetchInterval: 45000, // Actualizar cada 45 segundos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de firmware
 */
export const useFirmwareIssueDevices = () => {
  return useApiQuery(
    ['devices', 'firmware-issues'],
    deviceService.getFirmwareIssueDevices,
    {
      refetchInterval: 120000, // Actualizar cada 2 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de configuración
 */
export const useConfigurationIssueDevices = () => {
  return useApiQuery(
    ['devices', 'configuration-issues'],
    deviceService.getConfigurationIssueDevices,
    {
      refetchInterval: 180000, // Actualizar cada 3 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de seguridad
 */
export const useSecurityIssueDevices = () => {
  return useApiQuery(
    ['devices', 'security-issues'],
    deviceService.getSecurityIssueDevices,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de red
 */
export const useNetworkIssueDevices = () => {
  return useApiQuery(
    ['devices', 'network-issues'],
    deviceService.getNetworkIssueDevices,
    {
      refetchInterval: 30000, // Actualizar cada 30 segundos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de sincronización
 */
export const useSyncIssueDevices = () => {
  return useApiQuery(
    ['devices', 'sync-issues'],
    deviceService.getSyncIssueDevices,
    {
      refetchInterval: 90000, // Actualizar cada 1.5 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de calibración
 */
export const useCalibrationIssueDevices = () => {
  return useApiQuery(
    ['devices', 'calibration-issues'],
    deviceService.getCalibrationIssueDevices,
    {
      refetchInterval: 300000, // Actualizar cada 5 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de mantenimiento
 */
export const useMaintenanceIssueDevices = () => {
  return useApiQuery(
    ['devices', 'maintenance-issues'],
    deviceService.getMaintenanceIssueDevices,
    {
      refetchInterval: 360000, // Actualizar cada 6 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de licencia
 */
export const useLicenseIssueDevices = () => {
  return useApiQuery(
    ['devices', 'license-issues'],
    deviceService.getLicenseIssueDevices,
    {
      refetchInterval: 600000, // Actualizar cada 10 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de actualización
 */
export const useUpdateIssueDevices = () => {
  return useApiQuery(
    ['devices', 'update-issues'],
    deviceService.getUpdateIssueDevices,
    {
      refetchInterval: 300000, // Actualizar cada 5 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de backup
 */
export const useBackupIssueDevices = () => {
  return useApiQuery(
    ['devices', 'backup-issues'],
    deviceService.getBackupIssueDevices,
    {
      refetchInterval: 600000, // Actualizar cada 10 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de restauración
 */
export const useRestoreIssueDevices = () => {
  return useApiQuery(
    ['devices', 'restore-issues'],
    deviceService.getRestoreIssueDevices,
    {
      refetchInterval: 600000, // Actualizar cada 10 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de migración
 */
export const useMigrationIssueDevices = () => {
  return useApiQuery(
    ['devices', 'migration-issues'],
    deviceService.getMigrationIssueDevices,
    {
      refetchInterval: 900000, // Actualizar cada 15 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de integración
 */
export const useIntegrationIssueDevices = () => {
  return useApiQuery(
    ['devices', 'integration-issues'],
    deviceService.getIntegrationIssueDevices,
    {
      refetchInterval: 300000, // Actualizar cada 5 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de API
 */
export const useApiIssueDevices = () => {
  return useApiQuery(
    ['devices', 'api-issues'],
    deviceService.getApiIssueDevices,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de autenticación
 */
export const useAuthIssueDevices = () => {
  return useApiQuery(
    ['devices', 'auth-issues'],
    deviceService.getAuthIssueDevices,
    {
      refetchInterval: 120000, // Actualizar cada 2 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de autorización
 */
export const useAuthorizationIssueDevices = () => {
  return useApiQuery(
    ['devices', 'authorization-issues'],
    deviceService.getAuthorizationIssueDevices,
    {
      refetchInterval: 120000, // Actualizar cada 2 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de rate limiting
 */
export const useRateLimitIssueDevices = () => {
  return useApiQuery(
    ['devices', 'rate-limit-issues'],
    deviceService.getRateLimitIssueDevices,
    {
      refetchInterval: 300000, // Actualizar cada 5 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de timeout
 */
export const useTimeoutIssueDevices = () => {
  return useApiQuery(
    ['devices', 'timeout-issues'],
    deviceService.getTimeoutIssueDevices,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de timeout de conexión
 */
export const useConnectionTimeoutIssueDevices = () => {
  return useApiQuery(
    ['devices', 'connection-timeout-issues'],
    deviceService.getConnectionTimeoutIssueDevices,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de timeout de respuesta
 */
export const useResponseTimeoutIssueDevices = () => {
  return useApiQuery(
    ['devices', 'response-timeout-issues'],
    deviceService.getResponseTimeoutIssueDevices,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de timeout de procesamiento
 */
export const useProcessingTimeoutIssueDevices = () => {
  return useApiQuery(
    ['devices', 'processing-timeout-issues'],
    deviceService.getProcessingTimeoutIssueDevices,
    {
      refetchInterval: 120000, // Actualizar cada 2 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de timeout de sincronización
 */
export const useSyncTimeoutIssueDevices = () => {
  return useApiQuery(
    ['devices', 'sync-timeout-issues'],
    deviceService.getSyncTimeoutIssueDevices,
    {
      refetchInterval: 180000, // Actualizar cada 3 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de timeout de actualización
 */
export const useUpdateTimeoutIssueDevices = () => {
  return useApiQuery(
    ['devices', 'update-timeout-issues'],
    deviceService.getUpdateTimeoutIssueDevices,
    {
      refetchInterval: 300000, // Actualizar cada 5 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de timeout de backup
 */
export const useBackupTimeoutIssueDevices = () => {
  return useApiQuery(
    ['devices', 'backup-timeout-issues'],
    deviceService.getBackupTimeoutIssueDevices,
    {
      refetchInterval: 600000, // Actualizar cada 10 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de timeout de restauración
 */
export const useRestoreTimeoutIssueDevices = () => {
  return useApiQuery(
    ['devices', 'restore-timeout-issues'],
    deviceService.getRestoreTimeoutIssueDevices,
    {
      refetchInterval: 600000, // Actualizar cada 10 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de timeout de migración
 */
export const useMigrationTimeoutIssueDevices = () => {
  return useApiQuery(
    ['devices', 'migration-timeout-issues'],
    deviceService.getMigrationTimeoutIssueDevices,
    {
      refetchInterval: 900000, // Actualizar cada 15 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de timeout de integración
 */
export const useIntegrationTimeoutIssueDevices = () => {
  return useApiQuery(
    ['devices', 'integration-timeout-issues'],
    deviceService.getIntegrationTimeoutIssueDevices,
    {
      refetchInterval: 300000, // Actualizar cada 5 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de timeout de API
 */
export const useApiTimeoutIssueDevices = () => {
  return useApiQuery(
    ['devices', 'api-timeout-issues'],
    deviceService.getApiTimeoutIssueDevices,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de timeout de autenticación
 */
export const useAuthTimeoutIssueDevices = () => {
  return useApiQuery(
    ['devices', 'auth-timeout-issues'],
    deviceService.getAuthTimeoutIssueDevices,
    {
      refetchInterval: 120000, // Actualizar cada 2 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de timeout de autorización
 */
export const useAuthorizationTimeoutIssueDevices = () => {
  return useApiQuery(
    ['devices', 'authorization-timeout-issues'],
    deviceService.getAuthorizationTimeoutIssueDevices,
    {
      refetchInterval: 120000, // Actualizar cada 2 minutos
    }
  );
};

/**
 * Hook para obtener dispositivos con problemas de timeout de rate limiting
 */
export const useRateLimitTimeoutIssueDevices = () => {
  return useApiQuery(
    ['devices', 'rate-limit-timeout-issues'],
    deviceService.getRateLimitTimeoutIssueDevices,
    {
      refetchInterval: 300000, // Actualizar cada 5 minutos
    }
  );
}; 
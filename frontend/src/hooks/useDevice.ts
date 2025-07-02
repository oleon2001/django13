import { Device } from '../types/unified';
import { deviceService } from '../services/deviceService';
import { useQueryClient, useQuery, useMutation } from '@tanstack/react-query';
import { PaginationParams } from '../types/unified';

// ============================================================================
// DEVICE HOOKS - Hooks específicos para dispositivos
// ============================================================================

/**
 * Hook para operaciones CRUD de dispositivos
 */
export const useDeviceCrud = () => {
  const queryClient = useQueryClient();

  const useGetAll = (params: PaginationParams = {}) => {
    return useQuery({
      queryKey: ['devices', 'list', params],
      queryFn: () => deviceService.getAll(),
    });
  };

  const useGetById = (id: number) => {
    return useQuery({
      queryKey: ['devices', 'detail', id.toString()],
      queryFn: () => deviceService.getById(id),
      enabled: !!id,
    });
  };

  const useCreate = () => {
    return useMutation({
      mutationFn: (data: Partial<Device>) => deviceService.createDevice(data),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['devices'] });
      },
    });
  };

  const useUpdate = () => {
    return useMutation({
      mutationFn: ({ id, data }: { id: number; data: Partial<Device> }) => 
        deviceService.updateDevice(id, data),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['devices'] });
      },
    });
  };

  const useDelete = () => {
    return useMutation({
      mutationFn: (id: number) => deviceService.deleteDevice(id),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['devices'] });
      },
    });
  };

  return {
    useGetAll,
    useGetById,
    useCreate,
    useUpdate,
    useDelete,
  };
};

/**
 * Hook para obtener el historial de firmware de un dispositivo
 */
export const useDeviceFirmwareHistory = (deviceId: number) => {
  return useQuery({
    queryKey: ['devices', 'firmware-history', deviceId.toString()],
    queryFn: () => deviceService.getFirmwareHistory(deviceId),
    enabled: !!deviceId,
  });
};

/**
 * Hook para obtener dispositivos por ruta
 */
export const useDevicesByRoute = (route: number) => {
  return useQuery({
    queryKey: ['devices', 'route', route.toString()],
    queryFn: () => deviceService.getDevicesByRoute(route),
    enabled: !!route,
  });
};

/**
 * Hook para obtener estadísticas de dispositivos
 */
export const useDeviceStats = (deviceId?: number) => {
  return useQuery({
    queryKey: ['devices', 'stats', deviceId?.toString()],
    queryFn: () => deviceService.getDeviceStats(deviceId),
    refetchInterval: 30000, // Actualizar cada 30 segundos
  });
};

/**
 * Hook para obtener el estado actual de un dispositivo
 */
export const useDeviceCurrentStatus = (deviceId: number) => {
  return useQuery({
    queryKey: ['devices', 'status', deviceId.toString()],
    queryFn: () => deviceService.getCurrentStatus(deviceId),
    enabled: !!deviceId,
    refetchInterval: 10000, // Actualizar cada 10 segundos
  });
};

/**
 * Hook para obtener sesiones activas
 */
export const useActiveSessions = () => {
  return useQuery({
    queryKey: ['devices', 'active-sessions'],
    queryFn: () => deviceService.getActiveSessions(),
    refetchInterval: 15000, // Actualizar cada 15 segundos
  });
};

/**
 * Hook para enviar comandos a dispositivos
 */
export const useSendDeviceCommand = () => {
  return useMutation({
    mutationFn: ({ imei, command, params }: { imei: number; command: string; params?: Record<string, any> }) =>
      deviceService.sendCommand(imei, command, params),
  });
};

/**
 * Hook para asignar ruta a dispositivo
 */
export const useAssignRoute = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ imei, route, economico }: { imei: number; route: number; economico?: number }) =>
      deviceService.assignRoute(imei, route, economico),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['devices'] });
    },
  });
};

/**
 * Hook para resetear dispositivo
 */
export const useResetDevice = () => {
  return useMutation({
    mutationFn: (imei: number) => deviceService.resetDevice(imei),
  });
};

/**
 * Hook para actualizar firmware
 */
export const useUpdateFirmware = () => {
  return useMutation({
    mutationFn: ({ imei, firmwareFile }: { imei: number; firmwareFile: string }) =>
      deviceService.updateFirmware(imei, firmwareFile),
  });
};

/**
 * Hook para actualización masiva de dispositivos
 */
export const useBulkUpdateDevices = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (devices: Array<{ imei: number; data: Partial<Device> }>) => 
      deviceService.bulkUpdateDevices(devices),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['devices'] });
    },
  });
};

/**
 * Hook para exportar datos de dispositivos
 */
export const useExportDeviceData = () => {
  return useMutation({
    mutationFn: ({ imei, startDate, endDate, format }: { 
      imei: number; 
      startDate: string; 
      endDate: string; 
      format?: 'csv' | 'json' 
    }) => deviceService.exportDeviceData(imei, startDate, endDate, format),
  });
};

/**
 * Hook para probar conexión de dispositivo
 */
export const useTestDeviceConnection = () => {
  return useMutation({
    mutationFn: (imei: number) => deviceService.testConnection(imei),
  });
};

/**
 * Hook para verificar estado de todos los dispositivos
 */
export const useCheckAllDevicesStatus = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (timeout?: number) => deviceService.checkAllDevicesStatus(timeout),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['devices'] });
    },
  });
};

/**
 * Hook para obtener posiciones en tiempo real
 */
export const useRealTimePositions = () => {
  return useQuery({
    queryKey: ['devices', 'real-time-positions'],
    queryFn: () => deviceService.getRealTimePositions(),
    refetchInterval: 5000, // Actualizar cada 5 segundos
  });
};

/**
 * Hook para obtener ruta de dispositivo
 */
export const useDeviceTrail = (deviceId: number, hours: number = 24) => {
  return useQuery({
    queryKey: ['devices', 'trail', deviceId.toString(), hours.toString()],
    queryFn: () => deviceService.getDeviceTrail(deviceId, hours),
    enabled: !!deviceId,
  });
}; 
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { geofencingService } from '../services/geofencingService';

// ============================================================================
// GEOFENCING HOOKS - Hooks específicos para geofencing
// ============================================================================

/**
 * Hook para obtener todos los geofences
 */
export const useGetAllGeofences = () => {
  return useQuery({
    queryKey: ['geofences', 'all'],
    queryFn: () => geofencingService.getAllGeofences(),
    refetchInterval: 60000, // Actualizar cada minuto
  });
};

/**
 * Hook para obtener un geofence por ID
 */
export const useGetGeofenceById = (geofenceId: number) => {
  return useQuery({
    queryKey: ['geofences', 'detail', geofenceId.toString()],
    queryFn: () => geofencingService.getGeofence(geofenceId),
    enabled: !!geofenceId,
  });
};

/**
 * Hook para crear un geofence
 */
export const useCreateGeofence = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: any) => geofencingService.createGeofence(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['geofences'] });
    },
  });
};

/**
 * Hook para actualizar un geofence
 */
export const useUpdateGeofence = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => 
      geofencingService.updateGeofence(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['geofences'] });
    },
  });
};

/**
 * Hook para eliminar un geofence
 */
export const useDeleteGeofence = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => geofencingService.deleteGeofence(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['geofences'] });
    },
  });
};

/**
 * Hook para obtener eventos de geofence
 */
export const useGeofenceEvents = (geofenceId: number, params: any = {}) => {
  return useQuery({
    queryKey: ['geofences', 'events', geofenceId.toString(), params],
    queryFn: () => geofencingService.getGeofenceEvents(geofenceId, params),
    enabled: !!geofenceId,
  });
};

/**
 * Hook para obtener dispositivos dentro de un geofence
 */
export const useDevicesInsideGeofence = (geofenceId: number) => {
  return useQuery({
    queryKey: ['geofences', 'devices-inside', geofenceId.toString()],
    queryFn: () => geofencingService.getDevicesInside(geofenceId),
    enabled: !!geofenceId,
    refetchInterval: 10000, // Actualizar cada 10 segundos
  });
};

/**
 * Hook para verificar si un dispositivo está en un geofence
 */
export const useCheckDeviceInGeofence = (deviceId: number, geofenceId: number) => {
  return useQuery({
    queryKey: ['geofences', 'device-check', deviceId.toString(), geofenceId.toString()],
    queryFn: () => geofencingService.checkDeviceInGeofence(deviceId, geofenceId),
    enabled: !!(deviceId && geofenceId),
    refetchInterval: 5000, // Actualizar cada 5 segundos
  });
};

/**
 * Hook para exportar datos de geofence
 */
export const useExportGeofenceData = () => {
  return useMutation({
    mutationFn: ({ geofenceId, startDate, endDate, format }: { 
      geofenceId: number; 
      startDate: string;
      endDate: string;
      format?: 'csv' | 'json'; 
    }) => geofencingService.exportGeofenceData(geofenceId, startDate, endDate, format || 'csv'),
  });
}; 
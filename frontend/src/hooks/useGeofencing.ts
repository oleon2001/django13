import { useCrudOperations, useApiQuery, useApiMutation, useRealtimeQuery } from './useApi';
import { GeoFence, GeofenceEvent, GeofenceStatistics, MonitoringData } from '../types/unified';
import { geofencingService } from '../services/geofencingService';

// ============================================================================
// GEOFENCING HOOKS - Hooks específicos para geofencing
// ============================================================================

/**
 * Hook para operaciones CRUD de geofences
 */
export const useGeofenceCrud = () => {
  return useCrudOperations<GeoFence>('geofences', {
    getAll: geofencingService.getAllGeofences,
    getById: geofencingService.getGeofence,
    create: geofencingService.createGeofence,
    update: geofencingService.updateGeofence,
    delete: geofencingService.deleteGeofence,
  });
};

/**
 * Hook para obtener eventos de geofence
 */
export const useGeofenceEvents = (geofenceId: number, params: any = {}) => {
  return useApiQuery(
    ['geofences', 'events', geofenceId.toString()],
    () => geofencingService.getGeofenceEvents(geofenceId, params),
    {
      enabled: !!geofenceId,
    }
  );
};

/**
 * Hook para obtener dispositivos dentro de un geofence
 */
export const useDevicesInsideGeofence = (geofenceId: number) => {
  return useApiQuery(
    ['geofences', 'devices-inside', geofenceId.toString()],
    () => geofencingService.getDevicesInside(geofenceId),
    {
      enabled: !!geofenceId,
      refetchInterval: 10000, // Actualizar cada 10 segundos
    }
  );
};

/**
 * Hook para obtener estadísticas de geofence
 */
export const useGeofenceStatistics = (geofenceId: number) => {
  return useApiQuery(
    ['geofences', 'statistics', geofenceId.toString()],
    () => geofencingService.getGeofenceStatistics(geofenceId),
    {
      enabled: !!geofenceId,
      refetchInterval: 30000, // Actualizar cada 30 segundos
    }
  );
};

/**
 * Hook para monitoreo en tiempo real de geofences
 */
export const useGeofenceMonitoring = (interval: number = 5000) => {
  return useRealtimeQuery(
    ['geofences', 'monitoring'],
    geofencingService.monitorGeofences,
    interval,
    {
      refetchIntervalInBackground: true,
    }
  );
};

/**
 * Hook para verificar si un dispositivo está en un geofence
 */
export const useCheckDeviceInGeofence = (deviceId: number, geofenceId: number) => {
  return useApiQuery(
    ['geofences', 'device-check', deviceId.toString(), geofenceId.toString()],
    () => geofencingService.checkDeviceInGeofence(deviceId, geofenceId),
    {
      enabled: !!(deviceId && geofenceId),
      refetchInterval: 5000, // Actualizar cada 5 segundos
    }
  );
};

/**
 * Hook para iniciar monitoreo de geofence en tiempo real
 */
export const useStartGeofenceMonitoring = () => {
  return useApiMutation(
    geofencingService.startGeofenceMonitoring,
    {
      successMessage: 'Geofence monitoring started',
      errorMessage: 'Failed to start geofence monitoring',
    }
  );
};

/**
 * Hook para exportar datos de geofence
 */
export const useExportGeofenceData = () => {
  return useApiMutation(
    geofencingService.exportGeofenceData,
    {
      successMessage: 'Geofence data exported successfully',
      errorMessage: 'Failed to export geofence data',
    }
  );
};

/**
 * Hook para obtener geofences por tipo
 */
export const useGeofencesByType = (type: string) => {
  return useApiQuery(
    ['geofences', 'type', type],
    () => geofencingService.getGeofencesByType(type),
    {
      enabled: !!type,
    }
  );
};

/**
 * Hook para obtener geofences por estado
 */
export const useGeofencesByStatus = (status: string) => {
  return useApiQuery(
    ['geofences', 'status', status],
    () => geofencingService.getGeofencesByStatus(status),
    {
      enabled: !!status,
    }
  );
};

/**
 * Hook para obtener geofences por ubicación
 */
export const useGeofencesByLocation = (latitude: number, longitude: number, radius: number = 10) => {
  return useApiQuery(
    ['geofences', 'location', latitude.toString(), longitude.toString(), radius.toString()],
    () => geofencingService.getGeofencesByLocation(latitude, longitude, radius),
    {
      enabled: !!(latitude && longitude),
    }
  );
};

/**
 * Hook para obtener geofences activos
 */
export const useActiveGeofences = () => {
  return useApiQuery(
    ['geofences', 'active'],
    geofencingService.getActiveGeofences,
    {
      refetchInterval: 15000, // Actualizar cada 15 segundos
    }
  );
};

/**
 * Hook para obtener geofences inactivos
 */
export const useInactiveGeofences = () => {
  return useApiQuery(
    ['geofences', 'inactive'],
    geofencingService.getInactiveGeofences,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con alertas
 */
export const useGeofencesWithAlerts = () => {
  return useApiQuery(
    ['geofences', 'alerts'],
    geofencingService.getGeofencesWithAlerts,
    {
      refetchInterval: 10000, // Actualizar cada 10 segundos
    }
  );
};

/**
 * Hook para obtener geofences con violaciones
 */
export const useGeofencesWithViolations = () => {
  return useApiQuery(
    ['geofences', 'violations'],
    geofencingService.getGeofencesWithViolations,
    {
      refetchInterval: 10000, // Actualizar cada 10 segundos
    }
  );
};

/**
 * Hook para obtener geofences con entradas
 */
export const useGeofencesWithEntries = () => {
  return useApiQuery(
    ['geofences', 'entries'],
    geofencingService.getGeofencesWithEntries,
    {
      refetchInterval: 10000, // Actualizar cada 10 segundos
    }
  );
};

/**
 * Hook para obtener geofences con salidas
 */
export const useGeofencesWithExits = () => {
  return useApiQuery(
    ['geofences', 'exits'],
    geofencingService.getGeofencesWithExits,
    {
      refetchInterval: 10000, // Actualizar cada 10 segundos
    }
  );
};

/**
 * Hook para obtener geofences con tiempo excedido
 */
export const useGeofencesWithTimeExceeded = () => {
  return useApiQuery(
    ['geofences', 'time-exceeded'],
    geofencingService.getGeofencesWithTimeExceeded,
    {
      refetchInterval: 15000, // Actualizar cada 15 segundos
    }
  );
};

/**
 * Hook para obtener geofences con velocidad excedida
 */
export const useGeofencesWithSpeedExceeded = () => {
  return useApiQuery(
    ['geofences', 'speed-exceeded'],
    geofencingService.getGeofencesWithSpeedExceeded,
    {
      refetchInterval: 10000, // Actualizar cada 10 segundos
    }
  );
};

/**
 * Hook para obtener geofences con distancia excedida
 */
export const useGeofencesWithDistanceExceeded = () => {
  return useApiQuery(
    ['geofences', 'distance-exceeded'],
    geofencingService.getGeofencesWithDistanceExceeded,
    {
      refetchInterval: 15000, // Actualizar cada 15 segundos
    }
  );
};

/**
 * Hook para obtener geofences con horario excedido
 */
export const useGeofencesWithScheduleExceeded = () => {
  return useApiQuery(
    ['geofences', 'schedule-exceeded'],
    geofencingService.getGeofencesWithScheduleExceeded,
    {
      refetchInterval: 30000, // Actualizar cada 30 segundos
    }
  );
};

/**
 * Hook para obtener geofences con capacidad excedida
 */
export const useGeofencesWithCapacityExceeded = () => {
  return useApiQuery(
    ['geofences', 'capacity-exceeded'],
    geofencingService.getGeofencesWithCapacityExceeded,
    {
      refetchInterval: 20000, // Actualizar cada 20 segundos
    }
  );
};

/**
 * Hook para obtener geofences con temperatura excedida
 */
export const useGeofencesWithTemperatureExceeded = () => {
  return useApiQuery(
    ['geofences', 'temperature-exceeded'],
    geofencingService.getGeofencesWithTemperatureExceeded,
    {
      refetchInterval: 30000, // Actualizar cada 30 segundos
    }
  );
};

/**
 * Hook para obtener geofences con humedad excedida
 */
export const useGeofencesWithHumidityExceeded = () => {
  return useApiQuery(
    ['geofences', 'humidity-exceeded'],
    geofencingService.getGeofencesWithHumidityExceeded,
    {
      refetchInterval: 30000, // Actualizar cada 30 segundos
    }
  );
};

/**
 * Hook para obtener geofences con presión excedida
 */
export const useGeofencesWithPressureExceeded = () => {
  return useApiQuery(
    ['geofences', 'pressure-exceeded'],
    geofencingService.getGeofencesWithPressureExceeded,
    {
      refetchInterval: 45000, // Actualizar cada 45 segundos
    }
  );
};

/**
 * Hook para obtener geofences con nivel de luz excedido
 */
export const useGeofencesWithLightLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'light-level-exceeded'],
    geofencingService.getGeofencesWithLightLevelExceeded,
    {
      refetchInterval: 30000, // Actualizar cada 30 segundos
    }
  );
};

/**
 * Hook para obtener geofences con nivel de ruido excedido
 */
export const useGeofencesWithNoiseLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'noise-level-exceeded'],
    geofencingService.getGeofencesWithNoiseLevelExceeded,
    {
      refetchInterval: 30000, // Actualizar cada 30 segundos
    }
  );
};

/**
 * Hook para obtener geofences con nivel de CO2 excedido
 */
export const useGeofencesWithCO2LevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'co2-level-exceeded'],
    geofencingService.getGeofencesWithCO2LevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de VOC excedido
 */
export const useGeofencesWithVOCLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'voc-level-exceeded'],
    geofencingService.getGeofencesWithVOCLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de PM2.5 excedido
 */
export const useGeofencesWithPM25LevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'pm25-level-exceeded'],
    geofencingService.getGeofencesWithPM25LevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de PM10 excedido
 */
export const useGeofencesWithPM10LevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'pm10-level-exceeded'],
    geofencingService.getGeofencesWithPM10LevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de ozono excedido
 */
export const useGeofencesWithOzoneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'ozone-level-exceeded'],
    geofencingService.getGeofencesWithOzoneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de monóxido de carbono excedido
 */
export const useGeofencesWithCOLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'co-level-exceeded'],
    geofencingService.getGeofencesWithCOLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de dióxido de azufre excedido
 */
export const useGeofencesWithSO2LevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'so2-level-exceeded'],
    geofencingService.getGeofencesWithSO2LevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de dióxido de nitrógeno excedido
 */
export const useGeofencesWithNO2LevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'no2-level-exceeded'],
    geofencingService.getGeofencesWithNO2LevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de amoníaco excedido
 */
export const useGeofencesWithNH3LevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'nh3-level-exceeded'],
    geofencingService.getGeofencesWithNH3LevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de metano excedido
 */
export const useGeofencesWithCH4LevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'ch4-level-exceeded'],
    geofencingService.getGeofencesWithCH4LevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de propano excedido
 */
export const useGeofencesWithC3H8LevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'c3h8-level-exceeded'],
    geofencingService.getGeofencesWithC3H8LevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de butano excedido
 */
export const useGeofencesWithC4H10LevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'c4h10-level-exceeded'],
    geofencingService.getGeofencesWithC4H10LevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de alcohol excedido
 */
export const useGeofencesWithAlcoholLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'alcohol-level-exceeded'],
    geofencingService.getGeofencesWithAlcoholLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de benceno excedido
 */
export const useGeofencesWithBenzeneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'benzene-level-exceeded'],
    geofencingService.getGeofencesWithBenzeneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de hexano excedido
 */
export const useGeofencesWithHexaneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'hexane-level-exceeded'],
    geofencingService.getGeofencesWithHexaneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de tolueno excedido
 */
export const useGeofencesWithTolueneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'toluene-level-exceeded'],
    geofencingService.getGeofencesWithTolueneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de xileno excedido
 */
export const useGeofencesWithXyleneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'xylene-level-exceeded'],
    geofencingService.getGeofencesWithXyleneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de formaldehído excedido
 */
export const useGeofencesWithFormaldehydeLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'formaldehyde-level-exceeded'],
    geofencingService.getGeofencesWithFormaldehydeLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de acetaldehído excedido
 */
export const useGeofencesWithAcetaldehydeLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'acetaldehyde-level-exceeded'],
    geofencingService.getGeofencesWithAcetaldehydeLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de acroleína excedido
 */
export const useGeofencesWithAcroleinLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'acrolein-level-exceeded'],
    geofencingService.getGeofencesWithAcroleinLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de 1,3-butadieno excedido
 */
export const useGeofencesWithButadieneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'butadiene-level-exceeded'],
    geofencingService.getGeofencesWithButadieneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de 1,2-dicloroetano excedido
 */
export const useGeofencesWithDichloroethaneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'dichloroethane-level-exceeded'],
    geofencingService.getGeofencesWithDichloroethaneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de diclorometano excedido
 */
export const useGeofencesWithDichloromethaneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'dichloromethane-level-exceeded'],
    geofencingService.getGeofencesWithDichloromethaneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de tricloroetileno excedido
 */
export const useGeofencesWithTrichloroethyleneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'trichloroethylene-level-exceeded'],
    geofencingService.getGeofencesWithTrichloroethyleneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de tetracloroetileno excedido
 */
export const useGeofencesWithTetrachloroethyleneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'tetrachloroethylene-level-exceeded'],
    geofencingService.getGeofencesWithTetrachloroethyleneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de cloroformo excedido
 */
export const useGeofencesWithChloroformLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'chloroform-level-exceeded'],
    geofencingService.getGeofencesWithChloroformLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de bromoformo excedido
 */
export const useGeofencesWithBromoformLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'bromoform-level-exceeded'],
    geofencingService.getGeofencesWithBromoformLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de dibromoclorometano excedido
 */
export const useGeofencesWithDibromochloromethaneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'dibromochloromethane-level-exceeded'],
    geofencingService.getGeofencesWithDibromochloromethaneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de bromodiclorometano excedido
 */
export const useGeofencesWithBromodichloromethaneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'bromodichloromethane-level-exceeded'],
    geofencingService.getGeofencesWithBromodichloromethaneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de dibromometano excedido
 */
export const useGeofencesWithDibromomethaneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'dibromomethane-level-exceeded'],
    geofencingService.getGeofencesWithDibromomethaneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de 1,2-dicloropropano excedido
 */
export const useGeofencesWithDichloropropaneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'dichloropropane-level-exceeded'],
    geofencingService.getGeofencesWithDichloropropaneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de 1,3-dicloropropano excedido
 */
export const useGeofencesWithDichloropropane13LevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'dichloropropane13-level-exceeded'],
    geofencingService.getGeofencesWithDichloropropane13LevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de 1,1,1-tricloroetano excedido
 */
export const useGeofencesWithTrichloroethaneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'trichloroethane-level-exceeded'],
    geofencingService.getGeofencesWithTrichloroethaneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de 1,1,2-tricloroetano excedido
 */
export const useGeofencesWithTrichloroethane112LevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'trichloroethane112-level-exceeded'],
    geofencingService.getGeofencesWithTrichloroethane112LevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de 1,1-dicloroetano excedido
 */
export const useGeofencesWithDichloroethane11LevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'dichloroethane11-level-exceeded'],
    geofencingService.getGeofencesWithDichloroethane11LevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de 1,2-dicloroetano excedido
 */
export const useGeofencesWithDichloroethane12LevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'dichloroethane12-level-exceeded'],
    geofencingService.getGeofencesWithDichloroethane12LevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de 1,1,1,2-tetracloroetano excedido
 */
export const useGeofencesWithTetrachloroethaneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'tetrachloroethane-level-exceeded'],
    geofencingService.getGeofencesWithTetrachloroethaneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de 1,1,2,2-tetracloroetano excedido
 */
export const useGeofencesWithTetrachloroethane1122LevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'tetrachloroethane1122-level-exceeded'],
    geofencingService.getGeofencesWithTetrachloroethane1122LevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de 1,1-dicloroeteno excedido
 */
export const useGeofencesWithDichloroethene11LevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'dichloroethene11-level-exceeded'],
    geofencingService.getGeofencesWithDichloroethene11LevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de 1,2-dicloroeteno excedido
 */
export const useGeofencesWithDichloroethene12LevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'dichloroethene12-level-exceeded'],
    geofencingService.getGeofencesWithDichloroethene12LevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de tricloroeteno excedido
 */
export const useGeofencesWithTrichloroetheneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'trichloroethene-level-exceeded'],
    geofencingService.getGeofencesWithTrichloroetheneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de tetracloroeteno excedido
 */
export const useGeofencesWithTetrachloroetheneLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'tetrachloroethene-level-exceeded'],
    geofencingService.getGeofencesWithTetrachloroetheneLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de cloruro de vinilo excedido
 */
export const useGeofencesWithVinylChlorideLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'vinyl-chloride-level-exceeded'],
    geofencingService.getGeofencesWithVinylChlorideLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de cloruro de metileno excedido
 */
export const useGeofencesWithMethyleneChlorideLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'methylene-chloride-level-exceeded'],
    geofencingService.getGeofencesWithMethyleneChlorideLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de cloruro de metilo excedido
 */
export const useGeofencesWithMethylChlorideLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'methyl-chloride-level-exceeded'],
    geofencingService.getGeofencesWithMethylChlorideLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de cloruro de etilo excedido
 */
export const useGeofencesWithEthylChlorideLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'ethyl-chloride-level-exceeded'],
    geofencingService.getGeofencesWithEthylChlorideLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de cloruro de propilo excedido
 */
export const useGeofencesWithPropylChlorideLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'propyl-chloride-level-exceeded'],
    geofencingService.getGeofencesWithPropylChlorideLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de cloruro de butilo excedido
 */
export const useGeofencesWithButylChlorideLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'butyl-chloride-level-exceeded'],
    geofencingService.getGeofencesWithButylChlorideLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de cloruro de pentilo excedido
 */
export const useGeofencesWithPentylChlorideLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'pentyl-chloride-level-exceeded'],
    geofencingService.getGeofencesWithPentylChlorideLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de cloruro de hexilo excedido
 */
export const useGeofencesWithHexylChlorideLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'hexyl-chloride-level-exceeded'],
    geofencingService.getGeofencesWithHexylChlorideLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de cloruro de heptilo excedido
 */
export const useGeofencesWithHeptylChlorideLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'heptyl-chloride-level-exceeded'],
    geofencingService.getGeofencesWithHeptylChlorideLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de cloruro de octilo excedido
 */
export const useGeofencesWithOctylChlorideLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'octyl-chloride-level-exceeded'],
    geofencingService.getGeofencesWithOctylChlorideLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de cloruro de nonilo excedido
 */
export const useGeofencesWithNonylChlorideLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'nonyl-chloride-level-exceeded'],
    geofencingService.getGeofencesWithNonylChlorideLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
};

/**
 * Hook para obtener geofences con nivel de cloruro de decylo excedido
 */
export const useGeofencesWithDecylChlorideLevelExceeded = () => {
  return useApiQuery(
    ['geofences', 'decyl-chloride-level-exceeded'],
    geofencingService.getGeofencesWithDecylChlorideLevelExceeded,
    {
      refetchInterval: 60000, // Actualizar cada minuto
    }
  );
}; 
import { QueryClient } from '@tanstack/react-query';

// ============================================================================
// QUERY CLIENT CONFIGURATION - Configuración del cliente de React Query
// ============================================================================

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Tiempo que los datos se consideran frescos
      staleTime: 5 * 60 * 1000, // 5 minutos
      
      // Tiempo que los datos se mantienen en cache
      gcTime: 10 * 60 * 1000, // 10 minutos (anteriormente cacheTime)
      
      // Reintentos en caso de error
      retry: (failureCount, error) => {
        // No reintentar en errores 4xx (excepto 408, 429)
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          if (error?.response?.status === 408 || error?.response?.status === 429) {
            return failureCount < 3;
          }
          return false;
        }
        
        // Reintentar hasta 3 veces para otros errores
        return failureCount < 3;
      },
      
      // Función de retry con backoff exponencial
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      
      // Refetch en window focus
      refetchOnWindowFocus: false,
      
      // Refetch en reconnect
      refetchOnReconnect: true,
      
      // Refetch en mount
      refetchOnMount: true,
      
      // Mostrar loading state
      notifyOnChangeProps: ['data', 'error', 'isLoading', 'isFetching'],
    },
    mutations: {
      // Reintentos para mutaciones
      retry: 1,
      
      // Tiempo de retry para mutaciones
      retryDelay: 1000,
    },
  },
});

// ============================================================================
// QUERY KEYS - Claves para organizar las queries
// ============================================================================

export const queryKeys = {
  // Device queries
  devices: {
    all: ['devices'] as const,
    lists: () => [...queryKeys.devices.all, 'list'] as const,
    list: (filters: any) => [...queryKeys.devices.lists(), filters] as const,
    details: () => [...queryKeys.devices.all, 'detail'] as const,
    detail: (id: number) => [...queryKeys.devices.details(), id] as const,
    firmware: (id: number) => [...queryKeys.devices.all, 'firmware', id] as const,
    position: (id: number) => [...queryKeys.devices.all, 'position', id] as const,
    polling: (id: number) => [...queryKeys.devices.all, 'polling', id] as const,
    statistics: () => [...queryKeys.devices.all, 'statistics'] as const,
    alerts: () => [...queryKeys.devices.all, 'alerts'] as const,
    offline: () => [...queryKeys.devices.all, 'offline'] as const,
    lowBattery: () => [...queryKeys.devices.all, 'low-battery'] as const,
    weakSignal: () => [...queryKeys.devices.all, 'weak-signal'] as const,
    gpsIssues: () => [...queryKeys.devices.all, 'gps-issues'] as const,
    connectivityIssues: () => [...queryKeys.devices.all, 'connectivity-issues'] as const,
    temperatureIssues: () => [...queryKeys.devices.all, 'temperature-issues'] as const,
    memoryIssues: () => [...queryKeys.devices.all, 'memory-issues'] as const,
    powerIssues: () => [...queryKeys.devices.all, 'power-issues'] as const,
    sensorIssues: () => [...queryKeys.devices.all, 'sensor-issues'] as const,
    firmwareIssues: () => [...queryKeys.devices.all, 'firmware-issues'] as const,
    configurationIssues: () => [...queryKeys.devices.all, 'configuration-issues'] as const,
    securityIssues: () => [...queryKeys.devices.all, 'security-issues'] as const,
    networkIssues: () => [...queryKeys.devices.all, 'network-issues'] as const,
    syncIssues: () => [...queryKeys.devices.all, 'sync-issues'] as const,
    calibrationIssues: () => [...queryKeys.devices.all, 'calibration-issues'] as const,
    maintenanceIssues: () => [...queryKeys.devices.all, 'maintenance-issues'] as const,
    licenseIssues: () => [...queryKeys.devices.all, 'license-issues'] as const,
    updateIssues: () => [...queryKeys.devices.all, 'update-issues'] as const,
    backupIssues: () => [...queryKeys.devices.all, 'backup-issues'] as const,
    restoreIssues: () => [...queryKeys.devices.all, 'restore-issues'] as const,
    migrationIssues: () => [...queryKeys.devices.all, 'migration-issues'] as const,
    integrationIssues: () => [...queryKeys.devices.all, 'integration-issues'] as const,
    apiIssues: () => [...queryKeys.devices.all, 'api-issues'] as const,
    authIssues: () => [...queryKeys.devices.all, 'auth-issues'] as const,
    authorizationIssues: () => [...queryKeys.devices.all, 'authorization-issues'] as const,
    rateLimitIssues: () => [...queryKeys.devices.all, 'rate-limit-issues'] as const,
    timeoutIssues: () => [...queryKeys.devices.all, 'timeout-issues'] as const,
    connectionTimeoutIssues: () => [...queryKeys.devices.all, 'connection-timeout-issues'] as const,
    responseTimeoutIssues: () => [...queryKeys.devices.all, 'response-timeout-issues'] as const,
    processingTimeoutIssues: () => [...queryKeys.devices.all, 'processing-timeout-issues'] as const,
    syncTimeoutIssues: () => [...queryKeys.devices.all, 'sync-timeout-issues'] as const,
    updateTimeoutIssues: () => [...queryKeys.devices.all, 'update-timeout-issues'] as const,
    backupTimeoutIssues: () => [...queryKeys.devices.all, 'backup-timeout-issues'] as const,
    restoreTimeoutIssues: () => [...queryKeys.devices.all, 'restore-timeout-issues'] as const,
    migrationTimeoutIssues: () => [...queryKeys.devices.all, 'migration-timeout-issues'] as const,
    integrationTimeoutIssues: () => [...queryKeys.devices.all, 'integration-timeout-issues'] as const,
    apiTimeoutIssues: () => [...queryKeys.devices.all, 'api-timeout-issues'] as const,
    authTimeoutIssues: () => [...queryKeys.devices.all, 'auth-timeout-issues'] as const,
    authorizationTimeoutIssues: () => [...queryKeys.devices.all, 'authorization-timeout-issues'] as const,
    rateLimitTimeoutIssues: () => [...queryKeys.devices.all, 'rate-limit-timeout-issues'] as const,
  },

  // Geofencing queries
  geofences: {
    all: ['geofences'] as const,
    lists: () => [...queryKeys.geofences.all, 'list'] as const,
    list: (filters: any) => [...queryKeys.geofences.lists(), filters] as const,
    details: () => [...queryKeys.geofences.all, 'detail'] as const,
    detail: (id: number) => [...queryKeys.geofences.details(), id] as const,
    events: (id: number) => [...queryKeys.geofences.all, 'events', id] as const,
    devicesInside: (id: number) => [...queryKeys.geofences.all, 'devices-inside', id] as const,
    statistics: (id: number) => [...queryKeys.geofences.all, 'statistics', id] as const,
    monitoring: () => [...queryKeys.geofences.all, 'monitoring'] as const,
    deviceCheck: (deviceId: number, geofenceId: number) => 
      [...queryKeys.geofences.all, 'device-check', deviceId, geofenceId] as const,
    active: () => [...queryKeys.geofences.all, 'active'] as const,
    inactive: () => [...queryKeys.geofences.all, 'inactive'] as const,
    alerts: () => [...queryKeys.geofences.all, 'alerts'] as const,
    violations: () => [...queryKeys.geofences.all, 'violations'] as const,
    entries: () => [...queryKeys.geofences.all, 'entries'] as const,
    exits: () => [...queryKeys.geofences.all, 'exits'] as const,
    timeExceeded: () => [...queryKeys.geofences.all, 'time-exceeded'] as const,
    speedExceeded: () => [...queryKeys.geofences.all, 'speed-exceeded'] as const,
    distanceExceeded: () => [...queryKeys.geofences.all, 'distance-exceeded'] as const,
    scheduleExceeded: () => [...queryKeys.geofences.all, 'schedule-exceeded'] as const,
    capacityExceeded: () => [...queryKeys.geofences.all, 'capacity-exceeded'] as const,
    temperatureExceeded: () => [...queryKeys.geofences.all, 'temperature-exceeded'] as const,
    humidityExceeded: () => [...queryKeys.geofences.all, 'humidity-exceeded'] as const,
    pressureExceeded: () => [...queryKeys.geofences.all, 'pressure-exceeded'] as const,
    lightLevelExceeded: () => [...queryKeys.geofences.all, 'light-level-exceeded'] as const,
    noiseLevelExceeded: () => [...queryKeys.geofences.all, 'noise-level-exceeded'] as const,
    co2LevelExceeded: () => [...queryKeys.geofences.all, 'co2-level-exceeded'] as const,
    vocLevelExceeded: () => [...queryKeys.geofences.all, 'voc-level-exceeded'] as const,
    pm25LevelExceeded: () => [...queryKeys.geofences.all, 'pm25-level-exceeded'] as const,
    pm10LevelExceeded: () => [...queryKeys.geofences.all, 'pm10-level-exceeded'] as const,
    ozoneLevelExceeded: () => [...queryKeys.geofences.all, 'ozone-level-exceeded'] as const,
    coLevelExceeded: () => [...queryKeys.geofences.all, 'co-level-exceeded'] as const,
    so2LevelExceeded: () => [...queryKeys.geofences.all, 'so2-level-exceeded'] as const,
    no2LevelExceeded: () => [...queryKeys.geofences.all, 'no2-level-exceeded'] as const,
    nh3LevelExceeded: () => [...queryKeys.geofences.all, 'nh3-level-exceeded'] as const,
    ch4LevelExceeded: () => [...queryKeys.geofences.all, 'ch4-level-exceeded'] as const,
    c3h8LevelExceeded: () => [...queryKeys.geofences.all, 'c3h8-level-exceeded'] as const,
    c4h10LevelExceeded: () => [...queryKeys.geofences.all, 'c4h10-level-exceeded'] as const,
    alcoholLevelExceeded: () => [...queryKeys.geofences.all, 'alcohol-level-exceeded'] as const,
    benzeneLevelExceeded: () => [...queryKeys.geofences.all, 'benzene-level-exceeded'] as const,
    hexaneLevelExceeded: () => [...queryKeys.geofences.all, 'hexane-level-exceeded'] as const,
    tolueneLevelExceeded: () => [...queryKeys.geofences.all, 'toluene-level-exceeded'] as const,
    xyleneLevelExceeded: () => [...queryKeys.geofences.all, 'xylene-level-exceeded'] as const,
    formaldehydeLevelExceeded: () => [...queryKeys.geofences.all, 'formaldehyde-level-exceeded'] as const,
    acetaldehydeLevelExceeded: () => [...queryKeys.geofences.all, 'acetaldehyde-level-exceeded'] as const,
    acroleinLevelExceeded: () => [...queryKeys.geofences.all, 'acrolein-level-exceeded'] as const,
    butadieneLevelExceeded: () => [...queryKeys.geofences.all, 'butadiene-level-exceeded'] as const,
    dichloroethaneLevelExceeded: () => [...queryKeys.geofences.all, 'dichloroethane-level-exceeded'] as const,
    dichloromethaneLevelExceeded: () => [...queryKeys.geofences.all, 'dichloromethane-level-exceeded'] as const,
    trichloroethyleneLevelExceeded: () => [...queryKeys.geofences.all, 'trichloroethylene-level-exceeded'] as const,
    tetrachloroethyleneLevelExceeded: () => [...queryKeys.geofences.all, 'tetrachloroethylene-level-exceeded'] as const,
    chloroformLevelExceeded: () => [...queryKeys.geofences.all, 'chloroform-level-exceeded'] as const,
    bromoformLevelExceeded: () => [...queryKeys.geofences.all, 'bromoform-level-exceeded'] as const,
    dibromochloromethaneLevelExceeded: () => [...queryKeys.geofences.all, 'dibromochloromethane-level-exceeded'] as const,
    bromodichloromethaneLevelExceeded: () => [...queryKeys.geofences.all, 'bromodichloromethane-level-exceeded'] as const,
    dibromomethaneLevelExceeded: () => [...queryKeys.geofences.all, 'dibromomethane-level-exceeded'] as const,
    dichloropropaneLevelExceeded: () => [...queryKeys.geofences.all, 'dichloropropane-level-exceeded'] as const,
    dichloropropane13LevelExceeded: () => [...queryKeys.geofences.all, 'dichloropropane13-level-exceeded'] as const,
    trichloroethaneLevelExceeded: () => [...queryKeys.geofences.all, 'trichloroethane-level-exceeded'] as const,
    trichloroethane112LevelExceeded: () => [...queryKeys.geofences.all, 'trichloroethane112-level-exceeded'] as const,
    dichloroethane11LevelExceeded: () => [...queryKeys.geofences.all, 'dichloroethane11-level-exceeded'] as const,
    dichloroethane12LevelExceeded: () => [...queryKeys.geofences.all, 'dichloroethane12-level-exceeded'] as const,
    tetrachloroethaneLevelExceeded: () => [...queryKeys.geofences.all, 'tetrachloroethane-level-exceeded'] as const,
    tetrachloroethane1122LevelExceeded: () => [...queryKeys.geofences.all, 'tetrachloroethane1122-level-exceeded'] as const,
    dichloroethene11LevelExceeded: () => [...queryKeys.geofences.all, 'dichloroethene11-level-exceeded'] as const,
    dichloroethene12LevelExceeded: () => [...queryKeys.geofences.all, 'dichloroethene12-level-exceeded'] as const,
    trichloroetheneLevelExceeded: () => [...queryKeys.geofences.all, 'trichloroethene-level-exceeded'] as const,
    tetrachloroetheneLevelExceeded: () => [...queryKeys.geofences.all, 'tetrachloroethene-level-exceeded'] as const,
    vinylChlorideLevelExceeded: () => [...queryKeys.geofences.all, 'vinyl-chloride-level-exceeded'] as const,
    methyleneChlorideLevelExceeded: () => [...queryKeys.geofences.all, 'methylene-chloride-level-exceeded'] as const,
    methylChlorideLevelExceeded: () => [...queryKeys.geofences.all, 'methyl-chloride-level-exceeded'] as const,
    ethylChlorideLevelExceeded: () => [...queryKeys.geofences.all, 'ethyl-chloride-level-exceeded'] as const,
    propylChlorideLevelExceeded: () => [...queryKeys.geofences.all, 'propyl-chloride-level-exceeded'] as const,
    butylChlorideLevelExceeded: () => [...queryKeys.geofences.all, 'butyl-chloride-level-exceeded'] as const,
    pentylChlorideLevelExceeded: () => [...queryKeys.geofences.all, 'pentyl-chloride-level-exceeded'] as const,
    hexylChlorideLevelExceeded: () => [...queryKeys.geofences.all, 'hexyl-chloride-level-exceeded'] as const,
    heptylChlorideLevelExceeded: () => [...queryKeys.geofences.all, 'heptyl-chloride-level-exceeded'] as const,
    octylChlorideLevelExceeded: () => [...queryKeys.geofences.all, 'octyl-chloride-level-exceeded'] as const,
    nonylChlorideLevelExceeded: () => [...queryKeys.geofences.all, 'nonyl-chloride-level-exceeded'] as const,
    decylChlorideLevelExceeded: () => [...queryKeys.geofences.all, 'decyl-chloride-level-exceeded'] as const,
  },

  // Report queries
  reports: {
    all: ['reports'] as const,
    lists: () => [...queryKeys.reports.all, 'list'] as const,
    list: (filters: any) => [...queryKeys.reports.lists(), filters] as const,
    details: () => [...queryKeys.reports.all, 'detail'] as const,
    detail: (id: number) => [...queryKeys.reports.details(), id] as const,
    pending: () => [...queryKeys.reports.all, 'pending'] as const,
    processing: () => [...queryKeys.reports.all, 'processing'] as const,
    completed: () => [...queryKeys.reports.all, 'completed'] as const,
    failed: () => [...queryKeys.reports.all, 'failed'] as const,
    statistics: () => [...queryKeys.reports.all, 'statistics'] as const,
    recent: (limit: number) => [...queryKeys.reports.all, 'recent', limit] as const,
    byType: (type: string) => [...queryKeys.reports.all, 'type', type] as const,
    byStatus: (status: string) => [...queryKeys.reports.all, 'status', status] as const,
    byDate: (startDate: string, endDate: string) => 
      [...queryKeys.reports.all, 'date', startDate, endDate] as const,
    byUser: (userId: number) => [...queryKeys.reports.all, 'user', userId] as const,
    byRoute: (routeId: number) => [...queryKeys.reports.all, 'route', routeId] as const,
    byDriver: (driverId: number) => [...queryKeys.reports.all, 'driver', driverId] as const,
    byDevice: (deviceId: number) => [...queryKeys.reports.all, 'device', deviceId] as const,
    byVehicle: (vehicleId: number) => [...queryKeys.reports.all, 'vehicle', vehicleId] as const,
    byGeofence: (geofenceId: number) => [...queryKeys.reports.all, 'geofence', geofenceId] as const,
    byFormat: (format: string) => [...queryKeys.reports.all, 'format', format] as const,
    byFileSize: (minSize: number, maxSize: number) => 
      [...queryKeys.reports.all, 'file-size', minSize, maxSize] as const,
  },

  // Vehicle queries
  vehicles: {
    all: ['vehicles'] as const,
    lists: () => [...queryKeys.vehicles.all, 'list'] as const,
    list: (filters: any) => [...queryKeys.vehicles.lists(), filters] as const,
    details: () => [...queryKeys.vehicles.all, 'detail'] as const,
    detail: (id: number) => [...queryKeys.vehicles.details(), id] as const,
  },

  // Driver queries
  drivers: {
    all: ['drivers'] as const,
    lists: () => [...queryKeys.drivers.all, 'list'] as const,
    list: (filters: any) => [...queryKeys.drivers.lists(), filters] as const,
    details: () => [...queryKeys.drivers.all, 'detail'] as const,
    detail: (id: number) => [...queryKeys.drivers.details(), id] as const,
  },

  // Route queries
  routes: {
    all: ['routes'] as const,
    lists: () => [...queryKeys.routes.all, 'list'] as const,
    list: (filters: any) => [...queryKeys.routes.lists(), filters] as const,
    details: () => [...queryKeys.routes.all, 'detail'] as const,
    detail: (id: number) => [...queryKeys.routes.details(), id] as const,
  },

  // User queries
  users: {
    all: ['users'] as const,
    lists: () => [...queryKeys.users.all, 'list'] as const,
    list: (filters: any) => [...queryKeys.users.lists(), filters] as const,
    details: () => [...queryKeys.users.all, 'detail'] as const,
    detail: (id: number) => [...queryKeys.users.details(), id] as const,
    profile: (id: number) => [...queryKeys.users.all, 'profile', id] as const,
  },

  // System queries
  system: {
    health: () => ['system', 'health'] as const,
    settings: () => ['system', 'settings'] as const,
    protocols: () => ['system', 'protocols'] as const,
  },
};

// ============================================================================
// UTILITY FUNCTIONS - Funciones de utilidad para el query client
// ============================================================================

/**
 * Función para invalidar todas las queries relacionadas con dispositivos
 */
export const invalidateDeviceQueries = () => {
  queryClient.invalidateQueries({ queryKey: queryKeys.devices.all });
};

/**
 * Función para invalidar todas las queries relacionadas con geofences
 */
export const invalidateGeofenceQueries = () => {
  queryClient.invalidateQueries({ queryKey: queryKeys.geofences.all });
};

/**
 * Función para invalidar todas las queries relacionadas con reportes
 */
export const invalidateReportQueries = () => {
  queryClient.invalidateQueries({ queryKey: queryKeys.reports.all });
};

/**
 * Función para invalidar todas las queries relacionadas con vehículos
 */
export const invalidateVehicleQueries = () => {
  queryClient.invalidateQueries({ queryKey: queryKeys.vehicles.all });
};

/**
 * Función para invalidar todas las queries relacionadas con conductores
 */
export const invalidateDriverQueries = () => {
  queryClient.invalidateQueries({ queryKey: queryKeys.drivers.all });
};

/**
 * Función para invalidar todas las queries relacionadas con rutas
 */
export const invalidateRouteQueries = () => {
  queryClient.invalidateQueries({ queryKey: queryKeys.routes.all });
};

/**
 * Función para invalidar todas las queries relacionadas con usuarios
 */
export const invalidateUserQueries = () => {
  queryClient.invalidateQueries({ queryKey: queryKeys.users.all });
};

/**
 * Función para invalidar todas las queries del sistema
 */
export const invalidateSystemQueries = () => {
  queryClient.invalidateQueries({ queryKey: queryKeys.system.all });
};

/**
 * Función para invalidar todas las queries
 */
export const invalidateAllQueries = () => {
  queryClient.invalidateQueries();
};

/**
 * Función para limpiar el cache
 */
export const clearQueryCache = () => {
  queryClient.clear();
};

/**
 * Función para obtener el estado de las queries
 */
export const getQueryState = (queryKey: any[]) => {
  return queryClient.getQueryState(queryKey);
};

/**
 * Función para obtener los datos de una query
 */
export const getQueryData = (queryKey: any[]) => {
  return queryClient.getQueryData(queryKey);
};

/**
 * Función para establecer los datos de una query
 */
export const setQueryData = (queryKey: any[], data: any) => {
  queryClient.setQueryData(queryKey, data);
};

/**
 * Función para remover una query del cache
 */
export const removeQueries = (queryKey: any[]) => {
  queryClient.removeQueries({ queryKey });
};

/**
 * Función para cancelar queries en curso
 */
export const cancelQueries = (queryKey: any[]) => {
  queryClient.cancelQueries({ queryKey });
};

/**
 * Función para refetch queries
 */
export const refetchQueries = (queryKey: any[]) => {
  queryClient.refetchQueries({ queryKey });
}; 
import { useQuery, useMutation, useQueryClient, UseQueryOptions } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import {
  authService,
  deviceService,
  vehicleService,
  driverService,
  geofenceService,
  trackingService,
  reportService,
  parkingService,
  communicationService,
  ticketService,
  coordinateService
} from '../services/unifiedApi';
import {
  GPSDevice,
  Vehicle,
  Driver,
  GeoFence,
  Location,
  DeviceEvent,
  NetworkEvent,
  Alert,
  Route,
  DeviceStatus,
  GPRSSession,
  CarPark,
  CarLane,
  CarSlot,
  Report,
  CellTower,
  ServerSMS,
  TicketDetail,
  User,
  AuthTokens,
  DeviceStats,
  DeviceFilters,
  VehicleFilters,
  DriverFilters,
  GeofenceFilters,
  DateRange,
  RealTimePosition,
  DeviceTrail,
  DeviceCommand,
  GeofenceEvent
} from '../types/unified';

// ============================================================================
// QUERY KEYS
// ============================================================================

export const queryKeys = {
  // Auth
  auth: {
    currentUser: ['auth', 'currentUser'] as const,
  },
  
  // Devices
  devices: {
    all: ['devices'] as const,
    lists: () => [...queryKeys.devices.all, 'list'] as const,
    list: (filters: DeviceFilters) => [...queryKeys.devices.lists(), filters] as const,
    details: () => [...queryKeys.devices.all, 'detail'] as const,
    detail: (imei: number) => [...queryKeys.devices.details(), imei] as const,
    history: (imei: number) => [...queryKeys.devices.detail(imei), 'history'] as const,
    events: (imei: number) => [...queryKeys.devices.detail(imei), 'events'] as const,
    trail: (imei: number) => [...queryKeys.devices.detail(imei), 'trail'] as const,
    connections: (imei: number) => [...queryKeys.devices.detail(imei), 'connections'] as const,
    status: (imei: number) => [...queryKeys.devices.detail(imei), 'status'] as const,
    stats: (imei: number) => [...queryKeys.devices.detail(imei), 'stats'] as const,
  },
  
  // Vehicles
  vehicles: {
    all: ['vehicles'] as const,
    lists: () => [...queryKeys.vehicles.all, 'list'] as const,
    list: (filters: VehicleFilters) => [...queryKeys.vehicles.lists(), filters] as const,
    details: () => [...queryKeys.vehicles.all, 'detail'] as const,
    detail: (id: number) => [...queryKeys.vehicles.details(), id] as const,
    availableDevices: ['vehicles', 'available-devices'] as const,
    availableDrivers: ['vehicles', 'available-drivers'] as const,
  },
  
  // Drivers
  drivers: {
    all: ['drivers'] as const,
    lists: () => [...queryKeys.drivers.all, 'list'] as const,
    list: (filters: DriverFilters) => [...queryKeys.drivers.lists(), filters] as const,
    details: () => [...queryKeys.drivers.all, 'detail'] as const,
    detail: (id: number) => [...queryKeys.drivers.details(), id] as const,
    availableVehicles: ['drivers', 'available-vehicles'] as const,
  },
  
  // Geofences
  geofences: {
    all: ['geofences'] as const,
    lists: () => [...queryKeys.geofences.all, 'list'] as const,
    list: (filters: GeofenceFilters) => [...queryKeys.geofences.lists(), filters] as const,
    details: () => [...queryKeys.geofences.all, 'detail'] as const,
    detail: (id: number) => [...queryKeys.geofences.details(), id] as const,
    events: (id: number) => [...queryKeys.geofences.detail(id), 'events'] as const,
    stats: (id: number) => [...queryKeys.geofences.detail(id), 'stats'] as const,
    monitor: ['geofences', 'monitor'] as const,
  },
  
  // Tracking
  tracking: {
    realTimePositions: ['tracking', 'real-time-positions'] as const,
    activeSessions: ['tracking', 'active-sessions'] as const,
    alerts: ['tracking', 'alerts'] as const,
    deviceRoutes: (deviceId: number) => ['tracking', 'device-routes', deviceId] as const,
    deviceStatus: (deviceId: number) => ['tracking', 'device-status', deviceId] as const,
    allDevicesStatus: ['tracking', 'all-devices-status'] as const,
    devicesActivity: ['tracking', 'devices-activity'] as const,
  },
  
  // Reports
  reports: {
    all: ['reports'] as const,
    lists: () => [...queryKeys.reports.all, 'list'] as const,
    list: () => [...queryKeys.reports.lists()] as const,
    details: () => [...queryKeys.reports.all, 'detail'] as const,
    detail: (id: number) => [...queryKeys.reports.details(), id] as const,
  },
  
  // Parking
  parking: {
    carParks: ['parking', 'car-parks'] as const,
    carPark: (id: number) => ['parking', 'car-park', id] as const,
    carLanes: (parkId: number) => ['parking', 'car-lanes', parkId] as const,
    carSlots: (laneId: number) => ['parking', 'car-slots', laneId] as const,
  },
  
  // Communication
  communication: {
    cellTowers: ['communication', 'cell-towers'] as const,
    smsHistory: ['communication', 'sms-history'] as const,
  },
  
  // Tickets
  tickets: {
    all: ['tickets'] as const,
    lists: () => [...queryKeys.tickets.all, 'list'] as const,
    list: () => [...queryKeys.tickets.lists()] as const,
  },
  
  // Coordinates
  coordinates: {
    all: ['coordinates'] as const,
    lists: () => [...queryKeys.coordinates.all, 'list'] as const,
    list: (deviceId?: string) => [...queryKeys.coordinates.lists(), deviceId] as const,
    latest: (deviceId?: string) => [...queryKeys.coordinates.all, 'latest', deviceId] as const,
  },
};

// ============================================================================
// AUTHENTICATION HOOKS
// ============================================================================

export const useCurrentUser = (options?: UseQueryOptions<User>) => {
  return useQuery({
    queryKey: queryKeys.auth.currentUser,
    queryFn: authService.getCurrentUser,
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options,
  });
};

export const useLogin = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: authService.login,
    onSuccess: (data: AuthTokens) => {
      // Store tokens in localStorage or secure storage
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      
      // Invalidate and refetch user data
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.currentUser });
      
      toast.success('Inicio de sesión exitoso');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error en el inicio de sesión');
    },
  });
};

export const useLogout = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: authService.logout,
    onSuccess: () => {
      // Clear tokens
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      // Clear all queries
      queryClient.clear();
      
      toast.success('Sesión cerrada exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al cerrar sesión');
    },
  });
};

// ============================================================================
// DEVICE HOOKS
// ============================================================================

export const useDevices = (filters?: DeviceFilters, options?: UseQueryOptions<GPSDevice[]>) => {
  return useQuery({
    queryKey: queryKeys.devices.list(filters || {}),
    queryFn: () => deviceService.getDevices(filters),
    staleTime: 30 * 1000, // 30 seconds
    ...options,
  });
};

export const useDevice = (imei: number, options?: UseQueryOptions<GPSDevice>) => {
  return useQuery({
    queryKey: queryKeys.devices.detail(imei),
    queryFn: () => deviceService.getDevice(imei),
    enabled: !!imei,
    staleTime: 30 * 1000,
    ...options,
  });
};

export const useCreateDevice = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: deviceService.createDevice,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.devices.lists() });
      toast.success('Dispositivo creado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al crear dispositivo');
    },
  });
};

export const useUpdateDevice = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ imei, data }: { imei: number; data: Partial<GPSDevice> }) =>
      deviceService.updateDevice(imei, data),
    onSuccess: (_: GPSDevice, { imei }: { imei: number; data: Partial<GPSDevice> }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.devices.detail(imei) });
      queryClient.invalidateQueries({ queryKey: queryKeys.devices.lists() });
      toast.success('Dispositivo actualizado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al actualizar dispositivo');
    },
  });
};

export const useDeleteDevice = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: deviceService.deleteDevice,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.devices.lists() });
      toast.success('Dispositivo eliminado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al eliminar dispositivo');
    },
  });
};

export const useDeviceHistory = (
  imei: number,
  startDate?: string,
  endDate?: string,
  options?: UseQueryOptions<Location[]>
) => {
  return useQuery({
    queryKey: queryKeys.devices.history(imei),
    queryFn: () => deviceService.getDeviceHistory(imei, startDate, endDate),
    enabled: !!imei,
    staleTime: 60 * 1000, // 1 minute
    ...options,
  });
};

export const useDeviceEvents = (
  imei: number,
  eventType?: string,
  startDate?: string,
  endDate?: string,
  options?: UseQueryOptions<DeviceEvent[]>
) => {
  return useQuery({
    queryKey: queryKeys.devices.events(imei),
    queryFn: () => deviceService.getDeviceEvents(imei, eventType, startDate, endDate),
    enabled: !!imei,
    staleTime: 60 * 1000,
    ...options,
  });
};

export const useDeviceTrail = (
  imei: number,
  startDate?: string,
  endDate?: string,
  options?: UseQueryOptions<DeviceTrail>
) => {
  return useQuery({
    queryKey: queryKeys.devices.trail(imei),
    queryFn: () => deviceService.getDeviceTrail(imei, startDate, endDate),
    enabled: !!imei,
    staleTime: 60 * 1000,
    ...options,
  });
};

export const useDeviceConnections = (
  imei: number,
  startTime?: string,
  endTime?: string,
  options?: UseQueryOptions<NetworkEvent[]>
) => {
  return useQuery({
    queryKey: queryKeys.devices.connections(imei),
    queryFn: () => deviceService.getConnectionHistory(imei, startTime, endTime),
    enabled: !!imei,
    staleTime: 60 * 1000,
    ...options,
  });
};

export const useDeviceStatus = (imei: number, options?: UseQueryOptions<DeviceStatus>) => {
  return useQuery({
    queryKey: queryKeys.devices.status(imei),
    queryFn: () => deviceService.getCurrentStatus(imei),
    enabled: !!imei,
    staleTime: 30 * 1000,
    refetchInterval: 30 * 1000, // Refetch every 30 seconds
    ...options,
  });
};

export const useSendDeviceCommand = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ imei, command }: { imei: number; command: DeviceCommand }) =>
      deviceService.sendCommand(imei, command),
    onSuccess: (_: DeviceCommand, { imei }: { imei: number; command: DeviceCommand }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.devices.detail(imei) });
      toast.success('Comando enviado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al enviar comando');
    },
  });
};

// ============================================================================
// VEHICLE HOOKS
// ============================================================================

export const useVehicles = (filters?: VehicleFilters, options?: UseQueryOptions<Vehicle[]>) => {
  return useQuery({
    queryKey: queryKeys.vehicles.list(filters || {}),
    queryFn: () => vehicleService.getVehicles(filters),
    staleTime: 60 * 1000,
    ...options,
  });
};

export const useVehicle = (id: number, options?: UseQueryOptions<Vehicle>) => {
  return useQuery({
    queryKey: queryKeys.vehicles.detail(id),
    queryFn: () => vehicleService.getVehicle(id),
    enabled: !!id,
    staleTime: 60 * 1000,
    ...options,
  });
};

export const useCreateVehicle = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: vehicleService.createVehicle,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.vehicles.lists() });
      toast.success('Vehículo creado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al crear vehículo');
    },
  });
};

export const useUpdateVehicle = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Vehicle> }) =>
      vehicleService.updateVehicle(id, data),
    onSuccess: (_: Vehicle, { id }: { id: number; data: Partial<Vehicle> }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.vehicles.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.vehicles.lists() });
      toast.success('Vehículo actualizado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al actualizar vehículo');
    },
  });
};

export const useDeleteVehicle = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: vehicleService.deleteVehicle,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.vehicles.lists() });
      toast.success('Vehículo eliminado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al eliminar vehículo');
    },
  });
};

export const useAvailableDevices = (options?: UseQueryOptions<GPSDevice[]>) => {
  return useQuery({
    queryKey: queryKeys.vehicles.availableDevices,
    queryFn: vehicleService.getAvailableDevices,
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options,
  });
};

export const useAvailableDrivers = (options?: UseQueryOptions<Driver[]>) => {
  return useQuery({
    queryKey: queryKeys.vehicles.availableDrivers,
    queryFn: vehicleService.getAvailableDrivers,
    staleTime: 5 * 60 * 1000,
    ...options,
  });
};

export const useAssignDeviceToVehicle = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ vehicleId, deviceId }: { vehicleId: number; deviceId: number }) =>
      vehicleService.assignDevice(vehicleId, deviceId),
    onSuccess: (_: Vehicle, { vehicleId }: { vehicleId: number; deviceId: number }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.vehicles.detail(vehicleId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.vehicles.lists() });
      queryClient.invalidateQueries({ queryKey: queryKeys.vehicles.availableDevices });
      toast.success('Dispositivo asignado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al asignar dispositivo');
    },
  });
};

export const useAssignDriverToVehicle = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ vehicleId, driverId }: { vehicleId: number; driverId: number }) =>
      vehicleService.assignDriver(vehicleId, driverId),
    onSuccess: (_: Vehicle, { vehicleId }: { vehicleId: number; driverId: number }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.vehicles.detail(vehicleId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.vehicles.lists() });
      queryClient.invalidateQueries({ queryKey: queryKeys.vehicles.availableDrivers });
      toast.success('Conductor asignado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al asignar conductor');
    },
  });
};

// ============================================================================
// DRIVER HOOKS
// ============================================================================

export const useDrivers = (filters?: DriverFilters, options?: UseQueryOptions<Driver[]>) => {
  return useQuery({
    queryKey: queryKeys.drivers.list(filters || {}),
    queryFn: () => driverService.getDrivers(filters),
    staleTime: 60 * 1000,
    ...options,
  });
};

export const useDriver = (id: number, options?: UseQueryOptions<Driver>) => {
  return useQuery({
    queryKey: queryKeys.drivers.detail(id),
    queryFn: () => driverService.getDriver(id),
    enabled: !!id,
    staleTime: 60 * 1000,
    ...options,
  });
};

export const useCreateDriver = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: driverService.createDriver,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.drivers.lists() });
      toast.success('Conductor creado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al crear conductor');
    },
  });
};

export const useUpdateDriver = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Driver> }) =>
      driverService.updateDriver(id, data),
    onSuccess: (_: Driver, { id }: { id: number; data: Partial<Driver> }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.drivers.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.drivers.lists() });
      toast.success('Conductor actualizado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al actualizar conductor');
    },
  });
};

export const useDeleteDriver = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: driverService.deleteDriver,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.drivers.lists() });
      toast.success('Conductor eliminado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al eliminar conductor');
    },
  });
};

export const useAvailableVehicles = (options?: UseQueryOptions<Vehicle[]>) => {
  return useQuery({
    queryKey: queryKeys.drivers.availableVehicles,
    queryFn: driverService.getAvailableVehicles,
    staleTime: 5 * 60 * 1000,
    ...options,
  });
};

export const useAssignVehicleToDriver = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ driverId, vehicleId }: { driverId: number; vehicleId: number }) =>
      driverService.assignVehicle(driverId, vehicleId),
    onSuccess: (_: Driver, { driverId }: { driverId: number; vehicleId: number }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.drivers.detail(driverId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.drivers.lists() });
      queryClient.invalidateQueries({ queryKey: queryKeys.drivers.availableVehicles });
      toast.success('Vehículo asignado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al asignar vehículo');
    },
  });
};

// ============================================================================
// GEOFENCING HOOKS
// ============================================================================

export const useGeofences = (filters?: GeofenceFilters, options?: UseQueryOptions<GeoFence[]>) => {
  return useQuery({
    queryKey: queryKeys.geofences.list(filters || {}),
    queryFn: () => geofenceService.getGeofences(filters),
    staleTime: 60 * 1000,
    ...options,
  });
};

export const useGeofence = (id: number, options?: UseQueryOptions<GeoFence>) => {
  return useQuery({
    queryKey: queryKeys.geofences.detail(id),
    queryFn: () => geofenceService.getGeofence(id),
    enabled: !!id,
    staleTime: 60 * 1000,
    ...options,
  });
};

export const useCreateGeofence = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: geofenceService.createGeofence,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.geofences.lists() });
      toast.success('Geocerca creada exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al crear geocerca');
    },
  });
};

export const useUpdateGeofence = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<GeoFence> }) =>
      geofenceService.updateGeofence(id, data),
    onSuccess: (_: GeoFence, { id }: { id: number; data: Partial<GeoFence> }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.geofences.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.geofences.lists() });
      toast.success('Geocerca actualizada exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al actualizar geocerca');
    },
  });
};

export const useDeleteGeofence = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: geofenceService.deleteGeofence,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.geofences.lists() });
      toast.success('Geocerca eliminada exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al eliminar geocerca');
    },
  });
};

export const useGeofenceEvents = (
  id: number,
  startDate?: string,
  endDate?: string,
  options?: UseQueryOptions<GeofenceEvent[]>
) => {
  return useQuery({
    queryKey: queryKeys.geofences.events(id),
    queryFn: () => geofenceService.getGeofenceEvents(id, startDate, endDate),
    enabled: !!id,
    staleTime: 60 * 1000,
    ...options,
  });
};

export const useGeofenceStats = (
  id: number,
  startDate?: string,
  endDate?: string,
  options?: UseQueryOptions<any>
) => {
  return useQuery({
    queryKey: queryKeys.geofences.stats(id),
    queryFn: () => geofenceService.getGeofenceStats(id, startDate, endDate),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options,
  });
};

export const useMonitorGeofences = (options?: UseQueryOptions<any>) => {
  return useQuery({
    queryKey: queryKeys.geofences.monitor,
    queryFn: geofenceService.monitorGeofences,
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 30 * 1000, // Refetch every 30 seconds
    ...options,
  });
};

// ============================================================================
// TRACKING HOOKS
// ============================================================================

export const useRealTimePositions = (options?: UseQueryOptions<RealTimePosition[]>) => {
  return useQuery({
    queryKey: queryKeys.tracking.realTimePositions,
    queryFn: trackingService.getRealTimePositions,
    staleTime: 10 * 1000, // 10 seconds
    refetchInterval: 10 * 1000, // Refetch every 10 seconds
    ...options,
  });
};

export const useActiveSessions = (options?: UseQueryOptions<GPRSSession[]>) => {
  return useQuery({
    queryKey: queryKeys.tracking.activeSessions,
    queryFn: trackingService.getActiveSessions,
    staleTime: 30 * 1000,
    refetchInterval: 30 * 1000,
    ...options,
  });
};

export const useAlerts = (deviceId?: number, acknowledged?: boolean, options?: UseQueryOptions<Alert[]>) => {
  return useQuery({
    queryKey: queryKeys.tracking.alerts,
    queryFn: () => trackingService.getAlerts(deviceId, acknowledged),
    staleTime: 60 * 1000,
    ...options,
  });
};

export const useAcknowledgeAlert = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: trackingService.acknowledgeAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tracking.alerts });
      toast.success('Alerta reconocida exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al reconocer alerta');
    },
  });
};

export const useDeviceRoutes = (
  deviceId: number,
  completed?: boolean,
  options?: UseQueryOptions<Route[]>
) => {
  return useQuery({
    queryKey: queryKeys.tracking.deviceRoutes(deviceId),
    queryFn: () => trackingService.getDeviceRoutes(deviceId, completed),
    enabled: !!deviceId,
    staleTime: 5 * 60 * 1000,
    ...options,
  });
};

export const useTrackingDeviceStatus = (deviceId: number, options?: UseQueryOptions<DeviceStatus>) => {
  return useQuery({
    queryKey: queryKeys.tracking.deviceStatus(deviceId),
    queryFn: () => trackingService.getDeviceStatus(deviceId),
    enabled: !!deviceId,
    staleTime: 30 * 1000,
    refetchInterval: 30 * 1000,
    ...options,
  });
};

export const useAllDevicesStatus = (options?: UseQueryOptions<DeviceStats>) => {
  return useQuery({
    queryKey: queryKeys.tracking.allDevicesStatus,
    queryFn: trackingService.checkAllDevicesStatus,
    staleTime: 30 * 1000,
    refetchInterval: 30 * 1000,
    ...options,
  });
};

export const useDevicesActivity = (options?: UseQueryOptions<any>) => {
  return useQuery({
    queryKey: queryKeys.tracking.devicesActivity,
    queryFn: trackingService.getDevicesActivityStatus,
    staleTime: 60 * 1000,
    refetchInterval: 60 * 1000,
    ...options,
  });
};

// ============================================================================
// REPORT HOOKS
// ============================================================================

export const useReports = (options?: UseQueryOptions<Report[]>) => {
  return useQuery({
    queryKey: queryKeys.reports.list(),
    queryFn: reportService.getReports,
    staleTime: 5 * 60 * 1000,
    ...options,
  });
};

export const useReport = (id: number, options?: UseQueryOptions<Report>) => {
  return useQuery({
    queryKey: queryKeys.reports.detail(id),
    queryFn: () => reportService.getReport(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
    ...options,
  });
};

export const useCreateReport = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: reportService.createReport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.reports.lists() });
      toast.success('Reporte creado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al crear reporte');
    },
  });
};

export const useGenerateRouteReport = () => {
  return useMutation({
    mutationFn: ({ routeId, dateRange }: { routeId: number; dateRange: DateRange }) =>
      reportService.generateRouteReport(routeId, dateRange),
    onSuccess: () => {
      toast.success('Reporte de ruta generado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al generar reporte de ruta');
    },
  });
};

export const useGenerateDriverReport = () => {
  return useMutation({
    mutationFn: ({ driverId, dateRange }: { driverId: number; dateRange: DateRange }) =>
      reportService.generateDriverReport(driverId, dateRange),
    onSuccess: () => {
      toast.success('Reporte de conductor generado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al generar reporte de conductor');
    },
  });
};

export const useGenerateDeviceReport = () => {
  return useMutation({
    mutationFn: ({ deviceId, dateRange }: { deviceId: number; dateRange: DateRange }) =>
      reportService.generateDeviceReport(deviceId, dateRange),
    onSuccess: () => {
      toast.success('Reporte de dispositivo generado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al generar reporte de dispositivo');
    },
  });
};

// ============================================================================
// PARKING HOOKS
// ============================================================================

export const useCarParks = (options?: UseQueryOptions<CarPark[]>) => {
  return useQuery({
    queryKey: queryKeys.parking.carParks,
    queryFn: parkingService.getCarParks,
    staleTime: 5 * 60 * 1000,
    ...options,
  });
};

export const useCarPark = (id: number, options?: UseQueryOptions<CarPark & { lanes: CarLane[] }>) => {
  return useQuery({
    queryKey: queryKeys.parking.carPark(id),
    queryFn: () => parkingService.getCarPark(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
    ...options,
  });
};

export const useCarLanes = (parkId: number, options?: UseQueryOptions<CarLane[]>) => {
  return useQuery({
    queryKey: queryKeys.parking.carLanes(parkId),
    queryFn: () => parkingService.getCarLanes(parkId),
    enabled: !!parkId,
    staleTime: 5 * 60 * 1000,
    ...options,
  });
};

export const useCarSlots = (laneId: number, options?: UseQueryOptions<CarSlot[]>) => {
  return useQuery({
    queryKey: queryKeys.parking.carSlots(laneId),
    queryFn: () => parkingService.getCarSlots(laneId),
    enabled: !!laneId,
    staleTime: 30 * 1000,
    refetchInterval: 30 * 1000,
    ...options,
  });
};

export const useAssignCarToSlot = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ slotId, carSerial }: { slotId: number; carSerial: string }) =>
      parkingService.assignCarToSlot(slotId, carSerial),
    onSuccess: (_: CarSlot) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: queryKeys.parking.carParks });
      toast.success('Vehículo asignado al espacio exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al asignar vehículo al espacio');
    },
  });
};

export const useRemoveCarFromSlot = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: parkingService.removeCarFromSlot,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.parking.carParks });
      toast.success('Vehículo removido del espacio exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al remover vehículo del espacio');
    },
  });
};

// ============================================================================
// COMMUNICATION HOOKS
// ============================================================================

export const useCellTowers = (options?: UseQueryOptions<CellTower[]>) => {
  return useQuery({
    queryKey: queryKeys.communication.cellTowers,
    queryFn: communicationService.getCellTowers,
    staleTime: 5 * 60 * 1000,
    ...options,
  });
};

export const useSMSHistory = (deviceId?: number, options?: UseQueryOptions<ServerSMS[]>) => {
  return useQuery({
    queryKey: queryKeys.communication.smsHistory,
    queryFn: () => communicationService.getSMSHistory(deviceId),
    staleTime: 60 * 1000,
    ...options,
  });
};

export const useSendSMS = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ deviceId, message }: { deviceId: number; message: string }) =>
      communicationService.sendSMS(deviceId, message),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.communication.smsHistory });
      toast.success('SMS enviado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al enviar SMS');
    },
  });
};

// ============================================================================
// TICKET HOOKS
// ============================================================================

export const useTicketDetails = (deviceId?: number, options?: UseQueryOptions<TicketDetail[]>) => {
  return useQuery({
    queryKey: queryKeys.tickets.list(),
    queryFn: () => ticketService.getTicketDetails(deviceId),
    staleTime: 5 * 60 * 1000,
    ...options,
  });
};

export const useCreateTicketDetail = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ticketService.createTicketDetail,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tickets.lists() });
      toast.success('Ticket creado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al crear ticket');
    },
  });
};

// ============================================================================
// COORDINATE HOOKS
// ============================================================================

export const useCoordinates = (deviceId?: string, options?: UseQueryOptions<any[]>) => {
  return useQuery({
    queryKey: queryKeys.coordinates.list(deviceId),
    queryFn: () => coordinateService.getCoordinates(deviceId),
    staleTime: 30 * 1000,
    ...options,
  });
};

export const useLatestCoordinates = (deviceId?: string, options?: UseQueryOptions<any>) => {
  return useQuery({
    queryKey: queryKeys.coordinates.latest(deviceId),
    queryFn: () => coordinateService.getLatestCoordinates(deviceId),
    staleTime: 10 * 1000,
    refetchInterval: 10 * 1000,
    ...options,
  });
};

export const useGenerateTestData = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ deviceId, points }: { deviceId: string; points?: number }) =>
      coordinateService.generateTestData(deviceId, points),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.coordinates.lists() });
      toast.success('Datos de prueba generados exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Error al generar datos de prueba');
    },
  });
}; 
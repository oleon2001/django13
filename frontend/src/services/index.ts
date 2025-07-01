// Core Services
export { default as api } from './api';
export { default as authService } from './auth';

// GPS and Device Services
export { deviceService } from './deviceService';
export { gpsService } from './gpsService';
export { coordinateService } from './coordinateService';
export { gpsDeviceService } from './gps/GPSDeviceService';
export { gpsConnectionService } from './hardware/gpsConnection';

// Vehicle and Driver Services
export { vehicleService } from './vehicleService';
export { driverService } from './driverService';

// Parking and Sensor Services
export { parkingService } from './parkingService';
export { sensorService } from './sensorService';

// Report and Geofencing Services
export { reportService } from './reportService';
export { geofencingService } from './geofencingService';

// Communication and Monitoring Services
export { communicationService } from './communicationService';
export { monitoringService } from './monitoringService';

// Tracking Service
export { trackingService } from './trackingService';

// Real-time and WebSocket Services
export { realTimeService } from './realTimeService';
export { default as WebSocketService } from './websocket';

// Route Service
export { routeService } from './routeService';

// Shared Services
export * from './shared/coordinateService';

// Export all service types from individual services
export type {
  // Geofencing Types
  GeoFence,
  GeofenceEvent,
  GeofenceAlert,
  GeofenceRule,
  GeofenceStatistics,
  MonitoringData,
} from './geofencingService';

export type {
  // Report Types
  Report,
  RouteReport,
  DriverReport,
  DeviceStatistics,
  DailyStatistics,
} from './reportService';

export type {
  // Communication Types
  BluetoothDevice,
  SatelliteConnection,
  CommunicationMessage,
  CommunicationStats,
} from './communicationService';

export type {
  // Monitoring Types
  AlarmLog,
  SystemHealth,
  PerformanceMetrics,
  MonitoringAlert,
} from './monitoringService';

export type {
  // Tracking Types
  TrackingSession,
  TrackingWaypoint,
  TrackingRoute,
  TrackingCommand,
  TrackingStats,
} from './trackingService'; 
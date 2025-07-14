/**
 * Core interfaces for the GPS tracking system.
 * Migrated from backend Django interfaces to TypeScript.
 */

export interface Point {
  latitude: number;
  longitude: number;
}

export interface LocationData {
  latitude: number;
  longitude: number;
  speed: number;
  course: number;
  altitude: number;
  satellites: number;
  accuracy: number;
  timestamp: Date;
}

export interface EventData {
  type: string;
  position?: Point;
  speed: number;
  course: number;
  altitude: number;
  timestamp: Date;
  odometer: number;
  rawData?: string;
}

export interface GPSLocation {
  id: number;
  device: number;
  timestamp: Date;
  position: Point;
  speed: number;
  course: number;
  altitude: number;
  satellites: number;
  accuracy: number;
  hdop?: number;
  pdop?: number;
  fixQuality?: number;
  fixType?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface GPSEvent {
  id: number;
  device: number;
  type: string;
  position?: Point;
  speed: number;
  course: number;
  altitude: number;
  timestamp: Date;
  odometer: number;
  rawData?: string;
  source?: string;
  text?: string;
  inputs: number;
  outputs: number;
  inputChanges: number;
  outputChanges: number;
  alarmChanges: number;
  changesDescription?: string;
  createdAt: Date;
}

export interface ILocationService {
  processLocation(device: any, locationData: LocationData): Promise<void>;
  getDeviceHistory(imei: string, startTime: Date, endTime: Date): Promise<LocationData[]>;
}

export interface IEventService {
  processEvent(device: any, eventData: EventData): Promise<void>;
  getDeviceEvents(imei: string, eventType?: string): Promise<EventData[]>;
}

export interface IDeviceRepository {
  getDevice(imei: string): Promise<any | null>;
  getAllDevices(): Promise<any[]>;
  saveDevice(device: any): Promise<void>;
  updateDevicePosition(imei: string, position: Point): Promise<void>;
  getDeviceLocations(imei: string, startTime?: Date, endTime?: Date): Promise<GPSLocation[]>;
  getDeviceEvents(imei: string, eventType?: string): Promise<GPSEvent[]>;
}

export interface IProtocolHandler {
  decodePacket(data: Uint8Array): Record<string, any>;
  encodeCommand(command: string, params: Record<string, any>): Uint8Array;
  validatePacket(data: Uint8Array): boolean;
  sendPing(device: any): Promise<Record<string, any>>;
}

export interface IDeviceServer {
  start(host?: string, port?: number): Promise<void>;
  stop(): Promise<void>;
  isRunning(): boolean;
}

export interface INotificationService {
  sendNotification(message: any, recipients: any[], channels?: string[]): Promise<Record<string, any>>;
  sendDeviceAlarm(device: any, alarmType: string, position?: Point, additionalData?: Record<string, any>): Promise<void>;
}

export interface IAnalyticsService {
  generateRealTimeMetrics(timeWindowHours?: number): Promise<any>;
  analyzeDevicePerformance(deviceImei: string, daysBack?: number): Promise<any>;
  detectDrivingPatterns(deviceImei: string, daysBack?: number): Promise<Record<string, any>>;
}

export interface IReportService {
  generateReport(reportType: string, deviceId: number, startDate: Date, endDate: Date, format?: string): Promise<any>;
  getAvailableReports(): Promise<Record<string, any>[]>;
}

export interface ISecurityService {
  signCommand(command: string, deviceImei: string, userId: number, additionalData?: Record<string, any>): Promise<Record<string, any>>;
  verifyCommand(signedCommand: Record<string, any>, device: any, user: any): Promise<Record<string, any>>;
  getCommandRiskLevel(command: string): string;
}

export interface IConnectionService {
  registerConnection(device: any, ipAddress: string, port: number, protocol: string): Promise<any>;
  registerDisconnection(device: any, sessionId: string, reason?: string): Promise<void>;
  getActiveSessions(): Promise<any[]>;
  cleanupOldSessions(days?: number): Promise<number>;
}

export interface IMaintenanceService {
  scheduleMaintenance(device: any, maintenanceType: string, scheduledDate: Date): Promise<any>;
  recordMaintenance(device: any, maintenanceType: string, description: string, performedBy: any): Promise<any>;
  getMaintenanceHistory(device: any): Promise<any[]>;
}

export interface IGeofenceService {
  createGeofence(name: string, geometry: Point, owner: any): Promise<any>;
  checkDeviceInGeofence(device: any, geofence: any): Promise<boolean>;
  getDeviceGeofences(device: any): Promise<any[]>;
}

export interface IAlertService {
  createAlert(device: any, alertType: string, message: string, position?: Point): Promise<any>;
  acknowledgeAlert(alert: any, acknowledgedBy: any): Promise<void>;
  getUnacknowledgedAlerts(user: any): Promise<any[]>;
}

export interface ITrackingService {
  startTrackingSession(device: any, user: any): Promise<any>;
  stopTrackingSession(session: any): Promise<void>;
  addTrackingPoint(session: any, position: Point, speed: number, timestamp: Date): Promise<any>;
  getActiveSessions(user: any): Promise<any[]>;
}

export interface IConfigurationService {
  getDeviceConfig(device: any): Promise<Record<string, any>>;
  updateDeviceConfig(device: any, config: Record<string, any>): Promise<void>;
  getSystemConfig(): Promise<Record<string, any>>;
  updateSystemConfig(config: Record<string, any>): Promise<void>;
}

export interface ILoggingService {
  logDeviceEvent(device: any, eventType: string, message: string, level?: string): Promise<void>;
  logSystemEvent(eventType: string, message: string, level?: string, user?: any): Promise<void>;
  getDeviceLogs(device: any, startTime?: Date, endTime?: Date): Promise<any[]>;
}

export interface IStatisticsService {
  calculateDeviceStatistics(device: any, startDate: Date, endDate: Date): Promise<Record<string, any>>;
  calculateFleetStatistics(devices: any[], startDate: Date, endDate: Date): Promise<Record<string, any>>;
  generateDailyReport(date: Date): Promise<Record<string, any>>;
}

export interface IBackupService {
  createBackup(backupType?: string): Promise<string>;
  restoreBackup(backupPath: string): Promise<boolean>;
  listBackups(): Promise<Record<string, any>[]>;
  cleanupOldBackups(daysToKeep?: number): Promise<number>;
}

export interface IHealthCheckService {
  checkSystemHealth(): Promise<Record<string, any>>;
  checkDeviceHealth(device: any): Promise<Record<string, any>>;
  checkDatabaseHealth(): Promise<Record<string, any>>;
  checkNetworkHealth(): Promise<Record<string, any>>;
} 
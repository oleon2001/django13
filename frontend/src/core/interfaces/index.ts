// Core interfaces migrated from Django backend
// Based on skyguard/apps/core/interfaces.py

export interface Point {
  x: number; // longitude
  y: number; // latitude
}

export interface GPSDevice {
  imei: number;
  name: string;
  position?: Point;
  speed: number;
  course: number;
  altitude: number;
  last_log?: string;
  owner?: User;
  icon: string;
  odometer: number;
  created_at: string;
  updated_at: string;
  connection_status: 'ONLINE' | 'OFFLINE' | 'SLEEPING' | 'ERROR';
  is_active: boolean;
  protocol: string;
  route?: number;
  economico?: number;
}

export interface GPSLocation {
  id: number;
  device: GPSDevice;
  timestamp: string;
  position: Point;
  speed: number;
  course: number;
  altitude: number;
  satellites: number;
  accuracy: number;
  hdop?: number;
  pdop?: number;
  fix_quality?: number;
  fix_type?: number;
  created_at: string;
}

export interface GPSEvent {
  id: number;
  device: GPSDevice;
  type: string;
  position?: Point;
  speed: number;
  course: number;
  altitude: number;
  timestamp: string;
  odometer: number;
  raw_data?: string;
  source?: string;
  text?: string;
  inputs: number;
  outputs: number;
  input_changes: number;
  output_changes: number;
  alarm_changes: number;
  changes_description?: string;
  created_at: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  is_superuser: boolean;
}

export interface LocationData {
  latitude: number;
  longitude: number;
  timestamp: string;
  speed: number;
  course: number;
  altitude: number;
  satellites: number;
  accuracy: number;
  hdop?: number;
  pdop?: number;
  fix_quality?: number;
  fix_type?: number;
}

export interface EventData {
  type: string;
  timestamp: string;
  position?: Point;
  speed: number;
  course: number;
  altitude: number;
  odometer: number;
  source?: string;
  text?: string;
  inputs: number;
  outputs: number;
  input_changes: number;
  output_changes: number;
  alarm_changes: number;
  changes_description?: string;
}

export interface NotificationMessage {
  id: string;
  title: string;
  message: string;
  category: string;
  priority: string;
  timestamp: string;
  device_imei?: string;
  position?: Point;
  data?: Record<string, any>;
  action_url?: string;
  expiry?: string;
}

export interface NotificationRecipient {
  user_id: number;
  name: string;
  email?: string;
  phone?: string;
  push_token?: string;
  preferred_channels?: string[];
  timezone: string;
}

export interface NotificationResult {
  success: boolean;
  message_id?: string;
  error?: string;
  channels_sent?: string[];
}

export interface DeviceSession {
  id: string;
  device: GPSDevice;
  start_time: string;
  end_time?: string;
  ip_address: string;
  port: number;
  protocol: string;
  is_active: boolean;
  last_activity: string;
  bytes_sent: number;
  bytes_received: number;
  packets_sent: number;
  packets_received: number;
  created_at: string;
  updated_at: string;
}

export interface AnalyticsMetrics {
  total_devices: number;
  online_devices: number;
  offline_devices: number;
  avg_speed: number;
  max_speed: number;
  total_distance: number;
  alerts_count: number;
  battery_avg: number;
  signal_avg: number;
  anomalies_detected: number;
  efficiency_score: number;
}

export interface DeviceAnalytics {
  device_imei: string;
  total_locations: number;
  avg_speed: number;
  max_speed: number;
  distance_traveled: number;
  uptime_percentage: number;
  battery_health: string;
  signal_quality: string;
  anomaly_score: number;
  efficiency_rating: string;
  predicted_maintenance?: string;
}

// Core Service Interfaces
export interface IDeviceRepository {
  getDevice(imei: number): Promise<GPSDevice | null>;
  getAllDevices(): Promise<GPSDevice[]>;
  saveDevice(device: GPSDevice): Promise<void>;
  updateDevicePosition(imei: number, position: Point): Promise<void>;
  getDeviceLocations(imei: number, startTime?: string, endTime?: string): Promise<GPSLocation[]>;
  getDeviceEvents(imei: number, eventType?: string): Promise<GPSEvent[]>;
}

export interface ILocationService {
  processLocation(device: GPSDevice, locationData: LocationData): Promise<void>;
  getDeviceHistory(imei: number, startTime: string, endTime: string): Promise<LocationData[]>;
}

export interface IEventService {
  processEvent(device: GPSDevice, eventData: EventData): Promise<void>;
  getDeviceEvents(imei: number, eventType?: string): Promise<EventData[]>;
}

export interface INotificationService {
  sendNotification(message: NotificationMessage, recipients: NotificationRecipient[], channels?: string[]): Promise<NotificationResult>;
  sendDeviceAlarm(device: GPSDevice, alarmType: string, position?: Point, additionalData?: Record<string, any>): Promise<void>;
}

export interface ISecurityService {
  signCommand(command: string, deviceImei: string, userId: number, additionalData?: Record<string, any>): Promise<Record<string, any>>;
  verifyCommand(signedCommand: Record<string, any>, device: GPSDevice, user: User): Promise<Record<string, any>>;
  getCommandRiskLevel(command: string): string;
}

export interface IConnectionService {
  registerConnection(device: GPSDevice, ipAddress: string, port: number, protocol: string): Promise<DeviceSession>;
  registerDisconnection(device: GPSDevice, sessionId: string, reason?: string): Promise<void>;
  getActiveSessions(): Promise<DeviceSession[]>;
  cleanupOldSessions(days: number): Promise<number>;
}

export interface ILoggingService {
  logDeviceEvent(device: GPSDevice, eventType: string, message: string, level?: string): Promise<void>;
  logSystemEvent(eventType: string, message: string, level?: string, user?: User): Promise<void>;
  getDeviceLogs(device: GPSDevice, startTime?: string, endTime?: string): Promise<any[]>;
}

export interface IHealthCheckService {
  checkSystemHealth(): Promise<Record<string, any>>;
  checkDeviceHealth(device: GPSDevice): Promise<Record<string, any>>;
  checkDatabaseHealth(): Promise<Record<string, any>>;
  checkNetworkHealth(): Promise<Record<string, any>>;
}

export interface IConfigurationService {
  getDeviceConfig(device: GPSDevice): Promise<Record<string, any>>;
  updateDeviceConfig(device: GPSDevice, config: Record<string, any>): Promise<void>;
  getSystemConfig(): Promise<Record<string, any>>;
  updateSystemConfig(config: Record<string, any>): Promise<void>;
}

export interface IAnalyticsService {
  generateRealTimeMetrics(timeWindowHours?: number): Promise<AnalyticsMetrics>;
  analyzeDevicePerformance(deviceImei: string, daysBack?: number): Promise<DeviceAnalytics>;
  detectDrivingPatterns(deviceImei: string, daysBack?: number): Promise<Record<string, any>>;
}

export interface IReportService {
  generateReport(reportType: string, deviceId: number, startDate: string, endDate: string, format?: string): Promise<Blob>;
  getAvailableReports(): Promise<Record<string, any>[]>;
}

// Enums migrated from Django constants
export enum DeviceStatus {
  ONLINE = 'ONLINE',
  OFFLINE = 'OFFLINE',
  SLEEPING = 'SLEEPING',
  ERROR = 'ERROR'
}

export enum EventType {
  TRACK = 'TRACK',
  IO_FIX = 'IO_FIX',
  IO_NOFIX = 'IO_NOFIX',
  GPS_LOST = 'GPS_LOST',
  GPS_OK = 'GPS_OK',
  CURRENT_FIX = 'CURRENT_FIX',
  CURRENT_TIME = 'CURRENT_TIME',
  STARTUP_FIX = 'STARTUP_FIX',
  STARTUP_TIME = 'STARTUP_TIME',
  SMS_RECEIVED = 'SMS_RECEIVED',
  CALL_RECEIVED = 'CALL_RECEIVED',
  RESET = 'RESET',
  ALARM = 'ALARM',
  PRESSURE = 'PRESSURE',
  PEOPLE = 'PEOPLE'
}

export enum ProtocolType {
  CONCOX = 'concox',
  MEILIGAO = 'meiligao',
  WIALON = 'wialon',
  BLUETOOTH = 'bluetooth',
  SATELLITE = 'satellite'
}

export enum AlertType {
  SOS = 'SOS',
  LOW_BATTERY = 'LOW_BATTERY',
  GEOFENCE = 'GEOFENCE',
  SPEED = 'SPEED',
  TAMPER = 'TAMPER',
  POWER = 'POWER',
  OTHER = 'OTHER'
}

export enum NotificationChannel {
  EMAIL = 'email',
  SMS = 'sms',
  PUSH = 'push',
  WEBSOCKET = 'websocket',
  WEBHOOK = 'webhook'
}

export enum NotificationPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
  EMERGENCY = 'emergency'
}

export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
  CRITICAL = 'CRITICAL'
}

export enum MaintenanceType {
  ROUTINE = 'ROUTINE',
  REPAIR = 'REPAIR',
  UPGRADE = 'UPGRADE',
  BATTERY = 'BATTERY',
  OTHER = 'OTHER'
}

export enum ReportFormat {
  PDF = 'pdf',
  CSV = 'csv',
  JSON = 'json',
  XLSX = 'xlsx'
}

export enum CommandRiskLevel {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
} 
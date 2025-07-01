import { ReactNode } from 'react';

// ============================================================================
// CORE TYPES - Tipos fundamentales del sistema
// ============================================================================

export interface BaseEntity {
  id: number;
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  pagination?: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
  };
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
  ordering?: string;
  search?: string;
}

// ============================================================================
// GPS & DEVICE TYPES - Tipos para dispositivos GPS
// ============================================================================

export interface GPSLocation {
  id: number;
  device_id: number;
  latitude: number;
  longitude: number;
  altitude?: number;
  speed: number;
  heading: number;
  course: number;
  satellites: number;
  hdop: number;
  pdop: number;
  fix_quality: number;
  fix_type: string;
  accuracy?: number;
  timestamp: string;
}

export interface GPSDevice extends BaseEntity {
  imei: number;
  name: string;
  serial: string;
  model?: string;
  software_version?: string;
  protocol: 'GT06' | 'GT06N' | 'GT06E' | 'GT06A' | 'GT06C' | 'GT06F' | 'GT06H' | 'GT06I' | 'GT06J' | 'GT06K' | 'GT06L' | 'GT06M' | 'GT06N' | 'GT06O' | 'GT06P' | 'GT06Q' | 'GT06R' | 'GT06S' | 'GT06T' | 'GT06U' | 'GT06V' | 'GT06W' | 'GT06X' | 'GT06Y' | 'GT06Z' | 'CONCOX' | 'MEILIGAO' | 'NMEA';
  connection_status: 'ONLINE' | 'OFFLINE' | 'SLEEPING' | 'ERROR' | 'CONNECTING' | 'DISCONNECTED';
  last_heartbeat: string;
  position?: {
    latitude: number;
    longitude: number;
  };
  speed?: number;
  course?: number;
  altitude?: number;
  satellites?: number;
  hdop?: number;
  pdop?: number;
  fix_quality?: number;
  fix_type?: string;
  battery_level?: number;
  signal_strength?: number;
  route?: number;
  economico?: number;
  current_ip?: string;
  current_port?: number;
  total_connections: number;
  error_count: number;
  last_error?: string;
  harness?: {
    id: number;
    name: string;
    in00: string;
    in01: string;
    out00: string;
  };
  sim_card?: {
    iccid: string;
    phone: string;
    provider: string;
    provider_name: string;
  };
  driver?: Driver;
  vehicle?: Vehicle;
}

export interface DeviceEvent extends BaseEntity {
  device_id: number;
  event_type: 'connection' | 'disconnection' | 'error' | 'command' | 'location' | 'alarm' | 'status_change';
  description: string;
  metadata?: any;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface DeviceCommand extends BaseEntity {
  device_id: number;
  command_type: 'reboot' | 'factory_reset' | 'get_config' | 'set_config' | 'get_status' | 'set_interval' | 'get_location' | 'set_alarm' | 'clear_alarm';
  parameters?: any;
  status: 'pending' | 'sent' | 'delivered' | 'executed' | 'failed' | 'timeout';
  sent_at?: string;
  delivered_at?: string;
  executed_at?: string;
  error_message?: string;
}

// ============================================================================
// VEHICLE & DRIVER TYPES - Tipos para vehículos y conductores
// ============================================================================

export interface Vehicle extends BaseEntity {
  name: string;
  plate: string;
  brand?: string;
  model?: string;
  year?: number;
  color?: string;
  vin?: string;
  engine_number?: string;
  fuel_type?: 'gasoline' | 'diesel' | 'electric' | 'hybrid' | 'lpg' | 'cng';
  status: 'active' | 'inactive' | 'maintenance' | 'retired';
  device_id?: number;
  driver_id?: number;
  device?: GPSDevice;
  driver?: Driver;
  last_maintenance?: string;
  next_maintenance?: string;
  total_mileage?: number;
  insurance_expiry?: string;
  registration_expiry?: string;
}

export interface Driver extends BaseEntity {
  name: string;
  middle_name?: string;
  last_name?: string;
  full_name: string;
  is_active: boolean;
  is_license_valid: boolean;
  birth_date: string;
  civil_status: 'single' | 'married' | 'divorced' | 'widowed';
  payroll: string;
  social_security: string;
  tax_id: string;
  license: string;
  license_type?: 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G' | 'H' | 'I' | 'J' | 'K' | 'L' | 'M' | 'N' | 'O' | 'P' | 'Q' | 'R' | 'S' | 'T' | 'U' | 'V' | 'W' | 'X' | 'Y' | 'Z';
  license_expiry?: string;
  address: string;
  phone: string;
  email?: string;
  emergency_contact?: {
    name: string;
    phone: string;
    relationship: string;
  };
  device_id?: number;
  vehicle_id?: number;
  device?: GPSDevice;
  vehicle?: Vehicle;
  hire_date?: string;
  termination_date?: string;
  salary?: number;
  department?: string;
  position?: string;
}

// ============================================================================
// PARKING TYPES - Tipos para sistema de parqueo
// ============================================================================

export interface CarPark extends BaseEntity {
  name: string;
  location: string;
  address?: string;
  capacity: number;
  occupied_count: number;
  available_count: number;
  status: 'active' | 'inactive' | 'maintenance';
  lanes: CarLane[];
  total_revenue?: number;
  hourly_rate?: number;
  daily_rate?: number;
  monthly_rate?: number;
}

export interface CarLane extends BaseEntity {
  park_id: number;
  name: string;
  prefix: string;
  slot_count: number;
  occupied_count: number;
  available_count: number;
  single: boolean;
  status: 'active' | 'inactive' | 'maintenance';
  slots: CarSlot[];
}

export interface CarSlot extends BaseEntity {
  lane_id: number;
  number: string;
  display_name: string;
  is_occupied: boolean;
  car_serial?: string;
  check_in_time?: string;
  check_out_time?: string;
  duration_hours?: number;
  cost?: number;
  status: 'available' | 'occupied' | 'reserved' | 'maintenance';
}

// ============================================================================
// SENSOR TYPES - Tipos para sensores y alarmas
// ============================================================================

export interface PressureSensor extends BaseEntity {
  device_id: number;
  name: string;
  sensor_type: 'pressure' | 'temperature' | 'humidity' | 'vibration' | 'tilt';
  unit: string;
  min_threshold: number;
  max_threshold: number;
  current_value?: number;
  last_reading?: PressureReading;
  status: 'active' | 'inactive' | 'error';
  calibration_date?: string;
  next_calibration?: string;
}

export interface PressureReading extends BaseEntity {
  sensor_id: number;
  value: number;
  unit: string;
  quality: 'good' | 'fair' | 'poor';
  metadata?: any;
}

export interface AlarmLog extends BaseEntity {
  device_id: number;
  device_name: string;
  alarm_type: 'low_battery' | 'geofence_breach' | 'speed_limit' | 'engine_on' | 'engine_off' | 'panic' | 'ignition' | 'door_open' | 'door_close' | 'temperature' | 'pressure' | 'vibration' | 'tilt' | 'custom';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  acknowledged: boolean;
  acknowledged_by?: number;
  acknowledged_at?: string;
  location?: {
    latitude: number;
    longitude: number;
  };
  metadata?: any;
}

// ============================================================================
// GEOFENCING TYPES - Tipos para cercas geográficas
// ============================================================================

export interface GeoFence extends BaseEntity {
  name: string;
  polygon: {
    coordinates: number[][][];
    type: string;
  };
  owner: number;
  route?: number;
  description?: string;
  color?: string;
  is_active: boolean;
  rules: GeofenceRule[];
}

export interface GeofenceEvent extends BaseEntity {
  device: {
    id: number;
    name: string;
    imei: number;
  };
  geofence: {
    id: number;
    name: string;
  };
  event_type: 'entry' | 'exit';
  location: {
    latitude: number;
    longitude: number;
  };
  speed?: number;
  duration?: number;
}

export interface GeofenceRule extends BaseEntity {
  geofence: number;
  rule_type: 'entry_allowed' | 'exit_allowed' | 'speed_limit' | 'time_limit' | 'schedule' | 'device_restriction';
  devices: number[];
  value: any;
  is_active: boolean;
  description?: string;
}

// ============================================================================
// REPORT TYPES - Tipos para reportes y estadísticas
// ============================================================================

export interface Report extends BaseEntity {
  title: string;
  type: 'route' | 'driver' | 'device' | 'vehicle' | 'geofence' | 'alarm' | 'custom';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  data?: any;
  filters?: any;
  generated_by?: number;
  file_url?: string;
  file_size?: number;
  format: 'csv' | 'json' | 'pdf' | 'excel';
}

export interface RouteReport {
  route: {
    code: number;
    name: string;
  };
  date: string;
  devices_count: number;
  tickets_count: number;
  total_revenue: number;
  total_received: number;
  total_laps: number;
  tickets: any[];
  timesheets: any[];
  statistics: {
    avg_speed: number;
    total_distance: number;
    total_duration: number;
    fuel_consumption?: number;
  };
}

export interface DriverReport {
  driver: {
    id: number;
    name: string;
    full_name: string;
  };
  date_range: string;
  total_tickets: number;
  total_revenue: number;
  total_laps: number;
  avg_laps_per_day: number;
  tickets: any[];
  timesheets: any[];
  performance: {
    avg_speed: number;
    total_distance: number;
    total_duration: number;
    fuel_efficiency?: number;
    safety_score?: number;
  };
}

export interface DeviceStatistics {
  device: GPSDevice;
  total_locations: number;
  total_distance: number;
  avg_speed: number;
  first_location: GPSLocation;
  last_location: GPSLocation;
  date_range: string;
  uptime_percentage: number;
  error_rate: number;
  battery_usage: {
    avg_level: number;
    min_level: number;
    max_level: number;
  };
}

export interface DailyStatistics {
  date: string;
  devices_processed: number;
  statistics: DeviceStatistics[];
  summary: {
    total_devices: number;
    online_devices: number;
    offline_devices: number;
    total_distance: number;
    total_alarms: number;
    avg_speed: number;
  };
}

// ============================================================================
// COMMUNICATION TYPES - Tipos para comunicación
// ============================================================================

export interface BluetoothDevice {
  id: number;
  name: string;
  address: string;
  device_type: string;
  status: 'connected' | 'disconnected' | 'error' | 'scanning';
  last_seen: string;
  signal_strength: number;
  battery_level?: number;
  paired: boolean;
  trusted: boolean;
}

export interface SatelliteConnection {
  id: number;
  device_id: number;
  satellite_id: string;
  status: 'connected' | 'disconnected' | 'connecting' | 'error' | 'searching';
  signal_strength: number;
  last_contact: string;
  message_count: number;
  error_count: number;
  satellite_name?: string;
  frequency?: string;
  data_rate?: number;
}

export interface CommunicationMessage extends BaseEntity {
  device_id: number;
  message_type: 'command' | 'data' | 'status' | 'alert' | 'configuration';
  content: string;
  status: 'sent' | 'delivered' | 'failed' | 'pending' | 'timeout';
  channel: 'bluetooth' | 'satellite' | 'cellular' | 'wifi';
  priority: 'low' | 'medium' | 'high' | 'critical';
  retry_count: number;
  max_retries: number;
  sent_at?: string;
  delivered_at?: string;
  error_message?: string;
}

export interface CommunicationStats {
  total_messages: number;
  successful_messages: number;
  failed_messages: number;
  bluetooth_devices: number;
  satellite_connections: number;
  avg_response_time: number;
  last_24h_messages: number;
  success_rate: number;
  error_rate: number;
}

// ============================================================================
// MONITORING TYPES - Tipos para monitoreo del sistema
// ============================================================================

export interface SystemHealth {
  overall_status: 'healthy' | 'warning' | 'critical' | 'unknown';
  components: {
    database: 'healthy' | 'warning' | 'critical';
    gps_server: 'healthy' | 'warning' | 'critical';
    communication: 'healthy' | 'warning' | 'critical';
    storage: 'healthy' | 'warning' | 'critical';
    web_server: 'healthy' | 'warning' | 'critical';
    cache: 'healthy' | 'warning' | 'critical';
  };
  metrics: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    network_usage: number;
    active_connections: number;
    error_rate: number;
    response_time: number;
    throughput: number;
  };
  last_check: string;
  uptime: number;
  version: string;
}

export interface PerformanceMetrics {
  device_id: number;
  device_name: string;
  response_time: number;
  uptime: number;
  error_count: number;
  last_activity: string;
  connection_quality: number;
  battery_level?: number;
  signal_strength?: number;
  data_usage?: number;
  packet_loss?: number;
  latency?: number;
}

export interface MonitoringAlert extends BaseEntity {
  type: 'system' | 'device' | 'network' | 'security' | 'performance' | 'storage';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  resolved: boolean;
  resolved_at?: string;
  resolved_by?: number;
  metadata?: any;
  category: string;
  source: string;
}

// ============================================================================
// TRACKING TYPES - Tipos para seguimiento y rastreo
// ============================================================================

export interface TrackingSession extends BaseEntity {
  device_id: number;
  device_name: string;
  start_time: string;
  end_time?: string;
  status: 'active' | 'completed' | 'paused' | 'cancelled';
  total_distance: number;
  total_duration: number;
  start_location: {
    latitude: number;
    longitude: number;
  };
  end_location?: {
    latitude: number;
    longitude: number;
  };
  waypoints: TrackingWaypoint[];
  metadata?: any;
  route_id?: number;
  driver_id?: number;
  vehicle_id?: number;
  fuel_consumption?: number;
  stops_count: number;
  avg_speed: number;
  max_speed: number;
}

export interface TrackingWaypoint extends BaseEntity {
  session_id: number;
  latitude: number;
  longitude: number;
  speed: number;
  heading: number;
  altitude?: number;
  accuracy?: number;
  battery_level?: number;
  signal_strength?: number;
  event_type?: string;
  metadata?: any;
}

export interface TrackingRoute extends BaseEntity {
  name: string;
  description?: string;
  waypoints: {
    latitude: number;
    longitude: number;
    order: number;
    name?: string;
  }[];
  total_distance: number;
  estimated_duration: number;
  is_active: boolean;
  color?: string;
  created_by?: number;
}

export interface TrackingCommand extends BaseEntity {
  device_id: number;
  command_type: string;
  parameters: any;
  status: 'pending' | 'sent' | 'delivered' | 'executed' | 'failed' | 'timeout';
  sent_at: string;
  delivered_at?: string;
  executed_at?: string;
  error_message?: string;
  retry_count: number;
  max_retries: number;
}

export interface TrackingStats {
  total_sessions: number;
  active_sessions: number;
  total_distance: number;
  total_duration: number;
  avg_speed: number;
  devices_tracked: number;
  last_24h_sessions: number;
  fuel_consumption: number;
  stops_count: number;
  alerts_count: number;
}

// ============================================================================
// USER & AUTH TYPES - Tipos para usuarios y autenticación
// ============================================================================

export interface User extends BaseEntity {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  last_login?: string;
  date_joined: string;
  groups: string[];
  permissions: string[];
  profile?: UserProfile;
}

export interface UserProfile extends BaseEntity {
  user_id: number;
  phone?: string;
  avatar?: string;
  timezone?: string;
  language?: string;
  preferences?: any;
  notification_settings?: {
    email: boolean;
    sms: boolean;
    push: boolean;
    alerts: boolean;
    reports: boolean;
  };
}

// ============================================================================
// CONFIGURATION TYPES - Tipos para configuración del sistema
// ============================================================================

export interface ServerSettings extends BaseEntity {
  server_name: string;
  logo_url: string;
  favicon_url: string;
  primary_color: string;
  secondary_color: string;
  smtp_server: string;
  smtp_port: number;
  smtp_user: string;
  smtp_password?: string;
  smtp_use_tls: boolean;
  email_from: string;
  timezone: string;
  language: string;
  maintenance_mode: boolean;
  debug_mode: boolean;
  version: string;
  build_date: string;
}

export interface Protocol extends BaseEntity {
  name: string;
  port: number;
  is_active: boolean;
  description: string;
  version: string;
  supported_commands: string[];
  configuration: any;
}

// ============================================================================
// UTILITY TYPES - Tipos de utilidad
// ============================================================================

export interface Column<T> {
  id: string;
  label: string;
  minWidth?: number;
  align?: 'right' | 'left' | 'center';
  header: string;
  accessor: keyof T | ((item: T) => ReactNode);
  sortable?: boolean;
  filterable?: boolean;
  hidden?: boolean;
}

export interface FilterOption {
  value: string | number;
  label: string;
  count?: number;
}

export interface SortOption {
  field: string;
  direction: 'asc' | 'desc';
}

export interface DateRange {
  start_date: string;
  end_date: string;
}

export interface MapBounds {
  north: number;
  south: number;
  east: number;
  west: number;
}

export interface Notification extends BaseEntity {
  user_id: number;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  read: boolean;
  action_url?: string;
  metadata?: any;
}

// ============================================================================
// CONSTANTS - Constantes del sistema
// ============================================================================

export const ROUTE_CHOICES = [
  { value: 1, label: 'Ruta 1' },
  { value: 2, label: 'Ruta 2' },
  { value: 3, label: 'Ruta 3' },
  { value: 4, label: 'Ruta 4' },
  { value: 5, label: 'Ruta 5' },
];

export const DEVICE_STATUSES = {
  ONLINE: 'ONLINE',
  OFFLINE: 'OFFLINE',
  SLEEPING: 'SLEEPING',
  ERROR: 'ERROR',
  CONNECTING: 'CONNECTING',
  DISCONNECTED: 'DISCONNECTED',
} as const;

export const ALARM_SEVERITIES = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
} as const;

export const REPORT_TYPES = {
  ROUTE: 'route',
  DRIVER: 'driver',
  DEVICE: 'device',
  VEHICLE: 'vehicle',
  GEOFENCE: 'geofence',
  ALARM: 'alarm',
  CUSTOM: 'custom',
} as const;

export const EXPORT_FORMATS = {
  CSV: 'csv',
  JSON: 'json',
  PDF: 'pdf',
  EXCEL: 'excel',
  GPX: 'gpx',
} as const; 
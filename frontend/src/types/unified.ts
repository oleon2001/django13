import { ReactNode } from 'react';

// ============================================================================
// BASE TYPES
// ============================================================================

export interface BaseEntity {
  id: number;
  created_at: string;
  updated_at: string;
}

export interface Position {
  latitude: number;
  longitude: number;
}

export interface Point {
  x: number; // longitude
  y: number; // latitude
}

// ============================================================================
// USER & AUTHENTICATION
// ============================================================================

export interface User extends BaseEntity {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  last_login: string;
  date_joined: string;
  groups: string[];
  user_permissions: string[];
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name: string;
  last_name: string;
}

// ============================================================================
// GPS DEVICES
// ============================================================================

export interface Device extends BaseEntity {
  imei: number;
  name: string;
  position: Point | null;
  speed: number;
  course: number;
  altitude: number;
  last_log: string | null;
  owner: User | null;
  icon: string;
  odometer: number;
  connection_status: 'ONLINE' | 'OFFLINE' | 'SLEEPING' | 'ERROR';
  route: number;
  economico: number;
  protocol: string;
  is_active: boolean;
  last_heartbeat: string | null;
  current_ip: string | null;
  current_port: number | null;
  total_connections: number;
  error_count: number;
  last_error: string | null;
  firmware_version: string | null;
  battery_level: number | null;
  signal_strength: number | null;
  satellites: number | null;
  hdop: number | null;
  pdop: number | null;
  fix_quality: number | null;
  fix_type: string | null;
  accuracy: number | null;
}

export interface GPSDevice extends BaseEntity {
  imei: number;
  name: string;
  position: Point | null;
  speed: number;
  course: number;
  altitude: number;
  last_log: string | null;
  owner: User | null;
  icon: string;
  odometer: number;
  connection_status: 'ONLINE' | 'OFFLINE' | 'SLEEPING' | 'ERROR';
  route: number;
  economico: number;
  protocol: string;
  is_active: boolean;
  last_heartbeat: string | null;
  current_ip: string | null;
  current_port: number | null;
  total_connections: number;
  error_count: number;
  last_error: string | null;
  firmware_version: string | null;
  battery_level: number | null;
  signal_strength: number | null;
  satellites: number | null;
  hdop: number | null;
  pdop: number | null;
  fix_quality: number | null;
  fix_type: string | null;
  accuracy: number | null;
}

export interface DeviceStats extends BaseEntity {
  name: string;
  route: number;
  economico: number;
  date_start: string | null;
  date_end: string;
  latitude: number | null;
  longitude: number | null;
  distance: number | null;
  sub_del: number | null;
  baj_del: number | null;
  sub_tra: number | null;
  baj_tra: number | null;
  speed_avg: number | null;
}

export interface FirmwareHistory extends BaseEntity {
  device: Device;
  version: string;
  installed_at: string;
  status: 'SUCCESS' | 'FAILED' | 'PENDING';
  file_size: number;
  checksum: string;
  notes: string | null;
}

export interface DeviceData extends BaseEntity {
  device: Device;
  timestamp: string;
  data_type: 'GPS' | 'SENSOR' | 'STATUS' | 'EVENT' | 'CONFIG';
  data: any;
  processed: boolean;
}

// ============================================================================
// LOCATION & TRACKING
// ============================================================================

export interface Location extends BaseEntity {
  device: GPSDevice;
  timestamp: string;
  position: Point;
  speed: number;
  course: number;
  altitude: number;
  satellites: number;
  accuracy: number;
  hdop: number;
  pdop: number;
  fix_quality: number;
  fix_type: number;
}

export interface GPSLocation extends Location {
  // Extends Location with GPS-specific fields
}

// ============================================================================
// EVENTS & NETWORK
// ============================================================================

export interface NetworkEvent extends BaseEntity {
  device: GPSDevice;
  event_type: 'CONNECT' | 'DISCONNECT' | 'TIMEOUT' | 'ERROR' | 'RECONNECT' | 'AUTH_FAIL' | 'PROTOCOL_ERROR';
  timestamp: string;
  ip_address: string;
  port: number;
  protocol: string;
  session_id: string | null;
  duration: string | null;
  error_message: string | null;
  raw_data: any | null;
}

export interface DeviceEvent extends BaseEntity {
  device: GPSDevice;
  type: 'CONNECT' | 'DISCONNECT' | 'LOGIN' | 'LOGOUT' | 'ALARM' | 'TRACK' | 'STATUS' | 'CONFIG' | 'OTHER';
  timestamp: string;
  position: Point | null;
  speed: number | null;
  course: number | null;
  altitude: number | null;
  odometer: number | null;
  data: any;
}

// ============================================================================
// VEHICLES & DRIVERS
// ============================================================================

export interface Vehicle extends BaseEntity {
  plate: string;
  make: string;
  model: string;
  year: number;
  color: string;
  vehicle_type: 'CAR' | 'TRUCK' | 'MOTORCYCLE' | 'BUS' | 'VAN' | 'OTHER';
  status: 'ACTIVE' | 'INACTIVE' | 'MAINTENANCE' | 'REPAIR';
  vin: string | null;
  economico: string | null;
  fuel_type: 'GASOLINE' | 'DIESEL' | 'ELECTRIC' | 'HYBRID' | 'GAS';
  engine_size: string | null;
  passenger_capacity: number | null;
  cargo_capacity: number | null;
  insurance_policy: string | null;
  insurance_expiry: string | null;
  registration_expiry: string | null;
  mileage: number;
  last_service_date: string | null;
  next_service_date: string | null;
  device: GPSDevice | null;
  driver: Driver | null;
}

export interface Driver extends BaseEntity {
  name: string;
  middle_name: string;
  last_name: string;
  birth_date: string;
  civil_status: 'SOL' | 'CAS' | 'VIU' | 'DIV';
  payroll: string;
  social_security: string;
  tax_id: string;
  license: string | null;
  license_expiry: string | null;
  address: string;
  phone: string;
  phone1: string | null;
  phone2: string | null;
  is_active: boolean;
  vehicles: Vehicle[];
}

// ============================================================================
// GEOFENCING
// ============================================================================

export interface GeoFence extends BaseEntity {
  name: string;
  geometry: any; // GeoJSON Polygon
  owner: User;
  description: string | null;
  is_active: boolean;
  color: string | null;
  alert_on_entry: boolean;
  alert_on_exit: boolean;
  alert_on_stay: boolean;
  stay_threshold: number | null;
}

export interface GeofenceEvent extends BaseEntity {
  geofence: GeoFence;
  device: GPSDevice;
  event_type: 'ENTRY' | 'EXIT' | 'STAY';
  timestamp: string;
  position: Point;
  duration: number | null;
}

// ============================================================================
// TRACKING & MONITORING
// ============================================================================

export interface Alert extends BaseEntity {
  device: GPSDevice;
  alert_type: 'SOS' | 'LOW_BATTERY' | 'GEOFENCE' | 'SPEED' | 'TAMPER' | 'POWER' | 'OTHER';
  position: Point | null;
  message: string;
  is_acknowledged: boolean;
  acknowledged_by: User | null;
  acknowledged_at: string | null;
}

export interface Route extends BaseEntity {
  device: GPSDevice;
  start_time: string;
  end_time: string | null;
  distance: number;
  average_speed: number;
  max_speed: number;
  is_completed: boolean;
}

export interface DeviceStatus extends BaseEntity {
  device: GPSDevice;
  is_online: boolean;
  last_heartbeat: string | null;
  battery_level: number | null;
  signal_strength: number | null;
  firmware_version: string | null;
  last_maintenance: string | null;
  next_maintenance: string | null;
}

// ============================================================================
// SESSIONS & PROTOCOLS
// ============================================================================

export interface GPRSSession extends BaseEntity {
  start: string;
  end: string;
  ip: string;
  port: number;
  device: GPSDevice;
  bytes_transferred: number;
  packets_count: number;
  records_count: number;
  events_count: number;
  is_active: boolean;
}

export interface UDPSession extends BaseEntity {
  session: number;
  imei: GPSDevice;
  expires: string;
  host: string;
  port: number;
  lastRec: number;
}

// ============================================================================
// ASSETS & PARKING
// ============================================================================

export interface CarPark extends BaseEntity {
  name: string;
  description: string | null;
}

export interface CarLane extends BaseEntity {
  park: CarPark;
  name: string;
  prefix: string;
  slot_count: number;
  single: boolean;
}

export interface CarSlot extends BaseEntity {
  lane: CarLane;
  number: number;
  position: Point;
  car_serial: string | null;
  car_date: string | null;
}

// ============================================================================
// REPORTS & STATISTICS
// ============================================================================

export interface Report extends BaseEntity {
  title: string;
  description: string | null;
  report_type: string;
  parameters: any;
  generated_by: User;
  file_path: string | null;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
}

export interface Statistics extends BaseEntity {
  device: GPSDevice;
  date: string;
  total_distance: number;
  total_time: number;
  average_speed: number;
  max_speed: number;
  stops_count: number;
  alerts_count: number;
}

// ============================================================================
// COMMUNICATION
// ============================================================================

export interface CellTower extends BaseEntity {
  mcc: number;
  mnc: number;
  lac: number;
  cell_id: number;
  signal_strength: number | null;
}

export interface ServerSMS extends BaseEntity {
  device: GPSDevice;
  message: string;
  sent_at: string;
  status: 'PENDING' | 'SENT' | 'DELIVERED' | 'FAILED';
  response: string | null;
}

// ============================================================================
// TICKETS & LOGS
// ============================================================================

export interface TicketDetail extends BaseEntity {
  device: GPSDevice;
  date: string | null;
  driver_name: string;
  total: number;
  received: number;
  ticket_data: string;
}

// ============================================================================
// UI & COMPONENTS
// ============================================================================

export interface Column<T> {
  id: string;
  label: string;
  minWidth?: number;
  align?: 'right' | 'left' | 'center';
  header: string;
  accessor: keyof T | ((item: T) => ReactNode);
}

export interface ServerSettings extends BaseEntity {
  server_name: string;
  logo_url: string;
  favicon_url: string;
  primary_color: string;
  secondary_color: string;
  smtp_host: string;
  smtp_port: number;
  smtp_user: string;
  smtp_password: string | null;
  smtp_use_tls: boolean;
  email_from: string;
}

export interface Protocol extends BaseEntity {
  name: string;
  port: number;
  is_active: boolean;
  description: string;
}

// ============================================================================
// API RESPONSES
// ============================================================================

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface DeviceStats {
  total: number;
  online: number;
  offline: number;
  error: number;
}

// ============================================================================
// FILTERS & QUERY PARAMS
// ============================================================================

export interface PaginationParams {
  page?: number;
  page_size?: number;
  ordering?: string;
  search?: string;
}

export interface DeviceFilters {
  status?: string;
  route?: number;
  owner?: number;
  is_active?: boolean;
  connection_status?: string;
}

export interface VehicleFilters {
  status?: string;
  vehicle_type?: string;
  with_gps?: boolean;
  with_driver?: boolean;
  available?: boolean;
}

export interface DriverFilters {
  is_active?: boolean;
  with_vehicle?: boolean;
  available?: boolean;
}

export interface GeofenceFilters {
  owner?: number;
  is_active?: boolean;
}

export interface DateRange {
  start_date: string;
  end_date: string;
}

// ============================================================================
// REAL-TIME DATA
// ============================================================================

export interface RealTimePosition {
  device: GPSDevice;
  position: Point;
  speed: number;
  course: number;
  timestamp: string;
  is_moving: boolean;
}

export interface DeviceTrail {
  device: GPSDevice;
  positions: Point[];
  timestamps: string[];
  speeds: number[];
  total_distance: number;
  duration: number;
}

// ============================================================================
// COMMANDS & ACTIONS
// ============================================================================

export interface DeviceCommand {
  device: GPSDevice;
  command_type: string;
  parameters: any;
  status: 'PENDING' | 'SENT' | 'ACKNOWLEDGED' | 'FAILED';
  sent_at: string | null;
  acknowledged_at: string | null;
  response: string | null;
}

export interface GeofenceAction {
  geofence: GeoFence;
  action_type: 'CREATE' | 'UPDATE' | 'DELETE' | 'ACTIVATE' | 'DEACTIVATE';
  parameters: any;
  status: 'PENDING' | 'COMPLETED' | 'FAILED';
  executed_at: string | null;
  error_message: string | null;
} 
// GPS interfaces migrated from Django backend
// Based on skyguard/apps/gps/models/

import { GPSDevice, GPSLocation, GPSEvent, User, Point } from '../../core/interfaces';

// Device Models
export interface SimCard {
  iccid: number;
  imsi?: number;
  provider: number;
  phone: string;
}

export interface DeviceHarness {
  id: number;
  name: string;
  in00: string;
  in01: string;
  in02?: string;
  in03?: string;
  in04?: string;
  in05?: string;
  in06: string;
  in07: string;
  in08: string;
  in09?: string;
  in10?: string;
  in11?: string;
  in12?: string;
  in13?: string;
  in14?: string;
  in15?: string;
  out00: string;
  out01?: string;
  out02?: string;
  out03?: string;
  out04?: string;
  out05?: string;
  out06?: string;
  out07?: string;
  out08?: string;
  out09?: string;
  out10?: string;
  out11?: string;
  out12?: string;
  out13?: string;
  out14?: string;
  out15?: string;
  input_config?: string;
}

export interface ExtendedGPSDevice extends GPSDevice {
  serial: number;
  model: number;
  software_version: string;
  inputs: number;
  outputs: number;
  alarm_mask: number;
  alarms: number;
  firmware_file?: string;
  last_firmware_update?: string;
  comments?: string;
  sim_card?: SimCard;
  harness?: DeviceHarness;
  new_outputs?: number;
  new_input_flags?: string;
  first_connection?: string;
  last_connection?: string;
  current_ip?: string;
  current_port?: number;
  total_connections: number;
  firmware_history: string[];
  last_error?: string;
  error_count: number;
  connection_quality: number;
  last_heartbeat?: string;
}

// Location Models
export interface ExtendedGPSLocation extends GPSLocation {
  hdop?: number;
  pdop?: number;
  fix_quality?: number;
  fix_type?: number;
}

// Event Models
export interface ExtendedGPSEvent extends GPSEvent {
  source?: string;
  text?: string;
  inputs: number;
  outputs: number;
  input_changes: number;
  output_changes: number;
  alarm_changes: number;
  changes_description?: string;
}

export interface IOEvent extends ExtendedGPSEvent {
  input_delta: number;
  output_delta: number;
  alarm_delta: number;
  changes?: string;
}

export interface GSMEvent extends ExtendedGPSEvent {
  // source and text are already in parent
}

export interface ResetEvent extends ExtendedGPSEvent {
  reason: string;
}

// Network Models
export interface NetworkEvent {
  id: number;
  device: GPSDevice;
  event_type: string;
  timestamp: string;
  ip_address: string;
  port: number;
  protocol: string;
  session_id?: string;
  duration?: string;
  error_message?: string;
  raw_data?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface NetworkSession {
  id: number;
  device: GPSDevice;
  start_time: string;
  end_time?: string;
  ip_address: string;
  port: number;
  protocol: string;
  bytes_sent: number;
  bytes_received: number;
  packets_sent: number;
  packets_received: number;
  created_at: string;
  updated_at: string;
}

export interface NetworkMessage {
  id: number;
  session: NetworkSession;
  message_type: string;
  timestamp: string;
  direction: 'IN' | 'OUT';
  raw_data?: Record<string, any>;
  created_at: string;
}

// Protocol Models
export interface GPRSSession {
  id: number;
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
  created_at: string;
  updated_at: string;
}

export interface GPRSPacket {
  id: number;
  session: GPRSSession;
  request: string;
  response: string;
  timestamp: string;
}

export interface GPRSRecord {
  id: number;
  packet: GPRSPacket;
  id_byte: number;
  data: string;
  timestamp: string;
}

export interface UDPSession {
  session: number;
  device: GPSDevice;
  expires: string;
  host: string;
  port: number;
  last_record: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProtocolLog {
  id: number;
  device: GPSDevice;
  protocol: string;
  level: string;
  message: string;
  data?: Record<string, any>;
  timestamp: string;
}

// Sensor Models
export interface PressureSensorCalibration {
  id: number;
  device: GPSDevice;
  sensor: string;
  offset_psi1: number;
  offset_psi2: number;
  multiplier_psi1: number;
  multiplier_psi2: number;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface PressureWeightLog {
  id: number;
  device: GPSDevice;
  sensor: string;
  date: string;
  psi1: number;
  psi2: number;
  created_at: string;
}

export interface AlarmLog {
  id: number;
  device: GPSDevice;
  sensor: string;
  date: string;
  checksum: number;
  duration: number;
  comment: string;
  created_at: string;
}

// Geofence Models
export interface GeoFence {
  id: number;
  name: string;
  geometry: Point[];
  owner: User;
  description?: string;
  is_active: boolean;
  notify_on_entry: boolean;
  notify_on_exit: boolean;
  notify_owners: User[];
  base?: number;
  created_at: string;
  updated_at: string;
}

export interface GeoFenceEvent {
  id: number;
  fence: GeoFence;
  device: GPSDevice;
  event_type: 'ENTRY' | 'EXIT';
  position: Point;
  timestamp: string;
  created_at: string;
}

// Vehicle Models
export interface Vehicle {
  id: number;
  plate: string;
  make: string;
  model: string;
  year: number;
  color: string;
  vehicle_type: string;
  status: string;
  vin?: string;
  economico?: string;
  fuel_type: string;
  engine_size?: string;
  passenger_capacity?: number;
  cargo_capacity?: number;
  insurance_policy?: string;
  insurance_expiry?: string;
  registration_expiry?: string;
  device?: GPSDevice;
  driver?: Driver;
  mileage: number;
  last_service_date?: string;
  next_service_date?: string;
  created_at: string;
  updated_at: string;
}

// Driver Models
export interface Driver {
  id: number;
  name: string;
  middle_name: string;
  last_name: string;
  birth_date: string;
  civil_status: string;
  payroll: string;
  social_security: string;
  tax_id: string;
  license?: string;
  license_expiry?: string;
  address: string;
  phone: string;
  phone1?: string;
  phone2?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Asset Models
export interface CarPark {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface CarLane {
  id: number;
  prefix: string;
  slot_count: number;
  start: Point;
  end: Point;
  single: boolean;
  park: CarPark;
  created_at: string;
  updated_at: string;
}

export interface CarSlot {
  id: number;
  lane: CarLane;
  number: number;
  position: Point;
  car_serial?: string;
  car_date?: string;
  created_at: string;
  updated_at: string;
}

export interface GridlessCar {
  id: number;
  position: Point;
  car_serial?: string;
  car_date?: string;
  created_at: string;
}

export interface DemoCar {
  id: number;
  position: Point;
  car_serial?: string;
  car_date?: string;
  created_at: string;
}

// Ticket Models
export interface TicketLog {
  id: number;
  data: string;
  route?: number;
  date?: string;
  created_at: string;
}

export interface TicketDetail {
  id: number;
  device: GPSDevice;
  date?: string;
  driver_name: string;
  total: number;
  received: number;
  ticket_data: string;
  created_at: string;
}

export interface TimeSheetCapture {
  id: number;
  name: string;
  date?: string;
  driver_name: string;
  laps: number;
  times: string;
  created_at: string;
}

export interface CardTransaction {
  line_name: string;
  branch_name: string;
  line: number;
  economico: number;
  date: string;
  type: number;
  unit: string;
  card: number;
  amount: number;
}

// Acceleration Models
export interface AccelerationLog {
  id: number;
  device: GPSDevice;
  position: Point;
  date: string;
  duration: number;
  error_duration: number;
  entry: number;
  error_entry: number;
  peak: number;
  error_exit: number;
  exit: number;
}

// Overlay Models
export interface Overlay {
  id: number;
  name: string;
  geometry: Point[];
  owner: User;
  base?: number;
  created_at: string;
  updated_at: string;
}

// Address Cache
export interface AddressCache {
  id: number;
  position: Point;
  date: string;
  text: string;
}

// Device Stats
export interface DeviceStats {
  id: number;
  name: string;
  route: number;
  economico: number;
  date_start?: string;
  date_end: string;
  latitude?: number;
  longitude?: number;
  distance?: number;
  sub_del?: number;
  baj_del?: number;
  sub_tra?: number;
  baj_tra?: number;
  speed_avg?: number;
}

// Server SMS
export interface ServerSMS {
  id: number;
  device: GPSDevice;
  command: number;
  direction: number;
  status: number;
  message: string;
  sent?: string;
  issued: string;
}

// Enums
export enum DeviceModel {
  UNKNOWN = 0,
  SGB4612 = 1,
  SGP4612 = 2
}

export enum GSMOperator {
  TELCEL = 0,
  MOVISTAR = 1,
  IUSACELL = 2
}

export enum Route {
  RUTA_4 = 92,
  RUTA_6 = 112,
  RUTA_12 = 114,
  RUTA_31 = 115,
  RUTA_82 = 90,
  RUTA_118 = 88,
  RUTA_140 = 215,
  RUTA_202 = 89,
  RUTA_207 = 116,
  RUTA_400 = 96,
  RUTA_408 = 97
}

export enum ConnectionStatus {
  ONLINE = 'ONLINE',
  OFFLINE = 'OFFLINE',
  SLEEPING = 'SLEEPING',
  ERROR = 'ERROR'
}

export enum Protocol {
  CONCOX = 'concox',
  MEILIGAO = 'meiligao',
  WIALON = 'wialon'
}

export enum CivilStatus {
  SOLTERO = 'SOL',
  CASADO = 'CAS',
  VIUDO = 'VIU',
  DIVORCIADO = 'DIV'
}

export enum VehicleType {
  CAR = 'CAR',
  TRUCK = 'TRUCK',
  MOTORCYCLE = 'MOTORCYCLE',
  BUS = 'BUS',
  VAN = 'VAN',
  OTHER = 'OTHER'
}

export enum VehicleStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  MAINTENANCE = 'MAINTENANCE',
  REPAIR = 'REPAIR'
}

export enum FuelType {
  GASOLINE = 'GASOLINE',
  DIESEL = 'DIESEL',
  ELECTRIC = 'ELECTRIC',
  HYBRID = 'HYBRID',
  GAS = 'GAS'
}

export enum SMSCommand {
  SEND_SMS = 1,
  SEND_POSITION = 2,
  EXECUTE_COMMAND = 3
}

export enum SMSDirection {
  FROM_SERVER = 0,
  FROM_DEVICE = 1
}

export enum SMSStatus {
  PENDING = 0,
  SUCCESS = 1,
  FAILED = 2
}

export enum NetworkEventType {
  CONNECT = 'CONNECT',
  DISCONNECT = 'DISCONNECT',
  TIMEOUT = 'TIMEOUT',
  ERROR = 'ERROR',
  RECONNECT = 'RECONNECT',
  AUTH_FAIL = 'AUTH_FAIL',
  PROTOCOL_ERROR = 'PROTOCOL_ERROR'
}

export enum MessageType {
  COMMAND = 'COMMAND',
  RESPONSE = 'RESPONSE',
  ALERT = 'ALERT',
  DATA = 'DATA'
}

export enum ProtocolType {
  GPRS = 'GPRS',
  UDP = 'UDP',
  TCP = 'TCP',
  HTTP = 'HTTP',
  OTHER = 'OTHER'
}

export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
  CRITICAL = 'CRITICAL'
} 
/**
 * GPS interfaces for the tracking system.
 * Migrated from backend Django models to TypeScript.
 */

export interface GPSDevice {
  imei: string;
  name: string;
  position?: {
    latitude: number;
    longitude: number;
  };
  speed: number;
  course: number;
  altitude: number;
  lastLog?: Date;
  owner?: number;
  icon: string;
  odometer: number;
  createdAt: Date;
  updatedAt: Date;
  serial: number;
  model: number;
  softwareVersion: string;
  inputs: number;
  outputs: number;
  alarmMask: number;
  alarms: number;
  firmwareFile?: string;
  lastFirmwareUpdate?: Date;
  comments?: string;
  simCard?: SimCard;
  protocol: string;
  route?: number;
  economico?: number;
  harness?: DeviceHarness;
  newOutputs?: number;
  newInputFlags?: string;
  firstConnection?: Date;
  lastConnection?: Date;
  connectionStatus: string;
  currentIp?: string;
  currentPort?: number;
  totalConnections: number;
  firmwareHistory: any[];
  lastError?: string;
  errorCount: number;
  connectionQuality: number;
  lastHeartbeat?: Date;
  isActive: boolean;
}

export interface SimCard {
  iccid: string;
  imsi?: string;
  provider: number;
  phone: string;
}

export interface DeviceHarness {
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
  inputConfig?: string;
}

export interface NetworkEvent {
  id: number;
  device: number;
  eventType: string;
  timestamp: Date;
  ipAddress: string;
  port: number;
  protocol: string;
  sessionId?: string;
  duration?: number;
  errorMessage?: string;
  rawData?: any;
  createdAt: Date;
  updatedAt: Date;
}

export interface DeviceSession {
  id: number;
  device: number;
  startTime: Date;
  endTime?: Date;
  ipAddress: string;
  port: number;
  protocol: string;
  isActive: boolean;
  lastActivity: Date;
  bytesSent: number;
  bytesReceived: number;
  packetsSent: number;
  packetsReceived: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface GeoFence {
  id: number;
  name: string;
  geometry: any;
  owner: number;
  description?: string;
  isActive: boolean;
  notifyOnEntry: boolean;
  notifyOnExit: boolean;
  notifyOwners: number[];
  base?: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface GeoFenceEvent {
  id: number;
  fence: number;
  device: number;
  eventType: string;
  position: {
    latitude: number;
    longitude: number;
  };
  timestamp: Date;
  createdAt: Date;
}

export interface Vehicle {
  id: number;
  plate: string;
  make: string;
  model: string;
  year: number;
  color: string;
  vehicleType: string;
  status: string;
  vin?: string;
  economico?: string;
  fuelType: string;
  engineSize?: string;
  passengerCapacity?: number;
  cargoCapacity?: number;
  insurancePolicy?: string;
  insuranceExpiry?: Date;
  registrationExpiry?: Date;
  device?: number;
  driver?: number;
  mileage: number;
  lastServiceDate?: Date;
  nextServiceDate?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface Driver {
  id: number;
  name: string;
  middleName: string;
  lastName: string;
  birthDate: Date;
  civilStatus: string;
  payroll: string;
  socialSecurity: string;
  taxId: string;
  license?: string;
  licenseExpiry?: Date;
  address: string;
  phone: string;
  phone1?: string;
  phone2?: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Location {
  id: number;
  device: number;
  timestamp: Date;
  position: {
    latitude: number;
    longitude: number;
  };
  speed: number;
  course: number;
  altitude: number;
  satellites: number;
  accuracy: number;
  hdop: number;
  pdop: number;
  fixQuality: number;
  fixType: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface GPSEvent {
  id: number;
  device: number;
  type: string;
  position?: {
    latitude: number;
    longitude: number;
  };
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

export interface IOEvent extends GPSEvent {
  inputDelta: number;
  outputDelta: number;
  alarmDelta: number;
  changes: string;
}

export interface GSMEvent extends GPSEvent {
  // Inherits from GPSEvent
}

export interface ResetEvent extends GPSEvent {
  reason: string;
}

export interface AccelerationLog {
  id: number;
  device: number;
  position: {
    latitude: number;
    longitude: number;
  };
  date: Date;
  duration: number;
  errorDuration: number;
  entry: number;
  errorEntry: number;
  peak: number;
  errorExit: number;
  exit: number;
}

export interface Overlay {
  id: number;
  name: string;
  geometry: any;
  owner: number;
  base?: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface AddressCache {
  id: number;
  position: {
    latitude: number;
    longitude: number;
  };
  date: Date;
  text: string;
}

export interface CarPark {
  id: number;
  name: string;
  description?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface CarLane {
  id: number;
  prefix: string;
  slotCount: number;
  start: {
    latitude: number;
    longitude: number;
  };
  end: {
    latitude: number;
    longitude: number;
  };
  single: boolean;
  park: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface CarSlot {
  id: number;
  lane: number;
  number: number;
  position: {
    latitude: number;
    longitude: number;
  };
  carSerial?: string;
  carDate?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface GridlessCar {
  id: number;
  position: {
    latitude: number;
    longitude: number;
  };
  carSerial?: string;
  carDate?: Date;
  createdAt: Date;
}

export interface DemoCar {
  id: number;
  position: {
    latitude: number;
    longitude: number;
  };
  carSerial?: string;
  carDate?: Date;
  createdAt: Date;
}

export interface GPRSSession {
  id: number;
  start: Date;
  end: Date;
  ip: string;
  port: number;
  device: number;
  bytesTransferred: number;
  packetsCount: number;
  recordsCount: number;
  eventsCount: number;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface UDPSession {
  session: number;
  device: number;
  expires: Date;
  host: string;
  port: number;
  lastRecord: number;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface ProtocolLog {
  id: number;
  device: number;
  protocol: string;
  level: string;
  message: string;
  data?: any;
  timestamp: Date;
}

export interface PressureSensorCalibration {
  id: number;
  device: number;
  sensor: string;
  offsetPsi1: number;
  offsetPsi2: number;
  multiplierPsi1: number;
  multiplierPsi2: number;
  name: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface PressureWeightLog {
  id: number;
  device: number;
  sensor: string;
  date: Date;
  psi1: number;
  psi2: number;
  createdAt: Date;
}

export interface AlarmLog {
  id: number;
  device: number;
  sensor: string;
  date: Date;
  checksum: number;
  duration: number;
  comment: string;
  createdAt: Date;
}

export interface Tracking {
  id: number;
  tracking: string;
  device: number;
  stopFence: number;
  fences: number[];
  start: Date;
  stop?: Date;
  createdAt: Date;
}

export interface ServerSMS {
  id: number;
  device: number;
  command: number;
  direction: number;
  status: number;
  message: string;
  sent?: Date;
  issued: Date;
}

export interface DeviceStats {
  id: number;
  name: string;
  route: number;
  economico: number;
  dateStart?: Date;
  dateEnd: Date;
  latitude?: number;
  longitude?: number;
  distance?: number;
  subDel?: number;
  bajDel?: number;
  subTra?: number;
  bajTra?: number;
  speedAvg?: number;
}

export interface TicketLog {
  id: number;
  data: string;
  route?: number;
  date?: Date;
  createdAt: Date;
}

export interface TicketDetail {
  id: number;
  device: number;
  date?: Date;
  driverName: string;
  total: number;
  received: number;
  ticketData: string;
  createdAt: Date;
}

export interface TimeSheetCapture {
  id: number;
  name: string;
  date?: Date;
  driverName: string;
  laps: number;
  times: string;
  createdAt: Date;
}

export interface CardTransaction {
  lineName: string;
  branchName: string;
  line: number;
  economico: number;
  date: Date;
  type: number;
  unit: string;
  card: number;
  amount: number;
}

export interface NetworkSession {
  id: number;
  device: number;
  startTime: Date;
  endTime?: Date;
  ipAddress: string;
  port: number;
  protocol: string;
  bytesSent: number;
  bytesReceived: number;
  packetsSent: number;
  packetsReceived: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface NetworkMessage {
  id: number;
  session: number;
  messageType: string;
  timestamp: Date;
  direction: string;
  rawData?: any;
  createdAt: Date;
}

export interface CellTower {
  id: number;
  mcc: number;
  mnc: number;
  lac: number;
  cellId: string;
  signalStrength?: number;
  createdAt: Date;
}

export interface WiFiAccessPoint {
  id: number;
  macAddress: string;
  signalStrength: number;
  ssid?: string;
  createdAt: Date;
} 
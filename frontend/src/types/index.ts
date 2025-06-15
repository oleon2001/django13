import { ReactNode } from 'react';

export interface Device {
    id: number;
    imei: number;
    name: string;
    protocol: string;
    status: string;
    lastUpdate: string;
    lastSeen: string;
    latitude: number;
    longitude: number;
    speed: number;
    heading: number;
    altitude?: number;
    satellites?: number;
    hdop?: number;
    pdop?: number;
    fix_quality?: number;
    fix_type?: string;
    battery_level?: number;
    signal_strength?: number;
    raw_data?: any;
    
    // NEW: Migrated fields from backend
    connection_status?: 'ONLINE' | 'OFFLINE' | 'SLEEPING' | 'ERROR';
    route?: number;
    economico?: number;
    current_ip?: string;
    current_port?: number;
    total_connections?: number;
    error_count?: number;
    last_error?: string;
    harness?: DeviceHarness;
    sim_card?: SimCard;
}

// NEW: Device management types
export interface DeviceHarness {
    id: number;
    name: string;
    in00: string; // PANIC
    in01: string; // IGNITION
    out00: string; // MOTOR
    // ... other input/output configurations
}

export interface SimCard {
    iccid: number;
    phone: string;
    provider: number;
    provider_name: string;
}

export interface ServerSMS {
    id: number;
    device: number;
    command: number;
    direction: number;
    status: number;
    message: string;
    sent?: string;
    issued: string;
}

export interface DeviceStats {
    id: number;
    name: string;
    route: number;
    economico: number;
    date_start?: string;
    date_end: string;
    distance?: number;
    speed_avg?: number;
}

export interface DeviceEvent {
    id: number;
    device: number;
    type: 'TRACK' | 'ALARM' | 'STATUS' | 'MAINTENANCE';
    timestamp: string;
    position: {
        latitude: number;
        longitude: number;
    };
    speed: number;
    course: number;
    altitude: number;
    odometer: number;
    raw_data: any;
}

export interface DeviceData {
    id: number;
    device: number;
    event: number;
    timestamp: string;
    data_type: string;
    data: any;
    created_at: string;
    updated_at: string;
}

export interface NetworkEvent {
    id: number;
    device: number;
    event_type: 'CONNECT' | 'DISCONNECT' | 'TIMEOUT' | 'ERROR';
    timestamp: string;
    ip_address?: string;
    port?: number;
    protocol: string;
    raw_data?: any;
}

// NEW: Driver management types
export interface Driver {
    id: number;
    name: string;
    middle_name: string;
    last_name: string;
    full_name: string;
    birth_date: string;
    civil_status: 'SOL' | 'CAS' | 'VIU' | 'DIV';
    payroll: string;
    social_security: string;
    tax_id: string;
    license?: string;
    license_expiry?: string;
    is_license_valid: boolean;
    address: string;
    phone: string;
    phone1?: string;
    phone2?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface TicketLog {
    id: number;
    data: string;
    route?: number;
    date?: string;
    created_at: string;
}

export interface TicketDetail {
    id: number;
    device: number;
    date?: string;
    driver_name: string;
    total: number;
    received: number;
    ticket_data: string;
    created_at: string;
}

// NEW: Asset management types
export interface CarPark {
    id: number;
    name: string;
    description?: string;
    lanes: CarLane[];
    created_at: string;
    updated_at: string;
}

export interface CarLane {
    id: number;
    prefix: string;
    slot_count: number;
    start: [number, number]; // [lat, lng]
    end: [number, number];   // [lat, lng]
    single: boolean;
    park: number;
    slots: CarSlot[];
}

export interface CarSlot {
    id: number;
    lane: number;
    number: number;
    position: [number, number]; // [lat, lng]
    car_serial?: string;
    car_date?: string;
    is_occupied: boolean;
    display_name: string; // e.g., "A001"
}

// NEW: Sensor types
export interface PressureSensor {
    id: number;
    device: number;
    name: string;
    sensor: string;
    offset_psi1: number;
    offset_psi2: number;
    multiplier_psi1: number;
    multiplier_psi2: number;
    latest_reading?: PressureReading;
}

export interface PressureReading {
    id: number;
    device: number;
    sensor: string;
    date: string;
    psi1: number;
    psi2: number;
}

export interface AlarmLog {
    id: number;
    device: number;
    sensor: string;
    date: string;
    checksum: number;
    duration: number;
    comment: string;
}

// NEW: Protocol types
export interface GPRSSession {
    id: number;
    device: number;
    start: string;
    end?: string;
    ip: string;
    port: number;
    is_active: boolean;
    packets_count: number;
    records_count: number;
    bytes_transferred: number;
    events_count: number;
}

export interface UDPSession {
    session: number;
    device: number;
    expires: string;
    host: string;
    port: number;
    last_record: number;
    is_active: boolean;
    is_expired: boolean;
}

// NEW: Route management
export interface RouteChoice {
    value: number;
    label: string;
}

export const ROUTE_CHOICES: RouteChoice[] = [
    { value: 92, label: "Ruta 4" },
    { value: 112, label: "Ruta 6" },
    { value: 114, label: "Ruta 12" },
    { value: 115, label: "Ruta 31" },
    { value: 90, label: "Ruta 82" },
    { value: 88, label: "Ruta 118" },
    { value: 215, label: "Ruta 140" },
    { value: 89, label: "Ruta 202" },
    { value: 116, label: "Ruta 207" },
    { value: 96, label: "Ruta 400" },
    { value: 97, label: "Ruta 408" },
];

// Existing types (keeping compatibility)
export interface User {
    id: number;
    username: string;
    email: string;
    is_staff: boolean;
}

export interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    loading: boolean;
    error: string | null;
}

export interface DeviceState {
    devices: Device[];
    loading: boolean;
    error: string | null;
}

export interface Vehicle {
    id: number;
    name: string;
    plate: string;
    model: string;
    brand: string;
    year: number;
    status: 'active' | 'maintenance' | 'inactive';
    lastUpdate: string;
    device: Device;
}

export interface Alert {
    id: number;
    type: string;
    severity: 'low' | 'medium' | 'high';
    message: string;
    timestamp: string;
    device: Device;
    status: 'active' | 'resolved';
}

export interface Report {
    id: number;
    title: string;
    type: string;
    status: string;
    createdAt: string;
    updatedAt: string;
    data: Record<string, any>;
}

export interface Column<T> {
    header: string;
    accessor: keyof T | ((row: T) => ReactNode);
} 
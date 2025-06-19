import { ReactNode } from 'react';

// Dispositivo GPS
export interface Device {
    id?: number;
    name: string;
    serial?: string;
    model?: string;
    software_version?: string;
    imei: number;
    status?: string;
    protocol?: string;
    last_seen?: string;
    lastUpdate?: string;
    lastSeen?: string;
    position?: {
        latitude: number;
        longitude: number;
    };
    speed?: number;
    heading?: number;
    course?: number;
    altitude?: number;
    odometer?: number;
    satellites?: number;
    hdop?: number;
    pdop?: number;
    fix_quality?: number;
    fix_type?: string;
    battery_level?: number;
    signal_strength?: number;
    connection_status?: 'ONLINE' | 'OFFLINE' | 'SLEEPING' | 'ERROR';
    route?: number;
    economico?: number;
    current_ip?: string;
    current_port?: number;
    last_connection?: string;
    last_heartbeat?: string;
    total_connections?: number;
    error_count?: number;
    last_error?: string;
    created_at?: string;
    updated_at?: string;
    harness?: {
        id: number;
        name: string;
        in00: string;
        in01: string;
        out00: string;
    };
    sim_card?: {
        iccid: number;
        phone: string;
        provider: number;
        provider_name: string;
    };
}

// Vehículo
export interface Vehicle {
    id: number;
    name: string;
    plate: string;
    brand?: string;
    model?: string;
    year?: number;
    status?: string;
    lastUpdate?: string;
    device_id?: number;
    device?: Device; // Referencia al dispositivo GPS vinculado
    driver_id?: number;
    driver?: Driver; // Referencia al conductor asignado
}

// Conductor
export interface Driver {
    id: number;
    name: string;
    middle_name?: string;
    last_name?: string;
    full_name: string;
    is_active: boolean;
    is_license_valid: boolean;
    birth_date: string;
    civil_status: string;
    payroll: string;
    social_security: string;
    tax_id: string;
    license: string;
    address: string;
    phone: string;
    device_id?: number;
    device?: Device; // Referencia al dispositivo GPS vinculado
    vehicle_id?: number;
    vehicle?: Vehicle; // Referencia al vehículo asignado
}

// Evento de dispositivo
export interface DeviceEvent {
    id: number;
    device_id: number;
    timestamp: string;
    type: string;
    description?: string;
}

// Evento de red
export interface NetworkEvent {
    id: number;
    timestamp: string;
    eventType: string;
    details: string;
}

// Datos de dispositivo
export interface DeviceData {
    id: number;
    device_id: number;
    timestamp: string;
    latitude: number;
    longitude: number;
    speed: number;
}

// Estadísticas de dispositivo
export interface DeviceStats {
    total: number;
    online: number;
    offline: number;
}

// SMS del servidor
export interface ServerSMS {
    id: number;
    message: string;
    sent_at: string;
}

// Sesiones GPRS/UDP
export interface GPRSSession {
    id: number;
    device_id: number;
    started_at: string;
    ended_at?: string;
}

export interface UDPSession {
    id: number;
    device_id: number;
    started_at: string;
    ended_at?: string;
}

// Ticket de conductor
export interface TicketLog {
    id: number;
    driver_id: number;
    issued_at: string;
    reason: string;
}

export interface TicketDetail {
    id: number;
    ticket_id: number;
    description: string;
}

// Parqueo
export interface CarPark {
    id: number;
    name: string;
    location: string;
}

export interface CarLane {
    id: number;
    park_id: number;
    name: string;
    prefix: string;
    slot_count: number;
    single: boolean;
}

export interface CarSlot {
    id: number;
    lane_id: number;
    number: string;
    display_name: string;
    is_occupied: boolean;
    car_serial?: string;
}

// Sensores de presión
export interface PressureSensor {
    id: number;
    device_id: number;
    name: string;
    latest_reading?: {
        psi1: number;
        date: string;
    };
}

export interface PressureReading {
    id: number;
    sensor_id: number;
    value: number;
    timestamp: string;
}

export interface AlarmLog {
    id: number;
    device: number;
    comment?: string;
    date: string;
}

// Usuario
export interface User {
    id: number;
    username: string;
    email: string;
    is_active: boolean;
}

// Reporte
export interface Report {
    id: number;
    title: string;
    created_at: string;
}

// Columna para tablas
export interface Column<T> {
    id: string;
    label: string;
    minWidth?: number;
    align?: 'right' | 'left' | 'center';
    header: string;
    accessor: keyof T | ((item: T) => ReactNode);
}

// Configuración del servidor
export interface ServerSettings {
    id: number;
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
}

// Protocolo de comunicación
export interface Protocol {
    id: number;
    name: string;
    port: number;
    is_active: boolean;
    description: string;
}

// Opciones de rutas
export const ROUTE_CHOICES = [
    { value: 1, label: 'Ruta 1' },
    { value: 2, label: 'Ruta 2' },
    { value: 3, label: 'Ruta 3' },
    { value: 4, label: 'Ruta 4' },
    { value: 5, label: 'Ruta 5' },
]; 
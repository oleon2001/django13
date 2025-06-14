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
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
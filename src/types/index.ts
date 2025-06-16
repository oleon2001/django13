export interface Device {
    id: number;
    name: string;
    serial_number: string;
    status: string;
    last_seen?: string;
    latitude?: number;
    longitude?: number;
}

export interface CarLane {
    id: number;
    prefix: string;
    slot_count: number;
    single: boolean;
}

export interface CarSlot {
    id: number;
    display_name: string;
    is_occupied: boolean;
    car_serial?: string;
}

export interface PressureSensor {
    id: number;
    device: number;
    name: string;
    latest_reading?: {
        psi1: number;
        date: string;
    };
}

export interface AlarmLog {
    id: number;
    device: number;
    comment?: string;
    date: string;
}

export interface ExtendedPressureSensor {
    id: number;
    deviceId: number;
    name: string;
    currentPressure: number;
    lastUpdate: string;
}

export interface ExtendedAlarmLog {
    id: number;
    sensorId: number;
    message: string;
    timestamp: string;
}

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
}

export interface Column<T> {
    header: string;
    accessor: keyof T | ((item: T) => React.ReactNode);
} 
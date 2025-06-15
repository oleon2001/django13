import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface GPSDevice {
    id: number;
    imei: string;
    name: string;
    position: {
        latitude: number;
        longitude: number;
    };
    speed: number;
    course: number;
    altitude: number;
    last_seen: string;
    connection_status: string;
    battery: number;
    signal: number;
    satellites: number;
}

export interface GPSEvent {
    id: number;
    device_id: number;
    type: string;
    timestamp: string;
    position: {
        latitude: number;
        longitude: number;
    };
    speed: number;
    course: number;
    altitude: number;
}

class GPSService {
    private token: string;

    constructor() {
        this.token = localStorage.getItem('token') || '';
    }

    setToken(token: string) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    private getHeaders() {
        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }

    async getDevices(): Promise<GPSDevice[]> {
        const response = await axios.get(`${API_URL}/api/gps/devices/`, {
            headers: this.getHeaders()
        });
        return response.data;
    }

    async getDevice(imei: string): Promise<GPSDevice> {
        const response = await axios.get(`${API_URL}/api/gps/devices/${imei}/`, {
            headers: this.getHeaders()
        });
        return response.data;
    }

    async getDeviceEvents(imei: string, startDate?: string, endDate?: string): Promise<GPSEvent[]> {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);

        const response = await axios.get(`${API_URL}/api/gps/devices/${imei}/events/`, {
            headers: this.getHeaders(),
            params
        });
        return response.data;
    }

    async updateDeviceStatus(imei: string, status: string): Promise<void> {
        await axios.patch(`${API_URL}/api/gps/devices/${imei}/`, {
            connection_status: status
        }, {
            headers: this.getHeaders()
        });
    }

    async sendCommand(imei: string, command: string, params: any): Promise<void> {
        await axios.post(`${API_URL}/api/gps/devices/${imei}/command/`, {
            command,
            params
        }, {
            headers: this.getHeaders()
        });
    }
}

export const gpsService = new GPSService(); 
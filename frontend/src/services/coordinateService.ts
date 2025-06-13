import { Device } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

interface CoordinateResponse {
    id: number;
    latitude: number;
    longitude: number;
    timestamp: string;
    device_id: string;
}

export const coordinateService = {
    // Obtener datos de prueba del backend
    async generateTestData(deviceId: string = 'test_device', points: number = 10): Promise<Device[]> {
        const response = await fetch(`${API_BASE_URL}/coordinates/generate_test_data/?device_id=${deviceId}&points=${points}`);
        if (!response.ok) {
            throw new Error('Error generating test data');
        }
        const data: CoordinateResponse[] = await response.json();
        
        // Transformar los datos al formato Device
        return data.map((coord, index) => ({
            id: coord.id,
            imei: 123456789012345 + index,
            name: `Dispositivo ${coord.device_id}`,
            protocol: 'GT06',
            status: 'online',
            lastUpdate: coord.timestamp,
            lastSeen: coord.timestamp,
            latitude: coord.latitude,
            longitude: coord.longitude,
            speed: Math.floor(Math.random() * 100),
            heading: Math.floor(Math.random() * 360),
        }));
    },

    // Obtener la última coordenada
    async getLatestCoordinate(deviceId?: string): Promise<Device> {
        const url = deviceId 
            ? `${API_BASE_URL}/coordinates/get_latest/?device_id=${deviceId}`
            : `${API_BASE_URL}/coordinates/get_latest/`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Error getting latest coordinate');
        }
        const coord: CoordinateResponse = await response.json();
        
        return {
            id: coord.id,
            imei: 123456789012345,
            name: `Dispositivo ${coord.device_id}`,
            protocol: 'GT06',
            status: 'online',
            lastUpdate: coord.timestamp,
            lastSeen: coord.timestamp,
            latitude: coord.latitude,
            longitude: coord.longitude,
            speed: Math.floor(Math.random() * 100),
            heading: Math.floor(Math.random() * 360),
        };
    },

    // Obtener todas las coordenadas
    async getAllCoordinates(): Promise<Device[]> {
        const response = await fetch(`${API_BASE_URL}/coordinates/`);
        if (!response.ok) {
            throw new Error('Error getting coordinates');
        }
        const data: CoordinateResponse[] = await response.json();
        
        // Transformar los datos al formato Device
        return data.map((coord, index) => ({
            id: coord.id,
            imei: 123456789012345 + index,
            name: `Dispositivo ${coord.device_id}`,
            protocol: 'GT06',
            status: 'online',
            lastUpdate: coord.timestamp,
            lastSeen: coord.timestamp,
            latitude: coord.latitude,
            longitude: coord.longitude,
            speed: Math.floor(Math.random() * 100),
            heading: Math.floor(Math.random() * 360),
        }));
    }
}; 
import { Device } from '../../types/index';

const API_BASE_URL = 'http://localhost:8000/api';

interface CoordinateResponse {
    id: number;
    latitude: number;
    longitude: number;
    timestamp: string;
    device_id: string;
}

class CoordinateService {
    private static instance: CoordinateService;
    private updateInterval: NodeJS.Timeout | null = null;
    private subscribers: ((devices: Device[]) => void)[] = [];
    private currentDevices: Device[] = [];

    private constructor() {
        // Inicializar con datos de prueba
        this.generateTestData();
    }

    public static getInstance(): CoordinateService {
        if (!CoordinateService.instance) {
            CoordinateService.instance = new CoordinateService();
        }
        return CoordinateService.instance;
    }

    // Suscribirse a actualizaciones de coordenadas
    public subscribe(callback: (devices: Device[]) => void): () => void {
        this.subscribers.push(callback);
        // Enviar datos actuales inmediatamente
        callback(this.currentDevices);
        
        // Retornar función para desuscribirse
        return () => {
            this.subscribers = this.subscribers.filter(cb => cb !== callback);
        };
    }

    // Notificar a todos los suscriptores
    private notifySubscribers() {
        this.subscribers.forEach(callback => callback(this.currentDevices));
    }

    // Iniciar actualizaciones automáticas
    public startAutoUpdate(interval: number = 5000) {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        this.updateInterval = setInterval(() => {
            this.generateTestData();
        }, interval);
    }

    // Detener actualizaciones automáticas
    public stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    // Generar datos de prueba
    public async generateTestData(deviceId: string = 'test_device', points: number = 10): Promise<Device[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/coordinates/generate_test_data/?device_id=${deviceId}&points=${points}`);
            if (!response.ok) {
                throw new Error('Error generating test data');
            }
            const data: CoordinateResponse[] = await response.json();
            
            // Transformar los datos al formato Device
            this.currentDevices = data.map((coord, index) => ({
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
                altitude: Math.floor(Math.random() * 1000),
                satellites: Math.floor(Math.random() * 12),
                hdop: Math.random() * 2,
                pdop: Math.random() * 3,
                fix_quality: Math.floor(Math.random() * 5),
                fix_type: '3D',
                battery_level: Math.floor(Math.random() * 100),
                signal_strength: Math.floor(Math.random() * 100)
            }));

            // Notificar a los suscriptores
            this.notifySubscribers();
            return this.currentDevices;
        } catch (error) {
            console.error('Error generating test data:', error);
            return [];
        }
    }

    // Obtener la última coordenada
    public async getLatestCoordinate(deviceId?: string): Promise<Device | null> {
        try {
            const url = deviceId 
                ? `${API_BASE_URL}/coordinates/get_latest/?device_id=${deviceId}`
                : `${API_BASE_URL}/coordinates/get_latest/`;
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Error getting latest coordinate');
            }
            const coord: CoordinateResponse = await response.json();
            
            const device: Device = {
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
                altitude: Math.floor(Math.random() * 1000),
                satellites: Math.floor(Math.random() * 12),
                hdop: Math.random() * 2,
                pdop: Math.random() * 3,
                fix_quality: Math.floor(Math.random() * 5),
                fix_type: '3D',
                battery_level: Math.floor(Math.random() * 100),
                signal_strength: Math.floor(Math.random() * 100)
            };

            // Actualizar el dispositivo en la lista actual
            const index = this.currentDevices.findIndex(d => d.id === device.id);
            if (index !== -1) {
                this.currentDevices[index] = device;
            } else {
                this.currentDevices.push(device);
            }

            // Notificar a los suscriptores
            this.notifySubscribers();
            return device;
        } catch (error) {
            console.error('Error getting latest coordinate:', error);
            return null;
        }
    }

    // Obtener todos los dispositivos actuales
    public getCurrentDevices(): Device[] {
        return this.currentDevices;
    }
}

// Exportar una instancia única del servicio
export const coordinateService = CoordinateService.getInstance(); 
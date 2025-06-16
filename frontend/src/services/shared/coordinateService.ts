import { Device } from '../../types';

const API_BASE_URL = 'http://localhost:8000/api';

class CoordinateService {
    private subscribers: ((devices: Device[]) => void)[] = [];
    private currentDevices: Device[] = [];
    private updateInterval: NodeJS.Timeout | null = null;

    constructor() {
        this.startUpdates();
    }

    private async fetchCoordinates(): Promise<Device[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/coordinates/`);
            const data = await response.json();
            
            // Transformar los datos al formato Device
            this.currentDevices = data.map((coord: any, index: number) => ({
                id: coord.id,
                imei: 123456789012345 + index,
                name: `Dispositivo ${coord.device_id}`,
                protocol: 'GT06',
                status: 'online',
                lastUpdate: new Date().toISOString(),
                lastSeen: new Date().toISOString(),
                latitude: coord.latitude,
                longitude: coord.longitude,
                speed: coord.speed || 0,
                heading: coord.heading || 0,
                altitude: coord.altitude || 0,
                satellites: coord.satellites || 0,
                hdop: coord.hdop || 0,
                pdop: coord.pdop || 0,
                fix_quality: coord.fix_quality || 0,
                fix_type: coord.fix_type || 'none',
                battery_level: coord.battery_level || 100,
                signal_strength: coord.signal_strength || 5,
                connection_status: 'ONLINE',
                route: coord.route || 1,
                economico: coord.economico || 1,
                current_ip: coord.current_ip || '192.168.1.1',
                current_port: coord.current_port || 8080,
                total_connections: coord.total_connections || 1,
                error_count: coord.error_count || 0,
                last_error: coord.last_error || undefined,
                harness: {
                    id: 1,
                    name: 'Default Harness',
                    in00: 'PANIC',
                    in01: 'IGNITION',
                    out00: 'MOTOR'
                },
                sim_card: {
                    iccid: 12345678901234567890,
                    phone: '+1234567890',
                    provider: 1,
                    provider_name: 'Test Provider'
                }
            }));
            return this.currentDevices;
        } catch (error) {
            console.error('Error fetching coordinates:', error);
            return this.currentDevices;
        }
    }

    private startUpdates() {
        // Actualizar cada 5 segundos
        this.updateInterval = setInterval(async () => {
            const devices = await this.fetchCoordinates();
            this.notifySubscribers(devices);
        }, 5000);
    }

    private notifySubscribers(devices: Device[]) {
        this.subscribers.forEach(callback => callback(devices));
    }

    public subscribe(callback: (devices: Device[]) => void): () => void {
        this.subscribers.push(callback);
        // Notificar inmediatamente con los datos actuales
        callback(this.currentDevices);
        return () => {
            this.subscribers = this.subscribers.filter(cb => cb !== callback);
        };
    }

    public async getLatestCoordinates(): Promise<Device[]> {
        return this.fetchCoordinates();
    }

    public stopUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    // Obtener todos los dispositivos actuales
    public getCurrentDevices(): Device[] {
        return this.currentDevices;
    }
}

// Exportar una instancia única del servicio
export const coordinateService = new CoordinateService(); 
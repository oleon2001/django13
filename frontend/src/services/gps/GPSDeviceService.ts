import { Device } from '../../types/index';

export interface GPSDeviceConfig {
    host: string;
    port: number;
    deviceId: string;
}

export class GPSDeviceService {
    private device: Device | null = null;
    private subscribers: ((device: Device) => void)[] = [];
    private config: GPSDeviceConfig | null = null;

    constructor() {
        // Inicialización del servicio
    }

    public async connect(config: GPSDeviceConfig): Promise<boolean> {
        try {
            this.config = config;
            // Aquí implementaremos la lógica de conexión usando el config
            console.log(`Conectando a dispositivo GPS en ${config.host}:${config.port}`);
            return true;
        } catch (error) {
            console.error('Error al conectar:', error);
            return false;
        }
    }

    public disconnect(): void {
        if (this.config) {
            console.log(`Desconectando de dispositivo GPS en ${this.config.host}:${this.config.port}`);
            this.config = null;
        }
        this.device = null;
    }

    public subscribe(callback: (device: Device) => void): () => void {
        this.subscribers.push(callback);
        if (this.device) {
            callback(this.device);
        }
        return () => {
            this.subscribers = this.subscribers.filter(cb => cb !== callback);
        };
    }

    private notifySubscribers(device: Device): void {
        this.subscribers.forEach(callback => callback(device));
    }

    public updateDevice(device: Device): void {
        this.device = device;
        this.notifySubscribers(device);
    }

    public getConfig(): GPSDeviceConfig | null {
        return this.config;
    }
}

export const gpsDeviceService = new GPSDeviceService(); 
import { Device } from '../../types';

export interface GPSConfig {
    host: string;
    port: number;
    protocol: 'TCP' | 'UDP';
    deviceId: string;
}

class GPSConnectionService {
    private socket: WebSocket | null = null;
    private subscribers: ((device: Device) => void)[] = [];
    private currentDevice: Device | null = null;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;
    private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;

    public async connect(config: GPSConfig): Promise<boolean> {
        try {
            const wsUrl = `ws://${config.host}:${config.port}`;
            this.socket = new WebSocket(wsUrl);

            this.socket.onopen = () => {
                this.reconnectAttempts = 0;
                this.sendInitialConfig(config);
            };

            this.socket.onmessage = (event) => {
                this.handleMessage(event.data);
            };

            this.socket.onclose = () => {
                this.handleDisconnect(config);
            };

            this.socket.onerror = () => {
                this.handleError();
            };

            return true;
        } catch (error) {
            return false;
        }
    }

    private sendInitialConfig(config: GPSConfig) {
        if (this.socket?.readyState === WebSocket.OPEN) {
            const message = {
                type: 'config',
                data: {
                    deviceId: config.deviceId,
                    protocol: config.protocol
                }
            };
            this.socket.send(JSON.stringify(message));
        }
    }

    private handleMessage(data: string) {
        try {
            const message = JSON.parse(data);
            switch (message.type) {
                case 'position':
                    this.updateDevicePosition(message.data);
                    break;
                case 'status':
                    this.updateDeviceStatus(message.data);
                    break;
                case 'error':
                    break;
                default:
            }
        } catch (error) {}
    }

    private updateDevicePosition(data: any) {
        const device: Device = {
            id: data.deviceId,
            imei: data.imei,
            name: `GPS ${data.deviceId}`,
            serial: `SN${data.deviceId}`,
            protocol: 'GT06',
            connection_status: 'ONLINE',
            last_heartbeat: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            position: {
                latitude: data.latitude,
                longitude: data.longitude
            },
            speed: data.speed,
            course: data.heading,
            altitude: data.altitude,
            satellites: data.satellites,
            hdop: data.hdop,
            pdop: data.pdop,
            fix_quality: data.fixQuality,
            fix_type: data.fixType,
            battery_level: data.batteryLevel,
            signal_strength: data.signalStrength,
            route: data.route,
            economico: data.economico,
            current_ip: data.ip,
            current_port: data.port,
            total_connections: data.totalConnections,
            error_count: data.errorCount,
            last_error: data.lastError,
            harness: {
                id: 1,
                name: 'Default Harness',
                in00: 'PANIC',
                in01: 'IGNITION',
                out00: 'MOTOR'
            },
            sim_card: {
                iccid: data.iccid,
                phone: data.phone,
                provider: data.provider,
                provider_name: data.providerName
            }
        };
        this.currentDevice = device;
        this.notifySubscribers(device);
    }

    private updateDeviceStatus(data: any) {
        if (this.currentDevice) {
            this.currentDevice = {
                ...this.currentDevice,
                connection_status: data.status,
                battery_level: data.battery_level,
                signal_strength: data.signal_strength,
                updated_at: new Date().toISOString()
            };
            this.notifySubscribers(this.currentDevice);
        }
    }

    private handleDisconnect(config: GPSConfig) {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            if (this.reconnectTimeout) {
                clearTimeout(this.reconnectTimeout);
            }
            this.reconnectTimeout = setTimeout(() => {
                this.connect(config);
            }, 5000);
        }
    }

    private handleError() {
        if (this.socket) {
            this.socket.close();
        }
    }

    public disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }
        this.currentDevice = null;
    }

    public sendCommand(command: string): boolean {
        if (this.socket?.readyState === WebSocket.OPEN) {
            const message = {
                type: 'command',
                data: {
                    command
                }
            };
            this.socket.send(JSON.stringify(message));
            return true;
        }
        return false;
    }

    public subscribe(callback: (device: Device) => void): () => void {
        this.subscribers.push(callback);
        if (this.currentDevice) {
            callback(this.currentDevice);
        }
        return () => {
            this.subscribers = this.subscribers.filter(cb => cb !== callback);
        };
    }

    private notifySubscribers(device: Device) {
        this.subscribers.forEach(callback => callback(device));
    }
}

export const gpsConnectionService = new GPSConnectionService(); 
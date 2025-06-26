/**
 * Enterprise WebSocket Service for Real-time GPS Communication
 * Provides robust, scalable WebSocket connectivity with automatic reconnection,
 * authentication, and message queuing.
 */

import authService from './auth';

export interface GPSUpdate {
    type: 'gps_update';
    device_imei: string;
    position: {
        latitude: number;
        longitude: number;
    };
    speed: number;
    course: number;
    timestamp: string;
    status: string;
    altitude?: number;
    satellites?: number;
    accuracy?: number;
}

export interface DeviceStatusChange {
    type: 'status_change';
    device_imei: string;
    status: string;
    timestamp: string;
    last_heartbeat?: string;
    connection_quality?: number;
    error_count?: number;
}

export interface AlarmNotification {
    type: 'alarm';
    device_imei: string;
    alarm_type: string;
    message: string;
    position?: {
        latitude: number;
        longitude: number;
    };
    timestamp: string;
    severity: 'low' | 'medium' | 'high';
    device_name?: string;
}

export interface DeviceListMessage {
    type: 'device_list';
    devices: Array<{
        imei: string;
        name: string;
        status: string;
        last_update?: string;
        position?: {
            latitude: number;
            longitude: number;
        };
        speed: number;
        course: number;
    }>;
}

export type WebSocketMessage = GPSUpdate | DeviceStatusChange | AlarmNotification | DeviceListMessage | {
    type: 'success' | 'error';
    message: string;
};

export type WebSocketMessageHandler = (message: WebSocketMessage) => void;

interface WebSocketServiceConfig {
    autoReconnect?: boolean;
    reconnectInterval?: number;
    maxReconnectAttempts?: number;
    heartbeatInterval?: number;
    messageQueueSize?: number;
}

class WebSocketService {
    private ws: WebSocket | null = null;
    private url: string;
    private token: string | null = null;
    private messageHandlers: Set<WebSocketMessageHandler> = new Set();
    private isConnecting = false;
    private isConnected = false;
    private reconnectAttempts = 0;
    private messageQueue: Array<any> = [];
    private heartbeatTimer: NodeJS.Timeout | null = null;
    private reconnectTimer: NodeJS.Timeout | null = null;
    
    // Configuration
    private config: Required<WebSocketServiceConfig> = {
        autoReconnect: true,
        reconnectInterval: 5000,
        maxReconnectAttempts: 10,
        heartbeatInterval: 30000,
        messageQueueSize: 100
    };

    constructor(config?: WebSocketServiceConfig) {
        this.config = { ...this.config, ...config };
        this.url = this.buildWebSocketUrl();
    }

    private buildWebSocketUrl(): string {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = process.env.REACT_APP_WS_HOST || window.location.host;
        return `${protocol}//${host}/ws/gps/realtime/`;
    }

    /**
     * Connect to WebSocket server
     */
    public async connect(): Promise<void> {
        if (this.isConnecting || this.isConnected) {
            return;
        }

        this.token = authService.getToken();
        if (!this.token) {
            throw new Error('No authentication token available');
        }

        this.isConnecting = true;

        try {
            const wsUrl = `${this.url}?token=${this.token}`;
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = this.handleOpen.bind(this);
            this.ws.onmessage = this.handleMessage.bind(this);
            this.ws.onclose = this.handleClose.bind(this);
            this.ws.onerror = this.handleError.bind(this);

            // Wait for connection to establish
            await new Promise<void>((resolve, reject) => {
                const timeout = setTimeout(() => {
                    reject(new Error('WebSocket connection timeout'));
                }, 10000);

                const originalOnOpen = this.ws!.onopen;
                this.ws!.onopen = (event) => {
                    clearTimeout(timeout);
                    originalOnOpen && originalOnOpen.call(this.ws!, event);
                    resolve();
                };

                const originalOnError = this.ws!.onerror;
                this.ws!.onerror = (event) => {
                    clearTimeout(timeout);
                    originalOnError && originalOnError.call(this.ws!, event);
                    reject(new Error('WebSocket connection failed'));
                };
            });

        } catch (error) {
            this.isConnecting = false;
            throw error;
        }
    }

    /**
     * Disconnect from WebSocket server
     */
    public disconnect(): void {
        this.config.autoReconnect = false;
        
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }

        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }

        if (this.ws) {
            this.ws.close(1000, 'Client disconnect');
            this.ws = null;
        }

        this.isConnected = false;
        this.isConnecting = false;
        this.reconnectAttempts = 0;
    }

    /**
     * Subscribe to device updates
     */
    public subscribeToDevice(deviceImei: string): void {
        this.sendMessage({
            type: 'subscribe_device',
            device_imei: deviceImei
        });
    }

    /**
     * Unsubscribe from device updates
     */
    public unsubscribeFromDevice(deviceImei: string): void {
        this.sendMessage({
            type: 'unsubscribe_device',
            device_imei: deviceImei
        });
    }

    /**
     * Send command to device
     */
    public sendDeviceCommand(deviceImei: string, command: string): void {
        this.sendMessage({
            type: 'send_command',
            device_imei: deviceImei,
            command: command
        });
    }

    /**
     * Request current device list
     */
    public requestDeviceList(): void {
        this.sendMessage({
            type: 'request_device_list'
        });
    }

    /**
     * Add message handler
     */
    public addMessageHandler(handler: WebSocketMessageHandler): () => void {
        this.messageHandlers.add(handler);
        
        // Return unsubscribe function
        return () => {
            this.messageHandlers.delete(handler);
        };
    }

    /**
     * Get connection status
     */
    public getConnectionStatus(): {
        isConnected: boolean;
        isConnecting: boolean;
        reconnectAttempts: number;
    } {
        return {
            isConnected: this.isConnected,
            isConnecting: this.isConnecting,
            reconnectAttempts: this.reconnectAttempts
        };
    }

    // Private methods
    private handleOpen(_event: Event): void {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.isConnecting = false;
        this.reconnectAttempts = 0;

        // Process queued messages
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.sendMessage(message);
        }

        // Start heartbeat
        this.startHeartbeat();

        // Request initial device list
        this.requestDeviceList();
    }

    private handleMessage(event: MessageEvent): void {
        try {
            const message: WebSocketMessage = JSON.parse(event.data);
            
            // Notify all handlers
            this.messageHandlers.forEach(handler => {
                try {
                    handler(message);
                } catch (error) {
                    console.error('Error in message handler:', error);
                }
            });

        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }

    private handleClose(event: CloseEvent): void {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.isConnected = false;
        this.isConnecting = false;

        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }

        // Auto-reconnect if enabled
        if (this.config.autoReconnect && this.reconnectAttempts < this.config.maxReconnectAttempts) {
            this.scheduleReconnect();
        }
    }

    private handleError(event: Event): void {
        console.error('WebSocket error:', event);
        this.isConnecting = false;
    }

    private sendMessage(message: any): void {
        if (this.isConnected && this.ws) {
            this.ws.send(JSON.stringify(message));
        } else {
            // Queue message for later
            if (this.messageQueue.length < this.config.messageQueueSize) {
                this.messageQueue.push(message);
            } else {
                console.warn('Message queue full, dropping message');
            }
        }
    }

    private startHeartbeat(): void {
        this.heartbeatTimer = setInterval(() => {
            if (this.isConnected) {
                this.sendMessage({ type: 'ping' });
            }
        }, this.config.heartbeatInterval);
    }

    private scheduleReconnect(): void {
        this.reconnectAttempts++;
        const delay = Math.min(this.config.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1), 30000);
        
        console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
        
        this.reconnectTimer = setTimeout(() => {
            this.connect().catch(error => {
                console.error('Reconnection failed:', error);
            });
        }, delay);
    }
}

// Export singleton instance
export const webSocketService = new WebSocketService();
export default webSocketService; 
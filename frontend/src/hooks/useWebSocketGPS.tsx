/**
 * Professional WebSocket GPS Hook
 * Replaces polling-based real-time updates with efficient WebSocket communication
 */

import { useState, useEffect, useCallback, useRef } from 'react';

import webSocketService, { 
    WebSocketMessage, 
    GPSUpdate, 
    DeviceStatusChange, 
    AlarmNotification,
    DeviceListMessage 
} from '../services/websocket';
import { Device } from '../types';

interface UseWebSocketGPSOptions {
    autoConnect?: boolean;
    subscribedDevices?: string[];
    onAlarm?: (alarm: AlarmNotification) => void;
    onDeviceUpdate?: (update: GPSUpdate) => void;
    onDeviceStatusChange?: (statusChange: DeviceStatusChange) => void;
    onError?: (error: Error) => void;
}

interface UseWebSocketGPSReturn {
    devices: Device[];
    isConnected: boolean;
    isConnecting: boolean;
    connectionStatus: {
        isConnected: boolean;
        isConnecting: boolean;
        reconnectAttempts: number;
    };
    lastUpdate: Date | null;
    error: string | null;
    // Methods
    connect: () => Promise<void>;
    disconnect: () => void;
    subscribeToDevice: (deviceImei: string) => void;
    unsubscribeFromDevice: (deviceImei: string) => void;
    sendDeviceCommand: (deviceImei: string, command: string) => void;
    refreshDeviceList: () => void;
    clearError: () => void;
}

export const useWebSocketGPS = (options: UseWebSocketGPSOptions = {}): UseWebSocketGPSReturn => {
    // State
    const [devices, setDevices] = useState<Device[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const [isConnecting, setIsConnecting] = useState(false);
    const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [connectionStatus, setConnectionStatus] = useState({
        isConnected: false,
        isConnecting: false,
        reconnectAttempts: 0
    });

    // Refs
    const devicesRef = useRef<Map<string, Device>>(new Map());
    const unsubscribeRef = useRef<(() => void) | null>(null);
    const statusCheckInterval = useRef<NodeJS.Timeout | null>(null);

    // Options
    const {
        autoConnect = true,
        subscribedDevices = [],
        onAlarm,
        onDeviceUpdate,
        onDeviceStatusChange,
        onError
    } = options;

    // Convert devices map to array
    const updateDevicesArray = useCallback(() => {
        const devicesArray = Array.from(devicesRef.current.values());
        setDevices(devicesArray);
        setLastUpdate(new Date());
    }, []);

    // WebSocket message handler
    const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
        try {
            switch (message.type) {
                case 'device_list':
                    handleDeviceList(message as DeviceListMessage);
                    break;
                
                case 'gps_update':
                    handleGPSUpdate(message as GPSUpdate);
                    break;
                
                case 'status_change':
                    handleDeviceStatusChange(message as DeviceStatusChange);
                    break;
                
                case 'alarm':
                    handleAlarmNotification(message as AlarmNotification);
                    break;
                
                case 'success':
                    console.log('WebSocket success:', message.message);
                    setError(null);
                    break;
                
                case 'error':
                    console.error('WebSocket error:', message.message);
                    setError(message.message);
                    onError?.(new Error(message.message));
                    break;
                
                default:
                    console.log('Unknown message type:', message);
            }
        } catch (error) {
            console.error('Error handling WebSocket message:', error);
            setError(error instanceof Error ? error.message : 'Unknown error');
        }
    }, [onAlarm, onDeviceUpdate, onDeviceStatusChange, onError]);

    // Handle device list
    const handleDeviceList = useCallback((message: DeviceListMessage) => {
        devicesRef.current.clear();
        
        message.devices.forEach(deviceData => {
            const device: Device = {
                id: parseInt(deviceData.imei),
                imei: parseInt(deviceData.imei),
                name: deviceData.name,
                connection_status: deviceData.status as any,
                last_heartbeat: deviceData.last_update || '',
                updated_at: deviceData.last_update || '',
                position: deviceData.position,
                speed: deviceData.speed || 0,
                course: deviceData.course || 0,
                // Add other fields with defaults
                serial: `SN${deviceData.imei}`,
                protocol: 'auto',
                battery_level: 0,
                signal_strength: 0,
                altitude: 0,
                odometer: 0
            };
            
            devicesRef.current.set(deviceData.imei, device);
        });
        
        updateDevicesArray();
    }, [updateDevicesArray]);

    // Handle GPS update
    const handleGPSUpdate = useCallback((update: GPSUpdate) => {
        const device = devicesRef.current.get(update.device_imei);
        if (device) {
            const updatedDevice: Device = {
                ...device,
                position: update.position,
                speed: update.speed,
                course: update.course,
                updated_at: update.timestamp,
                connection_status: update.status as any,
                altitude: update.altitude || device.altitude,
                // Update satellite and accuracy if available
                ...(update.satellites && { satellites: update.satellites }),
                ...(update.accuracy && { accuracy: update.accuracy })
            };
            
            devicesRef.current.set(update.device_imei, updatedDevice);
            updateDevicesArray();
            
            // Call callback
            onDeviceUpdate?.(update);
        }
    }, [updateDevicesArray, onDeviceUpdate]);

    // Handle device status change
    const handleDeviceStatusChange = useCallback((statusChange: DeviceStatusChange) => {
        const device = devicesRef.current.get(statusChange.device_imei);
        if (device) {
            const updatedDevice: Device = {
                ...device,
                connection_status: statusChange.status as any,
                last_heartbeat: statusChange.last_heartbeat || device.last_heartbeat,
                updated_at: statusChange.timestamp,
                // Update other status fields if available
                ...(statusChange.connection_quality && { connection_quality: statusChange.connection_quality }),
                ...(statusChange.error_count && { error_count: statusChange.error_count })
            };
            
            devicesRef.current.set(statusChange.device_imei, updatedDevice);
            updateDevicesArray();
            
            // Call callback
            onDeviceStatusChange?.(statusChange);
        }
    }, [updateDevicesArray, onDeviceStatusChange]);

    // Handle alarm notification
    const handleAlarmNotification = useCallback((alarm: AlarmNotification) => {
        console.warn('GPS Alarm received:', alarm);
        
        // Update device position if provided
        if (alarm.position) {
            const device = devicesRef.current.get(alarm.device_imei);
            if (device) {
                const updatedDevice: Device = {
                    ...device,
                    position: alarm.position,
                    updated_at: alarm.timestamp
                };
                
                devicesRef.current.set(alarm.device_imei, updatedDevice);
                updateDevicesArray();
            }
        }
        
        // Call callback
        onAlarm?.(alarm);
    }, [updateDevicesArray, onAlarm]);

    // Connect to WebSocket
    const connect = useCallback(async () => {
        try {
            setIsConnecting(true);
            setError(null);
            
            await webSocketService.connect();
            
            // Subscribe to message events
            if (unsubscribeRef.current) {
                unsubscribeRef.current();
            }
            unsubscribeRef.current = webSocketService.addMessageHandler(handleWebSocketMessage);
            
            // Subscribe to specific devices if provided
            subscribedDevices.forEach(deviceImei => {
                webSocketService.subscribeToDevice(deviceImei);
            });
            
            setIsConnected(true);
            setIsConnecting(false);
            
        } catch (error) {
            setIsConnecting(false);
            const errorMessage = error instanceof Error ? error.message : 'Failed to connect';
            setError(errorMessage);
            onError?.(error instanceof Error ? error : new Error(errorMessage));
        }
    }, [handleWebSocketMessage, subscribedDevices, onError]);

    // Disconnect from WebSocket
    const disconnect = useCallback(() => {
        if (unsubscribeRef.current) {
            unsubscribeRef.current();
            unsubscribeRef.current = null;
        }
        
        if (statusCheckInterval.current) {
            clearInterval(statusCheckInterval.current);
            statusCheckInterval.current = null;
        }
        
        webSocketService.disconnect();
        setIsConnected(false);
        setIsConnecting(false);
    }, []);

    // Subscribe to device
    const subscribeToDevice = useCallback((deviceImei: string) => {
        webSocketService.subscribeToDevice(deviceImei);
    }, []);

    // Unsubscribe from device
    const unsubscribeFromDevice = useCallback((deviceImei: string) => {
        webSocketService.unsubscribeFromDevice(deviceImei);
    }, []);

    // Send device command
    const sendDeviceCommand = useCallback((deviceImei: string, command: string) => {
        webSocketService.sendDeviceCommand(deviceImei, command);
    }, []);

    // Refresh device list
    const refreshDeviceList = useCallback(() => {
        webSocketService.requestDeviceList();
    }, []);

    // Clear error
    const clearError = useCallback(() => {
        setError(null);
    }, []);

    // Update connection status periodically
    useEffect(() => {
        statusCheckInterval.current = setInterval(() => {
            const status = webSocketService.getConnectionStatus();
            setConnectionStatus(status);
            setIsConnected(status.isConnected);
            setIsConnecting(status.isConnecting);
        }, 1000);

        return () => {
            if (statusCheckInterval.current) {
                clearInterval(statusCheckInterval.current);
            }
        };
    }, []);

    // Auto-connect effect
    useEffect(() => {
        if (autoConnect) {
            connect();
        }

        return () => {
            disconnect();
        };
    }, [autoConnect]); // Only depend on autoConnect to avoid reconnecting unnecessarily

    return {
        devices,
        isConnected,
        isConnecting,
        connectionStatus,
        lastUpdate,
        error,
        // Methods
        connect,
        disconnect,
        subscribeToDevice,
        unsubscribeFromDevice,
        sendDeviceCommand,
        refreshDeviceList,
        clearError
    };
}; 
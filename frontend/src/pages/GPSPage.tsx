import React, { useState, useEffect, useRef } from 'react';
import { Device } from '../types';
import DeviceList from '../components/DeviceList';
import DeviceMap from '../components/DeviceMap';
import { deviceService } from '../services/deviceService';

const GPSPage: React.FC = () => {
    const [devices, setDevices] = useState<Device[]>([]);
    const [realTimePositions, setRealTimePositions] = useState<any[]>([]);
    const [selectedDevice, setSelectedDevice] = useState<Device | undefined>(undefined);
    const [isRealTimeEnabled, setIsRealTimeEnabled] = useState(true);
    const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
    const stopPollingRef = useRef<(() => void) | null>(null);

    // Fetch initial devices
    useEffect(() => {
        const fetchDevices = async () => {
            try {
                const data = await deviceService.getAll();
                setDevices(data);
            } catch (error) {
                console.error('Error fetching devices:', error);
            }
        };
        fetchDevices();
    }, []);

    // Start/stop real-time polling
    useEffect(() => {
        if (isRealTimeEnabled) {
            stopPollingRef.current = deviceService.startRealTimePolling(
                (positions) => {
                    setRealTimePositions(positions);
                    setLastUpdate(new Date());
                    
                    // Update devices with real-time positions
                    setDevices(prevDevices => 
                        prevDevices.map(device => {
                            const realtimePos = positions.find(pos => pos.imei === device.imei);
                            if (realtimePos) {
                                return {
                                    ...device,
                                    latitude: realtimePos.position.latitude,
                                    longitude: realtimePos.position.longitude,
                                    speed: realtimePos.speed,
                                    course: realtimePos.course,
                                    altitude: realtimePos.altitude,
                                    connection_status: realtimePos.connection_status,
                                    lastUpdate: realtimePos.last_update,
                                };
                            }
                            return device;
                        })
                    );
                },
                3000 // Poll every 3 seconds
            );
        } else {
            if (stopPollingRef.current) {
                stopPollingRef.current();
                stopPollingRef.current = null;
            }
        }

        return () => {
            if (stopPollingRef.current) {
                stopPollingRef.current();
            }
        };
    }, [isRealTimeEnabled]);

    const toggleRealTime = () => {
        setIsRealTimeEnabled(!isRealTimeEnabled);
    };

    return (
        <div className="h-screen flex flex-col">
            {/* Header with controls */}
            <div className="bg-white border-b border-gray-200 p-4">
                <div className="flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-gray-900">GPS Tracking</h1>
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center">
                            <button
                                onClick={toggleRealTime}
                                className={`px-4 py-2 rounded-md text-sm font-medium ${
                                    isRealTimeEnabled
                                        ? 'bg-green-600 text-white hover:bg-green-700'
                                        : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
                                }`}
                            >
                                {isRealTimeEnabled ? '🟢 En Vivo' : '⏸️ Pausado'}
                            </button>
                        </div>
                        {lastUpdate && (
                            <div className="text-sm text-gray-600">
                                Última actualización: {lastUpdate.toLocaleTimeString()}
                            </div>
                        )}
                        <div className="text-sm text-gray-600">
                            Dispositivos activos: {realTimePositions.length}
                        </div>
                    </div>
                </div>
            </div>

            {/* Main content */}
            <div className="flex-1 flex">
                <div className="w-1/4 border-r border-gray-200">
                    <div className="h-full overflow-y-auto">
                        <DeviceList
                            devices={devices}
                            selectedDevice={selectedDevice}
                            onDeviceSelect={setSelectedDevice}
                        />
                    </div>
                </div>
                <div className="flex-1">
                    <DeviceMap
                        devices={devices}
                        selectedDevice={selectedDevice}
                        onDeviceSelect={setSelectedDevice}
                    />
                </div>
            </div>
        </div>
    );
};

export default GPSPage; 
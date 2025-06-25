import React, { useState } from 'react';
import { Device } from '../types';
import DeviceList from '../components/DeviceList';
import DeviceMap from '../components/DeviceMap';
import { useRealTimeDevices } from '../hooks/useRealTimeDevices';
import { startTransition } from 'react';

const GPSPage: React.FC = () => {
    const [selectedDevice, setSelectedDevice] = useState<Device | undefined>(undefined);
    const [isRealTimeEnabled, setIsRealTimeEnabled] = useState(true);

    // Use the new centralized real-time hook
    const {
        devices,
        lastUpdate
    } = useRealTimeDevices({
        enabled: isRealTimeEnabled,
        componentId: 'gps-page',
        onError: (err: Error) => console.error('GPS Page real-time error:', err)
    });

    // Device selection handler
    const handleDeviceSelect = (device: Device) => {
        startTransition(() => {
            setSelectedDevice(device);
        });
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
                                onClick={() => setIsRealTimeEnabled(!isRealTimeEnabled)}
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
                            Dispositivos activos: {devices.length}
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
                            onDeviceSelect={handleDeviceSelect}
                        />
                    </div>
                </div>
                <div className="flex-1">
                    <DeviceMap
                        devices={devices}
                        selectedDevice={selectedDevice}
                        onDeviceSelect={handleDeviceSelect}
                    />
                </div>
            </div>
        </div>
    );
};

export default GPSPage; 
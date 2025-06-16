import React, { useState, useEffect } from 'react';
import { Device } from '../types';
import DeviceList from '../components/DeviceList';
import DeviceMap from '../components/DeviceMap';
import { deviceService } from '../services/deviceService';

const GPSPage: React.FC = () => {
    const [devices, setDevices] = useState<Device[]>([]);
    const [selectedDevice, setSelectedDevice] = useState<Device | undefined>(undefined);

    useEffect(() => {
        const fetchDevices = async () => {
            const data = await deviceService.getAll();
            setDevices(data);
        };
        fetchDevices();
    }, []);

    return (
        <div className="h-screen flex">
            <div className="w-1/4 border-r border-gray-200">
                <div className="h-[calc(100vh-8rem)] overflow-y-auto">
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
    );
};

export default GPSPage; 
import React, { useState, useEffect } from 'react';
import { Device } from '../types/index';
import { deviceService } from '../services/deviceService';
import DeviceMap from './DeviceMap';
import DeviceList from './DeviceList';
import './Dashboard.css';

const Dashboard: React.FC = () => {
    const [devices, setDevices] = useState<Device[]>([]);
    const [selectedDevice, setSelectedDevice] = useState<Device | undefined>(undefined);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchDevices = async () => {
            try {
                setLoading(true);
                const data = await deviceService.getAll();
                setDevices(data);
                setError(null);
            } catch (err) {
                setError('Error loading devices');
                console.error('Error loading devices:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchDevices();
    }, []);

    const handleDeviceSelect = (device: Device) => {
        setSelectedDevice(device);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-red-500">{error}</div>
            </div>
        );
    }

    return (
        <div className="h-screen flex flex-col">
            <div className="flex-1 flex">
                <div className="w-1/4 border-r border-gray-200">
                    <DeviceList
                        devices={devices}
                        selectedDevice={selectedDevice}
                        onDeviceSelect={handleDeviceSelect}
                    />
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

export default Dashboard; 
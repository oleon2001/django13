import React, { useState, useEffect } from 'react';
import { Device } from '../types/index';
import { coordinateService } from '../services/shared/coordinateService';
import DeviceList from '../components/DeviceList';
import DeviceMap from '../components/DeviceMap';

const GPS: React.FC = () => {
    const [devices, setDevices] = useState<Device[]>([]);
    const [selectedDevice, setSelectedDevice] = useState<Device | undefined>(undefined);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadInitialData = async () => {
            try {
                setLoading(true);
                const initialDevices = await coordinateService.getLatestCoordinates();
                setDevices(initialDevices);
                if (initialDevices.length > 0 && !selectedDevice) {
                    setSelectedDevice(initialDevices[0]);
                }
            } catch (error) {
                console.error('Error loading initial data:', error);
                setError('Error loading device data');
            } finally {
                setLoading(false);
            }
        };

        // Cargar datos iniciales
        loadInitialData();

        // Suscribirse a las actualizaciones
        const unsubscribe = coordinateService.subscribe((updatedDevices) => {
            setDevices(updatedDevices);
            if (updatedDevices.length > 0 && !selectedDevice) {
                setSelectedDevice(updatedDevices[0]);
            }
        });

        // Limpiar al desmontar
        return () => {
            unsubscribe();
            coordinateService.stopUpdates();
        };
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

export default GPS; 
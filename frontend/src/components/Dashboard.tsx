import React, { useState, useEffect } from 'react';
import { Device } from '../types';
import DeviceMap from './DeviceMap';
import DeviceList from './DeviceList';
import { deviceService } from '../services/deviceService';
import './Dashboard.css';

const Dashboard: React.FC = () => {
    const [devices, setDevices] = useState<Device[]>([]);
    const [selectedDevice, setSelectedDevice] = useState<Device | undefined>();
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
                setError('Error al cargar los dispositivos');
                console.error('Error fetching devices:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchDevices();
        const interval = setInterval(fetchDevices, 30000); // Actualizar cada 30 segundos

        return () => clearInterval(interval);
    }, []);

    const handleDeviceSelect = (device: Device) => {
        setSelectedDevice(device);
    };

    if (loading) {
        return <div className="dashboard-loading">Cargando dispositivos...</div>;
    }

    if (error) {
        return <div className="dashboard-error">{error}</div>;
    }

    return (
        <div className="dashboard">
            <DeviceList
                devices={devices}
                selectedDevice={selectedDevice}
                onDeviceSelect={handleDeviceSelect}
            />
            <DeviceMap
                devices={devices}
                selectedDevice={selectedDevice}
                onDeviceSelect={handleDeviceSelect}
            />
        </div>
    );
};

export default Dashboard; 
import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Paper,
    CircularProgress,
    Alert,
} from '@mui/material';
import DeviceMap from '../components/DeviceMap';
import { Device } from '../types';
import { deviceService } from '../services/deviceService';

const Tracking: React.FC = () => {
    const [devices, setDevices] = useState<Device[]>([]);
    const [selectedDevice, setSelectedDevice] = useState<Device | undefined>(undefined);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchDevices();
    }, []);

    const fetchDevices = async () => {
        try {
            setLoading(true);
            const data = await deviceService.getAll();
            // Filter only registered and connected devices
            const activeDevices = data.filter(device => 
                device.connection_status === 'ONLINE' || 
                device.connection_status === 'SLEEPING'
            );
            setDevices(activeDevices);
            if (activeDevices.length > 0) {
                setSelectedDevice(activeDevices[0]);
            }
            setError(null);
        } catch (err) {
            setError('Error loading devices');
            console.error('Error loading devices:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleDeviceSelect = (device: Device) => {
        setSelectedDevice(device);
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Box p={3}>
                <Alert severity="error">{error}</Alert>
            </Box>
        );
    }

    return (
        <Box p={3}>
            <Typography variant="h4" gutterBottom>
                Device Tracking
            </Typography>

            <Paper sx={{ height: 'calc(100vh - 200px)' }}>
                <DeviceMap
                    devices={devices}
                    selectedDevice={selectedDevice}
                    onDeviceSelect={handleDeviceSelect}
                />
            </Paper>
        </Box>
    );
};

export default Tracking; 
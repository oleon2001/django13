import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Paper,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    CircularProgress,
    Alert,
} from '@mui/material';
import {
    Warning as WarningIcon,
    TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { sensorService } from '../services/sensorService';
import { deviceService } from '../services/deviceService';
import { Device } from '../types';
import { SelectChangeEvent } from '@mui/material/Select';

interface ExtendedPressureSensor {
    id: number;
    deviceId: number;
    name: string;
    currentPressure: number;
    lastUpdate: string;
}

interface ExtendedAlarmLog {
    id: number;
    sensorId: number;
    message: string;
    timestamp: string;
}

const Sensors: React.FC = () => {
    const [devices, setDevices] = useState<Device[]>([]);
    const [selectedDeviceId, setSelectedDeviceId] = useState<number | ''>('');
    const [pressureSensors, setPressureSensors] = useState<ExtendedPressureSensor[]>([]);
    const [activeAlarms, setActiveAlarms] = useState<ExtendedAlarmLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchDevices();
    }, []);

    useEffect(() => {
        if (selectedDeviceId) {
            fetchSensors();
            fetchActiveAlarms();
        }
    }, [selectedDeviceId]);

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
                setSelectedDeviceId(activeDevices[0].id);
            }
            setError(null);
        } catch (err) {
            setError('Error loading devices');
            console.error('Error loading devices:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchSensors = async () => {
        if (!selectedDeviceId) return;
        try {
            const data = await sensorService.getPressureSensors(selectedDeviceId);
            const extendedSensors: ExtendedPressureSensor[] = data.map(sensor => ({
                id: sensor.id,
                deviceId: sensor.device_id,
                name: sensor.name,
                currentPressure: sensor.latest_reading?.psi1 || 0,
                lastUpdate: sensor.latest_reading?.date || new Date().toISOString()
            }));
            setPressureSensors(extendedSensors);
        } catch (error) {
            console.error('Error fetching pressure sensors:', error);
        }
    };

    const fetchActiveAlarms = async () => {
        if (!selectedDeviceId) return;
        try {
            const data = await sensorService.getActiveAlarms();
            const extendedAlarms: ExtendedAlarmLog[] = data.map(alarm => ({
                id: alarm.id,
                sensorId: alarm.device,
                message: alarm.comment || 'Unknown alarm',
                timestamp: alarm.date
            }));
            setActiveAlarms(extendedAlarms);
        } catch (error) {
            console.error('Error fetching active alarms:', error);
        }
    };

    const handleDeviceChange = (event: SelectChangeEvent<number | ''>) => {
        setSelectedDeviceId(event.target.value as number);
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
                Pressure Sensors
            </Typography>

            <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Select Device</InputLabel>
                <Select
                    value={selectedDeviceId}
                    onChange={handleDeviceChange}
                    label="Select Device"
                >
                    {devices.map((device) => (
                        <MenuItem key={device.id} value={device.id}>
                            {device.name || `Device ${device.imei}`}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>

            {selectedDeviceId && (
                <>
                    <Paper sx={{ p: 2, mb: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Active Alarms
                        </Typography>
                        <List>
                            {activeAlarms.map((alarm) => (
                                <ListItem key={alarm.id}>
                                    <ListItemIcon>
                                        <WarningIcon color="error" />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={alarm.message}
                                        secondary={new Date(alarm.timestamp).toLocaleString()}
                                    />
                                </ListItem>
                            ))}
                        </List>
                    </Paper>

                    <Paper sx={{ p: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            Pressure Sensors
                        </Typography>
                        <List>
                            {pressureSensors.map((sensor) => (
                                <ListItem key={sensor.id}>
                                    <ListItemIcon>
                                        <TrendingUpIcon color="primary" />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={sensor.name}
                                        secondary={`Current Pressure: ${sensor.currentPressure} PSI`}
                                    />
                                </ListItem>
                            ))}
                        </List>
                    </Paper>
                </>
            )}
        </Box>
    );
};

export default Sensors; 
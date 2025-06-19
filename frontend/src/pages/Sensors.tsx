import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
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
    Card,
    CardContent,
    Grid,
    Chip,
} from '@mui/material';
import {
    Warning as WarningIcon,
    Sensors as SensorsIcon,
} from '@mui/icons-material';
import { sensorService } from '../services/sensorService';
import { deviceService } from '../services/deviceService';
import { Device, PressureSensor, AlarmLog } from '../types';
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
    const { t } = useTranslation();
    const [devices, setDevices] = useState<Device[]>([]);
    const [selectedDevice, setSelectedDevice] = useState<number | ''>('');
    const [pressureSensors, setPressureSensors] = useState<ExtendedPressureSensor[]>([]);
    const [activeAlarms, setActiveAlarms] = useState<ExtendedAlarmLog[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchDevices();
    }, []);

    useEffect(() => {
        if (selectedDevice) {
            fetchSensors();
            fetchActiveAlarms();
        }
    }, [selectedDevice]);

    const fetchDevices = async () => {
        try {
            const data = await deviceService.getAll();
            const activeDevices = data.filter((device: Device) => device.connection_status === 'ONLINE');
            setDevices(activeDevices);
            if (activeDevices.length > 0 && activeDevices[0].imei) {
                setSelectedDevice(activeDevices[0].imei);
            }
        } catch (error) {
            console.error(t('sensors.errorLoading'), error);
            setError(t('sensors.errorLoading'));
        }
    };

    const fetchSensors = async () => {
        if (!selectedDevice) return;
        
        setLoading(true);
        try {
            const data = await sensorService.getPressureSensors(selectedDevice as number);
            const extendedSensors: ExtendedPressureSensor[] = data.map((sensor: PressureSensor) => ({
                id: sensor.id,
                name: sensor.name,
                deviceId: sensor.device_id,
                currentPressure: sensor.latest_reading?.psi1 || 0,
                lastUpdate: sensor.latest_reading?.date || new Date().toISOString(),
            }));
            setPressureSensors(extendedSensors);
        } catch (error) {
            console.error('Error fetching sensors:', error);
            setError(t('sensors.errorLoading'));
        } finally {
            setLoading(false);
        }
    };

    const fetchActiveAlarms = async () => {
        if (!selectedDevice) return;
        
        try {
            const data = await sensorService.getActiveAlarms();
            const extendedAlarms: ExtendedAlarmLog[] = data.map((alarm: AlarmLog) => ({
                id: alarm.id,
                sensorId: alarm.device,
                message: alarm.comment || t('alerts.message'),
                timestamp: alarm.date,
            }));
            setActiveAlarms(extendedAlarms);
        } catch (error) {
            console.error('Error fetching alarms:', error);
            setError(t('sensors.errorLoading'));
        }
    };

    const handleDeviceChange = (event: SelectChangeEvent<number | ''>) => {
        setSelectedDevice(event.target.value as number);
    };

    const getSeverityColor = (severity?: string) => {
        switch (severity) {
            case 'high':
            case 'critical':
                return 'error';
            case 'medium':
                return 'warning';
            case 'low':
                return 'info';
            default:
                return 'default';
        }
    };

    if (loading && pressureSensors.length === 0) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" gutterBottom>
                {t('sensors.title')}
            </Typography>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            <Grid container spacing={3}>
                {/* Device Selection */}
                <Grid item xs={12}>
                    <Paper sx={{ p: 2 }}>
                        <FormControl fullWidth>
                            <InputLabel id="device-select-label">
                                {t('sensors.selectDeviceLabel')}
                            </InputLabel>
                            <Select
                                labelId="device-select-label"
                                value={selectedDevice}
                                label={t('sensors.selectDeviceLabel')}
                                onChange={handleDeviceChange}
                            >
                                {devices.map((device) => (
                                    <MenuItem key={device.imei} value={device.imei}>
                                        {device.name || `${t('devices.title')} ${device.imei}`}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Paper>
                </Grid>

                {/* Pressure Sensors */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                {t('sensors.pressureSensors')}
                            </Typography>
                            {pressureSensors.length > 0 ? (
                                <List>
                                    {pressureSensors.map((sensor) => (
                                        <ListItem key={sensor.id}>
                                            <ListItemIcon>
                                                <SensorsIcon />
                                            </ListItemIcon>
                                            <ListItemText
                                                primary={sensor.name}
                                                secondary={t('sensors.currentPressure', { pressure: sensor.currentPressure })}
                                            />
                                            <Chip
                                                label={t('common.active')}
                                                color="success"
                                                size="small"
                                            />
                                        </ListItem>
                                    ))}
                                </List>
                            ) : (
                                <Typography color="text.secondary">
                                    {t('common.noData')}
                                </Typography>
                            )}
                        </CardContent>
                    </Card>
                </Grid>

                {/* Active Alarms */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                {t('sensors.activeAlarms')}
                            </Typography>
                            {activeAlarms.length > 0 ? (
                                <List>
                                    {activeAlarms.map((alarm) => (
                                        <ListItem key={alarm.id}>
                                            <ListItemIcon>
                                                <WarningIcon color="warning" />
                                            </ListItemIcon>
                                            <ListItemText
                                                primary={alarm.message}
                                                secondary={new Date(alarm.timestamp).toLocaleString()}
                                            />
                                            <Chip
                                                label={t('alerts.medium')}
                                                color={getSeverityColor('medium')}
                                                size="small"
                                            />
                                        </ListItem>
                                    ))}
                                </List>
                            ) : (
                                <Typography color="text.secondary">
                                    {t('common.noData')}
                                </Typography>
                            )}
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
};

export default Sensors; 
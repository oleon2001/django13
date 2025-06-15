import React, { useState, useEffect } from 'react';
import {
    Grid,
    Paper,
    Typography,
    Box,
    Card,
    CardContent,
    List,
    ListItem,
    ListItemText,
    Divider,
    Chip,
    ListItemIcon,
    Button,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    CircularProgress,
    Alert,
} from '@mui/material';
import {
    Sensors as SensorsIcon,
    Speed as SpeedIcon,
    Warning as WarningIcon,
    CheckCircleOutline as CheckIcon,
    ErrorOutline as ErrorIcon,
    TrendingUp as TrendingUpIcon,
    GetApp as ExportIcon,
    Refresh as RefreshIcon,
} from '@mui/icons-material';
import { sensorService } from '../services/sensorService';
import { deviceService } from '../services/deviceService';
import { PressureSensor, PressureReading, AlarmLog, Device } from '../types';

const Sensors: React.FC = () => {
    const [devices, setDevices] = useState<Device[]>([]);
    const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);
    const [pressureSensors, setPressureSensors] = useState<PressureSensor[]>([]);
    const [pressureReadings, setPressureReadings] = useState<PressureReading[]>([]);
    const [alarmLogs, setAlarmLogs] = useState<AlarmLog[]>([]);
    const [activeAlarms, setActiveAlarms] = useState<AlarmLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [sensorStats, setSensorStats] = useState<any>(null);

    useEffect(() => {
        fetchDevices();
        fetchActiveAlarms();
    }, []);

    useEffect(() => {
        if (selectedDevice) {
            fetchPressureSensors(selectedDevice.imei);
            fetchPressureReadings(selectedDevice.imei);
            fetchAlarmLogs(selectedDevice.imei);
            fetchSensorStats(selectedDevice.imei);
        }
    }, [selectedDevice]);

    const fetchDevices = async () => {
        try {
            setLoading(true);
            const data = await deviceService.getAll();
            // Filter devices that have sensors
            const devicesWithSensors = data.filter(d => d.connection_status === 'ONLINE');
            setDevices(devicesWithSensors);
            if (devicesWithSensors.length > 0) {
                setSelectedDevice(devicesWithSensors[0]);
            }
        } catch (error) {
            console.error('Error fetching devices:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchPressureSensors = async (deviceId: number) => {
        try {
            const data = await sensorService.getPressureSensors(deviceId);
            setPressureSensors(data);
        } catch (error) {
            console.error('Error fetching pressure sensors:', error);
        }
    };

    const fetchPressureReadings = async (deviceId: number) => {
        try {
            const endDate = new Date().toISOString();
            const startDate = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(); // Last 24 hours
            const data = await sensorService.getPressureReadings(deviceId, undefined, startDate, endDate);
            setPressureReadings(data.slice(0, 20)); // Show last 20 readings
        } catch (error) {
            console.error('Error fetching pressure readings:', error);
        }
    };

    const fetchAlarmLogs = async (deviceId: number) => {
        try {
            const endDate = new Date().toISOString();
            const startDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(); // Last 7 days
            const data = await sensorService.getAlarmLogs(deviceId, startDate, endDate);
            setAlarmLogs(data);
        } catch (error) {
            console.error('Error fetching alarm logs:', error);
        }
    };

    const fetchActiveAlarms = async () => {
        try {
            const data = await sensorService.getActiveAlarms();
            setActiveAlarms(data);
        } catch (error) {
            console.error('Error fetching active alarms:', error);
        }
    };

    const fetchSensorStats = async (deviceId: number) => {
        try {
            const data = await sensorService.getSensorStats(deviceId);
            setSensorStats(data);
        } catch (error) {
            console.error('Error fetching sensor stats:', error);
        }
    };

    const handleExportSensorData = async () => {
        if (!selectedDevice) return;
        
        try {
            const endDate = new Date().toISOString().split('T')[0];
            const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]; // Last 30 days
            
            const blob = await sensorService.exportSensorData(selectedDevice.imei, startDate, endDate);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `sensor_data_${selectedDevice.name}_${endDate}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error exporting sensor data:', error);
        }
    };

    const getPressureColor = (psi: number) => {
        if (psi > 80) return 'error';
        if (psi > 60) return 'warning';
        if (psi > 30) return 'success';
        return 'info';
    };

    const getAlarmSeverityColor = (comment: string) => {
        if (comment.includes('CRITICAL') || comment.includes('HIGH')) return 'error';
        if (comment.includes('WARNING') || comment.includes('MEDIUM')) return 'warning';
        return 'info';
    };

    if (loading) {
        return (
            <Box sx={{ flexGrow: 1, p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <CircularProgress />
                <Typography sx={{ ml: 2 }}>Cargando sensores...</Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ flexGrow: 1, p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" gutterBottom component="h1">
                    Monitoreo de Sensores
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                        variant="outlined"
                        startIcon={<RefreshIcon />}
                        onClick={() => selectedDevice && fetchPressureReadings(selectedDevice.imei)}
                    >
                        Actualizar
                    </Button>
                    <Button
                        variant="outlined"
                        startIcon={<ExportIcon />}
                        onClick={handleExportSensorData}
                        disabled={!selectedDevice}
                    >
                        Exportar Datos
                    </Button>
                </Box>
            </Box>

            {/* Active Alarms Alert */}
            {activeAlarms.length > 0 && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    ⚠️ {activeAlarms.length} alarma(s) activa(s) en el sistema
                </Alert>
            )}

            <Grid container spacing={3} sx={{ flexGrow: 1, minHeight: 0 }}>
                {/* Device Selection and Stats */}
                <Grid item xs={12} md={4}>
                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        Selección de Dispositivo
                                    </Typography>
                                    <FormControl fullWidth>
                                        <InputLabel>Dispositivo</InputLabel>
                                        <Select
                                            value={selectedDevice?.imei || ''}
                                            onChange={(e) => {
                                                const device = devices.find(d => d.imei === e.target.value);
                                                setSelectedDevice(device || null);
                                            }}
                                        >
                                            {devices.map((device) => (
                                                <MenuItem key={device.imei} value={device.imei}>
                                                    {device.name} ({device.imei})
                                                </MenuItem>
                                            ))}
                                        </Select>
                                    </FormControl>
                                </CardContent>
                            </Card>
                        </Grid>

                        {/* Sensor Statistics */}
                        {sensorStats && (
                            <Grid item xs={12}>
                                <Card>
                                    <CardContent>
                                        <Typography variant="h6" gutterBottom>
                                            Estadísticas de Sensores
                                        </Typography>
                                        <List>
                                            <ListItem disablePadding>
                                                <ListItemText
                                                    primary="Sensores Activos"
                                                    secondary={`${pressureSensors.length} sensores`}
                                                />
                                                <Chip
                                                    label={pressureSensors.length}
                                                    color="primary"
                                                    size="small"
                                                />
                                            </ListItem>
                                            <ListItem disablePadding>
                                                <ListItemText
                                                    primary="Lecturas Hoy"
                                                    secondary={`${pressureReadings.length} lecturas`}
                                                />
                                                <Chip
                                                    label={pressureReadings.length}
                                                    color="success"
                                                    size="small"
                                                />
                                            </ListItem>
                                            <ListItem disablePadding>
                                                <ListItemText
                                                    primary="Alarmas Activas"
                                                    secondary={`${activeAlarms.length} alarmas`}
                                                />
                                                <Chip
                                                    label={activeAlarms.length}
                                                    color={activeAlarms.length > 0 ? 'error' : 'success'}
                                                    size="small"
                                                />
                                            </ListItem>
                                        </List>
                                    </CardContent>
                                </Card>
                            </Grid>
                        )}
                    </Grid>
                </Grid>

                {/* Pressure Sensors */}
                <Grid item xs={12} md={8}>
                    <Paper sx={{ height: 500, p: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            Sensores de Presión - {selectedDevice?.name || 'Seleccione un dispositivo'}
                        </Typography>
                        
                        <Grid container spacing={2}>
                            {pressureSensors.map((sensor) => (
                                <Grid item xs={12} md={6} key={sensor.id}>
                                    <Card sx={{ height: '100%' }}>
                                        <CardContent>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                                <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                                                    {sensor.name}
                                                </Typography>
                                                <SensorsIcon color="primary" />
                                            </Box>
                                            
                                            <Typography variant="caption" color="textSecondary">
                                                Serie: {sensor.sensor}
                                            </Typography>
                                            
                                            {sensor.latest_reading && (
                                                <Box sx={{ mt: 2 }}>
                                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                                        <Typography variant="body2">PSI 1:</Typography>
                                                        <Chip
                                                            label={`${sensor.latest_reading.psi1.toFixed(2)} PSI`}
                                                            color={getPressureColor(sensor.latest_reading.psi1)}
                                                            size="small"
                                                        />
                                                    </Box>
                                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                                        <Typography variant="body2">PSI 2:</Typography>
                                                        <Chip
                                                            label={`${sensor.latest_reading.psi2.toFixed(2)} PSI`}
                                                            color={getPressureColor(sensor.latest_reading.psi2)}
                                                            size="small"
                                                        />
                                                    </Box>
                                                    <Typography variant="caption" color="textSecondary">
                                                        Última lectura: {new Date(sensor.latest_reading.date).toLocaleString()}
                                                    </Typography>
                                                </Box>
                                            )}
                                        </CardContent>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    </Paper>
                </Grid>

                {/* Recent Readings and Alarms */}
                <Grid item xs={12}>
                    <Grid container spacing={3}>
                        {/* Recent Pressure Readings */}
                        <Grid item xs={12} md={6}>
                            <Card sx={{ height: 400 }}>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                                        <TrendingUpIcon sx={{ mr: 1 }} />
                                        Lecturas Recientes
                                    </Typography>
                                    <List sx={{ maxHeight: 300, overflowY: 'auto' }}>
                                        {pressureReadings.map((reading, index) => (
                                            <React.Fragment key={`${reading.id}-${index}`}>
                                                <ListItem>
                                                    <ListItemIcon>
                                                        <SpeedIcon />
                                                    </ListItemIcon>
                                                    <ListItemText
                                                        primary={`Sensor ${reading.sensor.substring(0, 8)}`}
                                                        secondary={
                                                            <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                                                                <Chip
                                                                    label={`PSI1: ${reading.psi1.toFixed(1)}`}
                                                                    color={getPressureColor(reading.psi1)}
                                                                    size="small"
                                                                />
                                                                <Chip
                                                                    label={`PSI2: ${reading.psi2.toFixed(1)}`}
                                                                    color={getPressureColor(reading.psi2)}
                                                                    size="small"
                                                                />
                                                            </Box>
                                                        }
                                                    />
                                                    <Typography variant="caption" color="textSecondary">
                                                        {new Date(reading.date).toLocaleTimeString()}
                                                    </Typography>
                                                </ListItem>
                                                <Divider variant="inset" component="li" />
                                            </React.Fragment>
                                        ))}
                                    </List>
                                </CardContent>
                            </Card>
                        </Grid>

                        {/* Alarm Logs */}
                        <Grid item xs={12} md={6}>
                            <Card sx={{ height: 400 }}>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                                        <WarningIcon sx={{ mr: 1 }} />
                                        Registro de Alarmas
                                    </Typography>
                                    <List sx={{ maxHeight: 300, overflowY: 'auto' }}>
                                        {alarmLogs.length > 0 ? alarmLogs.map((alarm, index) => (
                                            <React.Fragment key={`${alarm.id}-${index}`}>
                                                <ListItem>
                                                    <ListItemIcon>
                                                        {alarm.comment.includes('CRITICAL') || alarm.comment.includes('HIGH') ? 
                                                            <ErrorIcon color="error" /> : 
                                                            <WarningIcon color="warning" />
                                                        }
                                                    </ListItemIcon>
                                                    <ListItemText
                                                        primary={alarm.comment}
                                                        secondary={
                                                            <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                                                                <Chip
                                                                    label={alarm.sensor.substring(0, 8)}
                                                                    size="small"
                                                                    variant="outlined"
                                                                />
                                                                <Chip
                                                                    label={`${alarm.duration}s`}
                                                                    color={getAlarmSeverityColor(alarm.comment)}
                                                                    size="small"
                                                                />
                                                            </Box>
                                                        }
                                                    />
                                                    <Typography variant="caption" color="textSecondary">
                                                        {new Date(alarm.date).toLocaleString()}
                                                    </Typography>
                                                </ListItem>
                                                <Divider variant="inset" component="li" />
                                            </React.Fragment>
                                        )) : (
                                            <ListItem>
                                                <ListItemIcon>
                                                    <CheckIcon color="success" />
                                                </ListItemIcon>
                                                <ListItemText primary="No hay alarmas registradas" />
                                            </ListItem>
                                        )}
                                    </List>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
        </Box>
    );
};

export default Sensors; 
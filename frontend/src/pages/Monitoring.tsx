import React, { useState, useEffect } from 'react';
import {
    Box,
    Grid,
    Paper,
    Typography,
    Card,
    CardContent,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    Chip,
    CircularProgress,
    Alert,
} from '@mui/material';
import {
    DirectionsCar as DirectionsCarIcon,
    Speed as SpeedIcon,
    LocationOn as LocationOnIcon,
    Battery80 as BatteryIcon,
    SignalCellular4Bar as SignalIcon,
} from '@mui/icons-material';
import DeviceMap from '../components/DeviceMap';
import { deviceService } from '../services/deviceService';
import { Device } from '../types';

const Monitoring: React.FC = () => {
    const [devices, setDevices] = useState<Device[]>([]);
    const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchDevices();
        // Set up polling for real-time updates
        const interval = setInterval(fetchDevices, 10000); // Update every 10 seconds
        return () => clearInterval(interval);
    }, []);

    const fetchDevices = async () => {
        try {
            const data = await deviceService.getAll();
            if (Array.isArray(data)) {
                setDevices(data);
                // Select first device if none selected
                if (!selectedDevice && data.length > 0) {
                    setSelectedDevice(data[0]);
                }
                setError(null);
            } else {
                setDevices([]);
                setError('Invalid data format received from server');
            }
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

    const getStatusColor = (status: string) => {
        switch (status?.toLowerCase()) {
            case 'online':
                return 'success';
            case 'offline':
                return 'error';
            default:
                return 'default';
        }
    };

    const onlineDevices = devices.filter(d => d.connection_status === 'ONLINE').length;
    const totalDevices = devices.length;

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box sx={{ flexGrow: 1, p: 3 }}>
            <Typography variant="h4" gutterBottom>
                Monitoreo en Tiempo Real
            </Typography>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            <Grid container spacing={3}>
                {/* Map Section */}
                <Grid item xs={12} md={8}>
                    <Paper sx={{ p: 2, height: '500px' }}>
                        <DeviceMap 
                            devices={devices}
                            selectedDevice={selectedDevice || undefined}
                            onDeviceSelect={handleDeviceSelect}
                        />
                    </Paper>
                </Grid>

                {/* Device Details */}
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 2, height: '500px', overflow: 'auto' }}>
                        {selectedDevice ? (
                            <>
                                <Typography variant="h6" gutterBottom>
                                    {selectedDevice.name || `Device ${selectedDevice.imei}`}
                                </Typography>
                                <List>
                                    <ListItem>
                                        <ListItemIcon>
                                            <LocationOnIcon />
                                        </ListItemIcon>
                                        <ListItemText 
                                            primary="Ubicación"
                                            secondary={selectedDevice.latitude && selectedDevice.longitude ? 
                                                `${selectedDevice.latitude.toFixed(6)}, ${selectedDevice.longitude.toFixed(6)}` : 
                                                'No disponible'
                                            }
                                        />
                                    </ListItem>
                                    <ListItem>
                                        <ListItemIcon>
                                            <SpeedIcon />
                                        </ListItemIcon>
                                        <ListItemText 
                                            primary="Velocidad"
                                            secondary={`${selectedDevice.speed || 0} km/h`}
                                        />
                                    </ListItem>
                                    <ListItem>
                                        <ListItemIcon>
                                            <BatteryIcon />
                                        </ListItemIcon>
                                        <ListItemText 
                                            primary="Batería"
                                            secondary={`${selectedDevice.battery_level || 0}%`}
                                        />
                                    </ListItem>
                                    <ListItem>
                                        <ListItemIcon>
                                            <SignalIcon />
                                        </ListItemIcon>
                                        <ListItemText 
                                            primary="Señal"
                                            secondary={`${selectedDevice.signal_strength || 0}%`}
                                        />
                                    </ListItem>
                                </List>
                            </>
                        ) : (
                            <Typography variant="body2" color="text.secondary">
                                Seleccione un dispositivo para ver detalles
                            </Typography>
                        )}
                    </Paper>
                </Grid>

                {/* Statistics Cards */}
                <Grid item xs={12} sm={6} md={3}>
                    <Card>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                Dispositivos
                            </Typography>
                            <Typography variant="h5" component="div">
                                {totalDevices}
                            </Typography>
                            <Typography variant="body2">
                                Total registrados
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <Card>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                En Línea
                            </Typography>
                            <Typography variant="h5" component="div">
                                {onlineDevices}
                            </Typography>
                            <Typography variant="body2">
                                {totalDevices > 0 ? `${((onlineDevices / totalDevices) * 100).toFixed(0)}%` : '0%'} activos
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Device List */}
                <Grid item xs={12}>
                    <Paper sx={{ p: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            Lista de Dispositivos
                        </Typography>
                        <List>
                            {devices.length > 0 ? devices.map(device => (
                                <ListItem 
                                    key={device.imei}
                                    button
                                    onClick={() => handleDeviceSelect(device)}
                                    selected={selectedDevice?.imei === device.imei}
                                >
                                    <ListItemIcon>
                                        <DirectionsCarIcon />
                                    </ListItemIcon>
                                    <ListItemText 
                                        primary={device.name || `Device ${device.imei}`}
                                        secondary={`IMEI: ${device.imei} | Última actualización: ${
                                            device.lastUpdate ? new Date(device.lastUpdate).toLocaleString() : 'N/A'
                                        }`}
                                    />
                                    <Chip 
                                        label={device.connection_status || 'OFFLINE'}
                                        color={getStatusColor(device.connection_status || 'OFFLINE')}
                                        size="small"
                                    />
                                </ListItem>
                            )) : (
                                <ListItem>
                                    <ListItemText 
                                        primary="No hay dispositivos disponibles"
                                        secondary="Los dispositivos aparecerán aquí cuando se conecten"
                                    />
                                </ListItem>
                            )}
                        </List>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

export default Monitoring;
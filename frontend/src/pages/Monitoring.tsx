import React, { useState } from 'react';
import {
    Paper,
    Typography,
    Box,
    Card,
    CardContent,
    List,
    ListItem,
    ListItemText,
    Divider,
    Stack,
    Grid,
    IconButton,
    Tooltip,
    Chip,
    ListItemIcon,
} from '@mui/material';
import {
    Speed as SpeedIcon,
    LocationOn as LocationIcon,
    AccessTime as TimeIcon,
    DirectionsCar as VehicleIcon,
    Refresh as RefreshIcon,
} from '@mui/icons-material';
import { mockDevices, mockVehicles } from '../data/mockData';
import DeviceMap from '../components/DeviceMap';

const Monitoring: React.FC = () => {
    const [selectedDevice, setSelectedDevice] = useState(mockDevices[0]);
    const [isRefreshing, setIsRefreshing] = useState(false);

    const handleDeviceSelect = (device: typeof mockDevices[0]) => {
        setSelectedDevice(device);
    };

    const handleRefresh = () => {
        setIsRefreshing(true);
        setTimeout(() => {
            console.log("Refrescando datos...");
            setIsRefreshing(false);
        }, 1000);
    };

    const getStatusChipColor = (status: string) => {
        return status === 'online' ? 'success' : 'error';
    };

    return (
        <Box sx={{ flexGrow: 1, p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" component="h1">
                    Monitoreo en Tiempo Real
                </Typography>
                <Typography variant="subtitle1" color="text.secondary">
                    Última actualización: {new Date().toLocaleTimeString()}
                </Typography>
            </Box>

            <Grid container spacing={3}>
                {/* Mapa y Lista de Dispositivos */}
                <Grid item xs={12} md={8}>
                    <Paper sx={{ height: 550, p: 2 }}>
                        <DeviceMap
                            devices={mockDevices}
                            selectedDevice={selectedDevice}
                            onDeviceSelect={handleDeviceSelect}
                        />
                    </Paper>
                </Grid>

                {/* Panel de Control y Lista de Dispositivos */}
                <Grid item xs={12} md={4}>
                    <Stack spacing={3} sx={{ height: '100%' }}>
                        <Card sx={{ flexGrow: 1 }}>
                            <CardContent>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                    <Typography variant="h6">
                                        Panel de Control
                                    </Typography>
                                    <Tooltip title="Actualizar datos">
                                        <IconButton
                                            onClick={handleRefresh}
                                            disabled={isRefreshing}
                                            color="primary"
                                        >
                                            <RefreshIcon sx={{ animation: isRefreshing ? 'spin 1s linear infinite' : 'none' }} />
                                        </IconButton>
                                    </Tooltip>
                                </Box>
                                <List dense>
                                    <ListItem disablePadding>
                                        <ListItemText
                                            primary="Dispositivos Activos"
                                            secondary={`${mockDevices.filter(d => d.status === 'online').length} de ${mockDevices.length}`}
                                        />
                                    </ListItem>
                                    <ListItem disablePadding>
                                        <ListItemText
                                            primary="Vehículos en Servicio"
                                            secondary={`${mockVehicles.filter(v => v.status === 'active').length} de ${mockVehicles.length}`}
                                        />
                                    </ListItem>
                                </List>
                            </CardContent>
                        </Card>

                        <Card sx={{ flexGrow: 1 }}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Lista de Dispositivos
                                </Typography>
                                <List dense sx={{ maxHeight: 250, overflow: 'auto' }}>
                                    {mockDevices.map(device => (
                                        <React.Fragment key={device.id}>
                                            <ListItem
                                                button
                                                selected={selectedDevice?.id === device.id}
                                                onClick={() => handleDeviceSelect(device)}
                                                sx={{ py: 0.5 }}
                                            >
                                                <ListItemText
                                                    primary={device.name}
                                                    secondary={
                                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                                                            <Chip
                                                                size="small"
                                                                label={device.status}
                                                                color={getStatusChipColor(device.status)}
                                                            />
                                                            <Typography variant="caption" color="text.secondary">
                                                                {new Date(device.lastUpdate).toLocaleTimeString()}
                                                            </Typography>
                                                        </Box>
                                                    }
                                                />
                                            </ListItem>
                                            <Divider component="li" variant="inset" sx={{ my: 0.5 }} />
                                        </React.Fragment>
                                    ))}
                                </List>
                            </CardContent>
                        </Card>
                    </Stack>
                </Grid>

                {/* Detalles del Dispositivo Seleccionado */}
                {selectedDevice && (
                    <Grid item xs={12}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" gutterBottom>
                                    Detalles del Dispositivo: {selectedDevice.name}
                                </Typography>
                                <Grid container spacing={3}>
                                    <Grid item xs={12} md={6}>
                                        <List dense>
                                            <ListItem disablePadding>
                                                <ListItemIcon><VehicleIcon /></ListItemIcon>
                                                <ListItemText
                                                    primary="Vehículo"
                                                    secondary={selectedDevice.name}
                                                />
                                            </ListItem>
                                            <ListItem disablePadding>
                                                <ListItemIcon><LocationIcon /></ListItemIcon>
                                                <ListItemText
                                                    primary="Ubicación"
                                                    secondary={`${selectedDevice.latitude.toFixed(4)}, ${selectedDevice.longitude.toFixed(4)}`}
                                                />
                                            </ListItem>
                                            <ListItem disablePadding>
                                                <ListItemIcon><TimeIcon /></ListItemIcon>
                                                <ListItemText
                                                    primary="Última Actualización"
                                                    secondary={new Date(selectedDevice.lastUpdate).toLocaleString()}
                                                />
                                            </ListItem>
                                            <ListItem disablePadding>
                                                <ListItemText
                                                    primary="Última Vista"
                                                    secondary={new Date(selectedDevice.lastSeen).toLocaleString()}
                                                />
                                            </ListItem>
                                        </List>
                                    </Grid>
                                    <Grid item xs={12} md={6}>
                                        <List dense>
                                            <ListItem disablePadding>
                                                <ListItemIcon><SpeedIcon /></ListItemIcon>
                                                <ListItemText
                                                    primary="Velocidad"
                                                    secondary={`${selectedDevice.speed} km/h`}
                                                />
                                            </ListItem>
                                            <ListItem disablePadding>
                                                <ListItemText
                                                    primary="Protocolo"
                                                    secondary={selectedDevice.protocol}
                                                />
                                            </ListItem>
                                            <ListItem disablePadding>
                                                <ListItemText
                                                    primary="IMEI"
                                                    secondary={selectedDevice.imei}
                                                />
                                            </ListItem>
                                        </List>
                                    </Grid>
                                </Grid>
                            </CardContent>
                        </Card>
                    </Grid>
                )}
            </Grid>
            <style>{`
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `}</style>
        </Box>
    );
};

export default Monitoring;
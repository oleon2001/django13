import React, { useState } from 'react';
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
    LinearProgress,
    Chip,
    ListItemIcon,
} from '@mui/material';
import {
    Speed as SpeedIcon,
    LocationOn as LocationOnIcon,
    CheckCircleOutline as CheckCircleOutlineIcon,
    ErrorOutline as ErrorOutlineIcon,
    WarningAmber as WarningAmberIcon,
} from '@mui/icons-material';
import { mockDevices, mockVehicles, mockAlerts } from '../data/mockData';
import DeviceMap from '../components/DeviceMap';

const Dashboard: React.FC = () => {
    const [selectedDevice, setSelectedDevice] = useState(mockDevices[0]);
    const onlineDevices = mockDevices.filter(device => device.status === 'online');
    const activeAlerts = mockAlerts.filter(alert => alert.status === 'active');

    const handleDeviceSelect = (device: typeof mockDevices[0]) => {
        setSelectedDevice(device);
    };

    const getAlertChipColor = (severity: string) => {
        switch (severity) {
            case 'high': return 'error';
            case 'medium': return 'warning';
            case 'low': return 'info';
            default: return 'default';
        }
    };

    return (
      <Box sx={{ flexGrow: 1, p: 3 }}>
            <Typography variant="h4" gutterBottom component="h1">
                Panel de Control
        </Typography>

        <Grid container spacing={3} sx={{ flexGrow: 1, minHeight: 0 }}>
                {/* Mapa de Dispositivos */}
                <Grid item xs={12} md={8}>
            <Paper sx={{ height: 500, p: 2 }}>
              <DeviceMap
                            devices={mockDevices}
                selectedDevice={selectedDevice}
                onDeviceSelect={handleDeviceSelect}
              />
            </Paper>
          </Grid>

                <Grid item xs={12} md={4}>
                    <Grid container spacing={3}>
            <Grid item xs={12}>
                            <Card sx={{ height: '100%' }}>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        Estado General
                    </Typography>
                                    <List>
                                        <ListItem disablePadding>
                                            <ListItemText
                                                primary="Dispositivos Activos"
                                                secondary={`${onlineDevices.length} de ${mockDevices.length}`}
                                            />
                                            <LinearProgress
                                                variant="determinate"
                                                value={(onlineDevices.length / mockDevices.length) * 100}
                                                color="success"
                                                sx={{ width: 100, height: 8, borderRadius: 5 }}
                                            />
                                        </ListItem>
                                        <ListItem disablePadding>
                                            <ListItemText
                                                primary="Vehículos en Servicio"
                                                secondary={`${mockVehicles.filter(v => v.status === 'active').length} de ${mockVehicles.length}`}
                                            />
                                            <LinearProgress
                                                variant="determinate"
                                                value={(mockVehicles.filter(v => v.status === 'active').length / mockVehicles.length) * 100}
                                                color="success"
                                                sx={{ width: 100, height: 8, borderRadius: 5 }}
                                            />
                                        </ListItem>
                                        <ListItem disablePadding>
                                            <ListItemText
                                                primary="Alertas Activas"
                                                secondary={activeAlerts.length}
                                            />
                                            <LinearProgress
                                                variant="determinate"
                                                value={(activeAlerts.length / mockAlerts.length) * 100}
                                                color="error"
                                                sx={{ width: 100, height: 8, borderRadius: 5 }}
                                            />
                                        </ListItem>
                                    </List>
                                </CardContent>
                            </Card>
                        </Grid>

                        <Grid item xs={12}>
                            <Card sx={{ height: '100%' }}>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        Alertas Recientes
                    </Typography>
                                    <List sx={{ maxHeight: 300, overflowY: 'auto' }}>
                                        {activeAlerts.length > 0 ? (activeAlerts.map(alert => (
                                            <React.Fragment key={alert.id}>
                                                <ListItem
                                                    secondaryAction={
                                                        <Chip
                                                            label={alert.severity}
                                                            color={getAlertChipColor(alert.severity)}
                                                            size="small"
                                                            icon={
                                                                alert.severity === 'high' ? <ErrorOutlineIcon fontSize="small" /> :
                                                                alert.severity === 'medium' ? <WarningAmberIcon fontSize="small" /> :
                                                                <CheckCircleOutlineIcon fontSize="small" />
                                                            }
                                                        />
                                                    }
                                                >
                                                    <ListItemText
                                                        primary={alert.message}
                                                        secondary={new Date(alert.timestamp).toLocaleString()}
                                                    />
                                                </ListItem>
                                                <Divider variant="inset" component="li" />
                                            </React.Fragment>
                                        ))) : (
                                            <ListItem>
                                                <ListItemText primary="No hay alertas activas." />
                                            </ListItem>
                                        )}
                                    </List>
                                </CardContent>
                            </Card>
                  </Grid>
                  </Grid>
                </Grid>

                {/* Detalles del Dispositivo Seleccionado */}
        {selectedDevice && (
          <Grid item xs={12}>
                        <Card sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                            <CardContent sx={{ maxHeight: 300, overflowY: 'auto', display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                                <Typography variant="h6" gutterBottom>
                                    Detalles del Dispositivo: {selectedDevice.name}
                                </Typography>
              <Grid container spacing={2}>
                                    <Grid item xs={12} md={6}>
                                        <List dense>
                                            <ListItem>
                                                <ListItemIcon><SpeedIcon /></ListItemIcon>
                                                <ListItemText
                                                    primary="Velocidad"
                                                    secondary={`${selectedDevice.speed} km/h`}
                                                />
                                            </ListItem>
                                            <ListItem>
                                                <ListItemIcon><LocationOnIcon /></ListItemIcon>
                                                <ListItemText
                                                    primary="Ubicación (Lat, Lon)"
                                                    secondary={`${selectedDevice.latitude}, ${selectedDevice.longitude}`}
                                                />
                                            </ListItem>
                                            <ListItem>
                                                <ListItemText
                                                    primary="Última Actualización"
                                                    secondary={new Date(selectedDevice.lastUpdate).toLocaleString()}
                                                />
                                            </ListItem>
                                            <ListItem>
                                                <ListItemText
                                                    primary="Última Vista"
                                                    secondary={new Date(selectedDevice.lastSeen).toLocaleString()}
                                                />
                                            </ListItem>
                                        </List>
                </Grid>
                                    <Grid item xs={12} md={6}>
                                        <List dense>
                                            <ListItem>
                                                <ListItemIcon><SpeedIcon /></ListItemIcon>
                                                <ListItemText
                                                    primary="Velocidad"
                                                    secondary={`${selectedDevice.speed} km/h`}
                                                />
                                            </ListItem>
                                            <ListItem>
                                                <ListItemText
                                                    primary="Protocolo"
                                                    secondary={selectedDevice.protocol}
                                                />
                                            </ListItem>
                                            <ListItem>
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
    </Box>
  );
};

export default Dashboard; 
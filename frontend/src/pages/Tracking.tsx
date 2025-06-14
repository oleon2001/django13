import React, { useState } from 'react';
import {
    Grid,
    Paper,
    Typography,
    Card,
    CardContent,
    Box,
    List,
    ListItem,
    ListItemText,
    Chip,
} from '@mui/material';
import {
    CheckCircleOutline as CheckCircleOutlineIcon,
    ErrorOutline as ErrorOutlineIcon,
} from '@mui/icons-material';
import DeviceMap from '../components/DeviceMap';
import { Device } from '../types';
import { mockDevices } from '../data/mockData';

const Tracking: React.FC = () => {
    const [selectedDevice, setSelectedDevice] = useState<Device | undefined>(undefined);
    const onlineDevices = mockDevices.filter((device) => device.status === 'online');
    const offlineDevices = mockDevices.filter((device) => device.status === 'offline');

    const handleDeviceSelect = (device: typeof mockDevices[0]) => {
        setSelectedDevice(device);
    };

    const getStatusChipColor = (status: string) => {
        return status === 'online' ? 'success' : 'error';
    };

    return (
        <Box sx={{ flexGrow: 1, p: 3 }}>
            <Typography variant="h4" gutterBottom component="h1">
                Rastreo de Vehículos
            </Typography>
            <Grid container spacing={3} sx={{ height: 'calc(100vh - 120px)' }}>
                <Grid item xs={12} md={3}>
                    <Paper
                        sx={{
                            height: '100%',
                            overflow: 'auto',
                            p: 2,
                        }}
                    >
                        <Typography variant="h6" gutterBottom>
                            Estado de Dispositivos
                        </Typography>
                        <Card sx={{ mb: 2, bgcolor: 'success.main', color: 'white' }}>
                            <CardContent>
                                <Box display="flex" alignItems="center" justifyContent="space-between">
                                    <Typography variant="h4">{onlineDevices.length}</Typography>
                                    <CheckCircleOutlineIcon sx={{ fontSize: 40 }} />
                                </Box>
                                <Typography>Online</Typography>
                            </CardContent>
                        </Card>
                        <Card sx={{ bgcolor: 'error.main', color: 'white' }}>
                            <CardContent>
                                <Box display="flex" alignItems="center" justifyContent="space-between">
                                    <Typography variant="h4">{offlineDevices.length}</Typography>
                                    <ErrorOutlineIcon sx={{ fontSize: 40 }} />
                                </Box>
                                <Typography>Offline</Typography>
                            </CardContent>
                        </Card>

                        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                            Seleccionar Dispositivo
                        </Typography>
                        <List dense>
                            {mockDevices.map((device) => (
                                <ListItem
                                    key={device.id}
                                    button
                                    selected={selectedDevice?.id === device.id}
                                    onClick={() => handleDeviceSelect(device)}
                                >
                                    <ListItemText
                                        primary={device.name}
                                        secondary={
                                            <Chip
                                                label={device.status}
                                                color={getStatusChipColor(device.status)}
                                                size="small"
                                                sx={{ mt: 0.5 }}
                                            />
                                        }
                                    />
                                </ListItem>
                            ))}
                        </List>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={9}>
                    <Paper
                        sx={{
                            height: '100%',
                            overflow: 'hidden',
                            p: 2,
                        }}
                    >
                        <DeviceMap
                            devices={mockDevices}
                            selectedDevice={selectedDevice}
                            onDeviceSelect={handleDeviceSelect}
                        />
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

export default Tracking; 
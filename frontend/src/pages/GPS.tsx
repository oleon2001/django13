import React, { useState } from 'react';
import {
    Grid,
    Paper,
    List,
    ListItem,
    ListItemText,
    Typography,
    Box,
    Chip,
} from '@mui/material';
import DeviceMap from '../components/DeviceMap';
import { mockDevices } from '../data/mockData';

const GPS: React.FC = () => {
    const [selectedDevice, setSelectedDevice] = useState(mockDevices[0]);

    const handleDeviceSelect = (device: typeof mockDevices[0]) => {
        setSelectedDevice(device);
    };

    const getStatusChipColor = (status: string) => {
        return status === 'online' ? 'success' : 'error';
    };

    return (
        <Box sx={{ flexGrow: 1, p: 3 }}>
            <Typography variant="h4" gutterBottom component="h1">
                Rastreo de Dispositivos GPS
            </Typography>
            <Grid container spacing={3} sx={{ height: 'calc(100vh - 120px)' }}> {/* Ajustar altura para dejar espacio al AppBar y padding */}
                <Grid item xs={12} md={3} sx={{ height: '100%' }}>
                    <Paper
                        sx={{
                            height: '100%',
                            display: 'flex',
                            flexDirection: 'column',
                            p: 1,
                        }}
                    >
                        <Typography variant="h6" sx={{ my: 2, ml: 1 }}>
                            Dispositivos
                        </Typography>
                        <List dense sx={{ flexGrow: 1, overflowY: 'auto', minHeight: 0 }}>
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

export default GPS; 
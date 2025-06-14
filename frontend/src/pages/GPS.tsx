import React, { useState, useEffect } from 'react';
import {
    Grid,
    Paper,
    List,
    ListItem,
    ListItemText,
    Typography,
    Box,
    Chip,
    Button,
} from '@mui/material';
import DeviceMap from '../components/DeviceMap';
import { mockDevices } from '../data/mockData';
import { coordinateService } from '../services/shared/coordinateService';
import { Device } from '../types';

const GPS: React.FC = () => {
    const [devices, setDevices] = useState<Device[]>(mockDevices);
    const [selectedDevice, setSelectedDevice] = useState<Device | undefined>(undefined);
    const [loading, setLoading] = useState(false);

    const handleDeviceSelect = (device: Device) => {
        setSelectedDevice(device);
    };

    const getStatusChipColor = (status: string) => {
        return status === 'online' ? 'success' : 'error';
    };

    const generateTestData = async () => {
        try {
            setLoading(true);
            await coordinateService.generateTestData();
        } catch (error) {
            console.error('Error generating test data:', error);
        } finally {
            setLoading(false);
        }
    };

    // Suscribirse a actualizaciones de coordenadas
    useEffect(() => {
        // Suscribirse a las actualizaciones
        const unsubscribe = coordinateService.subscribe((updatedDevices) => {
            setDevices(updatedDevices);
            if (updatedDevices.length > 0 && !selectedDevice) {
                setSelectedDevice(updatedDevices[0]);
            }
        });

        // Iniciar actualizaciones automáticas cada 5 segundos
        coordinateService.startAutoUpdate(5000);

        // Limpiar al desmontar
        return () => {
            unsubscribe();
            coordinateService.stopAutoUpdate();
        };
    }, []);

    return (
        <Box sx={{ flexGrow: 1, p: 3, height: 'calc(100vh - 64px)' }}>
            <Typography variant="h4" gutterBottom component="h1">
                Rastreo de Dispositivos GPS
            </Typography>
            <Box sx={{ mb: 2 }}>
                <Button 
                    variant="contained" 
                    onClick={generateTestData}
                    disabled={loading}
                >
                    {loading ? 'Generando...' : 'Generar Nuevos Datos de Prueba'}
                </Button>
            </Box>
            <Grid container spacing={3} sx={{ height: 'calc(100% - 100px)' }}>
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
                            {devices.map((device) => (
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
                <Grid item xs={12} md={9} sx={{ height: '100%' }}>
                    <Paper
                        sx={{
                            height: '100%',
                            overflow: 'hidden',
                            p: 2,
                        }}
                    >
                        <DeviceMap
                            devices={devices}
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
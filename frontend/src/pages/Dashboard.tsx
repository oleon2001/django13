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
    CircularProgress,
    Alert,
} from '@mui/material';
import {
    Speed as SpeedIcon,
    CheckCircleOutline as CheckCircleOutlineIcon,
    WarningAmber as WarningAmberIcon,
} from '@mui/icons-material';
import { deviceService } from '../services/deviceService';
import { Device } from '../types';
import DeviceMap from '../components/DeviceMap';

const Dashboard: React.FC = () => {
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

    const onlineDevices = devices.filter(device => device.connection_status === 'ONLINE');
    const sleepingDevices = devices.filter(device => device.connection_status === 'SLEEPING');

    return (
        <Box p={3}>
            <Grid container spacing={3}>
                <Grid item xs={12}>
                    <Typography variant="h4" gutterBottom>
                        Dashboard
                    </Typography>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Device Status
                            </Typography>
                            <List>
                                <ListItem>
                                    <ListItemIcon>
                                        <CheckCircleOutlineIcon color="success" />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary="Online Devices"
                                        secondary={onlineDevices.length}
                                    />
                                </ListItem>
                                <ListItem>
                                    <ListItemIcon>
                                        <WarningAmberIcon color="warning" />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary="Sleeping Devices"
                                        secondary={sleepingDevices.length}
                                    />
                                </ListItem>
                            </List>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12}>
                    <Paper sx={{ height: 'calc(100vh - 300px)' }}>
                        <DeviceMap
                            devices={devices}
                            selectedDevice={selectedDevice}
                            onDeviceSelect={handleDeviceSelect}
                        />
                    </Paper>
                </Grid>

                <Grid item xs={12}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Active Devices
                            </Typography>
                            <List>
                                {devices.map((device) => (
                                    <React.Fragment key={device.imei}>
                                        <ListItem>
                                            <ListItemIcon>
                                                {device.connection_status === 'ONLINE' ? (
                                                    <CheckCircleOutlineIcon color="success" />
                                                ) : (
                                                    <WarningAmberIcon color="warning" />
                                                )}
                                            </ListItemIcon>
                                            <ListItemText
                                                primary={device.name || `Device ${device.imei}`}
                                                secondary={
                                                    <>
                                                        <Typography component="span" variant="body2">
                                                            IMEI: {device.imei}
                                                        </Typography>
                                                        <br />
                                                        <Typography component="span" variant="body2">
                                                            Last Update: {new Date(device.lastUpdate).toLocaleString()}
                                                        </Typography>
                                                    </>
                                                }
                                            />
                                            <Box>
                                                <Chip
                                                    label={device.connection_status}
                                                    color={device.connection_status === 'ONLINE' ? 'success' : 'warning'}
                                                    size="small"
                                                    sx={{ mr: 1 }}
                                                />
                                                {device.speed !== undefined && (
                                                    <Chip
                                                        icon={<SpeedIcon />}
                                                        label={`${device.speed} km/h`}
                                                        size="small"
                                                    />
                                                )}
                                            </Box>
                                        </ListItem>
                                        <Divider />
                                    </React.Fragment>
                                ))}
                            </List>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
};

export default Dashboard; 
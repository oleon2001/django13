import React, { useState, useEffect, useRef } from 'react';
import {
    Box,
    Grid,
    Paper,
    Typography,
    Card,
    CardContent,
    Chip,
    IconButton,
    Tooltip,
    Alert,
    CircularProgress,
    Divider,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    ListItemSecondaryAction,
    Avatar,
    Badge,
    Switch,
    FormControlLabel,
} from '@mui/material';
import {
    Refresh as RefreshIcon,
    GpsFixed as GpsFixedIcon,
    Speed as SpeedIcon,
    Battery80 as BatteryIcon,
    SignalCellular4Bar as SignalIcon,
    DirectionsCar as CarIcon,
    Warning as WarningIcon,
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
    Visibility as VisibilityIcon,
    PlayArrow as PlayIcon,
    Pause as PauseIcon,
} from '@mui/icons-material';
import { Device } from '../types';
import { deviceService } from '../services/deviceService';
import DeviceMap from '../components/DeviceMap';

const Dashboard: React.FC = () => {
    const [devices, setDevices] = useState<Device[]>([]);
    const [realTimePositions, setRealTimePositions] = useState<any[]>([]);
    const [selectedDevice, setSelectedDevice] = useState<Device | undefined>(undefined);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
    const [isRealTimeEnabled, setIsRealTimeEnabled] = useState(true);
    const stopPollingRef = useRef<(() => void) | null>(null);

    const fetchDevices = async (showRefreshing = false) => {
        try {
            if (showRefreshing) setRefreshing(true);
            else setLoading(true);
            
            const data = await deviceService.getAll();
            setDevices(data);
            setLastUpdate(new Date());
            setError(null);
        } catch (err) {
            setError('Error loading devices');
            console.error('Error loading devices:', err);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        fetchDevices();
    }, []);

    // Real-time polling effect
    useEffect(() => {
        if (isRealTimeEnabled) {
            stopPollingRef.current = deviceService.startRealTimePolling(
                (positions) => {
                    setRealTimePositions(positions);
                    setLastUpdate(new Date());
                    
                    // Update devices with real-time positions
                    setDevices(prevDevices => 
                        prevDevices.map(device => {
                            const realtimePos = positions.find(pos => pos.imei === device.imei);
                            if (realtimePos) {
                                return {
                                    ...device,
                                    latitude: realtimePos.position.latitude,
                                    longitude: realtimePos.position.longitude,
                                    speed: realtimePos.speed,
                                    course: realtimePos.course,
                                    altitude: realtimePos.altitude,
                                    connection_status: realtimePos.connection_status,
                                    lastUpdate: realtimePos.last_update,
                                };
                            }
                            return device;
                        })
                    );
                },
                3000 // Poll every 3 seconds
            );
        } else {
            if (stopPollingRef.current) {
                stopPollingRef.current();
                stopPollingRef.current = null;
            }
        }

        return () => {
            if (stopPollingRef.current) {
                stopPollingRef.current();
            }
        };
    }, [isRealTimeEnabled]);

    const handleDeviceSelect = (device: Device) => {
        setSelectedDevice(device);
    };

    const handleRefresh = () => {
        fetchDevices(true);
    };

    const getStatusIcon = (status: string) => {
        switch (status?.toLowerCase()) {
            case 'online':
                return <CheckCircleIcon color="success" />;
            case 'offline':
                return <ErrorIcon color="error" />;
            default:
                return <WarningIcon color="warning" />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status?.toLowerCase()) {
            case 'online':
                return 'success';
            case 'offline':
                return 'error';
            default:
                return 'warning';
        }
    };

    // Calculate statistics
    const onlineDevices = devices.filter(d => d.connection_status === 'ONLINE').length;
    const offlineDevices = devices.filter(d => d.connection_status === 'OFFLINE').length;
    const totalDevices = devices.length;

    if (loading && !refreshing) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
                <CircularProgress size={60} />
            </Box>
        );
    }

    return (
        <Box sx={{ flexGrow: 1, p: 3, bgcolor: '#f5f5f5', minHeight: '100vh' }}>
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" component="h1" fontWeight="bold">
                        Dashboard GPS
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <FormControlLabel
                        control={
                            <Switch
                                checked={isRealTimeEnabled}
                                onChange={(e) => setIsRealTimeEnabled(e.target.checked)}
                                color="primary"
                            />
                        }
                        label={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                {isRealTimeEnabled ? <PlayIcon color="success" /> : <PauseIcon color="disabled" />}
                                <Typography variant="body2">
                                    {isRealTimeEnabled ? 'En Vivo' : 'Pausado'}
                                </Typography>
                            </Box>
                        }
                    />
                    <Typography variant="body2" color="text.secondary">
                        Última actualización: {lastUpdate.toLocaleTimeString()}
                    </Typography>
                    <Typography variant="body2" color="primary">
                        Activos: {realTimePositions.length}
                    </Typography>
                    <Tooltip title="Actualizar datos">
                        <IconButton 
                            onClick={handleRefresh} 
                            disabled={refreshing}
                            color="primary"
                        >
                            <RefreshIcon sx={{ 
                                animation: refreshing ? 'spin 1s linear infinite' : 'none' 
                            }} />
                        </IconButton>
                    </Tooltip>
                </Box>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            {/* Statistics Cards */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6} md={4}>
                    <Card>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <Box>
                                    <Typography color="textSecondary" gutterBottom variant="body2">
                                        Total Dispositivos
                                    </Typography>
                                    <Typography variant="h4" component="div">
                                        {totalDevices}
                                    </Typography>
                                </Box>
                                <Avatar sx={{ bgcolor: 'primary.main' }}>
                                    <CarIcon />
                                </Avatar>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={4}>
                    <Card>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <Box>
                                    <Typography color="textSecondary" gutterBottom variant="body2">
                                        En Línea
                                    </Typography>
                                    <Typography variant="h4" component="div" color="success.main">
                                        {onlineDevices}
                                    </Typography>
                                </Box>
                                <Avatar sx={{ bgcolor: 'success.main' }}>
                                    <CheckCircleIcon />
                                </Avatar>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={4}>
                    <Card>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <Box>
                                    <Typography color="textSecondary" gutterBottom variant="body2">
                                        Fuera de Línea
                                    </Typography>
                                    <Typography variant="h4" component="div" color="error.main">
                                        {offlineDevices}
                                    </Typography>
                                </Box>
                                <Avatar sx={{ bgcolor: 'error.main' }}>
                                    <ErrorIcon />
                                </Avatar>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Main Content */}
            <Grid container spacing={3}>
                {/* Device List */}
                <Grid item xs={12} md={4}>
                    <Paper sx={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
                        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                            <Typography variant="h6" component="h2">
                                Dispositivos GPS
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                {totalDevices} dispositivos registrados
                            </Typography>
                        </Box>
                        
                        <Box sx={{ flex: 1, overflow: 'auto' }}>
                            {devices.length > 0 ? (
                                <List>
                                    {devices.map((device, index) => (
                                        <React.Fragment key={device.imei}>
                                            <ListItem
                                                button
                                                selected={selectedDevice?.imei === device.imei}
                                                onClick={() => handleDeviceSelect(device)}
                                                sx={{
                                                    '&.Mui-selected': {
                                                        bgcolor: 'primary.light',
                                                        '&:hover': {
                                                            bgcolor: 'primary.light',
                                                        },
                                                    },
                                                }}
                                            >
                                                <ListItemIcon>
                                                    <Badge
                                                        color={getStatusColor(device.connection_status || 'OFFLINE')}
                                                        variant="dot"
                                                    >
                                                        <CarIcon />
                                                    </Badge>
                                                </ListItemIcon>
                                                
                                                <ListItemText
                                                    primary={
                                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                            <Typography variant="subtitle2">
                                                                {device.name || `Device ${device.imei}`}
                                                            </Typography>
                                                            <Chip
                                                                label={device.connection_status || 'OFFLINE'}
                                                                size="small"
                                                                color={getStatusColor(device.connection_status || 'OFFLINE')}
                                                                variant="outlined"
                                                            />
                                                        </Box>
                                                    }
                                                    secondary={
                                                        <Box>
                                                            <Typography variant="caption" display="block">
                                                                IMEI: {device.imei}
                                                            </Typography>
                                                            <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                                    <SpeedIcon fontSize="small" />
                                                                    <Typography variant="caption">
                                                                        {device.speed || 0} km/h
                                                                    </Typography>
                                                                </Box>
                                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                                    <BatteryIcon fontSize="small" />
                                                                    <Typography variant="caption">
                                                                        {device.battery_level || 0}%
                                                                    </Typography>
                                                                </Box>
                                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                                    <SignalIcon fontSize="small" />
                                                                    <Typography variant="caption">
                                                                        {device.signal_strength || 0}%
                                                                    </Typography>
                                                                </Box>
                                                            </Box>
                                                        </Box>
                                                    }
                                                />
                                                
                                                <ListItemSecondaryAction>
                                                    <Tooltip title="Ver en mapa">
                                                        <IconButton
                                                            edge="end"
                                                            onClick={() => handleDeviceSelect(device)}
                                                        >
                                                            <VisibilityIcon />
                                                        </IconButton>
                                                    </Tooltip>
                                                </ListItemSecondaryAction>
                                            </ListItem>
                                            {index < devices.length - 1 && <Divider />}
                                        </React.Fragment>
                                    ))}
                                </List>
                            ) : (
                                <Box sx={{ p: 3, textAlign: 'center' }}>
                                    <GpsFixedIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                                    <Typography variant="h6" color="text.secondary">
                                        No hay dispositivos
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Los dispositivos aparecerán aquí cuando se conecten
                                    </Typography>
                                </Box>
                            )}
                        </Box>
                    </Paper>
                </Grid>

                {/* Map */}
                <Grid item xs={12} md={8}>
                    <Paper sx={{ height: '600px', p: 2 }}>
                        <Box sx={{ height: '100%' }}>
                            <DeviceMap
                                devices={devices}
                                selectedDevice={selectedDevice}
                                onDeviceSelect={handleDeviceSelect}
                            />
                        </Box>
                    </Paper>
                </Grid>
            </Grid>

            {/* Device Details Panel */}
            {selectedDevice && (
                <Paper sx={{ mt: 3, p: 3 }}>
                    <Typography variant="h6" gutterBottom>
                        Detalles del Dispositivo: {selectedDevice.name || `Device ${selectedDevice.imei}`}
                    </Typography>
                    
                    <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                            <List>
                                <ListItem>
                                    <ListItemIcon><CarIcon /></ListItemIcon>
                                    <ListItemText 
                                        primary="IMEI" 
                                        secondary={selectedDevice.imei} 
                                    />
                                </ListItem>
                                <ListItem>
                                    <ListItemIcon><GpsFixedIcon /></ListItemIcon>
                                    <ListItemText
                                        primary="Ubicación" 
                                        secondary={
                                            selectedDevice.position?.latitude && selectedDevice.position?.longitude
                                                ? `${selectedDevice.position.latitude.toFixed(6)}, ${selectedDevice.position.longitude.toFixed(6)}`
                                                : 'No disponible'
                                        }
                                    />
                                </ListItem>
                                <ListItem>
                                    <ListItemIcon><SpeedIcon /></ListItemIcon>
                                    <ListItemText
                                        primary="Velocidad" 
                                        secondary={`${selectedDevice.speed || 0} km/h`} 
                                    />
                                </ListItem>
                            </List>
                </Grid>

                        <Grid item xs={12} md={6}>
                            <List>
                                        <ListItem>
                                    <ListItemIcon><BatteryIcon /></ListItemIcon>
                                            <ListItemText
                                        primary="Batería" 
                                        secondary={`${selectedDevice.battery_level || 0}%`} 
                                    />
                                </ListItem>
                                <ListItem>
                                    <ListItemIcon><SignalIcon /></ListItemIcon>
                                    <ListItemText 
                                        primary="Señal" 
                                        secondary={`${selectedDevice.signal_strength || 0}%`} 
                                    />
                                </ListItem>
                                <ListItem>
                                    <ListItemIcon>{getStatusIcon(selectedDevice.connection_status || 'OFFLINE')}</ListItemIcon>
                                    <ListItemText 
                                        primary="Estado" 
                                        secondary={selectedDevice.connection_status || 'OFFLINE'} 
                                    />
                                        </ListItem>
                            </List>
                </Grid>
            </Grid>
                </Paper>
            )}

            <style>{`
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `}</style>
        </Box>
    );
};

export default Dashboard; 
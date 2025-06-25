import React, { useState, startTransition } from 'react';
import {
    Box,
    Typography,
    Paper,
    Alert,
    Grid,
    Card,
    CardContent,
    IconButton,
    Avatar,
    Tooltip,
    Switch,
    FormControlLabel,
    Chip,
    Divider,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    TextField,
    InputAdornment
} from '@mui/material';
import {
    DirectionsCar as DirectionsCarIcon,
    LocationOn as LocationOnIcon,
    Refresh as RefreshIcon,
    Speed as SpeedIcon,
    Timeline as TimelineIcon,
    Battery80 as BatteryIcon,
    SignalCellular4Bar as SignalIcon,
    Search as SearchIcon
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import DeviceMap from '../components/DeviceMap';
import { Device } from '../types';
import EnhancedLoading from '../components/EnhancedLoading';
import FormLoading from '../components/FormLoading';
import { useRealTimeDevices } from '../hooks/useRealTimeDevices';

const Tracking: React.FC = () => {
    const { t } = useTranslation();
    const [selectedDevice, setSelectedDevice] = useState<Device | undefined>(undefined);
    const [isRealTimeEnabled, setIsRealTimeEnabled] = useState(true);

    // Use the new centralized real-time hook
    const {
        devices,
        loading,
        error,
        lastUpdate,
        forceRefresh
    } = useRealTimeDevices({
        enabled: isRealTimeEnabled,
        componentId: 'tracking',
        onError: (err: Error) => console.error('Tracking real-time error:', err)
    });

    const handleDeviceSelect = (device: Device) => {
        startTransition(() => {
            setSelectedDevice(device);
        });
    };

    const handleRefresh = () => {
        forceRefresh();
    };

    const getStatusColor = (status: string) => {
        switch (status?.toLowerCase()) {
            case 'online':
                return 'success';
            case 'offline':
            case 'error':
                return 'error';
            case 'sleeping':
                return 'warning';
            default:
                return 'default';
        }
    };

    const getSpeedColor = (speed: number) => {
        if (speed > 80) return 'error';
        if (speed > 50) return 'warning';
        if (speed > 0) return 'success';
        return 'default';
    };

    const onlineDevices = devices.filter(d => d.connection_status === 'ONLINE').length;
    const movingDevices = devices.filter(d => d.speed && d.speed > 0).length;
    const totalDevices = devices.length;

    if (loading) {
        return (
            <EnhancedLoading 
                module="tracking" 
                message="Inicializando sistema de rastreo" 
                subMessage="Conectando con dispositivos GPS en tiempo real"
                variant="detailed"
            />
        );
    }

    if (error) {
        return (
            <Box p={3} display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
                <Alert 
                    severity="error" 
                    action={
                        <IconButton onClick={handleRefresh} color="inherit" size="small">
                            <RefreshIcon />
                        </IconButton>
                    }
                >
                    {error}
                </Alert>
            </Box>
        );
    }

    return (
        <Box sx={{ flexGrow: 1, p: 3, backgroundColor: 'background.default' }}>
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                        🎯 {t('tracking.title') || 'Rastreo en Tiempo Real'}
                    </Typography>
                    {lastUpdate && (
                        <Typography variant="body2" color="text.secondary">
                            Última actualización: {lastUpdate.toLocaleTimeString()}
                        </Typography>
                    )}
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <FormControlLabel
                        control={
                            <Switch
                                checked={isRealTimeEnabled}
                                onChange={(event) => setIsRealTimeEnabled(event.target.checked)}
                                color="primary"
                            />
                        }
                        label={isRealTimeEnabled ? "🟢 En Vivo" : "⏸️ Pausado"}
                    />
                    
                    <Tooltip title="Actualizar datos">
                        <IconButton 
                            onClick={handleRefresh} 
                            color="primary"
                            disabled={loading}
                            sx={{
                                backgroundColor: 'primary.light',
                                '&:hover': { backgroundColor: 'primary.main', color: 'white' }
                            }}
                        >
                            <RefreshIcon className={loading ? 'animate-spin' : ''} />
                        </IconButton>
                    </Tooltip>
                </Box>
            </Box>

            {/* Statistics Cards */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3, backgroundColor: 'white', border: '1px solid #e0e0e0' }}>
                        <CardContent sx={{ textAlign: 'center', py: 3 }}>
                            <Avatar sx={{ bgcolor: '#dc2626', mx: 'auto', mb: 2, width: 56, height: 56 }}>
                                <DirectionsCarIcon sx={{ fontSize: 28 }} />
                            </Avatar>
                            <Typography variant="h3" sx={{ fontWeight: 'bold', color: '#1f2937', mb: 1 }}>
                                {totalDevices}
                            </Typography>
                            <Typography variant="body2" sx={{ color: '#6b7280', fontWeight: 500 }}>
                                Total Dispositivos
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3, backgroundColor: 'white', border: '1px solid #e0e0e0' }}>
                        <CardContent sx={{ textAlign: 'center', py: 3 }}>
                            <Avatar sx={{ bgcolor: '#16a34a', mx: 'auto', mb: 2, width: 56, height: 56 }}>
                                <LocationOnIcon sx={{ fontSize: 28 }} />
                            </Avatar>
                            <Typography variant="h3" sx={{ fontWeight: 'bold', color: '#1f2937', mb: 1 }}>
                                {onlineDevices}
                            </Typography>
                            <Typography variant="body2" sx={{ color: '#6b7280', fontWeight: 500 }}>
                                En Línea
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3, backgroundColor: 'white', border: '1px solid #e0e0e0' }}>
                        <CardContent sx={{ textAlign: 'center', py: 3 }}>
                            <Avatar sx={{ bgcolor: '#2563eb', mx: 'auto', mb: 2, width: 56, height: 56 }}>
                                <SpeedIcon sx={{ fontSize: 28 }} />
                            </Avatar>
                            <Typography variant="h3" sx={{ fontWeight: 'bold', color: '#1f2937', mb: 1 }}>
                                {movingDevices}
                            </Typography>
                            <Typography variant="body2" sx={{ color: '#6b7280', fontWeight: 500 }}>
                                En Movimiento
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3, backgroundColor: 'white', border: '1px solid #e0e0e0' }}>
                        <CardContent sx={{ textAlign: 'center', py: 3 }}>
                            <Avatar sx={{ bgcolor: '#059669', mx: 'auto', mb: 2, width: 56, height: 56 }}>
                                <TimelineIcon sx={{ fontSize: 28 }} />
                            </Avatar>
                            <Typography variant="h3" sx={{ fontWeight: 'bold', color: '#1f2937', mb: 1 }}>
                                {Math.round(devices.reduce((sum, d) => sum + (d.speed || 0), 0) / Math.max(devices.length, 1))}
                            </Typography>
                            <Typography variant="body2" sx={{ color: '#6b7280', fontWeight: 500 }}>
                                Velocidad Promedio (km/h)
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            <Grid container spacing={3}>
                {/* Map Section */}
                <Grid item xs={12} lg={8}>
                    <Paper sx={{ borderRadius: 3, boxShadow: 3, position: 'relative' }}>
                        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                                🗺️ Mapa de Rastreo
                            </Typography>
                        </Box>
                        
                        {loading && (
                            <FormLoading 
                                open={loading} 
                                variant="inline" 
                                size="small" 
                                message="Actualizando posiciones..." 
                                action="sync"
                            />
                        )}
                        
                        <Box sx={{ height: '500px', position: 'relative' }}>
                            <DeviceMap
                                devices={devices}
                                selectedDevice={selectedDevice}
                                onDeviceSelect={handleDeviceSelect}
                            />
                        </Box>
                    </Paper>
                </Grid>

                {/* Device Panel */}
                <Grid item xs={12} lg={4}>
                    <Paper sx={{ borderRadius: 3, boxShadow: 3, height: '100%' }}>
                        {/* Filters */}
                        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
                                📡 Dispositivos ({devices.length})
                            </Typography>
                            
                            <TextField
                                fullWidth
                                size="small"
                                placeholder="Buscar dispositivo..."
                                value={''}
                                onChange={() => {}}
                                sx={{ mb: 2 }}
                                InputProps={{
                                    startAdornment: (
                                        <InputAdornment position="start">
                                            <SearchIcon color="action" />
                                        </InputAdornment>
                                    ),
                                }}
                            />
                        </Box>

                        {/* Device List */}
                        <Box sx={{ maxHeight: '400px', overflow: 'auto' }}>
                            <List sx={{ p: 0 }}>
                                {devices.length > 0 ? devices.map((device, index) => (
                                    <React.Fragment key={device.imei}>
                                        <ListItem 
                                            button
                                            onClick={() => handleDeviceSelect(device)}
                                            selected={selectedDevice?.imei === device.imei}
                                            sx={{ 
                                                py: 2,
                                                '&.Mui-selected': {
                                                    backgroundColor: 'primary.light',
                                                    '&:hover': {
                                                        backgroundColor: 'primary.light',
                                                    },
                                                },
                                            }}
                                        >
                                            <ListItemIcon>
                                                <Avatar sx={{ 
                                                    bgcolor: getStatusColor(device.connection_status || 'offline') + '.main',
                                                    width: 32, 
                                                    height: 32 
                                                }}>
                                                    <DirectionsCarIcon fontSize="small" />
                                                </Avatar>
                                            </ListItemIcon>
                                            <ListItemText
                                                primary={
                                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                        <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                                                            {device.name || `Dispositivo ${device.imei}`}
                                                        </Typography>
                                                        <Chip 
                                                            label={device.connection_status || 'OFFLINE'}
                                                            color={getStatusColor(device.connection_status || 'OFFLINE')}
                                                            size="small"
                                                        />
                                                    </Box>
                                                }
                                                secondary={
                                                    <Box sx={{ mt: 1 }}>
                                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                                            <Typography variant="caption" color="text.secondary">
                                                                IMEI: {device.imei}
                                                            </Typography>
                                                            <Chip 
                                                                label={`${device.speed || 0} km/h`}
                                                                color={getSpeedColor(device.speed || 0)}
                                                                size="small"
                                                                variant="outlined"
                                                            />
                                                        </Box>
                                                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                                                            <BatteryIcon fontSize="small" color="action" />
                                                            <Typography variant="caption">
                                                                {device.battery_level || 0}%
                                                            </Typography>
                                                            <SignalIcon fontSize="small" color="action" />
                                                            <Typography variant="caption">
                                                                {device.signal_strength || 0}/5
                                                            </Typography>
                                                        </Box>
                                                    </Box>
                                                }
                                            />
                                        </ListItem>
                                        {index < devices.length - 1 && <Divider />}
                                    </React.Fragment>
                                )) : (
                                    <ListItem>
                                        <ListItemText 
                                            primary="No hay dispositivos disponibles"
                                            secondary="Los dispositivos de rastreo aparecerán aquí"
                                            sx={{ textAlign: 'center', py: 4 }}
                                        />
                                    </ListItem>
                                )}
                            </List>
                        </Box>
                    </Paper>
                </Grid>
            </Grid>

            {/* Device Details Panel */}
            {selectedDevice && (
                <Box sx={{ mt: 3 }}>
                    <Paper sx={{ p: 3, borderRadius: 3, boxShadow: 3 }}>
                        <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
                            📊 Detalles del Dispositivo: {selectedDevice.name || `Dispositivo ${selectedDevice.imei}`}
                        </Typography>
                        
                        <Grid container spacing={3}>
                            <Grid item xs={12} md={6}>
                                <Card sx={{ borderRadius: 2, bgcolor: 'background.default' }}>
                                    <CardContent>
                                        <Typography variant="subtitle2" color="primary" gutterBottom>
                                            Información General
                                        </Typography>
                                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <Typography variant="body2" color="text.secondary">IMEI:</Typography>
                                                <Typography variant="body2" sx={{ fontWeight: 'medium' }}>{selectedDevice.imei}</Typography>
                                            </Box>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <Typography variant="body2" color="text.secondary">Estado:</Typography>
                                                <Chip 
                                                    label={selectedDevice.connection_status || 'OFFLINE'}
                                                    color={getStatusColor(selectedDevice.connection_status || 'OFFLINE')}
                                                    size="small"
                                                />
                                            </Box>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <Typography variant="body2" color="text.secondary">Velocidad:</Typography>
                                                <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                    {selectedDevice.speed || 0} km/h
                                                </Typography>
                                            </Box>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <Typography variant="body2" color="text.secondary">Batería:</Typography>
                                                <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                    {selectedDevice.battery_level || 0}%
                                                </Typography>
                                            </Box>
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Grid>
                            
                            <Grid item xs={12} md={6}>
                                <Card sx={{ borderRadius: 2, bgcolor: 'background.default' }}>
                                    <CardContent>
                                        <Typography variant="subtitle2" color="primary" gutterBottom>
                                            Ubicación y Señal
                                        </Typography>
                                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <Typography variant="body2" color="text.secondary">Latitud:</Typography>
                                                <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                    {selectedDevice.position?.latitude?.toFixed(6) || 'N/A'}
                                                </Typography>
                                            </Box>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <Typography variant="body2" color="text.secondary">Longitud:</Typography>
                                                <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                    {selectedDevice.position?.longitude?.toFixed(6) || 'N/A'}
                                                </Typography>
                                            </Box>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <Typography variant="body2" color="text.secondary">Señal:</Typography>
                                                <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                    {selectedDevice.signal_strength || 0}/5
                                                </Typography>
                                            </Box>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <Typography variant="body2" color="text.secondary">Última actualización:</Typography>
                                                <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                    {selectedDevice.lastUpdate ? new Date(selectedDevice.lastUpdate).toLocaleString() : 'N/A'}
                                                </Typography>
                                            </Box>
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Grid>
                        </Grid>
                    </Paper>
                </Box>
            )}
        </Box>
    );
};

export default Tracking; 
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
    IconButton,
    TextField,
    InputAdornment,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Avatar,
    Divider,
    Stack,
    Badge,
    Switch,
    FormControlLabel,
} from '@mui/material';
import {
    DirectionsCar as DirectionsCarIcon,
    Speed as SpeedIcon,
    LocationOn as LocationOnIcon,
    Battery80 as BatteryIcon,
    SignalCellular4Bar as SignalIcon,
    Refresh as RefreshIcon,
    Search as SearchIcon,
    FilterList as FilterIcon,
    Timeline as TimelineIcon,
    Warning as WarningIcon,
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
} from '@mui/icons-material';
import DeviceMap from '../components/DeviceMap';
import { deviceService } from '../services/deviceService';
import { Device } from '../types';

const Monitoring: React.FC = () => {
    const [devices, setDevices] = useState<Device[]>([]);
    const [filteredDevices, setFilteredDevices] = useState<Device[]>([]);
    const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);
    const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

    useEffect(() => {
        fetchDevices();
        if (autoRefresh) {
            startAutoRefresh();
        }
        return () => {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
        };
    }, [autoRefresh]);

    useEffect(() => {
        filterDevices();
    }, [devices, searchTerm, statusFilter]);

    const startAutoRefresh = () => {
        if (refreshInterval) {
            clearInterval(refreshInterval);
        }
        const interval = setInterval(() => {
            fetchDevices();
        }, 10000); // Update every 10 seconds
        setRefreshInterval(interval);
    };

    const stopAutoRefresh = () => {
        if (refreshInterval) {
            clearInterval(refreshInterval);
            setRefreshInterval(null);
        }
    };

    const fetchDevices = async () => {
        try {
            const data = await deviceService.getAll();
            if (Array.isArray(data)) {
                setDevices(data);
                // Update selected device if it exists in the new data
                if (selectedDevice) {
                    const updatedDevice = data.find(d => d.imei === selectedDevice.imei);
                    if (updatedDevice) {
                        setSelectedDevice(updatedDevice);
                    }
                }
                // Select first device if none selected
                if (!selectedDevice && data.length > 0) {
                    setSelectedDevice(data[0]);
                }
                setError(null);
                setLastUpdate(new Date());
            } else {
                setDevices([]);
                setError('Formato de datos inválido recibido del servidor');
            }
        } catch (err) {
            setError('Error al cargar los dispositivos');
            console.error('Error loading devices:', err);
        } finally {
            setLoading(false);
        }
    };

    const filterDevices = () => {
        let filtered = devices;

        // Filter by search term
        if (searchTerm) {
            filtered = filtered.filter(device =>
                (device.name && device.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
                device.imei.toString().includes(searchTerm)
            );
        }

        // Filter by status
        if (statusFilter !== 'all') {
            filtered = filtered.filter(device => 
                device.connection_status?.toLowerCase() === statusFilter.toLowerCase()
            );
        }

        setFilteredDevices(filtered);
    };

    const handleDeviceSelect = (device: Device) => {
        setSelectedDevice(device);
    };

    const handleRefresh = () => {
        fetchDevices();
    };

    const handleAutoRefreshToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
        setAutoRefresh(event.target.checked);
        if (event.target.checked) {
            startAutoRefresh();
        } else {
            stopAutoRefresh();
        }
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

    const getBatteryColor = (level: number) => {
        if (level > 50) return 'success';
        if (level > 20) return 'warning';
        return 'error';
    };

    const getSignalColor = (strength: number) => {
        if (strength > 70) return 'success';
        if (strength > 40) return 'warning';
        return 'error';
    };

    const onlineDevices = devices.filter(d => d.connection_status === 'ONLINE').length;
    const offlineDevices = devices.filter(d => d.connection_status === 'OFFLINE').length;
    const totalDevices = devices.length;
    const movingDevices = devices.filter(d => d.speed && d.speed > 0).length;

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
                <CircularProgress size={60} />
            </Box>
        );
    }

    return (
        <Box sx={{ flexGrow: 1, p: 3 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                    Monitoreo en Tiempo Real
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                        Última actualización: {lastUpdate.toLocaleTimeString()}
                    </Typography>
                    <FormControlLabel
                        control={
                            <Switch
                                checked={autoRefresh}
                                onChange={handleAutoRefreshToggle}
                                color="primary"
                            />
                        }
                        label="Auto-actualizar"
                    />
                    <IconButton onClick={handleRefresh} color="primary">
                        <RefreshIcon />
                    </IconButton>
                </Box>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                    {error}
                </Alert>
            )}

            {/* Statistics Cards */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'primary.main', mx: 'auto', mb: 1 }}>
                                <DirectionsCarIcon />
                            </Avatar>
                            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                                {totalDevices}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Total Dispositivos
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'success.main', mx: 'auto', mb: 1 }}>
                                <CheckCircleIcon />
                            </Avatar>
                            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                                {onlineDevices}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                En Línea
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'error.main', mx: 'auto', mb: 1 }}>
                                <ErrorIcon />
                            </Avatar>
                            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'error.main' }}>
                                {offlineDevices}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Fuera de Línea
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'info.main', mx: 'auto', mb: 1 }}>
                                <TimelineIcon />
                            </Avatar>
                            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'info.main' }}>
                                {movingDevices}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                En Movimiento
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            <Grid container spacing={3}>
                {/* Map Section */}
                <Grid item xs={12} lg={8}>
                    <Paper sx={{ borderRadius: 3, boxShadow: 2 }}>
                        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                                Mapa de Dispositivos
                            </Typography>
                        </Box>
                        <Box sx={{ height: '500px', position: 'relative' }}>
                            <DeviceMap 
                                devices={filteredDevices}
                                selectedDevice={selectedDevice || undefined}
                                onDeviceSelect={handleDeviceSelect}
                            />
                        </Box>
                    </Paper>
                </Grid>

                {/* Device Panel */}
                <Grid item xs={12} lg={4}>
                    <Paper sx={{ borderRadius: 3, boxShadow: 2, height: '100%' }}>
                        {/* Filters */}
                        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
                                Dispositivos
                            </Typography>
                            <Stack spacing={2}>
                                <TextField
                                    fullWidth
                                    size="small"
                                    placeholder="Buscar dispositivos..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    InputProps={{
                                        startAdornment: (
                                            <InputAdornment position="start">
                                                <SearchIcon color="action" />
                                            </InputAdornment>
                                        ),
                                    }}
                                />
                                <FormControl fullWidth size="small">
                                    <InputLabel>Estado</InputLabel>
                                    <Select
                                        value={statusFilter}
                                        label="Estado"
                                        onChange={(e) => setStatusFilter(e.target.value)}
                                    >
                                        <MenuItem value="all">Todos</MenuItem>
                                        <MenuItem value="online">En Línea</MenuItem>
                                        <MenuItem value="offline">Fuera de Línea</MenuItem>
                                    </Select>
                                </FormControl>
                                <Typography variant="body2" color="text.secondary">
                                    <FilterIcon sx={{ verticalAlign: 'middle', mr: 1, fontSize: 16 }} />
                                    {filteredDevices.length} de {totalDevices} dispositivos
                                </Typography>
                            </Stack>
                        </Box>

                        {/* Device List */}
                        <Box sx={{ height: '400px', overflow: 'auto' }}>
                            <List sx={{ p: 0 }}>
                                {filteredDevices.length > 0 ? filteredDevices.map((device, index) => (
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
                                                <Badge
                                                    overlap="circular"
                                                    anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                                                    badgeContent={getStatusIcon(device.connection_status || 'OFFLINE')}
                                                >
                                                    <Avatar sx={{ bgcolor: 'primary.main' }}>
                                                        <DirectionsCarIcon />
                                                    </Avatar>
                                                </Badge>
                                            </ListItemIcon>
                                            <ListItemText 
                                                primary={
                                                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                                                        {device.name || `Dispositivo ${device.imei}`}
                                                    </Typography>
                                                }
                                                secondary={
                                                    <Stack spacing={0.5}>
                                                        <Typography variant="caption" color="text.secondary">
                                                            IMEI: {device.imei}
                                                        </Typography>
                                                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                                                            <Chip 
                                                                label={device.connection_status || 'OFFLINE'}
                                                                color={getStatusColor(device.connection_status || 'OFFLINE')}
                                                                size="small"
                                                                sx={{ fontSize: '0.7rem', height: 20 }}
                                                            />
                                                            {device.speed !== undefined && (
                                                                <Typography variant="caption" color="text.secondary">
                                                                    {device.speed} km/h
                                                                </Typography>
                                                            )}
                                                        </Box>
                                                    </Stack>
                                                }
                                            />
                                        </ListItem>
                                        {index < filteredDevices.length - 1 && <Divider />}
                                    </React.Fragment>
                                )) : (
                                    <ListItem>
                                        <ListItemText 
                                            primary="No hay dispositivos disponibles"
                                            secondary="Los dispositivos aparecerán aquí cuando se conecten"
                                            sx={{ textAlign: 'center', py: 4 }}
                                        />
                                    </ListItem>
                                )}
                            </List>
                        </Box>
                    </Paper>
                </Grid>

                {/* Device Details */}
                {selectedDevice && (
                    <Grid item xs={12}>
                        <Paper sx={{ p: 3, borderRadius: 3, boxShadow: 2 }}>
                            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
                                Detalles del Dispositivo: {selectedDevice.name || `Dispositivo ${selectedDevice.imei}`}
                            </Typography>
                            
                            <Grid container spacing={3}>
                                <Grid item xs={12} md={6}>
                                    <Card sx={{ borderRadius: 2, bgcolor: 'background.default' }}>
                                        <CardContent>
                                            <Typography variant="subtitle2" color="primary" gutterBottom>
                                                Información General
                                            </Typography>
                                            <Stack spacing={2}>
                                                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                                    <Typography variant="body2" color="text.secondary">
                                                        IMEI:
                                                    </Typography>
                                                    <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                        {selectedDevice.imei}
                                                    </Typography>
                                                </Box>
                                                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                                    <Typography variant="body2" color="text.secondary">
                                                        Estado:
                                                    </Typography>
                                                    <Chip 
                                                        label={selectedDevice.connection_status || 'OFFLINE'}
                                                        color={getStatusColor(selectedDevice.connection_status || 'OFFLINE')}
                                                        size="small"
                                                    />
                                                </Box>
                                                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                                    <Typography variant="body2" color="text.secondary">
                                                        Última actualización:
                                                    </Typography>
                                                    <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                        {selectedDevice.lastUpdate ? 
                                                            new Date(selectedDevice.lastUpdate).toLocaleString() : 
                                                            'N/A'
                                                        }
                                                    </Typography>
                                                </Box>
                                            </Stack>
                                        </CardContent>
                                    </Card>
                                </Grid>

                                <Grid item xs={12} md={6}>
                                    <Card sx={{ borderRadius: 2, bgcolor: 'background.default' }}>
                                        <CardContent>
                                            <Typography variant="subtitle2" color="primary" gutterBottom>
                                                Ubicación y Movimiento
                                            </Typography>
                                            <Stack spacing={2}>
                                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                        <LocationOnIcon color="action" fontSize="small" />
                                                        <Typography variant="body2" color="text.secondary">
                                                            Coordenadas:
                                                        </Typography>
                                                    </Box>
                                                    <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                        {selectedDevice.position?.latitude && selectedDevice.position?.longitude ? 
                                                            `${selectedDevice.position.latitude.toFixed(6)}, ${selectedDevice.position.longitude.toFixed(6)}` : 
                                                            'No disponible'
                                                        }
                                                    </Typography>
                                                </Box>
                                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                        <SpeedIcon color="action" fontSize="small" />
                                                        <Typography variant="body2" color="text.secondary">
                                                            Velocidad:
                                                        </Typography>
                                                    </Box>
                                                    <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                        {selectedDevice.speed || 0} km/h
                                                    </Typography>
                                                </Box>
                                            </Stack>
                                        </CardContent>
                                    </Card>
                                </Grid>

                                <Grid item xs={12} md={6}>
                                    <Card sx={{ borderRadius: 2, bgcolor: 'background.default' }}>
                                        <CardContent>
                                            <Typography variant="subtitle2" color="primary" gutterBottom>
                                                Estado del Dispositivo
                                            </Typography>
                                            <Stack spacing={2}>
                                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                        <BatteryIcon color="action" fontSize="small" />
                                                        <Typography variant="body2" color="text.secondary">
                                                            Batería:
                                                        </Typography>
                                                    </Box>
                                                    <Chip 
                                                        label={`${selectedDevice.battery_level || 0}%`}
                                                        color={getBatteryColor(selectedDevice.battery_level || 0)}
                                                        size="small"
                                                    />
                                                </Box>
                                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                        <SignalIcon color="action" fontSize="small" />
                                                        <Typography variant="body2" color="text.secondary">
                                                            Señal:
                                                        </Typography>
                                                    </Box>
                                                    <Chip 
                                                        label={`${selectedDevice.signal_strength || 0}%`}
                                                        color={getSignalColor(selectedDevice.signal_strength || 0)}
                                                        size="small"
                                                    />
                                                </Box>
                                            </Stack>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            </Grid>
                        </Paper>
                    </Grid>
                )}
            </Grid>
        </Box>
    );
};

export default Monitoring;
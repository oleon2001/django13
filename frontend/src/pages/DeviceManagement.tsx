import React, { useState, useEffect } from 'react';
import {
    Typography,
    Box,
    Grid,
    Card,
    CardContent,
    CardActions,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Button,
    CircularProgress,
    Alert,
    Paper,
    Avatar,
    Chip,
    Divider,
    Stack,
    InputAdornment,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Tooltip,
    Badge,
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    CheckCircleOutline as CheckCircleOutlineIcon,
    ErrorOutline as ErrorOutlineIcon,
    Refresh as RefreshIcon,
    Search as SearchIcon,
    FilterList as FilterIcon,
    DevicesOther as DevicesIcon,
    SignalCellular4Bar as SignalIcon,
    Battery80 as BatteryIcon,
    LocationOn as LocationIcon,
    Speed as SpeedIcon,
    Warning as WarningIcon,
} from '@mui/icons-material';
import { deviceService } from '../services/deviceService';
import { Device } from '../types';
import authService from '../services/auth';

interface DeviceFormData {
    imei: string;
    name: string;
    description: string;
}

const DeviceManagement: React.FC = () => {
    const [devices, setDevices] = useState<Device[]>([]);
    const [filteredDevices, setFilteredDevices] = useState<Device[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [openDialog, setOpenDialog] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [formData, setFormData] = useState<DeviceFormData>({
        imei: '',
        name: '',
        description: '',
    });
    const [editingDevice, setEditingDevice] = useState<Device | null>(null);
    const [testingConnection, setTestingConnection] = useState<number | null>(null);

    useEffect(() => {
        fetchDevices();
        // Auto-refresh every 30 seconds
        const interval = setInterval(fetchDevices, 30000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        filterDevices();
    }, [devices, searchTerm, statusFilter]);

    const fetchDevices = async () => {
        try {
            setLoading(true);
            const data = await deviceService.getAll();
            
            // Ensure data is an array
            if (Array.isArray(data)) {
                setDevices(data);
                setError(null);
            } else {
                console.error('Expected array but received:', data);
                setDevices([]);
                setError('Formato de datos inválido recibido del servidor');
            }
        } catch (err) {
            setError('Error al cargar los dispositivos');
            setDevices([]); // Ensure devices is always an array
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

    const handleOpenDialog = (device?: Device) => {
        if (device) {
            setEditingDevice(device);
            setFormData({
                imei: device.imei.toString(),
                name: device.name || '',
                description: '',
            });
        } else {
            setEditingDevice(null);
            setFormData({
                imei: '',
                name: '',
                description: '',
            });
        }
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setEditingDevice(null);
        setFormData({
            imei: '',
            name: '',
            description: '',
        });
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const deviceData: Partial<Device> = {
                imei: parseInt(formData.imei, 10),
                name: formData.name,
            };

            if (editingDevice) {
                await deviceService.updateDevice(editingDevice.imei, deviceData);
            } else {
                await deviceService.createDevice(deviceData);
            }
            handleCloseDialog();
            fetchDevices();
        } catch (err) {
            console.error('Error saving device:', err);
            setError('Error al guardar el dispositivo');
        }
    };

    const handleDelete = async (imei: number) => {
        if (window.confirm('¿Está seguro de que desea eliminar este dispositivo?')) {
            try {
                // Verificar autenticación
                if (!authService.isAuthenticated()) {
                    setError('Debe iniciar sesión para eliminar dispositivos');
                    window.location.href = '/login';
                    return;
                }

                await deviceService.deleteDevice(imei);
                await fetchDevices(); // Recargar la lista de dispositivos
            } catch (err: any) {
                console.error('Error deleting device:', err);
                if (err.response?.status === 401) {
                    setError('Su sesión ha expirado. Por favor, inicie sesión nuevamente.');
                    window.location.href = '/login';
                } else if (err.response?.status === 403) {
                    setError('No tiene permisos para eliminar dispositivos');
                } else {
                    setError('Error al eliminar el dispositivo: ' + (err.message || 'Error desconocido'));
                }
            }
        }
    };

    const handleTestConnection = async (imei: number) => {
        setTestingConnection(imei);
        try {
            const result = await deviceService.testConnection(imei);
            console.log('Test connection result:', result);
            
            // Actualizar la lista de dispositivos después de la prueba
            await fetchDevices();
            
            // Mostrar mensaje de éxito o error
            if (result.success) {
                setError(null);
                console.log(`✅ Dispositivo ${imei}: ${result.message}`);
            } else {
                setError(`Dispositivo ${imei}: ${result.message || result.error || 'Error desconocido'}`);
            }
        } catch (err: any) {
            console.error('Error testing connection:', err);
            setError(`Error al probar la conexión del dispositivo ${imei}: ${err.response?.data?.error || err.message || 'Error desconocido'}`);
        } finally {
            setTestingConnection(null);
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
                return <CheckCircleOutlineIcon color="success" />;
            case 'offline':
                return <ErrorOutlineIcon color="error" />;
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

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
                <CircularProgress size={60} />
            </Box>
        );
    }

    return (
        <Box p={3}>
            {/* Header */}
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                    Gestión de Dispositivos
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                    <IconButton onClick={fetchDevices} color="primary">
                        <RefreshIcon />
                    </IconButton>
                    <Button
                        variant="contained"
                        color="primary"
                        startIcon={<AddIcon />}
                        onClick={() => handleOpenDialog()}
                        sx={{ borderRadius: 2 }}
                    >
                        Agregar Dispositivo
                    </Button>
                </Box>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                    {error}
                </Alert>
            )}

            {/* Statistics Cards */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6} md={4}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'primary.main', mx: 'auto', mb: 1 }}>
                                <DevicesIcon />
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
                <Grid item xs={12} sm={6} md={4}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'success.main', mx: 'auto', mb: 1 }}>
                                <CheckCircleOutlineIcon />
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
                <Grid item xs={12} sm={6} md={4}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'error.main', mx: 'auto', mb: 1 }}>
                                <ErrorOutlineIcon />
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
            </Grid>

            {/* Filters */}
            <Paper sx={{ p: 2, mb: 3, borderRadius: 2 }}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={6}>
                        <TextField
                            fullWidth
                            placeholder="Buscar por nombre o IMEI..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <SearchIcon color="action" />
                                    </InputAdornment>
                                ),
                            }}
                            sx={{ borderRadius: 2 }}
                        />
                    </Grid>
                    <Grid item xs={12} md={3}>
                        <FormControl fullWidth>
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
                    </Grid>
                    <Grid item xs={12} md={3}>
                        <Typography variant="body2" color="text.secondary">
                            <FilterIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                            {filteredDevices.length} de {totalDevices} dispositivos
                        </Typography>
                    </Grid>
                </Grid>
            </Paper>

            {/* Device Cards */}
            {Array.isArray(filteredDevices) && filteredDevices.length > 0 ? (
                <Grid container spacing={3}>
                    {filteredDevices.map((device) => (
                        <Grid item xs={12} sm={6} md={4} key={device.imei}>
                            <Card sx={{ borderRadius: 3, boxShadow: 2, height: '100%' }}>
                                <CardContent>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <Badge
                                                overlap="circular"
                                                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                                                badgeContent={getStatusIcon(device.connection_status || 'OFFLINE')}
                                            >
                                                <Avatar sx={{ bgcolor: 'primary.main' }}>
                                                    <DevicesIcon />
                                                </Avatar>
                                            </Badge>
                                            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                                                {device.name || `Dispositivo ${device.imei}`}
                                            </Typography>
                                        </Box>
                                        <Chip
                                            label={device.connection_status || 'OFFLINE'}
                                            color={getStatusColor(device.connection_status || 'OFFLINE')}
                                            size="small"
                                            sx={{ borderRadius: 2 }}
                                        />
                                    </Box>
                                    
                                    <Divider sx={{ mb: 2 }} />
                                    
                                    <Stack spacing={1}>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <Typography variant="body2" color="text.secondary">
                                                IMEI:
                                            </Typography>
                                            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                {device.imei}
                                            </Typography>
                                        </Box>
                                        
                                                                {device.position && device.position.latitude && device.position.longitude && (
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                    <LocationIcon color="action" fontSize="small" />
                                    <Typography variant="body2" color="text.secondary">
                                        Ubicación:
                                    </Typography>
                                </Box>
                                <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                    {device.position.latitude.toFixed(4)}, {device.position.longitude.toFixed(4)}
                                </Typography>
                            </Box>
                        )}
                                        
                                        {device.speed !== undefined && (
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                    <SpeedIcon color="action" fontSize="small" />
                                                    <Typography variant="body2" color="text.secondary">
                                                        Velocidad:
                                                    </Typography>
                                                </Box>
                                                <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                    {device.speed} km/h
                                                </Typography>
                                            </Box>
                                        )}
                                        
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                <BatteryIcon color="action" fontSize="small" />
                                                <Typography variant="body2" color="text.secondary">
                                                    Batería:
                                                </Typography>
                                            </Box>
                                            <Chip 
                                                label={`${device.battery_level || 0}%`}
                                                color={getBatteryColor(device.battery_level || 0)}
                                                size="small"
                                            />
                                        </Box>
                                        
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                <SignalIcon color="action" fontSize="small" />
                                                <Typography variant="body2" color="text.secondary">
                                                    Señal:
                                                </Typography>
                                            </Box>
                                            <Chip 
                                                label={`${device.signal_strength || 0}%`}
                                                color={getSignalColor(device.signal_strength || 0)}
                                                size="small"
                                            />
                                        </Box>
                                        
                                                                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="body2" color="text.secondary">
                                Última actualización:
                            </Typography>
                            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                {device.last_heartbeat ? 
                                    new Date(device.last_heartbeat).toLocaleDateString() : 
                                    device.updated_at ? 
                                        new Date(device.updated_at).toLocaleDateString() : 
                                        'N/A'
                                }
                            </Typography>
                        </Box>
                                    </Stack>
                                </CardContent>
                                <CardActions sx={{ justifyContent: 'space-between', p: 2 }}>
                                    <Button
                                        size="small"
                                        onClick={() => handleTestConnection(device.imei)}
                                        disabled={testingConnection === device.imei}
                                        sx={{ borderRadius: 2 }}
                                    >
                                        {testingConnection === device.imei ? (
                                            <CircularProgress size={16} />
                                        ) : (
                                            'Probar Conexión'
                                        )}
                                    </Button>
                                    <Box>
                                        <Tooltip title="Editar">
                                            <IconButton
                                                size="small"
                                                onClick={() => handleOpenDialog(device)}
                                                color="primary"
                                            >
                                                <EditIcon />
                                            </IconButton>
                                        </Tooltip>
                                        <Tooltip title="Eliminar">
                                            <IconButton
                                                size="small"
                                                onClick={() => handleDelete(device.imei)}
                                                color="error"
                                            >
                                                <DeleteIcon />
                                            </IconButton>
                                        </Tooltip>
                                    </Box>
                                </CardActions>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            ) : (
                <Paper sx={{ p: 6, textAlign: 'center', borderRadius: 3 }}>
                    <DevicesIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                        {devices.length === 0 ? 'No hay dispositivos registrados' : 'No se encontraron dispositivos'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        {devices.length === 0 
                            ? 'Haz clic en "Agregar Dispositivo" para crear tu primer dispositivo'
                            : 'Intenta ajustar los filtros de búsqueda.'
                        }
                    </Typography>
                    {devices.length === 0 && (
                        <Button
                            variant="contained"
                            startIcon={<AddIcon />}
                            onClick={() => handleOpenDialog()}
                            sx={{ borderRadius: 2 }}
                        >
                            Agregar Primer Dispositivo
                        </Button>
                    )}
                </Paper>
            )}

            {/* Add/Edit Dialog */}
            <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
                <form onSubmit={handleSubmit}>
                    <DialogTitle sx={{ pb: 1 }}>
                        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                            {editingDevice ? 'Editar Dispositivo' : 'Agregar Nuevo Dispositivo'}
                        </Typography>
                    </DialogTitle>
                    <DialogContent sx={{ pt: 2 }}>
                        <Stack spacing={3}>
                            <TextField
                                autoFocus
                                name="imei"
                                label="IMEI"
                                type="text"
                                fullWidth
                                value={formData.imei}
                                onChange={handleInputChange}
                                required
                                disabled={!!editingDevice}
                                helperText={editingDevice ? "El IMEI no se puede modificar" : "Ingrese el IMEI del dispositivo"}
                            />
                            <TextField
                                name="name"
                                label="Nombre del Dispositivo"
                                type="text"
                                fullWidth
                                value={formData.name}
                                onChange={handleInputChange}
                                helperText="Nombre descriptivo para identificar el dispositivo"
                            />
                            <TextField
                                name="description"
                                label="Descripción"
                                type="text"
                                fullWidth
                                multiline
                                rows={4}
                                value={formData.description}
                                onChange={handleInputChange}
                                helperText="Descripción adicional del dispositivo (opcional)"
                            />
                        </Stack>
                    </DialogContent>
                    <DialogActions sx={{ p: 3, pt: 2 }}>
                        <Button onClick={handleCloseDialog} sx={{ borderRadius: 2 }}>
                            Cancelar
                        </Button>
                        <Button 
                            type="submit" 
                            variant="contained" 
                            color="primary"
                            sx={{ borderRadius: 2 }}
                        >
                            {editingDevice ? 'Guardar Cambios' : 'Agregar Dispositivo'}
                        </Button>
                    </DialogActions>
                </form>
            </Dialog>
        </Box>
    );
};

export default DeviceManagement;
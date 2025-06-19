import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    Chip,
    IconButton,
    CircularProgress,
    Alert,
    TextField,
    InputAdornment,
    Avatar,
    Stack,
    Divider,
} from '@mui/material';
import {
    Person as PersonIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    Phone as PhoneIcon,
    Badge as BadgeIcon,
    Search as SearchIcon,
    Refresh as RefreshIcon,
    GpsFixed as GpsIcon,
    DirectionsCar as CarIcon,
} from '@mui/icons-material';
import { driverService } from '../services/driverService';
import { Driver } from '../types';

const DriverList: React.FC = () => {
    const [drivers, setDrivers] = useState<Driver[]>([]);
    const [filteredDrivers, setFilteredDrivers] = useState<Driver[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchDrivers();
    }, []);

    useEffect(() => {
        filterDrivers();
    }, [drivers, searchTerm]);

    const fetchDrivers = async () => {
        try {
            setLoading(true);
            const data = await driverService.getDrivers();
            setDrivers(data);
            setError(null);
        } catch (err) {
            setError('Error al cargar los conductores');
            console.error('Error loading drivers:', err);
        } finally {
            setLoading(false);
        }
    };

    const filterDrivers = () => {
        let filtered = drivers;

        if (searchTerm) {
            filtered = filtered.filter(driver =>
                driver.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                driver.middle_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                driver.last_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                driver.payroll?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                driver.license?.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        setFilteredDrivers(filtered);
    };

    const handleDelete = async (driverId: number) => {
        if (window.confirm('¿Está seguro de eliminar este conductor?')) {
            try {
                await driverService.deleteDriver(driverId);
                fetchDrivers();
            } catch (err) {
                setError('Error al eliminar el conductor');
            }
        }
    };

    const getStatusColor = (isActive: boolean | undefined) => {
        return isActive ? 'success' : 'error';
    };

    const getLicenseColor = (isValid: boolean | undefined) => {
        return isValid ? 'success' : 'warning';
    };

    const activeDrivers = drivers.filter(d => d.is_active);
    const validLicenses = drivers.filter(d => d.is_license_valid).length;

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                <CircularProgress size={60} />
            </Box>
        );
    }

    return (
        <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                    Conductores ({filteredDrivers.length})
                </Typography>
                <IconButton onClick={fetchDrivers} color="primary">
                    <RefreshIcon />
                </IconButton>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            {/* Statistics */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center', py: 2 }}>
                            <Typography variant="h4" color="primary">
                                {drivers.length}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Total
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center', py: 2 }}>
                            <Typography variant="h4" color="success.main">
                                {activeDrivers.length}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Activos
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center', py: 2 }}>
                            <Typography variant="h4" color="success.main">
                                {validLicenses}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Licencias Válidas
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center', py: 2 }}>
                            <Typography variant="h4" color="error.main">
                                {drivers.length - activeDrivers.length}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Inactivos
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Search */}
            <TextField
                size="small"
                placeholder="Buscar conductores..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                    startAdornment: (
                        <InputAdornment position="start">
                            <SearchIcon />
                        </InputAdornment>
                    ),
                }}
                sx={{ width: '100%', mb: 3 }}
            />

            {/* Driver List */}
            <Card>
                <List sx={{ maxHeight: 400, overflowY: 'auto' }}>
                    {filteredDrivers.map((driver, index) => (
                        <React.Fragment key={driver.id}>
                            <ListItem
                                sx={{ 
                                    alignItems: 'flex-start',
                                    '&:hover': { bgcolor: 'action.hover' }
                                }}
                            >
                                <ListItemIcon>
                                    <Avatar sx={{ bgcolor: driver.is_active ? 'success.main' : 'error.main' }}>
                                        <PersonIcon />
                                    </Avatar>
                                </ListItemIcon>
                                
                                <ListItemText
                                    primary={
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <Typography variant="subtitle1" sx={{ fontWeight: 'medium' }}>
                                                {driver.full_name || `${driver.name} ${driver.middle_name} ${driver.last_name}`}
                                            </Typography>
                                            <Chip 
                                                label={driver.is_active ? 'Activo' : 'Inactivo'}
                                                color={getStatusColor(driver.is_active)}
                                                size="small"
                                            />
                                        </Box>
                                    }
                                    secondary={
                                        <Stack spacing={1} sx={{ mt: 1 }}>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                    <BadgeIcon fontSize="small" />
                                                    <Typography variant="caption">
                                                        {driver.payroll}
                                                    </Typography>
                                                </Box>
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                    <PhoneIcon fontSize="small" />
                                                    <Typography variant="caption">
                                                        {driver.phone}
                                                    </Typography>
                                                </Box>
                                            </Box>
                                            
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                <Typography variant="caption">
                                                    Licencia: {driver.license}
                                                </Typography>
                                                <Chip
                                                    label={driver.is_license_valid ? 'Válida' : 'Vencida'}
                                                    color={getLicenseColor(driver.is_license_valid)}
                                                    size="small"
                                                />
                                            </Box>

                                            {driver.vehicle && (
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    <CarIcon color="primary" fontSize="small" />
                                                    <Typography variant="caption">
                                                        Vehículo: {driver.vehicle.plate}
                                                    </Typography>
                                                </Box>
                                            )}

                                            {driver.device && (
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    <GpsIcon color="success" fontSize="small" />
                                                    <Typography variant="caption">
                                                        GPS: {driver.device.name || 'Conectado'}
                                                    </Typography>
                                                </Box>
                                            )}
                                        </Stack>
                                    }
                                />

                                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                    <IconButton size="small" color="primary">
                                        <EditIcon />
                                    </IconButton>
                                    <IconButton 
                                        size="small" 
                                        color="error"
                                        onClick={() => handleDelete(driver.id)}
                                    >
                                        <DeleteIcon />
                                    </IconButton>
                                </Box>
                            </ListItem>
                            {index < filteredDrivers.length - 1 && <Divider />}
                        </React.Fragment>
                    ))}
                </List>
            </Card>

            {filteredDrivers.length === 0 && !loading && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="h6" color="text.secondary">
                        No se encontraron conductores
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        {searchTerm 
                            ? 'Intenta ajustar los términos de búsqueda'
                            : 'Agrega tu primer conductor para comenzar'
                        }
                    </Typography>
                </Box>
            )}
        </Box>
    );
};

export default DriverList; 
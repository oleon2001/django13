import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    Chip,
    IconButton,
    CircularProgress,
    Alert,
    TextField,
    InputAdornment,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Avatar,
    Stack,
} from '@mui/material';
import {
    Edit as EditIcon,
    Delete as DeleteIcon,
    Search as SearchIcon,
    DirectionsCar as CarIcon,
    GpsFixed as GpsIcon,
    Person as PersonIcon,
    Refresh as RefreshIcon,
} from '@mui/icons-material';
import { vehicleService, Vehicle } from '../services/vehicleService';

const VehicleList: React.FC = () => {
    const [vehicles, setVehicles] = useState<Vehicle[]>([]);
    const [filteredVehicles, setFilteredVehicles] = useState<Vehicle[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');

    useEffect(() => {
        fetchVehicles();
    }, []);

    useEffect(() => {
        filterVehicles();
    }, [vehicles, searchTerm, statusFilter]);

    const fetchVehicles = async () => {
        try {
            setLoading(true);
            const data = await vehicleService.getAll();
            setVehicles(data);
            setError(null);
        } catch (err) {
            setError('Error al cargar los vehículos');
            console.error('Error loading vehicles:', err);
        } finally {
            setLoading(false);
        }
    };

    const filterVehicles = () => {
        let filtered = vehicles;

        if (searchTerm) {
            filtered = filtered.filter(vehicle =>
                vehicle.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                vehicle.plate?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                vehicle.brand?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                vehicle.model?.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        if (statusFilter !== 'all') {
            filtered = filtered.filter(vehicle => vehicle.status === statusFilter);
        }

        setFilteredVehicles(filtered);
    };

    const handleDelete = async (vehicleId: number) => {
        if (window.confirm('¿Está seguro de que desea eliminar este vehículo?')) {
            try {
                await vehicleService.delete(vehicleId);
                fetchVehicles();
            } catch (err) {
                setError('Error al eliminar el vehículo');
            }
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active':
                return 'success';
            case 'maintenance':
                return 'warning';
            case 'inactive':
                return 'error';
            default:
                return 'default';
        }
    };

    const getStatusLabel = (status: string) => {
        switch (status) {
            case 'active':
                return 'Activo';
            case 'maintenance':
                return 'Mantenimiento';
            case 'inactive':
                return 'Inactivo';
            default:
                return status;
        }
    };

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
                    Vehículos ({filteredVehicles.length})
                </Typography>
                <IconButton onClick={fetchVehicles} color="primary">
                    <RefreshIcon />
                </IconButton>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            {/* Filters */}
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                <TextField
                    size="small"
                    placeholder="Buscar vehículos..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <SearchIcon />
                            </InputAdornment>
                        ),
                    }}
                    sx={{ flex: 1 }}
                />
                <FormControl size="small" sx={{ minWidth: 120 }}>
                    <InputLabel>Estado</InputLabel>
                    <Select
                        value={statusFilter}
                        label="Estado"
                        onChange={(e) => setStatusFilter(e.target.value)}
                    >
                        <MenuItem value="all">Todos</MenuItem>
                        <MenuItem value="active">Activo</MenuItem>
                        <MenuItem value="maintenance">Mantenimiento</MenuItem>
                        <MenuItem value="inactive">Inactivo</MenuItem>
                    </Select>
                </FormControl>
            </Box>

            {/* Vehicle Cards */}
            <Grid container spacing={2}>
                {filteredVehicles.map((vehicle) => (
                    <Grid item xs={12} sm={6} md={4} key={vehicle.id}>
                        <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                            <CardContent sx={{ flex: 1 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                    <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                                        <CarIcon />
                                    </Avatar>
                                    <Box sx={{ flex: 1 }}>
                                        <Typography variant="h6" noWrap>
                                            {vehicle.plate || vehicle.name}
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            {vehicle.brand} {vehicle.model} ({vehicle.year})
                                        </Typography>
                                    </Box>
                                </Box>

                                <Stack spacing={1}>
                                    <Chip 
                                        label={getStatusLabel(vehicle.status)} 
                                        color={getStatusColor(vehicle.status)} 
                                        size="small"
                                    />
                                    
                                    {vehicle.device && (
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <GpsIcon color="success" fontSize="small" />
                                            <Typography variant="caption">
                                                GPS: {vehicle.device.name || 'Conectado'}
                                            </Typography>
                                        </Box>
                                    )}
                                    
                                    {vehicle.driver && (
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <PersonIcon color="primary" fontSize="small" />
                                            <Typography variant="caption">
                                                Conductor: {vehicle.driver.name}
                                            </Typography>
                                        </Box>
                                    )}
                                </Stack>
                            </CardContent>

                            <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between' }}>
                                <IconButton size="small" color="primary">
                                    <EditIcon />
                                </IconButton>
                                <IconButton 
                                    size="small" 
                                    color="error"
                                    onClick={() => handleDelete(vehicle.id)}
                                >
                                    <DeleteIcon />
                                </IconButton>
                            </Box>
                        </Card>
                    </Grid>
                ))}
            </Grid>

            {filteredVehicles.length === 0 && !loading && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="h6" color="text.secondary">
                        No se encontraron vehículos
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        {searchTerm || statusFilter !== 'all' 
                            ? 'Intenta ajustar los filtros de búsqueda'
                            : 'Agrega tu primer vehículo para comenzar'
                        }
                    </Typography>
                </Box>
            )}
        </Box>
    );
};

export default VehicleList; 
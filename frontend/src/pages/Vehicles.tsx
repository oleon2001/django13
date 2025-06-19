import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    Grid,
    Card,
    CardContent,
    CardActions,
    Button,
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
    Dialog,
    DialogTitle,
    DialogContent,
    Avatar,
    Divider,
    Stack,
} from '@mui/material';
import {
    Edit as EditIcon,
    Delete as DeleteIcon,
    Search as SearchIcon,
    Add as AddIcon,
    DirectionsCar as CarIcon,
    Speed as SpeedIcon,
    CalendarToday as CalendarIcon,
    LocationOn as LocationIcon,
    Refresh as RefreshIcon,
    FilterList as FilterIcon,
    GpsFixed as GpsIcon,
    Person as PersonIcon,
} from '@mui/icons-material';
import { vehicleService, Vehicle } from '../services/vehicleService';
import { VehicleForm } from '../components/VehicleForm';

const Vehicles: React.FC = () => {
    const [vehicles, setVehicles] = useState<Vehicle[]>([]);
    const [filteredVehicles, setFilteredVehicles] = useState<Vehicle[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [openDialog, setOpenDialog] = useState(false);
    const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);

    useEffect(() => {
        fetchVehicles();
        // Auto-refresh every 30 seconds
        const interval = setInterval(fetchVehicles, 30000);
        return () => clearInterval(interval);
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

        // Filter by search term
        if (searchTerm) {
            filtered = filtered.filter(vehicle =>
                vehicle.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                vehicle.plate.toLowerCase().includes(searchTerm.toLowerCase()) ||
                vehicle.brand.toLowerCase().includes(searchTerm.toLowerCase()) ||
                vehicle.model.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        // Filter by status
        if (statusFilter !== 'all') {
            filtered = filtered.filter(vehicle => vehicle.status === statusFilter);
        }

        setFilteredVehicles(filtered);
    };

    const handleEdit = (vehicle: Vehicle) => {
        setSelectedVehicle(vehicle);
        setOpenDialog(true);
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

    const handleAddNew = () => {
        setSelectedVehicle(null);
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setSelectedVehicle(null);
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

    const activeVehicles = vehicles.filter(v => v.status === 'active').length;
    const maintenanceVehicles = vehicles.filter(v => v.status === 'maintenance').length;
    const inactiveVehicles = vehicles.filter(v => v.status === 'inactive').length;

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
                <CircularProgress size={60} />
            </Box>
        );
    }

    return (
        <Box sx={{ p: 3 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                    Gestión de Vehículos
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                    <IconButton onClick={fetchVehicles} color="primary">
                        <RefreshIcon />
                    </IconButton>
                    <Button
                        variant="contained"
                        startIcon={<AddIcon />}
                        onClick={handleAddNew}
                        sx={{ borderRadius: 2 }}
                    >
                        Agregar Vehículo
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
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'primary.main', mx: 'auto', mb: 1 }}>
                                <CarIcon />
                            </Avatar>
                            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                                {vehicles.length}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Total Vehículos
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'success.main', mx: 'auto', mb: 1 }}>
                                <SpeedIcon />
                            </Avatar>
                            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                                {activeVehicles}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Activos
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'warning.main', mx: 'auto', mb: 1 }}>
                                <CalendarIcon />
                            </Avatar>
                            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'warning.main' }}>
                                {maintenanceVehicles}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Mantenimiento
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'error.main', mx: 'auto', mb: 1 }}>
                                <LocationIcon />
                            </Avatar>
                            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'error.main' }}>
                                {inactiveVehicles}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Inactivos
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
                            placeholder="Buscar por nombre, placa, marca o modelo..."
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
                                <MenuItem value="active">Activos</MenuItem>
                                <MenuItem value="maintenance">Mantenimiento</MenuItem>
                                <MenuItem value="inactive">Inactivos</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} md={3}>
                        <Typography variant="body2" color="text.secondary">
                            <FilterIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                            {filteredVehicles.length} de {vehicles.length} vehículos
                        </Typography>
                    </Grid>
                </Grid>
            </Paper>

            {/* Vehicle Cards */}
            {filteredVehicles.length > 0 ? (
                <Grid container spacing={3}>
                    {filteredVehicles.map((vehicle) => (
                        <Grid item xs={12} sm={6} md={4} key={vehicle.id}>
                            <Card sx={{ borderRadius: 3, boxShadow: 2, height: '100%' }}>
                                <CardContent>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                                        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                                            {vehicle.name}
                                        </Typography>
                                        <Chip
                                            label={getStatusLabel(vehicle.status)}
                                            color={getStatusColor(vehicle.status)}
                                            size="small"
                                            sx={{ borderRadius: 2 }}
                                        />
                                    </Box>
                                    
                                    <Divider sx={{ mb: 2 }} />
                                    
                                    <Stack spacing={1}>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <Typography variant="body2" color="text.secondary">
                                                Placa:
                                            </Typography>
                                            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                {vehicle.plate}
                                            </Typography>
                                        </Box>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <Typography variant="body2" color="text.secondary">
                                                Marca:
                                            </Typography>
                                            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                {vehicle.brand}
                                            </Typography>
                                        </Box>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <Typography variant="body2" color="text.secondary">
                                                Modelo:
                                            </Typography>
                                            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                {vehicle.model}
                                            </Typography>
                                        </Box>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <Typography variant="body2" color="text.secondary">
                                                Año:
                                            </Typography>
                                            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                {vehicle.year}
                                            </Typography>
                                        </Box>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <Typography variant="body2" color="text.secondary">
                                                Última actualización:
                                            </Typography>
                                            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                {new Date(vehicle.lastUpdate).toLocaleDateString()}
                                            </Typography>
                                        </Box>
                                        
                                        <Divider sx={{ my: 1 }} />
                                        
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <GpsIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                                            <Typography variant="body2" color="text.secondary">
                                                GPS:
                                            </Typography>
                                            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                {vehicle.device ? 
                                                    `${vehicle.device.name || `Device ${vehicle.device.imei}`}` : 
                                                    'Sin dispositivo'
                                                }
                                            </Typography>
                                        </Box>
                                        
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <PersonIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                                            <Typography variant="body2" color="text.secondary">
                                                Conductor:
                                            </Typography>
                                            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                {vehicle.driver ? 
                                                    vehicle.driver.full_name : 
                                                    'Sin conductor'
                                                }
                                            </Typography>
                                        </Box>
                                    </Stack>
                                </CardContent>
                                <CardActions sx={{ justifyContent: 'flex-end', p: 2 }}>
                                    <IconButton
                                        size="small"
                                        onClick={() => handleEdit(vehicle)}
                                        color="primary"
                                    >
                                        <EditIcon />
                                    </IconButton>
                                    <IconButton
                                        size="small"
                                        onClick={() => handleDelete(vehicle.id)}
                                        color="error"
                                    >
                                        <DeleteIcon />
                                    </IconButton>
                                </CardActions>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            ) : (
                <Paper sx={{ p: 6, textAlign: 'center', borderRadius: 3 }}>
                    <CarIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                        {vehicles.length === 0 ? 'No hay vehículos registrados' : 'No se encontraron vehículos'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        {vehicles.length === 0 
                            ? 'Los vehículos se pueden asociar a dispositivos GPS cuando estén disponibles.'
                            : 'Intenta ajustar los filtros de búsqueda.'
                        }
                    </Typography>
                    {vehicles.length === 0 && (
                        <Button
                            variant="contained"
                            startIcon={<AddIcon />}
                            onClick={handleAddNew}
                            sx={{ borderRadius: 2 }}
                        >
                            Agregar Primer Vehículo
                        </Button>
                    )}
                </Paper>
            )}

            {/* Add/Edit Dialog */}
            <Dialog open={openDialog} onClose={handleCloseDialog}>
                <DialogTitle>{selectedVehicle ? 'Editar Vehículo' : 'Agregar Vehículo'}</DialogTitle>
                <DialogContent>
                    <VehicleForm
                        initialData={selectedVehicle || undefined}
                        onSave={async (data: Partial<Vehicle>) => {
                            if (selectedVehicle?.id) {
                                await vehicleService.update(selectedVehicle.id, data);
                            } else {
                                await vehicleService.create(data);
                            }
                            fetchVehicles();
                            handleCloseDialog();
                        }}
                        onCancel={handleCloseDialog}
                    />
                </DialogContent>
            </Dialog>
        </Box>
    );
};

export default Vehicles;
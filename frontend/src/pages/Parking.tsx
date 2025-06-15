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
    LinearProgress,
    Chip,
    ListItemIcon,
    Button,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    TextField,
    IconButton,
    Tooltip,
} from '@mui/material';
import {
    LocalParking as ParkingIcon,
    DirectionsCar as CarIcon,
    Search as SearchIcon,
    GetApp as ExportIcon,
    Clear as ClearIcon,
    Refresh as RefreshIcon,
    ViewModule as GridIcon,
} from '@mui/icons-material';
import { parkingService } from '../services/parkingService';
import { CarPark, CarLane, CarSlot } from '../types';

const Parking: React.FC = () => {
    const [carParks, setCarParks] = useState<CarPark[]>([]);
    const [selectedPark, setSelectedPark] = useState<CarPark | null>(null);
    const [carLanes, setCarLanes] = useState<CarLane[]>([]);
    const [selectedLane, setSelectedLane] = useState<CarLane | null>(null);
    const [carSlots, setCarSlots] = useState<CarSlot[]>([]);
    const [searchSerial, setSearchSerial] = useState('');
    const [loading, setLoading] = useState(true);
    const [occupancyData, setOccupancyData] = useState<any>(null);

    useEffect(() => {
        fetchCarParks();
    }, []);

    useEffect(() => {
        if (selectedPark) {
            fetchCarLanes(selectedPark.id);
            fetchOccupancy(selectedPark.id);
        }
    }, [selectedPark]);

    useEffect(() => {
        if (selectedLane) {
            fetchCarSlots(selectedLane.id);
        }
    }, [selectedLane]);

    const fetchCarParks = async () => {
        try {
            setLoading(true);
            const data = await parkingService.getCarParks();
            setCarParks(data);
            if (data.length > 0) {
                setSelectedPark(data[0]);
            }
        } catch (error) {
            console.error('Error fetching car parks:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchCarLanes = async (parkId: number) => {
        try {
            const data = await parkingService.getCarLanes(parkId);
            setCarLanes(data);
            if (data.length > 0) {
                setSelectedLane(data[0]);
            }
        } catch (error) {
            console.error('Error fetching car lanes:', error);
        }
    };

    const fetchCarSlots = async (laneId: number) => {
        try {
            const data = await parkingService.getCarSlots(laneId);
            setCarSlots(data);
        } catch (error) {
            console.error('Error fetching car slots:', error);
        }
    };

    const fetchOccupancy = async (parkId: number) => {
        try {
            const data = await parkingService.getParkOccupancy(parkId);
            setOccupancyData(data);
        } catch (error) {
            console.error('Error fetching occupancy:', error);
        }
    };

    const handleSearchCar = async () => {
        if (!searchSerial.trim()) return;
        
        try {
            const results = await parkingService.searchCarBySerial(searchSerial);
            // Handle search results - could highlight found slots
            console.log('Search results:', results);
        } catch (error) {
            console.error('Error searching car:', error);
        }
    };

    const handleClearLot = async () => {
        if (!selectedPark) return;
        
        if (window.confirm(`¿Está seguro de limpiar todos los espacios del estacionamiento ${selectedPark.name}?`)) {
            try {
                await parkingService.clearLot(selectedPark.id);
                if (selectedLane) {
                    fetchCarSlots(selectedLane.id);
                }
                fetchOccupancy(selectedPark.id);
            } catch (error) {
                console.error('Error clearing lot:', error);
            }
        }
    };

    const handleExportData = async () => {
        if (!selectedPark) return;
        
        try {
            const blob = await parkingService.exportParkData(selectedPark.id);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `parking_${selectedPark.name}_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error exporting data:', error);
        }
    };

    const getOccupancyColor = (percentage: number) => {
        if (percentage > 80) return 'error';
        if (percentage > 60) return 'warning';
        return 'success';
    };

    if (loading) {
        return (
            <Box sx={{ flexGrow: 1, p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <Typography>Cargando estacionamientos...</Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ flexGrow: 1, p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" gutterBottom component="h1">
                    Gestión de Estacionamientos
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                        variant="outlined"
                        startIcon={<RefreshIcon />}
                        onClick={() => selectedPark && fetchOccupancy(selectedPark.id)}
                    >
                        Actualizar
                    </Button>
                    <Button
                        variant="outlined"
                        startIcon={<ExportIcon />}
                        onClick={handleExportData}
                        disabled={!selectedPark}
                    >
                        Exportar
                    </Button>
                    <Button
                        variant="outlined"
                        color="warning"
                        startIcon={<ClearIcon />}
                        onClick={handleClearLot}
                        disabled={!selectedPark}
                    >
                        Limpiar Lote
                    </Button>
                </Box>
            </Box>

            <Grid container spacing={3} sx={{ flexGrow: 1, minHeight: 0 }}>
                {/* Selección de Estacionamiento y Búsqueda */}
                <Grid item xs={12} md={4}>
                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        Selección de Estacionamiento
                                    </Typography>
                                    <FormControl fullWidth sx={{ mb: 2 }}>
                                        <InputLabel>Estacionamiento</InputLabel>
                                        <Select
                                            value={selectedPark?.id || ''}
                                            onChange={(e) => {
                                                const park = carParks.find(p => p.id === e.target.value);
                                                setSelectedPark(park || null);
                                            }}
                                        >
                                            {carParks.map((park) => (
                                                <MenuItem key={park.id} value={park.id}>
                                                    {park.name}
                                                </MenuItem>
                                            ))}
                                        </Select>
                                    </FormControl>
                                    
                                    <FormControl fullWidth sx={{ mb: 2 }}>
                                        <InputLabel>Carril</InputLabel>
                                        <Select
                                            value={selectedLane?.id || ''}
                                            onChange={(e) => {
                                                const lane = carLanes.find(l => l.id === e.target.value);
                                                setSelectedLane(lane || null);
                                            }}
                                        >
                                            {carLanes.map((lane) => (
                                                <MenuItem key={lane.id} value={lane.id}>
                                                    Carril {lane.prefix} ({lane.slot_count} espacios)
                                                </MenuItem>
                                            ))}
                                        </Select>
                                    </FormControl>

                                    <Box sx={{ display: 'flex', gap: 1 }}>
                                        <TextField
                                            fullWidth
                                            label="Buscar por serie"
                                            value={searchSerial}
                                            onChange={(e) => setSearchSerial(e.target.value)}
                                            onKeyPress={(e) => e.key === 'Enter' && handleSearchCar()}
                                        />
                                        <IconButton onClick={handleSearchCar}>
                                            <SearchIcon />
                                        </IconButton>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>

                        {/* Estadísticas de Ocupación */}
                        {occupancyData && (
                            <Grid item xs={12}>
                                <Card>
                                    <CardContent>
                                        <Typography variant="h6" gutterBottom>
                                            Estado de Ocupación
                                        </Typography>
                                        <List>
                                            <ListItem disablePadding>
                                                <ListItemText
                                                    primary="Espacios Ocupados"
                                                    secondary={`${occupancyData.occupied} de ${occupancyData.total}`}
                                                />
                                                <LinearProgress
                                                    variant="determinate"
                                                    value={(occupancyData.occupied / occupancyData.total) * 100}
                                                    color={getOccupancyColor((occupancyData.occupied / occupancyData.total) * 100)}
                                                    sx={{ width: 100, height: 8, borderRadius: 5 }}
                                                />
                                            </ListItem>
                                            <ListItem disablePadding>
                                                <ListItemText
                                                    primary="Porcentaje de Ocupación"
                                                    secondary={`${((occupancyData.occupied / occupancyData.total) * 100).toFixed(1)}%`}
                                                />
                                            </ListItem>
                                            <ListItem disablePadding>
                                                <ListItemText
                                                    primary="Espacios Disponibles"
                                                    secondary={occupancyData.total - occupancyData.occupied}
                                                />
                                            </ListItem>
                                        </List>
                                    </CardContent>
                                </Card>
                            </Grid>
                        )}
                    </Grid>
                </Grid>

                {/* Vista de Grilla de Espacios */}
                <Grid item xs={12} md={8}>
                    <Paper sx={{ height: 500, p: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                            <Typography variant="h6">
                                {selectedLane ? `Carril ${selectedLane.prefix}` : 'Seleccione un carril'}
                            </Typography>
                            <Chip
                                icon={<GridIcon />}
                                label={`${carSlots.length} espacios`}
                                color="primary"
                                variant="outlined"
                            />
                        </Box>
                        
                        <Box sx={{ 
                            display: 'grid', 
                            gridTemplateColumns: 'repeat(auto-fill, minmax(80px, 1fr))',
                            gap: 1,
                            maxHeight: 400,
                            overflowY: 'auto'
                        }}>
                            {carSlots.map((slot) => (
                                <Tooltip 
                                    key={slot.id} 
                                    title={slot.car_serial ? `Serie: ${slot.car_serial}` : 'Espacio libre'}
                                >
                                    <Card 
                                        sx={{ 
                                            minHeight: 60,
                                            backgroundColor: slot.is_occupied ? '#ffebee' : '#e8f5e8',
                                            border: slot.is_occupied ? '1px solid #f44336' : '1px solid #4caf50',
                                            cursor: 'pointer',
                                            '&:hover': {
                                                backgroundColor: slot.is_occupied ? '#ffcdd2' : '#c8e6c9'
                                            }
                                        }}
                                    >
                                        <CardContent sx={{ p: 1, textAlign: 'center' }}>
                                            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                                                <CarIcon 
                                                    fontSize="small" 
                                                    color={slot.is_occupied ? 'error' : 'success'}
                                                />
                                                <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
                                                    {slot.display_name}
                                                </Typography>
                                                {slot.car_serial && (
                                                    <Typography variant="caption" sx={{ fontSize: '0.6rem' }}>
                                                        {slot.car_serial.substring(0, 8)}...
                                                    </Typography>
                                                )}
                                            </Box>
                                        </CardContent>
                                    </Card>
                                </Tooltip>
                            ))}
                        </Box>
                    </Paper>
                </Grid>

                {/* Lista de Carriles */}
                <Grid item xs={12}>
                    <Card sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                        <CardContent sx={{ maxHeight: 300, overflowY: 'auto', display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                            <Typography variant="h6" gutterBottom>
                                Carriles del Estacionamiento
                            </Typography>
                            <List>
                                {carLanes.map((lane) => (
                                    <React.Fragment key={lane.id}>
                                        <ListItem
                                            onClick={() => setSelectedLane(lane)}
                                            sx={{ cursor: 'pointer' }}
                                        >
                                            <ListItemIcon>
                                                <ParkingIcon />
                                            </ListItemIcon>
                                            <ListItemText
                                                primary={`Carril ${lane.prefix}`}
                                                secondary={
                                                    <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                                                        <Chip
                                                            label={`${lane.slot_count} espacios`}
                                                            color="primary"
                                                            size="small"
                                                        />
                                                        <Chip
                                                            label={lane.single ? 'Sencillo' : 'Doble'}
                                                            color="secondary"
                                                            size="small"
                                                        />
                                                    </Box>
                                                }
                                            />
                                        </ListItem>
                                        <Divider variant="inset" component="li" />
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

export default Parking; 
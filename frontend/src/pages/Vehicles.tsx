import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Chip,
    IconButton,
    CircularProgress,
    Alert,
} from '@mui/material';
import {
    Edit as EditIcon,
    Delete as DeleteIcon,
} from '@mui/icons-material';
import { vehicleService, Vehicle } from '../services/vehicleService';

const Vehicles: React.FC = () => {
    const [vehicles, setVehicles] = useState<Vehicle[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchVehicles();
    }, []);

    const fetchVehicles = async () => {
        try {
            setLoading(true);
            const data = await vehicleService.getAll();
            setVehicles(data);
            setError(null);
        } catch (err) {
            setError('Error loading vehicles');
            console.error('Error loading vehicles:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleEdit = (vehicleId: number) => {
        // TODO: Implement edit functionality
        console.log('Edit vehicle:', vehicleId);
    };

    const handleDelete = (vehicleId: number) => {
        // TODO: Implement delete functionality
        console.log('Delete vehicle:', vehicleId);
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

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" gutterBottom>
                Gestión de Vehículos
            </Typography>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Nombre</TableCell>
                            <TableCell>Placa</TableCell>
                            <TableCell>Marca</TableCell>
                            <TableCell>Modelo</TableCell>
                            <TableCell>Año</TableCell>
                            <TableCell>Estado</TableCell>
                            <TableCell>Última Actualización</TableCell>
                            <TableCell>Acciones</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {vehicles.length > 0 ? (
                            vehicles.map((vehicle) => (
                                <TableRow key={vehicle.id}>
                                    <TableCell>{vehicle.name}</TableCell>
                                    <TableCell>{vehicle.plate}</TableCell>
                                    <TableCell>{vehicle.brand}</TableCell>
                                    <TableCell>{vehicle.model}</TableCell>
                                    <TableCell>{vehicle.year}</TableCell>
                                    <TableCell>
                                        <Chip
                                            label={vehicle.status}
                                            color={getStatusColor(vehicle.status)}
                                            size="small"
                                        />
                                    </TableCell>
                                    <TableCell>
                                        {new Date(vehicle.lastUpdate).toLocaleString()}
                                    </TableCell>
                                    <TableCell>
                                        <IconButton
                                            size="small"
                                            onClick={() => handleEdit(vehicle.id)}
                                        >
                                            <EditIcon />
                                        </IconButton>
                                        <IconButton
                                            size="small"
                                            onClick={() => handleDelete(vehicle.id)}
                                        >
                                            <DeleteIcon />
                                        </IconButton>
                                    </TableCell>
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell colSpan={8} align="center">
                                    <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                                        No hay vehículos registrados en este momento.
                                        Los vehículos se pueden asociar a dispositivos GPS cuando estén disponibles.
                                    </Typography>
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
        </Box>
    );
};

export default Vehicles; 
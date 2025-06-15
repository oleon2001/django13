import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    Grid,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    Divider,
    Button,
    TextField,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    IconButton,
    Tooltip,
} from '@mui/material';
import {
    Route as RouteIcon,
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
} from '@mui/icons-material';
import { ROUTE_CHOICES } from '../types';

interface Route {
    id: number;
    name: string;
    description: string;
    startPoint: string;
    endPoint: string;
    distance: number;
    estimatedTime: number;
    active: boolean;
}

const Routes: React.FC = () => {
    const [routes, setRoutes] = useState<Route[]>([]);
    const [openDialog, setOpenDialog] = useState(false);
    const [selectedRoute, setSelectedRoute] = useState<Route | null>(null);
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        startPoint: '',
        endPoint: '',
        distance: 0,
        estimatedTime: 0,
    });

    useEffect(() => {
        // TODO: Implementar la carga de rutas desde el backend
        // Por ahora usamos datos de ejemplo
        const mockRoutes: Route[] = ROUTE_CHOICES.map(route => ({
            id: route.value,
            name: route.label,
            description: `Descripción de ${route.label}`,
            startPoint: 'Punto de inicio',
            endPoint: 'Punto final',
            distance: Math.floor(Math.random() * 100),
            estimatedTime: Math.floor(Math.random() * 120),
            active: true,
        }));
        setRoutes(mockRoutes);
    }, []);

    const handleOpenDialog = (route?: Route) => {
        if (route) {
            setSelectedRoute(route);
            setFormData({
                name: route.name,
                description: route.description,
                startPoint: route.startPoint,
                endPoint: route.endPoint,
                distance: route.distance,
                estimatedTime: route.estimatedTime,
            });
        } else {
            setSelectedRoute(null);
            setFormData({
                name: '',
                description: '',
                startPoint: '',
                endPoint: '',
                distance: 0,
                estimatedTime: 0,
            });
        }
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setSelectedRoute(null);
    };

    const handleSubmit = async () => {
        try {
            if (selectedRoute) {
                // TODO: Implementar actualización de ruta
                console.log('Actualizando ruta:', { ...selectedRoute, ...formData });
            } else {
                // TODO: Implementar creación de ruta
                console.log('Creando nueva ruta:', formData);
            }
            handleCloseDialog();
        } catch (error) {
            console.error('Error al guardar la ruta:', error);
        }
    };

    const handleDelete = async (routeId: number) => {
        try {
            // TODO: Implementar eliminación de ruta
            console.log('Eliminando ruta:', routeId);
        } catch (error) {
            console.error('Error al eliminar la ruta:', error);
        }
    };

    return (
        <Box sx={{ p: 3 }}>
            <Grid container spacing={3}>
                <Grid item xs={12}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                        <Typography variant="h4" component="h1">
                            Gestión de Rutas
                        </Typography>
                        <Button
                            variant="contained"
                            startIcon={<AddIcon />}
                            onClick={() => handleOpenDialog()}
                        >
                            Nueva Ruta
                        </Button>
                    </Box>
                </Grid>
                <Grid item xs={12}>
                    <Paper sx={{ p: 2 }}>
                        <List>
                            {routes.map((route) => (
                                <React.Fragment key={route.id}>
                                    <ListItem
                                        secondaryAction={
                                            <Box>
                                                <Tooltip title="Editar">
                                                    <IconButton
                                                        edge="end"
                                                        onClick={() => handleOpenDialog(route)}
                                                    >
                                                        <EditIcon />
                                                    </IconButton>
                                                </Tooltip>
                                                <Tooltip title="Eliminar">
                                                    <IconButton
                                                        edge="end"
                                                        onClick={() => handleDelete(route.id)}
                                                    >
                                                        <DeleteIcon />
                                                    </IconButton>
                                                </Tooltip>
                                            </Box>
                                        }
                                    >
                                        <ListItemIcon>
                                            <RouteIcon />
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={route.name}
                                            secondary={
                                                <>
                                                    <Typography component="span" variant="body2">
                                                        {route.description}
                                                    </Typography>
                                                    <br />
                                                    <Typography component="span" variant="body2">
                                                        Distancia: {route.distance} km | Tiempo estimado: {route.estimatedTime} min
                                                    </Typography>
                                                </>
                                            }
                                        />
                                    </ListItem>
                                    <Divider />
                                </React.Fragment>
                            ))}
                        </List>
                    </Paper>
                </Grid>
            </Grid>

            <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
                <DialogTitle>
                    {selectedRoute ? 'Editar Ruta' : 'Nueva Ruta'}
                </DialogTitle>
                <DialogContent>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
                        <TextField
                            label="Nombre de la ruta"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            fullWidth
                        />
                        <TextField
                            label="Descripción"
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            fullWidth
                            multiline
                            rows={2}
                        />
                        <TextField
                            label="Punto de inicio"
                            value={formData.startPoint}
                            onChange={(e) => setFormData({ ...formData, startPoint: e.target.value })}
                            fullWidth
                        />
                        <TextField
                            label="Punto final"
                            value={formData.endPoint}
                            onChange={(e) => setFormData({ ...formData, endPoint: e.target.value })}
                            fullWidth
                        />
                        <TextField
                            label="Distancia (km)"
                            type="number"
                            value={formData.distance}
                            onChange={(e) => setFormData({ ...formData, distance: Number(e.target.value) })}
                            fullWidth
                        />
                        <TextField
                            label="Tiempo estimado (minutos)"
                            type="number"
                            value={formData.estimatedTime}
                            onChange={(e) => setFormData({ ...formData, estimatedTime: Number(e.target.value) })}
                            fullWidth
                        />
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>Cancelar</Button>
                    <Button onClick={handleSubmit} variant="contained">
                        {selectedRoute ? 'Actualizar' : 'Crear'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default Routes; 
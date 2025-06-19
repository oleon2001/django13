import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
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
import { routeService, Route as RouteType } from '../services/routeService';

const Routes: React.FC = () => {
    const { t } = useTranslation();
    const [routes, setRoutes] = useState<RouteType[]>([]);
    const [openDialog, setOpenDialog] = useState(false);
    const [selectedRoute, setSelectedRoute] = useState<RouteType | null>(null);
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        startPoint: '',
        endPoint: '',
        distance: 0,
        estimatedTime: 0,
    });

    useEffect(() => {
        fetchRoutes();
    }, []);

    const fetchRoutes = async () => {
        try {
            const data = await routeService.getAll();
            setRoutes(data);
        } catch (error) {
            setRoutes([]);
        }
    };

    const handleOpenDialog = (route?: RouteType) => {
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
                await routeService.update(selectedRoute.id, formData);
            } else {
                await routeService.create(formData);
            }
            handleCloseDialog();
            fetchRoutes();
        } catch (error) {
            console.error('Error al guardar la ruta:', error);
        }
    };

    const handleDelete = async (routeId: number) => {
        if (window.confirm(t('routes.deleteRoute'))) {
            try {
                await routeService.delete(routeId);
                fetchRoutes();
            } catch (error) {
                console.error('Error al eliminar la ruta:', error);
            }
        }
    };

    return (
        <Box sx={{ p: 3 }}>
            <Grid container spacing={3}>
                <Grid item xs={12}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                        <Typography variant="h4" component="h1">
                            {t('routes.title')}
                        </Typography>
                        <Button
                            variant="contained"
                            startIcon={<AddIcon />}
                            onClick={() => handleOpenDialog()}
                        >
                            {t('routes.newRoute')}
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
                                                <Tooltip title={t('routes.edit')}>
                                                    <IconButton
                                                        edge="end"
                                                        onClick={() => handleOpenDialog(route)}
                                                    >
                                                        <EditIcon />
                                                    </IconButton>
                                                </Tooltip>
                                                <Tooltip title={t('routes.delete')}>
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
                                                    {route.description}
                                                    <br />
                                                    <Typography component="span" variant="body2">
                                                        {t('routes.distanceKm', { distance: route.distance })} | {t('routes.estimatedTimeMin', { time: route.estimatedTime })}
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
                    {selectedRoute ? t('routes.editRoute') : t('routes.newRoute')}
                </DialogTitle>
                <DialogContent>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
                        <TextField
                            label={t('routes.routeNameLabel')}
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            fullWidth
                        />
                        <TextField
                            label={t('routes.description')}
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            fullWidth
                            multiline
                            rows={2}
                        />
                        <TextField
                            label={t('routes.startPointLabel')}
                            value={formData.startPoint}
                            onChange={(e) => setFormData({ ...formData, startPoint: e.target.value })}
                            fullWidth
                        />
                        <TextField
                            label={t('routes.endPointLabel')}
                            value={formData.endPoint}
                            onChange={(e) => setFormData({ ...formData, endPoint: e.target.value })}
                            fullWidth
                        />
                        <TextField
                            label={t('routes.distanceKm')}
                            type="number"
                            value={formData.distance}
                            onChange={(e) => setFormData({ ...formData, distance: Number(e.target.value) })}
                            fullWidth
                        />
                        <TextField
                            label={t('routes.estimatedTimeLabel')}
                            type="number"
                            value={formData.estimatedTime}
                            onChange={(e) => setFormData({ ...formData, estimatedTime: Number(e.target.value) })}
                            fullWidth
                        />
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>{t('common.cancel')}</Button>
                    <Button onClick={handleSubmit} variant="contained">
                        {selectedRoute ? t('common.update') : t('common.create')}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default Routes; 
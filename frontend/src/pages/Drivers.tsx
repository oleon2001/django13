import { useState, useEffect } from 'react';
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
    Dialog,
    DialogTitle,
    DialogContent,
    IconButton,
    Tooltip,
    Table,
    TableBody,
    TableCell,
    TableRow,
} from '@mui/material';
import {
    Person as PersonIcon,
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    Badge as BadgeIcon,
    Phone as PhoneIcon,
    GpsFixed as GpsIcon,
    DirectionsCar as CarIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { driverService } from '../services/driverService';
import { Driver } from '../types/unified';
import { DriverForm } from '../components/DriverForm';

export const Drivers = () => {
    const { t } = useTranslation();
    const [drivers, setDrivers] = useState<Driver[]>([]);
    const [selectedDriver, setSelectedDriver] = useState<Driver | null>(null);
    const [openForm, setOpenForm] = useState(false);
    const [editingDriver, setEditingDriver] = useState<Driver | null>(null);
    const [loading, setLoading] = useState(false);

    // Helper functions
    const getFullName = (driver: Driver) => {
        const parts = [driver.name, driver.middle_name, driver.last_name].filter(Boolean);
        return parts.join(' ');
    };

    const isLicenseValid = (driver: Driver) => {
        if (!driver.license_expiry) return false;
        return new Date(driver.license_expiry) > new Date();
    };

    const getDeviceInfo = (driver: Driver) => {
        const vehicleWithDevice = driver.vehicles?.find(vehicle => vehicle.device);
        return vehicleWithDevice ? vehicleWithDevice.device : null;
    };

    useEffect(() => {
        fetchDrivers();
    }, []);

    const fetchDrivers = async () => {
        try {
            setLoading(true);
            const data = await driverService.getDrivers();
            setDrivers(data);
        } catch (error) {
            console.error('Error fetching drivers:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateDriver = () => {
        setEditingDriver(null);
        setOpenForm(true);
    };

    const handleEditDriver = (driver: Driver) => {
        setEditingDriver(driver);
        setOpenForm(true);
    };

    const handleSaveDriver = async (driverData: Partial<Driver>) => {
        try {
            if (editingDriver?.id) {
                await driverService.updateDriver(editingDriver.id, driverData);
            } else {
                await driverService.createDriver(driverData);
            }
            fetchDrivers();
            setOpenForm(false);
            setEditingDriver(null);
        } catch (error) {
            console.error('Error saving driver:', error);
        }
    };

    const handleDeleteDriver = async (id: number) => {
        if (window.confirm('¿Está seguro de eliminar este chofer?')) {
            try {
                await driverService.deleteDriver(id);
                fetchDrivers();
            } catch (error) {
                console.error('Error deleting driver:', error);
            }
        }
    };

    const activeDrivers = drivers.filter(d => d.is_active);
    const validLicenses = drivers.filter(d => isLicenseValid(d)).length;

    const getStatusChipColor = (isActive: boolean) => {
        return isActive ? 'success' : 'default';
    };

    if (loading) {
        return (
            <Box sx={{ flexGrow: 1, p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <Typography>{t('common.loading')}...</Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ flexGrow: 1, p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" gutterBottom component="h1">
                    {t('drivers.title')}
                </Typography>
                <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={handleCreateDriver}
                >
                    {t('drivers.add')}
                </Button>
            </Box>

            <Grid container spacing={3} sx={{ flexGrow: 1, minHeight: 0 }}>
                {/* Estadísticas Generales */}
                <Grid item xs={12} md={4}>
                    <Card sx={{ height: '100%' }}>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                {t('drivers.generalStatus')}
                            </Typography>
                            <List>
                                <ListItem disablePadding>
                                    <ListItemText
                                        primary={t('drivers.activeDrivers')}
                                        secondary={`${activeDrivers.length} ${t('common.of')} ${drivers.length}`}
                                    />
                                    <LinearProgress
                                        variant="determinate"
                                        value={(activeDrivers.length / drivers.length) * 100}
                                        color="success"
                                        sx={{ width: 100, height: 8, borderRadius: 5 }}
                                    />
                                </ListItem>
                                <ListItem disablePadding>
                                    <ListItemText
                                        primary={t('drivers.validLicenses')}
                                        secondary={`${validLicenses} ${t('common.of')} ${drivers.length}`}
                                    />
                                    <LinearProgress
                                        variant="determinate"
                                        value={(validLicenses / drivers.length) * 100}
                                        color="success"
                                        sx={{ width: 100, height: 8, borderRadius: 5 }}
                                    />
                                </ListItem>
                            </List>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Lista de Choferes */}
                <Grid item xs={12} md={8}>
                    <Paper sx={{ height: 500, p: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            {t('drivers.driversList')}
                        </Typography>
                        <Table sx={{ minWidth: 650 }}>
                            <TableBody>
                                {drivers.map((driver) => (
                                    <TableRow 
                                        key={driver.id}
                                        onClick={() => setSelectedDriver(driver)}
                                        sx={{ 
                                            cursor: 'pointer',
                                            '&:hover': {
                                                backgroundColor: 'action.hover'
                                            },
                                            ...(selectedDriver?.id === driver.id && {
                                                backgroundColor: 'action.selected'
                                            })
                                        }}
                                    >
                                        <TableCell>{getFullName(driver)}</TableCell>
                                        <TableCell>{driver.license}</TableCell>
                                        <TableCell>
                                            <Chip
                                                label={driver.is_active ? t('active') : t('inactive')}
                                                color={getStatusChipColor(driver.is_active)}
                                                size="small"
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Box>
                                                <Tooltip title={t('common.edit')}>
                                                    <IconButton onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleEditDriver(driver);
                                                    }}>
                                                        <EditIcon />
                                                    </IconButton>
                                                </Tooltip>
                                                <Tooltip title={t('common.delete')}>
                                                    <IconButton onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleDeleteDriver(driver.id);
                                                    }}>
                                                        <DeleteIcon />
                                                    </IconButton>
                                                </Tooltip>
                                            </Box>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </Paper>
                </Grid>

                {/* Detalles del Chofer Seleccionado */}
                {selectedDriver && (
                    <Grid item xs={12}>
                        <Card sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                            <CardContent sx={{ maxHeight: 300, overflowY: 'auto', display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                                <Typography variant="h6" gutterBottom>
                                    {t('drivers.driverDetails')}: {getFullName(selectedDriver)}
                                </Typography>
                                <Grid container spacing={2}>
                                    <Grid item xs={12} md={6}>
                                        <List dense>
                                            <ListItem>
                                                <ListItemIcon><PersonIcon /></ListItemIcon>
                                                <ListItemText
                                                    primary={t('drivers.fields.payroll')}
                                                    secondary={selectedDriver.payroll}
                                                />
                                            </ListItem>
                                            <ListItem>
                                                <ListItemIcon><BadgeIcon /></ListItemIcon>
                                                <ListItemText
                                                    primary={t('drivers.fields.license')}
                                                    secondary={selectedDriver.license || t('common.notSpecified')}
                                                />
                                            </ListItem>
                                            <ListItem>
                                                <ListItemText
                                                    primary={t('drivers.fields.taxId')}
                                                    secondary={selectedDriver.tax_id}
                                                />
                                            </ListItem>
                                            <ListItem>
                                                <ListItemText
                                                    primary={t('drivers.fields.civilStatus')}
                                                    secondary={selectedDriver.civil_status}
                                                />
                                            </ListItem>
                                        </List>
                                    </Grid>
                                    <Grid item xs={12} md={6}>
                                        <List dense>
                                            <ListItem>
                                                <ListItemIcon><PhoneIcon /></ListItemIcon>
                                                <ListItemText
                                                    primary={t('drivers.fields.phone')}
                                                    secondary={selectedDriver.phone}
                                                />
                                            </ListItem>
                                            <ListItem>
                                                <ListItemText
                                                    primary={t('drivers.fields.birthDate')}
                                                    secondary={selectedDriver.birth_date ? new Date(selectedDriver.birth_date).toLocaleDateString() : t('common.notSpecified')}
                                                />
                                            </ListItem>
                                            <ListItem>
                                                <ListItemText
                                                    primary={t('drivers.fields.socialSecurity')}
                                                    secondary={selectedDriver.social_security}
                                                />
                                            </ListItem>
                                            <ListItem>
                                                <ListItemText
                                                    primary={t('drivers.fields.address')}
                                                    secondary={selectedDriver.address}
                                                />
                                            </ListItem>
                                        </List>
                                    </Grid>
                                </Grid>
                                
                                <Divider sx={{ my: 2 }} />
                                
                                <Typography variant="h6" gutterBottom>
                                    {t('drivers.assignments')}
                                </Typography>
                                
                                <Grid container spacing={2}>
                                    <Grid item xs={12} md={6}>
                                        <List dense>
                                            <ListItem>
                                                <ListItemIcon><GpsIcon /></ListItemIcon>
                                                <ListItemText
                                                    primary={t('drivers.fields.gpsDevice')}
                                                    secondary={
                                                        getDeviceInfo(selectedDriver) ? 
                                                        `${getDeviceInfo(selectedDriver)?.name || `Device ${getDeviceInfo(selectedDriver)?.imei}`} - IMEI: ${getDeviceInfo(selectedDriver)?.imei}` : 
                                                        t('drivers.noDeviceAssigned')
                                                    }
                                                />
                                            </ListItem>
                                        </List>
                                    </Grid>
                                    <Grid item xs={12} md={6}>
                                        <List dense>
                                            <ListItem>
                                                <ListItemIcon><CarIcon /></ListItemIcon>
                                                <ListItemText
                                                    primary={t('drivers.fields.assignedVehicle')}
                                                    secondary={
                                                        selectedDriver.vehicles && selectedDriver.vehicles.length > 0 ? 
                                                        `${selectedDriver.vehicles[0].plate} - ${selectedDriver.vehicles[0].make} ${selectedDriver.vehicles[0].model}` : 
                                                        t('drivers.noVehicleAssigned')
                                                    }
                                                />
                                            </ListItem>
                                        </List>
                                    </Grid>
                                </Grid>
                                <Typography variant="body1">
                                    <strong>{t('vehicles')}:</strong> {selectedDriver.vehicles?.length || 0}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                )}
            </Grid>

            {/* Dialog para Crear/Editar Chofer */}
            <Dialog open={openForm} onClose={() => setOpenForm(false)} maxWidth="md" fullWidth>
                <DialogTitle>
                    {editingDriver?.id ? t('drivers.editDriver') : t('drivers.newDriver')}
                </DialogTitle>
                <DialogContent>
                    <DriverForm
                        initialData={editingDriver || {}}
                        onSave={handleSaveDriver}
                        onCancel={() => setOpenForm(false)}
                    />
                </DialogContent>
            </Dialog>
        </Box>
    );
};

export default Drivers; 
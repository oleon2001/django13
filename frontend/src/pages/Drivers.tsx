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
    Dialog,
    DialogTitle,
    DialogContent,
    IconButton,
    Tooltip,
} from '@mui/material';
import {
    Person as PersonIcon,
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    CheckCircleOutline as CheckIcon,
    ErrorOutline as ErrorIcon,
    Badge as BadgeIcon,
    Phone as PhoneIcon,
    GpsFixed as GpsIcon,
    DirectionsCar as CarIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { driverService } from '../services/driverService';
import { Driver } from '../types';
import { DriverForm } from '../components/DriverForm';

const Drivers: React.FC = () => {
    const { t } = useTranslation();
    const [drivers, setDrivers] = useState<Driver[]>([]);
    const [selectedDriver, setSelectedDriver] = useState<Driver | null>(null);
    const [loading, setLoading] = useState(true);
    const [openDialog, setOpenDialog] = useState(false);
    const [editingDriver, setEditingDriver] = useState<Partial<Driver> | null>(null);

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
        setEditingDriver({
            name: '',
            middle_name: '',
            last_name: '',
            birth_date: '',
            civil_status: 'SOL',
            payroll: '',
            social_security: '',
            tax_id: '',
            license: '',
            address: '',
            phone: '',
            is_active: true
        });
        setOpenDialog(true);
    };

    const handleEditDriver = (driver: Driver) => {
        setEditingDriver(driver);
        setOpenDialog(true);
    };

    const handleSaveDriver = async (driverData: Partial<Driver>) => {
        try {
            if (driverData.id) {
                await driverService.updateDriver(driverData.id, driverData);
            } else {
                await driverService.createDriver(driverData);
            }
            fetchDrivers();
            setOpenDialog(false);
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
    const validLicenses = drivers.filter(d => d.is_license_valid).length;

    const getStatusChipColor = (isActive: boolean | undefined) => {
        return isActive ? 'success' : 'error';
    };

    const getLicenseChipColor = (isValid: boolean | undefined) => {
        return isValid ? 'success' : 'warning';
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
                        <List sx={{ maxHeight: 400, overflowY: 'auto' }}>
                            {drivers.map((driver) => (
                                <React.Fragment key={driver.id}>
                                    <ListItem
                                        onClick={() => setSelectedDriver(driver)}
                                        sx={{ cursor: 'pointer' }}
                                        secondaryAction={
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
                                        }
                                    >
                                        <ListItemIcon>
                                            <PersonIcon />
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={driver.full_name}
                                            secondary={
                                                <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                                                    <Chip
                                                        label={driver.is_active ? t('drivers.status.active') : t('drivers.status.inactive')}
                                                        color={getStatusChipColor(driver.is_active)}
                                                        size="small"
                                                        icon={driver.is_active ? <CheckIcon fontSize="small" /> : <ErrorIcon fontSize="small" />}
                                                    />
                                                    <Chip
                                                        label={driver.is_license_valid ? t('drivers.license.valid') : t('drivers.license.expired')}
                                                        color={getLicenseChipColor(driver.is_license_valid)}
                                                        size="small"
                                                        icon={<BadgeIcon fontSize="small" />}
                                                    />
                                                </Box>
                                            }
                                        />
                                    </ListItem>
                                    <Divider variant="inset" component="li" />
                                </React.Fragment>
                            ))}
                        </List>
                    </Paper>
                </Grid>

                {/* Detalles del Chofer Seleccionado */}
                {selectedDriver && (
                    <Grid item xs={12}>
                        <Card sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                            <CardContent sx={{ maxHeight: 300, overflowY: 'auto', display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                                <Typography variant="h6" gutterBottom>
                                    {t('drivers.driverDetails')}: {selectedDriver.full_name}
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
                                                        selectedDriver.device ? 
                                                        `${selectedDriver.device.name || `Device ${selectedDriver.device.imei}`} - IMEI: ${selectedDriver.device.imei}` : 
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
                                                        selectedDriver.vehicle ? 
                                                        `${selectedDriver.vehicle.name} - ${t('drivers.fields.plate')}: ${selectedDriver.vehicle.plate}` : 
                                                        t('drivers.noVehicleAssigned')
                                                    }
                                                />
                                            </ListItem>
                                        </List>
                                    </Grid>
                                </Grid>
                            </CardContent>
                        </Card>
                    </Grid>
                )}
            </Grid>

            {/* Dialog para Crear/Editar Chofer */}
            <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
                <DialogTitle>
                    {editingDriver?.id ? t('drivers.editDriver') : t('drivers.newDriver')}
                </DialogTitle>
                <DialogContent>
                    <DriverForm
                        initialData={editingDriver || {}}
                        onSave={handleSaveDriver}
                        onCancel={() => setOpenDialog(false)}
                    />
                </DialogContent>
            </Dialog>
        </Box>
    );
};

export default Drivers; 
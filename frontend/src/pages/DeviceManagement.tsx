import React, { useState, useEffect, startTransition } from 'react';
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
import { useTranslation } from 'react-i18next';
import { Device } from '../types';
import authService from '../services/auth';
import { useDeviceStatus } from '../hooks/useDeviceStatus';

interface DeviceFormData {
    imei: string;
    name: string;
    description: string;
}

const DeviceManagement: React.FC = () => {
    const { t } = useTranslation();
    // Usar el hook personalizado para manejo de dispositivos
    const {
        devices,
        loading,
        error,
        stats,
        fetchDevices,
        testDeviceConnection,
        updateDevice,
        createDevice,
        deleteDevice,
        checkAllDevicesStatus,
        setError
    } = useDeviceStatus({
        checkInterval: 30000, // Verificar cada 30 segundos
        heartbeatTimeout: 60000, // 1 minuto para considerar offline
        autoRefresh: true
    });

    const [filteredDevices, setFilteredDevices] = useState<Device[]>([]);
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
    const [checkingAllDevices, setCheckingAllDevices] = useState(false);

    useEffect(() => {
        filterDevices();
    }, [devices, searchTerm, statusFilter]);

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

        startTransition(() => {
            setFilteredDevices(filtered);
        });
    };

    const handleOpenDialog = (device?: Device) => {
        if (device) {
            startTransition(() => {
                setEditingDevice(device);
                setFormData({
                    imei: device.imei.toString(),
                    name: device.name || '',
                    description: '',
                });
            });
        } else {
            startTransition(() => {
                setEditingDevice(null);
                setFormData({
                    imei: '',
                    name: '',
                    description: '',
                });
            });
        }
        startTransition(() => {
            setOpenDialog(true);
        });
    };

    const handleCloseDialog = () => {
        startTransition(() => {
            setOpenDialog(false);
            setEditingDevice(null);
            setFormData({
                imei: '',
                name: '',
                description: '',
            });
        });
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        startTransition(() => {
            setFormData(prev => ({
                ...prev,
                [name]: value
            }));
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const deviceData: Partial<Device> = {
                imei: parseInt(formData.imei, 10),
                name: formData.name,
            };

            if (editingDevice) {
                await updateDevice(editingDevice.imei, deviceData);
            } else {
                await createDevice(deviceData);
            }
            handleCloseDialog();
        } catch (err) {
            console.error('Error saving device:', err);
            startTransition(() => {
                setError(t('errors.saving'));
            });
        }
    };

    const handleDelete = async (imei: number) => {
        if (window.confirm(t('devices.confirmDelete'))) {
            try {
                // Verificar autenticación
                if (!authService.isAuthenticated()) {
                    startTransition(() => {
                        setError(t('auth.loginRequired'));
                    });
                    window.location.href = '/login';
                    return;
                }

                const success = await deleteDevice(imei);
                if (!success) {
                    startTransition(() => {
                        setError(t('errors.deleting'));
                    });
                }
            } catch (err: any) {
                console.error('Error deleting device:', err);
                if (err.response?.status === 401) {
                    startTransition(() => {
                        setError(t('auth.sessionExpired'));
                    });
                    window.location.href = '/login';
                } else if (err.response?.status === 403) {
                    startTransition(() => {
                        setError(t('auth.noPermissions'));
                    });
                } else {
                    startTransition(() => {
                        setError(t('errors.deleting') + ': ' + (err.message || t('errors.unknown')));
                    });
                }
            }
        }
    };

    const handleTestConnection = async (imei: number) => {
        startTransition(() => {
            setTestingConnection(imei);
        });
        
        try {
            const result = await testDeviceConnection(imei);
            console.log('Test connection result:', result);
            
            // Mostrar mensaje de éxito o error
            if (result.success) {
                startTransition(() => {
                    setError(null);
                });
                console.log(`✅ Dispositivo ${imei}: ${result.message}`);
            } else {
                startTransition(() => {
                    setError(result.message || t('errors.testingConnection') + ` ${imei}: ${t('errors.unknown')}`);
                });
            }
        } catch (err: any) {
            console.error('Error testing connection:', err);
            startTransition(() => {
                setError(t('errors.testingConnection') + ` ${imei}: ${err.message || t('errors.unknown')}`);
            });
        } finally {
            startTransition(() => {
                setTestingConnection(null);
            });
        }
    };

    const handleCheckAllDevicesStatus = async () => {
        startTransition(() => {
            setCheckingAllDevices(true);
        });
        
        try {
            const result = await checkAllDevicesStatus(60); // 1 minuto de timeout
            
            if (result.success) {
                if (result.devicesUpdated > 0) {
                    startTransition(() => {
                        setError(null);
                    });
                    console.log(`✅ Verificación completada: ${result.devicesUpdated} dispositivos marcados como offline`);
                } else {
                    startTransition(() => {
                        setError(null);
                    });
                    console.log('✅ Verificación completada: Todos los dispositivos están actualizados');
                }
            } else {
                startTransition(() => {
                    setError(result.message || t('errors.checkingDevices') + `: ${t('errors.unknown')}`);
                });
            }
        } catch (err: any) {
            console.error('Error checking all devices:', err);
            startTransition(() => {
                setError(t('errors.checkingDevices') + `: ${err.message || t('errors.unknown')}`);
            });
        } finally {
            startTransition(() => {
                setCheckingAllDevices(false);
            });
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

    const { total: totalDevices, online: onlineDevices, offline: offlineDevices } = stats;

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
                    {t('deviceManagement.title')}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                    <IconButton onClick={fetchDevices} color="primary">
                        <RefreshIcon />
                    </IconButton>
                    <Button
                        variant="outlined"
                        color="secondary"
                        startIcon={checkingAllDevices ? <CircularProgress size={16} /> : <CheckCircleOutlineIcon />}
                        onClick={handleCheckAllDevicesStatus}
                        disabled={checkingAllDevices}
                        sx={{ borderRadius: 2 }}
                    >
                        {checkingAllDevices ? t('devices.checking') : t('devices.checkAllStatus')}
                    </Button>
                    <Button
                        variant="contained"
                        color="primary"
                        startIcon={<AddIcon />}
                        onClick={() => handleOpenDialog()}
                        sx={{ borderRadius: 2 }}
                    >
                        {t('deviceManagement.addDevice')}
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
                                {t('deviceManagement.totalDevices')}
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
                                {t('deviceManagement.onlineDevices')}
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
                                {t('deviceManagement.offlineDevices')}
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
                            placeholder={t('deviceManagement.searchPlaceholder')}
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
                            <InputLabel>{t('deviceManagement.statusLabel')}</InputLabel>
                            <Select
                                value={statusFilter}
                                label={t('deviceManagement.statusLabel')}
                                onChange={(e) => setStatusFilter(e.target.value)}
                            >
                                <MenuItem value="all">{t('deviceManagement.allDevices')}</MenuItem>
                                <MenuItem value="online">{t('deviceManagement.onlineDevices')}</MenuItem>
                                <MenuItem value="offline">{t('deviceManagement.offlineDevices')}</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} md={3}>
                        <Typography variant="body2" color="text.secondary">
                            <FilterIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                            {filteredDevices.length} {t('common.of')} {totalDevices} {t('devices.title').toLowerCase()}
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
                                                {device.name || `${t('devices.title')} ${device.imei}`}
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
                                        {t('devices.position')}:
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
                                                        {t('devices.speed')}:
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
                                                    {t('devices.battery')}:
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
                                                    {t('devices.signal')}:
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
                                {t('monitoring.lastUpdate')}:
                            </Typography>
                            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                {device.last_heartbeat ? 
                                    new Date(device.last_heartbeat).toLocaleDateString() : 
                                    device.updated_at ? 
                                        new Date(device.updated_at).toLocaleDateString() : 
                                        t('common.notAvailable')
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
                                            t('devices.testConnection')
                                        )}
                                    </Button>
                                    <Box>
                                        <Tooltip title={t('deviceManagement.edit')}>
                                            <IconButton
                                                size="small"
                                                onClick={() => handleOpenDialog(device)}
                                                color="primary"
                                            >
                                                <EditIcon />
                                            </IconButton>
                                        </Tooltip>
                                        <Tooltip title={t('deviceManagement.delete')}>
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
                        {devices.length === 0 ? t('deviceManagement.noDevicesRegistered') : t('deviceManagement.noDevicesFound')}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        {devices.length === 0 
                            ? t('deviceManagement.addFirstDevice')
                            : t('deviceManagement.tryAdjustingFilters')
                        }
                    </Typography>
                    {devices.length === 0 && (
                        <Button
                            variant="contained"
                            startIcon={<AddIcon />}
                            onClick={() => handleOpenDialog()}
                            sx={{ borderRadius: 2 }}
                        >
                            {t('deviceManagement.addFirstDevice')}
                        </Button>
                    )}
                </Paper>
            )}

            {/* Add/Edit Dialog */}
            <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
                <form onSubmit={handleSubmit}>
                    <DialogTitle sx={{ pb: 1 }}>
                        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                            {editingDevice ? t('deviceManagement.editDevice') : t('deviceManagement.addNewDevice')}
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
                                helperText={editingDevice ? t('deviceManagement.imeiCannotBeModified') : t('deviceManagement.enterDeviceImei')}
                            />
                            <TextField
                                name="name"
                                label={t('deviceManagement.deviceName')}
                                type="text"
                                fullWidth
                                value={formData.name}
                                onChange={handleInputChange}
                                helperText={t('deviceManagement.deviceNameDescription')}
                            />
                            <TextField
                                name="description"
                                label={t('deviceManagement.description')}
                                type="text"
                                fullWidth
                                multiline
                                rows={4}
                                value={formData.description}
                                onChange={handleInputChange}
                                helperText={t('deviceManagement.deviceDescriptionOptional')}
                            />
                        </Stack>
                    </DialogContent>
                    <DialogActions sx={{ p: 3, pt: 2 }}>
                        <Button onClick={handleCloseDialog} sx={{ borderRadius: 2 }}>
                            {t('deviceManagement.cancel')}
                        </Button>
                        <Button 
                            type="submit" 
                            variant="contained" 
                            color="primary"
                            sx={{ borderRadius: 2 }}
                        >
                            {editingDevice ? t('deviceManagement.saveChanges') : t('deviceManagement.addDevice')}
                        </Button>
                    </DialogActions>
                </form>
            </Dialog>
        </Box>
    );
};

export default DeviceManagement;
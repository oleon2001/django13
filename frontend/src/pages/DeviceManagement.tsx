import React, { useState, useEffect } from 'react';
import {
    Typography,
    Box,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Button,
    CircularProgress,
    Alert,
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    CheckCircleOutline as CheckCircleOutlineIcon,
    ErrorOutline as ErrorOutlineIcon,
} from '@mui/icons-material';
import { deviceService } from '../services/deviceService';
import { Device } from '../types';

interface DeviceFormData {
    imei: string;
    name: string;
    description: string;
}

const DeviceManagement: React.FC = () => {
    const [devices, setDevices] = useState<Device[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [openDialog, setOpenDialog] = useState(false);
    const [formData, setFormData] = useState<DeviceFormData>({
        imei: '',
        name: '',
        description: '',
    });
    const [editingDevice, setEditingDevice] = useState<Device | null>(null);

    useEffect(() => {
        fetchDevices();
    }, []);

    const fetchDevices = async () => {
        try {
            setLoading(true);
            const data = await deviceService.getAll();
            
            // Ensure data is an array
            if (Array.isArray(data)) {
                setDevices(data);
                setError(null);
            } else {
                console.error('Expected array but received:', data);
                setDevices([]);
                setError('Invalid data format received from server');
            }
        } catch (err) {
            setError('Error loading devices');
            setDevices([]); // Ensure devices is always an array
            console.error('Error loading devices:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleOpenDialog = (device?: Device) => {
        if (device) {
            setEditingDevice(device);
            setFormData({
                imei: device.imei.toString(),
                name: device.name || '',
                description: '',
            });
        } else {
            setEditingDevice(null);
            setFormData({
                imei: '',
                name: '',
                description: '',
            });
        }
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setEditingDevice(null);
        setFormData({
            imei: '',
            name: '',
            description: '',
        });
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const deviceData: Partial<Device> = {
                imei: parseInt(formData.imei, 10),
                name: formData.name,
            };

            if (editingDevice) {
                await deviceService.updateDevice(editingDevice.imei, deviceData);
            } else {
                await deviceService.createDevice(deviceData);
            }
            handleCloseDialog();
            fetchDevices();
        } catch (err) {
            console.error('Error saving device:', err);
            setError('Error saving device');
        }
    };

    const handleDelete = async (imei: number) => {
        if (window.confirm('Are you sure you want to delete this device?')) {
            try {
                await deviceService.deleteDevice(imei);
                fetchDevices();
            } catch (err) {
                console.error('Error deleting device:', err);
                setError('Error deleting device');
            }
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
        <Box p={3}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4">Device Management</Typography>
                <Button
                    variant="contained"
                    color="primary"
                    startIcon={<AddIcon />}
                    onClick={() => handleOpenDialog()}
                >
                    Add Device
                </Button>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            <List>
                {Array.isArray(devices) && devices.length > 0 ? devices.map((device) => (
                    <ListItem
                        key={device.imei}
                        secondaryAction={
                            <Box>
                                <IconButton
                                    edge="end"
                                    aria-label="edit"
                                    onClick={() => handleOpenDialog(device)}
                                    sx={{ mr: 1 }}
                                >
                                    <EditIcon />
                                </IconButton>
                                <IconButton
                                    edge="end"
                                    aria-label="delete"
                                    onClick={() => handleDelete(device.imei)}
                                >
                                    <DeleteIcon />
                                </IconButton>
                            </Box>
                        }
                    >
                        <ListItemIcon>
                            {device.connection_status === 'ONLINE' ? (
                                <CheckCircleOutlineIcon color="success" />
                            ) : (
                                <ErrorOutlineIcon color="error" />
                            )}
                        </ListItemIcon>
                        <ListItemText
                            primary={device.name || `Device ${device.imei}`}
                            secondary={
                                <>
                                    <Typography component="span" variant="body2">
                                        IMEI: {device.imei}
                                    </Typography>
                                    <br />
                                    <Typography component="span" variant="body2">
                                        Status: {device.connection_status}
                                    </Typography>
                                </>
                            }
                        />
                    </ListItem>
                )) : (
                    <ListItem>
                        <ListItemText
                            primary="No devices found"
                            secondary="Click 'Add Device' to create your first device"
                        />
                    </ListItem>
                )}
            </List>

            <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
                <form onSubmit={handleSubmit}>
                    <DialogTitle>
                        {editingDevice ? 'Edit Device' : 'Add New Device'}
                    </DialogTitle>
                    <DialogContent>
                        <TextField
                            autoFocus
                            margin="dense"
                            name="imei"
                            label="IMEI"
                            type="text"
                            fullWidth
                            value={formData.imei}
                            onChange={handleInputChange}
                            required
                            disabled={!!editingDevice}
                        />
                        <TextField
                            margin="dense"
                            name="name"
                            label="Device Name"
                            type="text"
                            fullWidth
                            value={formData.name}
                            onChange={handleInputChange}
                        />
                        <TextField
                            margin="dense"
                            name="description"
                            label="Description"
                            type="text"
                            fullWidth
                            multiline
                            rows={4}
                            value={formData.description}
                            onChange={handleInputChange}
                        />
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleCloseDialog}>Cancel</Button>
                        <Button type="submit" variant="contained" color="primary">
                            {editingDevice ? 'Save Changes' : 'Add Device'}
                        </Button>
                    </DialogActions>
                </form>
            </Dialog>
        </Box>
    );
};

export default DeviceManagement; 
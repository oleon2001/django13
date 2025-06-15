import React, { useState } from 'react';
import {
    Box,
    Typography,
    TextField,
    Button,
    Grid,
    Card,
    Alert,
    Snackbar,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Avatar,
    Divider,
    Paper,
    Stack,
    IconButton,
    InputAdornment,
    Switch,
    FormControlLabel,
    Tabs,
    Tab,
    Chip,
} from '@mui/material';
import {
    Person as PersonIcon,
    Lock as LockIcon,
    Settings as SettingsIcon,
    Notifications as NotificationsIcon,
    Security as SecurityIcon,
    Palette as PaletteIcon,
    Language as LanguageIcon,
    Edit as EditIcon,
    Save as SaveIcon,
    Visibility as VisibilityIcon,
    VisibilityOff as VisibilityOffIcon,
    Email as EmailIcon,
    Phone as PhoneIcon,
    LocationOn as LocationIcon,
} from '@mui/icons-material';
import { SelectChangeEvent } from '@mui/material/Select';
import { SnackbarCloseReason } from '@mui/material/Snackbar';

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

function TabPanel(props: TabPanelProps) {
    const { children, value, index, ...other } = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`settings-tabpanel-${index}`}
            aria-labelledby={`settings-tab-${index}`}
            {...other}
        >
            {value === index && (
                <Box sx={{ p: 3 }}>
                    {children}
                </Box>
            )}
        </div>
    );
}

const mockUser = {
    username: 'admin',
    email: 'admin@skyguard.com',
    fullName: 'Administrador del Sistema',
    phone: '+1 234 567 8900',
    location: 'Ciudad, País',
    avatar: '',
};

const Settings: React.FC = () => {
    const [tabValue, setTabValue] = useState(0);
    const [showPasswords, setShowPasswords] = useState({
        old: false,
        new: false,
        confirm: false,
    });
    const [formData, setFormData] = useState({
        username: mockUser.username,
        email: mockUser.email,
        fullName: mockUser.fullName,
        phone: mockUser.phone,
        location: mockUser.location,
        oldPassword: '',
        newPassword: '',
        confirmPassword: '',
        theme: 'light',
        language: 'es',
        notifications: {
            email: true,
            push: true,
            sms: false,
        },
        privacy: {
            profileVisible: true,
            locationSharing: false,
            dataCollection: true,
        },
    });
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
        setTabValue(newValue);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | SelectChangeEvent<string>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleNotificationChange = (name: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
        setFormData(prev => ({
            ...prev,
            notifications: {
                ...prev.notifications,
                [name]: event.target.checked,
            },
        }));
    };

    const handlePrivacyChange = (name: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
        setFormData(prev => ({
            ...prev,
            privacy: {
                ...prev.privacy,
                [name]: event.target.checked,
            },
        }));
    };

    const handlePasswordVisibilityToggle = (field: 'old' | 'new' | 'confirm') => {
        setShowPasswords(prev => ({
            ...prev,
            [field]: !prev[field],
        }));
    };

    const handleProfileSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);
        // Simular llamada a la API
        setTimeout(() => {
            setSuccess('Perfil actualizado correctamente!');
        }, 500);
    };

    const handlePasswordChangeSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);
        if (formData.newPassword !== formData.confirmPassword) {
            setError('Las nuevas contraseñas no coinciden.');
            return;
        }
        if (formData.newPassword.length < 6) {
            setError('La nueva contraseña debe tener al menos 6 caracteres.');
            return;
        }
        // Simular llamada a la API para cambiar contraseña
        setTimeout(() => {
            setSuccess('Contraseña actualizada correctamente!');
            setFormData(prev => ({
                ...prev,
                oldPassword: '',
                newPassword: '',
                confirmPassword: '',
            }));
        }, 500);
    };

    const handlePreferencesSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);
        // Simular llamada a la API
        setTimeout(() => {
            setSuccess('Preferencias guardadas correctamente!');
        }, 500);
    };

    const handleCloseSnackbar = (_event: React.SyntheticEvent | Event, reason: SnackbarCloseReason) => {
        if (reason === 'clickaway') {
            return;
        }
        setError(null);
        setSuccess(null);
    };

    return (
        <Box sx={{ flexGrow: 1, p: 3 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2, width: 56, height: 56 }}>
                    <SettingsIcon sx={{ fontSize: 32 }} />
                </Avatar>
                <Box>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                        Configuración
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        Gestiona tu perfil, seguridad y preferencias
                    </Typography>
                </Box>
            </Box>

            <Paper sx={{ borderRadius: 3, boxShadow: 2 }}>
                {/* Tabs */}
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={tabValue} onChange={handleTabChange} aria-label="settings tabs">
                        <Tab 
                            icon={<PersonIcon />} 
                            label="Perfil" 
                            iconPosition="start"
                            sx={{ minHeight: 64, textTransform: 'none', fontSize: '1rem' }}
                        />
                        <Tab 
                            icon={<SecurityIcon />} 
                            label="Seguridad" 
                            iconPosition="start"
                            sx={{ minHeight: 64, textTransform: 'none', fontSize: '1rem' }}
                        />
                        <Tab 
                            icon={<PaletteIcon />} 
                            label="Preferencias" 
                            iconPosition="start"
                            sx={{ minHeight: 64, textTransform: 'none', fontSize: '1rem' }}
                        />
                        <Tab 
                            icon={<NotificationsIcon />} 
                            label="Notificaciones" 
                            iconPosition="start"
                            sx={{ minHeight: 64, textTransform: 'none', fontSize: '1rem' }}
                        />
                    </Tabs>
                </Box>

                {/* Profile Tab */}
                <TabPanel value={tabValue} index={0}>
                    <Grid container spacing={4}>
                        <Grid item xs={12} md={4}>
                            <Card sx={{ borderRadius: 3, textAlign: 'center', p: 3 }}>
                                <Avatar
                                    sx={{
                                        width: 120,
                                        height: 120,
                                        mx: 'auto',
                                        mb: 2,
                                        bgcolor: 'primary.main',
                                        fontSize: '3rem',
                                    }}
                                >
                                    {formData.fullName.charAt(0)}
                                </Avatar>
                                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                                    {formData.fullName}
                                </Typography>
                                <Chip label="Administrador" color="primary" size="small" sx={{ mb: 2 }} />
                                <Button
                                    variant="outlined"
                                    startIcon={<EditIcon />}
                                    sx={{ borderRadius: 2 }}
                                >
                                    Cambiar Foto
                                </Button>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={8}>
                            <Card sx={{ borderRadius: 3, p: 3 }}>
                                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
                                    Información Personal
                                </Typography>
                                <form onSubmit={handleProfileSubmit}>
                                    <Grid container spacing={3}>
                                        <Grid item xs={12} sm={6}>
                                            <TextField
                                                fullWidth
                                                label="Nombre Completo"
                                                name="fullName"
                                                value={formData.fullName}
                                                onChange={handleInputChange}
                                                InputProps={{
                                                    startAdornment: (
                                                        <InputAdornment position="start">
                                                            <PersonIcon color="action" />
                                                        </InputAdornment>
                                                    ),
                                                }}
                                                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                                            />
                                        </Grid>
                                        <Grid item xs={12} sm={6}>
                                            <TextField
                                                fullWidth
                                                label="Nombre de Usuario"
                                                name="username"
                                                value={formData.username}
                                                onChange={handleInputChange}
                                                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                                            />
                                        </Grid>
                                        <Grid item xs={12} sm={6}>
                                            <TextField
                                                fullWidth
                                                label="Correo Electrónico"
                                                name="email"
                                                type="email"
                                                value={formData.email}
                                                onChange={handleInputChange}
                                                InputProps={{
                                                    startAdornment: (
                                                        <InputAdornment position="start">
                                                            <EmailIcon color="action" />
                                                        </InputAdornment>
                                                    ),
                                                }}
                                                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                                            />
                                        </Grid>
                                        <Grid item xs={12} sm={6}>
                                            <TextField
                                                fullWidth
                                                label="Teléfono"
                                                name="phone"
                                                value={formData.phone}
                                                onChange={handleInputChange}
                                                InputProps={{
                                                    startAdornment: (
                                                        <InputAdornment position="start">
                                                            <PhoneIcon color="action" />
                                                        </InputAdornment>
                                                    ),
                                                }}
                                                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                                            />
                                        </Grid>
                                        <Grid item xs={12}>
                                            <TextField
                                                fullWidth
                                                label="Ubicación"
                                                name="location"
                                                value={formData.location}
                                                onChange={handleInputChange}
                                                InputProps={{
                                                    startAdornment: (
                                                        <InputAdornment position="start">
                                                            <LocationIcon color="action" />
                                                        </InputAdornment>
                                                    ),
                                                }}
                                                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                                            />
                                        </Grid>
                                    </Grid>
                                    <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                                        <Button 
                                            type="submit" 
                                            variant="contained" 
                                            startIcon={<SaveIcon />}
                                            sx={{ borderRadius: 2, px: 4 }}
                                        >
                                            Guardar Cambios
                                        </Button>
                                    </Box>
                                </form>
                            </Card>
                        </Grid>
                    </Grid>
                </TabPanel>

                {/* Security Tab */}
                <TabPanel value={tabValue} index={1}>
                    <Grid container spacing={4}>
                        <Grid item xs={12} md={6}>
                            <Card sx={{ borderRadius: 3, p: 3 }}>
                                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
                                    Cambiar Contraseña
                                </Typography>
                                <form onSubmit={handlePasswordChangeSubmit}>
                                    <Stack spacing={3}>
                                        <TextField
                                            fullWidth
                                            label="Contraseña Actual"
                                            name="oldPassword"
                                            type={showPasswords.old ? 'text' : 'password'}
                                            value={formData.oldPassword}
                                            onChange={handleInputChange}
                                            InputProps={{
                                                startAdornment: (
                                                    <InputAdornment position="start">
                                                        <LockIcon color="action" />
                                                    </InputAdornment>
                                                ),
                                                endAdornment: (
                                                    <InputAdornment position="end">
                                                        <IconButton
                                                            onClick={() => handlePasswordVisibilityToggle('old')}
                                                            edge="end"
                                                        >
                                                            {showPasswords.old ? <VisibilityOffIcon /> : <VisibilityIcon />}
                                                        </IconButton>
                                                    </InputAdornment>
                                                ),
                                            }}
                                            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                                        />
                                        <TextField
                                            fullWidth
                                            label="Nueva Contraseña"
                                            name="newPassword"
                                            type={showPasswords.new ? 'text' : 'password'}
                                            value={formData.newPassword}
                                            onChange={handleInputChange}
                                            InputProps={{
                                                startAdornment: (
                                                    <InputAdornment position="start">
                                                        <LockIcon color="action" />
                                                    </InputAdornment>
                                                ),
                                                endAdornment: (
                                                    <InputAdornment position="end">
                                                        <IconButton
                                                            onClick={() => handlePasswordVisibilityToggle('new')}
                                                            edge="end"
                                                        >
                                                            {showPasswords.new ? <VisibilityOffIcon /> : <VisibilityIcon />}
                                                        </IconButton>
                                                    </InputAdornment>
                                                ),
                                            }}
                                            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                                        />
                                        <TextField
                                            fullWidth
                                            label="Confirmar Contraseña"
                                            name="confirmPassword"
                                            type={showPasswords.confirm ? 'text' : 'password'}
                                            value={formData.confirmPassword}
                                            onChange={handleInputChange}
                                            error={formData.newPassword !== formData.confirmPassword && formData.confirmPassword !== ''}
                                            helperText={formData.newPassword !== formData.confirmPassword && formData.confirmPassword !== '' ? 'Las contraseñas no coinciden' : ''}
                                            InputProps={{
                                                startAdornment: (
                                                    <InputAdornment position="start">
                                                        <LockIcon color="action" />
                                                    </InputAdornment>
                                                ),
                                                endAdornment: (
                                                    <InputAdornment position="end">
                                                        <IconButton
                                                            onClick={() => handlePasswordVisibilityToggle('confirm')}
                                                            edge="end"
                                                        >
                                                            {showPasswords.confirm ? <VisibilityOffIcon /> : <VisibilityIcon />}
                                                        </IconButton>
                                                    </InputAdornment>
                                                ),
                                            }}
                                            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                                        />
                                    </Stack>
                                    <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                                        <Button 
                                            type="submit" 
                                            variant="contained" 
                                            startIcon={<SaveIcon />}
                                            sx={{ borderRadius: 2, px: 4 }}
                                        >
                                            Cambiar Contraseña
                                        </Button>
                                    </Box>
                                </form>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Card sx={{ borderRadius: 3, p: 3 }}>
                                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
                                    Configuración de Privacidad
                                </Typography>
                                <Stack spacing={2}>
                                    <FormControlLabel
                                        control={
                                            <Switch
                                                checked={formData.privacy.profileVisible}
                                                onChange={handlePrivacyChange('profileVisible')}
                                                color="primary"
                                            />
                                        }
                                        label="Perfil visible para otros usuarios"
                                    />
                                    <FormControlLabel
                                        control={
                                            <Switch
                                                checked={formData.privacy.locationSharing}
                                                onChange={handlePrivacyChange('locationSharing')}
                                                color="primary"
                                            />
                                        }
                                        label="Compartir ubicación"
                                    />
                                    <FormControlLabel
                                        control={
                                            <Switch
                                                checked={formData.privacy.dataCollection}
                                                onChange={handlePrivacyChange('dataCollection')}
                                                color="primary"
                                            />
                                        }
                                        label="Permitir recopilación de datos para mejoras"
                                    />
                                </Stack>
                            </Card>
                        </Grid>
                    </Grid>
                </TabPanel>

                {/* Preferences Tab */}
                <TabPanel value={tabValue} index={2}>
                    <Card sx={{ borderRadius: 3, p: 3 }}>
                        <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
                            Preferencias de la Aplicación
                        </Typography>
                        <form onSubmit={handlePreferencesSubmit}>
                            <Grid container spacing={3}>
                                <Grid item xs={12} sm={6}>
                                    <FormControl fullWidth>
                                        <InputLabel id="theme-label">Tema</InputLabel>
                                        <Select
                                            labelId="theme-label"
                                            id="theme"
                                            name="theme"
                                            value={formData.theme}
                                            label="Tema"
                                            onChange={handleInputChange}
                                            startAdornment={
                                                <InputAdornment position="start">
                                                    <PaletteIcon color="action" />
                                                </InputAdornment>
                                            }
                                            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                                        >
                                            <MenuItem value="light">Claro</MenuItem>
                                            <MenuItem value="dark">Oscuro</MenuItem>
                                            <MenuItem value="auto">Automático</MenuItem>
                                        </Select>
                                    </FormControl>
                                </Grid>
                                <Grid item xs={12} sm={6}>
                                    <FormControl fullWidth>
                                        <InputLabel id="language-label">Idioma</InputLabel>
                                        <Select
                                            labelId="language-label"
                                            id="language"
                                            name="language"
                                            value={formData.language}
                                            label="Idioma"
                                            onChange={handleInputChange}
                                            startAdornment={
                                                <InputAdornment position="start">
                                                    <LanguageIcon color="action" />
                                                </InputAdornment>
                                            }
                                            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                                        >
                                            <MenuItem value="es">Español</MenuItem>
                                            <MenuItem value="en">Inglés</MenuItem>
                                            <MenuItem value="pt">Português</MenuItem>
                                        </Select>
                                    </FormControl>
                                </Grid>
                            </Grid>
                            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                                <Button 
                                    type="submit" 
                                    variant="contained" 
                                    startIcon={<SaveIcon />}
                                    sx={{ borderRadius: 2, px: 4 }}
                                >
                                    Guardar Preferencias
                                </Button>
                            </Box>
                        </form>
                    </Card>
                </TabPanel>

                {/* Notifications Tab */}
                <TabPanel value={tabValue} index={3}>
                    <Card sx={{ borderRadius: 3, p: 3 }}>
                        <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
                            Configuración de Notificaciones
                        </Typography>
                        <Stack spacing={3}>
                            <Box>
                                <Typography variant="subtitle1" sx={{ fontWeight: 'medium', mb: 2 }}>
                                    Tipos de Notificaciones
                                </Typography>
                                <Stack spacing={2}>
                                    <FormControlLabel
                                        control={
                                            <Switch
                                                checked={formData.notifications.email}
                                                onChange={handleNotificationChange('email')}
                                                color="primary"
                                            />
                                        }
                                        label="Notificaciones por correo electrónico"
                                    />
                                    <FormControlLabel
                                        control={
                                            <Switch
                                                checked={formData.notifications.push}
                                                onChange={handleNotificationChange('push')}
                                                color="primary"
                                            />
                                        }
                                        label="Notificaciones push en el navegador"
                                    />
                                    <FormControlLabel
                                        control={
                                            <Switch
                                                checked={formData.notifications.sms}
                                                onChange={handleNotificationChange('sms')}
                                                color="primary"
                                            />
                                        }
                                        label="Notificaciones por SMS"
                                    />
                                </Stack>
                            </Box>
                            <Divider />
                            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                                <Button 
                                    variant="contained" 
                                    startIcon={<SaveIcon />}
                                    sx={{ borderRadius: 2, px: 4 }}
                                    onClick={() => {
                                        setSuccess('Configuración de notificaciones guardada!');
                                    }}
                                >
                                    Guardar Configuración
                                </Button>
                            </Box>
                        </Stack>
                    </Card>
                </TabPanel>
            </Paper>

            {/* Snackbars */}
            <Snackbar open={!!error} autoHideDuration={6000} onClose={(event, reason) => handleCloseSnackbar(event, reason)}>
                <Alert onClose={() => handleCloseSnackbar(new Event('close'), 'timeout')} severity="error" sx={{ width: '100%' }}>
                    {error}
                </Alert>
            </Snackbar>
            <Snackbar open={!!success} autoHideDuration={6000} onClose={(event, reason) => handleCloseSnackbar(event, reason)}>
                <Alert onClose={() => handleCloseSnackbar(new Event('close'), 'timeout')} severity="success" sx={{ width: '100%' }}>
                    {success}
                </Alert>
            </Snackbar>
        </Box>
    );
};

export default Settings; 
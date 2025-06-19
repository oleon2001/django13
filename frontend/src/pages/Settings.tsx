import React, { useState, useEffect } from 'react';
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
import { useTranslation } from 'react-i18next';
import authService from '../services/auth';

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

const Settings: React.FC = () => {
    const { t, i18n } = useTranslation();
    const [tabValue, setTabValue] = useState(0);
    const [showPasswords, setShowPasswords] = useState({
        old: false,
        new: false,
        confirm: false,
    });
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        fullName: '',
        phone: '',
        location: '',
        oldPassword: '',
        newPassword: '',
        confirmPassword: '',
        theme: 'light',
        language: i18n.language || 'es',
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

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const user = await authService.getCurrentUser();
                setFormData(prev => ({
                    ...prev,
                    username: user.username,
                    email: user.email,
                }));
            } catch (err) {
                setError(t('configuration.errors.loadProfile'));
            }
        };
        fetchUser();
    }, []);

    const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
        setTabValue(newValue);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | SelectChangeEvent<string>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        
        // If language is changed, update i18n and persist to localStorage
        if (name === 'language') {
            i18n.changeLanguage(value);
            localStorage.setItem('selectedLanguage', value);
        }
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
            setSuccess(t('configuration.profile.updateSuccess', 'Perfil actualizado correctamente!'));
        }, 500);
    };

    const handlePasswordChangeSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);
        if (formData.newPassword !== formData.confirmPassword) {
            setError(t('validation.passwordMatch'));
            return;
        }
        if (formData.newPassword.length < 6) {
            setError(t('configuration.security.passwordMinLength'));
            return;
        }
        // Simular llamada a la API para cambiar contraseña
        setTimeout(() => {
            setSuccess(t('configuration.security.passwordUpdated', 'Contraseña actualizada correctamente!'));
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
            setSuccess(t('configuration.preferencesUpdated', 'Preferencias guardadas correctamente!'));
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
                        {t('configuration.title')}
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        {t('configuration.description')}
                    </Typography>
                </Box>
            </Box>

            <Paper sx={{ borderRadius: 3, boxShadow: 2 }}>
                {/* Tabs */}
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={tabValue} onChange={handleTabChange} aria-label="settings tabs">
                        <Tab 
                            icon={<PersonIcon />} 
                            label={t('configuration.tabs.profile')} 
                            iconPosition="start"
                            sx={{ minHeight: 64, textTransform: 'none', fontSize: '1rem' }}
                        />
                        <Tab 
                            icon={<SecurityIcon />} 
                            label={t('configuration.tabs.security')} 
                            iconPosition="start"
                            sx={{ minHeight: 64, textTransform: 'none', fontSize: '1rem' }}
                        />
                        <Tab 
                            icon={<PaletteIcon />} 
                            label={t('configuration.tabs.preferences')} 
                            iconPosition="start"
                            sx={{ minHeight: 64, textTransform: 'none', fontSize: '1rem' }}
                        />
                        <Tab 
                            icon={<NotificationsIcon />} 
                            label={t('configuration.tabs.notifications')} 
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
                                <Chip label={t('configuration.profile.administrator')} color="primary" size="small" sx={{ mb: 2 }} />
                                <Button
                                    variant="outlined"
                                    startIcon={<EditIcon />}
                                    sx={{ borderRadius: 2 }}
                                >
                                    {t('configuration.profile.changePhoto')}
                                </Button>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={8}>
                            <Card sx={{ borderRadius: 3, p: 3 }}>
                                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
                                    {t('configuration.profile.personalInfo')}
                                </Typography>
                                <form onSubmit={handleProfileSubmit}>
                                    <Grid container spacing={3}>
                                        <Grid item xs={12} sm={6}>
                                            <TextField
                                                fullWidth
                                                label={t('configuration.profile.fullName')}
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
                                                label={t('configuration.profile.username')}
                                                name="username"
                                                value={formData.username}
                                                onChange={handleInputChange}
                                                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                                            />
                                        </Grid>
                                        <Grid item xs={12} sm={6}>
                                            <TextField
                                                fullWidth
                                                label={t('configuration.profile.email')}
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
                                                label={t('configuration.profile.phone')}
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
                                                label={t('configuration.profile.location')}
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
                                            {t('configuration.profile.saveChanges')}
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
                                    {t('configuration.security.changePassword')}
                                </Typography>
                                <form onSubmit={handlePasswordChangeSubmit}>
                                    <Stack spacing={3}>
                                        <TextField
                                            fullWidth
                                            label={t('configuration.security.currentPassword')}
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
                                            label={t('configuration.security.newPassword')}
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
                                            label={t('configuration.security.confirmPassword')}
                                            name="confirmPassword"
                                            type={showPasswords.confirm ? 'text' : 'password'}
                                            value={formData.confirmPassword}
                                            onChange={handleInputChange}
                                            error={formData.newPassword !== formData.confirmPassword && formData.confirmPassword !== ''}
                                            helperText={formData.newPassword !== formData.confirmPassword && formData.confirmPassword !== '' ? t('validation.passwordMatch') : ''}
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
                                            {t('configuration.security.changePassword')}
                                        </Button>
                                    </Box>
                                </form>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Card sx={{ borderRadius: 3, p: 3 }}>
                                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
                                    {t('configuration.security.privacy')}
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
                                        label={t('configuration.security.profileVisible')}
                                    />
                                    <FormControlLabel
                                        control={
                                            <Switch
                                                checked={formData.privacy.locationSharing}
                                                onChange={handlePrivacyChange('locationSharing')}
                                                color="primary"
                                            />
                                        }
                                        label={t('configuration.security.locationSharing')}
                                    />
                                    <FormControlLabel
                                        control={
                                            <Switch
                                                checked={formData.privacy.dataCollection}
                                                onChange={handlePrivacyChange('dataCollection')}
                                                color="primary"
                                            />
                                        }
                                        label={t('configuration.security.dataCollection')}
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
                            {t('configuration.applicationPreferences')}
                        </Typography>
                        <form onSubmit={handlePreferencesSubmit}>
                            <Grid container spacing={3}>
                                <Grid item xs={12} sm={6}>
                                    <FormControl fullWidth>
                                        <InputLabel id="theme-label">{t('configuration.theme')}</InputLabel>
                                        <Select
                                            labelId="theme-label"
                                            id="theme"
                                            name="theme"
                                            value={formData.theme}
                                            label={t('configuration.theme')}
                                            onChange={handleInputChange}
                                            startAdornment={
                                                <InputAdornment position="start">
                                                    <PaletteIcon color="action" />
                                                </InputAdornment>
                                            }
                                            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                                        >
                                            <MenuItem value="light">{t('configuration.themes.light')}</MenuItem>
                                            <MenuItem value="dark">{t('configuration.themes.dark')}</MenuItem>
                                            <MenuItem value="auto">{t('configuration.themes.auto')}</MenuItem>
                                        </Select>
                                    </FormControl>
                                </Grid>
                                <Grid item xs={12} sm={6}>
                                    <FormControl fullWidth>
                                        <InputLabel id="language-label">{t('configuration.language')}</InputLabel>
                                        <Select
                                            labelId="language-label"
                                            id="language"
                                            name="language"
                                            value={formData.language}
                                            label={t('configuration.language')}
                                            onChange={handleInputChange}
                                            startAdornment={
                                                <InputAdornment position="start">
                                                    <LanguageIcon color="action" />
                                                </InputAdornment>
                                            }
                                            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                                        >
                                            <MenuItem value="es">{t('configuration.languages.es')}</MenuItem>
                                            <MenuItem value="en">{t('configuration.languages.en')}</MenuItem>
                                            <MenuItem value="pt">{t('configuration.languages.pt')}</MenuItem>
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
                                    {t('common.save')} {t('configuration.tabs.preferences')}
                                </Button>
                            </Box>
                        </form>
                    </Card>
                </TabPanel>

                {/* Notifications Tab */}
                <TabPanel value={tabValue} index={3}>
                    <Card sx={{ borderRadius: 3, p: 3 }}>
                        <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
                            {t('configuration.notifications.title')}
                        </Typography>
                        <Stack spacing={3}>
                            <Box>
                                <Typography variant="subtitle1" sx={{ fontWeight: 'medium', mb: 2 }}>
                                    {t('configuration.notifications.types')}
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
                                        label={t('configuration.notifications.email')}
                                    />
                                    <FormControlLabel
                                        control={
                                            <Switch
                                                checked={formData.notifications.push}
                                                onChange={handleNotificationChange('push')}
                                                color="primary"
                                            />
                                        }
                                        label={t('configuration.notifications.push')}
                                    />
                                    <FormControlLabel
                                        control={
                                            <Switch
                                                checked={formData.notifications.sms}
                                                onChange={handleNotificationChange('sms')}
                                                color="primary"
                                            />
                                        }
                                        label={t('configuration.notifications.sms')}
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
                                        setSuccess(t('configuration.notifications.saveSuccess'));
                                    }}
                                >
                                    {t('configuration.notifications.saveSettings')}
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
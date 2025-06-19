import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useTranslation } from 'react-i18next';
import { 
    Button, 
    TextField, 
    Box, 
    Typography, 
    Container, 
    Alert,
    InputAdornment,
    IconButton,
    CircularProgress,
    Avatar,
    Divider,
    Card,
    CardContent,
} from '@mui/material';
import {
    Person as PersonIcon,
    Lock as LockIcon,
    Visibility as VisibilityIcon,
    VisibilityOff as VisibilityOffIcon,
    Login as LoginIcon,
    GpsFixed as GpsIcon,
} from '@mui/icons-material';

const Login: React.FC = () => {
    const { t } = useTranslation();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [showPassword, setShowPassword] = useState(false);
    const { login, loading } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        
        try {
            await login(username, password);
            // Esperar un momento para asegurar que el estado se actualice
            setTimeout(() => {
                navigate('/dashboard');
            }, 100);
        } catch (err: any) {
            setError(err.message || t('login.errors.loginFailed'));
        }
    };

    const handleTogglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

    return (
        <Box
            sx={{
                minHeight: '100vh',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                p: 2,
            }}
        >
            <Container component="main" maxWidth="sm">
                <Card
                    sx={{
                        borderRadius: 4,
                        boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
                        overflow: 'hidden',
                        background: 'rgba(255, 255, 255, 0.95)',
                        backdropFilter: 'blur(10px)',
                    }}
                >
                    <CardContent sx={{ p: 0 }}>
                        {/* Header Section */}
                        <Box
                            sx={{
                                background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
                                color: 'white',
                                p: 4,
                                textAlign: 'center',
                            }}
                        >
                            <Avatar
                                sx={{
                                    bgcolor: 'rgba(255, 255, 255, 0.2)',
                                    width: 80,
                                    height: 80,
                                    mx: 'auto',
                                    mb: 2,
                                    backdropFilter: 'blur(10px)',
                                }}
                            >
                                <GpsIcon sx={{ fontSize: 40 }} />
                            </Avatar>
                            <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                                {t('app.name')}
                            </Typography>
                            <Typography variant="body1" sx={{ opacity: 0.9 }}>
                                {t('app.subtitle')}
                            </Typography>
                        </Box>

                        {/* Form Section */}
                        <Box sx={{ p: 4 }}>
                            <Typography 
                                variant="h5" 
                                sx={{ 
                                    textAlign: 'center', 
                                    mb: 3, 
                                    fontWeight: 'bold',
                                    color: 'text.primary'
                                }}
                            >
                                {t('login.title')}
                            </Typography>

                            {error && (
                                <Alert 
                                    severity="error" 
                                    sx={{ 
                                        mb: 3, 
                                        borderRadius: 2,
                                        '& .MuiAlert-icon': {
                                            fontSize: '1.2rem'
                                        }
                                    }}
                                >
                                    {error}
                                </Alert>
                            )}

                            <Box component="form" onSubmit={handleSubmit}>
                                <TextField
                                    margin="normal"
                                    required
                                    fullWidth
                                    id="username"
                                    label={t('login.username')}
                                    name="username"
                                    autoComplete="username"
                                    autoFocus
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    InputProps={{
                                        startAdornment: (
                                            <InputAdornment position="start">
                                                <PersonIcon color="action" />
                                            </InputAdornment>
                                        ),
                                    }}
                                    sx={{
                                        mb: 2,
                                        '& .MuiOutlinedInput-root': {
                                            borderRadius: 2,
                                            '&:hover fieldset': {
                                                borderColor: 'primary.main',
                                            },
                                        },
                                    }}
                                />
                                
                                <TextField
                                    margin="normal"
                                    required
                                    fullWidth
                                    name="password"
                                    label={t('login.password')}
                                    type={showPassword ? 'text' : 'password'}
                                    id="password"
                                    autoComplete="current-password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    InputProps={{
                                        startAdornment: (
                                            <InputAdornment position="start">
                                                <LockIcon color="action" />
                                            </InputAdornment>
                                        ),
                                        endAdornment: (
                                            <InputAdornment position="end">
                                                <IconButton
                                                    aria-label="toggle password visibility"
                                                    onClick={handleTogglePasswordVisibility}
                                                    edge="end"
                                                >
                                                    {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                                                </IconButton>
                                            </InputAdornment>
                                        ),
                                    }}
                                    sx={{
                                        mb: 3,
                                        '& .MuiOutlinedInput-root': {
                                            borderRadius: 2,
                                            '&:hover fieldset': {
                                                borderColor: 'primary.main',
                                            },
                                        },
                                    }}
                                />

                                <Button
                                    type="submit"
                                    fullWidth
                                    variant="contained"
                                    disabled={loading}
                                    startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <LoginIcon />}
                                    sx={{
                                        mt: 2,
                                        mb: 2,
                                        py: 1.5,
                                        borderRadius: 2,
                                        fontSize: '1.1rem',
                                        fontWeight: 'bold',
                                        background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
                                        boxShadow: '0 4px 15px rgba(25, 118, 210, 0.4)',
                                        '&:hover': {
                                            background: 'linear-gradient(135deg, #1565c0 0%, #0d47a1 100%)',
                                            boxShadow: '0 6px 20px rgba(25, 118, 210, 0.6)',
                                            transform: 'translateY(-2px)',
                                        },
                                        '&:disabled': {
                                            background: 'rgba(0, 0, 0, 0.12)',
                                            boxShadow: 'none',
                                            transform: 'none',
                                        },
                                        transition: 'all 0.3s ease',
                                    }}
                                >
                                    {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
                                </Button>

                                <Divider sx={{ my: 3 }}>
                                    <Typography variant="body2" color="text.secondary">
                                        Sistema GPS Tracker v1.0
                                    </Typography>
                                </Divider>

                                <Box sx={{ textAlign: 'center' }}>
                                    <Typography variant="body2" color="text.secondary">
                                        {t('login.accessProblems')}{' '}
                                        <Typography 
                                            component="span" 
                                            color="primary" 
                                            sx={{ 
                                                cursor: 'pointer',
                                                '&:hover': { textDecoration: 'underline' }
                                            }}
                                        >
                                            {t('login.contactSupport')}
                                        </Typography>
                                    </Typography>
                                </Box>
                            </Box>
                        </Box>
                    </CardContent>
                </Card>

                {/* Footer */}
                <Box sx={{ textAlign: 'center', mt: 3 }}>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                        {t('login.footer')}
                    </Typography>
                </Box>
            </Container>
        </Box>
    );
};

export default Login;
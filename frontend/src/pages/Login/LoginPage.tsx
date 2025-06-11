import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Box, TextField, Button, Typography, InputAdornment } from '@mui/material';
import { AccountCircle, Lock } from '@mui/icons-material';
import logo from '../../assets/img/skyguard.png';

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      await login(username, password);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError('Usuario o contraseña incorrectos');
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%)',
        fontFamily: 'Roboto, sans-serif',
        color: '#f5f5f5',
        p: 2,
        boxSizing: 'border-box',
      }}
    >
      <Box
        sx={{
          background: '#2a2a2a',
          p: { xs: 3, sm: 4.5 }, // Responsive padding
          borderRadius: '12px',
          boxShadow: '0 15px 30px rgba(0, 0, 0, 0.5)',
          width: '100%',
          maxWidth: '480px',
          textAlign: 'center',
          animation: 'fadeIn 0.8s ease-out',
          '@keyframes fadeIn': {
            from: { opacity: 0, transform: 'translateY(-20px)' },
            to: { opacity: 1, transform: 'translateY(0)' },
          },
        }}
      >
        <Box
          sx={{
            display: 'block',
            textAlign: 'center',
            mb: 3,
          }}
        >
          <Box
            component="img"
            src={logo}
            alt="SkyGuard Logo"
            sx={{
              maxWidth: '120px',
              mb: 2,
              mx: 'auto',
              display: 'block',
            }}
          />
          <Typography
            variant="h4"
            component="h1"
            sx={{ color: '#e01a22', fontWeight: 700, letterSpacing: '1px', mb: 0 }}
          >
            Ingresar
          </Typography>
        </Box>

        {error && (
          <Typography
            sx={{
              bgcolor: '#e01a22',
              color: 'white',
              p: 1.5,
              borderRadius: '8px',
              mb: 3,
              textAlign: 'center',
              fontWeight: 600,
              fontSize: '1.05rem',
              opacity: 0.9,
              animation: 'shake 0.5s ease-in-out',
              boxShadow: '0 4px 10px rgba(0, 0, 0, 0.3)',
              '@keyframes shake': {
                '0%, 100%': { transform: 'translateX(0)' },
                '20%, 60%': { transform: 'translateX(-5px)' },
                '40%, 80%': { transform: 'translateX(5px)' },
              },
            }}
          >
            {error}
          </Typography>
        )}

        <Box component="form" onSubmit={handleSubmit} noValidate>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              margin="normal"
              required
              id="username"
              label="Usuario"
              name="username"
              autoComplete="username"
              autoFocus
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              sx={{ flexGrow: 1 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <AccountCircle sx={{ color: '#888' }} />
                  </InputAdornment>
                ),
                sx: {
                  borderRadius: '8px',
                  bgcolor: '#333',
                  color: '#f5f5f5',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#444 !important' },
                  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#e01a22 !important' },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#e01a22 !important', boxShadow: '0 0 0 4px rgba(224, 26, 34, 0.4)' },
                  '& .MuiInputBase-input': { color: '#f5f5f5' },
                },
              }}
              InputLabelProps={{
                sx: { color: '#888' },
              }}
            />
            <TextField
              margin="normal"
              required
              name="password"
              label="Contraseña"
              type="password"
              id="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              sx={{ flexGrow: 1 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock sx={{ color: '#888' }} />
                  </InputAdornment>
                ),
                sx: {
                  borderRadius: '8px',
                  bgcolor: '#333',
                  color: '#f5f5f5',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#444 !important' },
                  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#e01a22 !important' },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#e01a22 !important', boxShadow: '0 0 0 4px rgba(224, 26, 34, 0.4)' },
                  '& .MuiInputBase-input': { color: '#f5f5f5' },
                },
              }}
              InputLabelProps={{
                sx: { color: '#888' },
              }}
            />
          </Box>
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{
              mt: 3, mb: 2,
              bgcolor: '#e01a22',
              color: 'white',
              py: 1.5,
              borderRadius: '8px',
              fontSize: '1.3rem',
              fontWeight: 700,
              letterSpacing: '0.5px',
              '&:hover': {
                bgcolor: '#c0151c',
                transform: 'translateY(-3px)',
                boxShadow: '0 8px 20px rgba(0, 0, 0, 0.4)',
              },
              '&:active': {
                transform: 'translateY(0)',
                boxShadow: 'none',
              },
            }}
          >
            Iniciar Sesión
          </Button>
        </Box>
      </Box>
    </Box>
  );
}; 
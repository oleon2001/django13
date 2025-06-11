import React, { useState } from 'react';
import {
    Box,
    Typography,
    TextField,
    Button,
    Grid,
    Card,
    CardContent,
    Alert,
    Snackbar,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
} from '@mui/material';
import { SelectChangeEvent } from '@mui/material/Select';
import { SnackbarCloseReason } from '@mui/material/Snackbar';
// import './Settings.css'; // Eliminar este import

const mockUser = {
  username: 'admin',
  email: 'admin@skyguard.com',
};

const Settings: React.FC = () => {
  const [formData, setFormData] = useState({
    username: mockUser.username,
    email: mockUser.email,
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
    theme: 'light',
    language: 'es',
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | SelectChangeEvent<string>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
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
      <Typography variant="h4" gutterBottom component="h1">
        Configuración de Usuario
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Perfil de Usuario
              </Typography>
              <form onSubmit={handleProfileSubmit}>
                <TextField
                  fullWidth
                  margin="normal"
                  label="Nombre de Usuario"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                />
                <TextField
                  fullWidth
                  margin="normal"
                  label="Correo Electrónico"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                />
                <Button type="submit" variant="contained" color="primary" sx={{ mt: 2 }}>
                  Guardar Cambios
                </Button>
              </form>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cambiar Contraseña
              </Typography>
              <form onSubmit={handlePasswordChangeSubmit}>
                <TextField
                  fullWidth
                  margin="normal"
                  label="Contraseña Actual"
                  name="oldPassword"
                  type="password"
                  value={formData.oldPassword}
                  onChange={handleInputChange}
                />
                <TextField
                  fullWidth
                  margin="normal"
                  label="Nueva Contraseña"
                  name="newPassword"
                  type="password"
                  value={formData.newPassword}
                  onChange={handleInputChange}
                />
                <TextField
                  fullWidth
                  margin="normal"
                  label="Confirmar Contraseña"
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  error={formData.newPassword !== formData.confirmPassword && formData.confirmPassword !== ''}
                  helperText={formData.newPassword !== formData.confirmPassword && formData.confirmPassword !== '' ? 'Las contraseñas no coinciden' : ''}
                />
                <Button type="submit" variant="contained" color="primary" sx={{ mt: 2 }}>
                  Cambiar Contraseña
                </Button>
              </form>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Preferencias
              </Typography>
              <form onSubmit={handlePreferencesSubmit}>
                <FormControl fullWidth margin="normal">
                  <InputLabel id="theme-label">Tema</InputLabel>
                  <Select
                    labelId="theme-label"
                    id="theme"
                    name="theme"
                    value={formData.theme}
                    label="Tema"
                    onChange={handleInputChange}
                  >
                    <MenuItem value="light">Claro</MenuItem>
                    <MenuItem value="dark">Oscuro</MenuItem>
                  </Select>
                </FormControl>
                <FormControl fullWidth margin="normal">
                  <InputLabel id="language-label">Idioma</InputLabel>
                  <Select
                    labelId="language-label"
                    id="language"
                    name="language"
                    value={formData.language}
                    label="Idioma"
                    onChange={handleInputChange}
                  >
                    <MenuItem value="es">Español</MenuItem>
                    <MenuItem value="en">Inglés</MenuItem>
                  </Select>
                </FormControl>
                <Button type="submit" variant="contained" color="primary" sx={{ mt: 2 }}>
                  Guardar Preferencias
                </Button>
              </form>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

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
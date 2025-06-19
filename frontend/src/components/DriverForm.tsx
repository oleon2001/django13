import React, { useState, useEffect } from 'react';
import { Driver, Device, Vehicle } from '../types';
import { 
  TextField, 
  Button, 
  Box, 
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Divider,
  Alert,
  Grid,
  Switch,
  FormControlLabel
} from '@mui/material';
import { driverService } from '../services/driverService';

interface Props {
  initialData?: Partial<Driver>;
  onSave: (data: Partial<Driver>) => void;
  onCancel: () => void;
}

export const DriverForm: React.FC<Props> = ({ initialData = {}, onSave, onCancel }) => {
  const [form, setForm] = useState<Partial<Driver>>({
    is_active: true,
    civil_status: 'SOL',
    ...initialData
  });
  const [availableDevices, setAvailableDevices] = useState<Device[]>([]);
  const [availableVehicles, setAvailableVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAvailableOptions();
  }, []);

  const loadAvailableOptions = async () => {
    try {
      setLoading(true);
      const [devices, vehicles] = await Promise.all([
        driverService.getAvailableDevices(),
        driverService.getAvailableVehicles()
      ]);
      setAvailableDevices(devices);
      setAvailableVehicles(vehicles);
    } catch (err) {
      setError('Error cargando opciones disponibles');
      console.error('Error loading options:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setForm({ 
      ...form, 
      [name]: type === 'checkbox' ? checked : value 
    });
  };

  const handleSelectChange = (name: string) => (event: any) => {
    setForm({ ...form, [name]: event.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      
      const driverData = {
        ...form,
        full_name: `${form.name} ${form.middle_name || ''} ${form.last_name || ''}`.trim()
      };
      
      await onSave(driverData);
      
    } catch (err) {
      setError('Error al guardar el conductor');
      console.error('Error saving driver:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Typography variant="h6" gutterBottom>
        Información Personal
      </Typography>
      
      <Grid container spacing={2}>
        <Grid item xs={12} sm={4}>
          <TextField
            name="name"
            label="Nombre"
            value={form.name || ''}
            onChange={handleChange}
            fullWidth
            margin="normal"
            required
          />
        </Grid>
        
        <Grid item xs={12} sm={4}>
          <TextField
            name="middle_name"
            label="Segundo Nombre"
            value={form.middle_name || ''}
            onChange={handleChange}
            fullWidth
            margin="normal"
          />
        </Grid>
        
        <Grid item xs={12} sm={4}>
          <TextField
            name="last_name"
            label="Apellido"
            value={form.last_name || ''}
            onChange={handleChange}
            fullWidth
            margin="normal"
            required
          />
        </Grid>
      </Grid>
      
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            name="birth_date"
            label="Fecha de Nacimiento"
            type="date"
            value={form.birth_date || ''}
            onChange={handleChange}
            fullWidth
            margin="normal"
            InputLabelProps={{ shrink: true }}
            required
          />
        </Grid>
        
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth margin="normal">
            <InputLabel>Estado Civil</InputLabel>
            <Select
              name="civil_status"
              value={form.civil_status || 'SOL'}
              onChange={handleSelectChange('civil_status')}
              label="Estado Civil"
            >
              <MenuItem value="SOL">Soltero</MenuItem>
              <MenuItem value="CAS">Casado</MenuItem>
              <MenuItem value="DIV">Divorciado</MenuItem>
              <MenuItem value="VIU">Viudo</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>
      
      <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
        Información Laboral
      </Typography>
      
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            name="payroll"
            label="Nómina"
            value={form.payroll || ''}
            onChange={handleChange}
            fullWidth
            margin="normal"
            required
          />
        </Grid>
        
        <Grid item xs={12} sm={6}>
          <TextField
            name="license"
            label="Licencia de Conducir"
            value={form.license || ''}
            onChange={handleChange}
            fullWidth
            margin="normal"
            required
          />
        </Grid>
      </Grid>
      
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            name="social_security"
            label="Seguro Social"
            value={form.social_security || ''}
            onChange={handleChange}
            fullWidth
            margin="normal"
          />
        </Grid>
        
        <Grid item xs={12} sm={6}>
          <TextField
            name="tax_id"
            label="RFC"
            value={form.tax_id || ''}
            onChange={handleChange}
            fullWidth
            margin="normal"
          />
        </Grid>
      </Grid>
      
      <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
        Información de Contacto
      </Typography>
      
      <TextField
        name="address"
        label="Dirección"
        value={form.address || ''}
        onChange={handleChange}
        fullWidth
        margin="normal"
        multiline
        rows={2}
      />
      
      <TextField
        name="phone"
        label="Teléfono"
        value={form.phone || ''}
        onChange={handleChange}
        fullWidth
        margin="normal"
        required
      />
      
      <FormControlLabel
        control={
          <Switch
            checked={form.is_active || false}
            onChange={handleChange}
            name="is_active"
          />
        }
        label="Conductor Activo"
        sx={{ mt: 1 }}
      />

      <Divider sx={{ my: 3 }} />
      
      <Typography variant="h6" gutterBottom>
        Vinculaciones
      </Typography>
      
      <FormControl fullWidth margin="normal">
        <InputLabel>Dispositivo GPS</InputLabel>
        <Select
          name="device_id"
          value={form.device_id || ''}
          onChange={handleSelectChange('device_id')}
          label="Dispositivo GPS"
        >
          <MenuItem value="">Sin dispositivo</MenuItem>
          {availableDevices.map((device) => (
            <MenuItem key={device.imei} value={device.imei}>
              {device.name || `Device ${device.imei}`} - IMEI: {device.imei}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      
      <FormControl fullWidth margin="normal">
        <InputLabel>Vehículo Asignado</InputLabel>
        <Select
          name="vehicle_id"
          value={form.vehicle_id || ''}
          onChange={handleSelectChange('vehicle_id')}
          label="Vehículo Asignado"
        >
          <MenuItem value="">Sin vehículo</MenuItem>
          {availableVehicles.map((vehicle) => (
            <MenuItem key={vehicle.id} value={vehicle.id}>
              {vehicle.name} - Placa: {vehicle.plate}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1, mt: 3 }}>
        <Button onClick={onCancel} disabled={loading}>
          Cancelar
        </Button>
        <Button 
          type="submit" 
          variant="contained" 
          disabled={loading}
        >
          {loading ? 'Guardando...' : 'Guardar'}
        </Button>
      </Box>
    </Box>
  );
};
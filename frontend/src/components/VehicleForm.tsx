import React, { useState, useEffect } from 'react';
import { Vehicle, Device, Driver } from '../types';
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
  Alert
} from '@mui/material';
import { vehicleService } from '../services/vehicleService';

interface Props {
  initialData?: Partial<Vehicle>;
  onSave: (data: Partial<Vehicle>) => void;
  onCancel: () => void;
}

export const VehicleForm: React.FC<Props> = ({ initialData = {}, onSave, onCancel }) => {
  const [form, setForm] = useState<Partial<Vehicle>>(initialData);
  const [availableDevices, setAvailableDevices] = useState<Device[]>([]);
  const [availableDrivers, setAvailableDrivers] = useState<Driver[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAvailableOptions();
  }, []);

  const loadAvailableOptions = async () => {
    try {
      setLoading(true);
      const [devices, drivers] = await Promise.all([
        vehicleService.getAvailableDevices(),
        vehicleService.getAvailableDrivers()
      ]);
      setAvailableDevices(devices);
      setAvailableDrivers(drivers);
    } catch (err) {
      setError('Error cargando opciones disponibles');
      console.error('Error loading options:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSelectChange = (name: string) => (event: any) => {
    setForm({ ...form, [name]: event.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      
      // Guardar el vehículo
      await onSave(form);
      
      // Si se seleccionó un dispositivo GPS, vincularlo
      if (form.device_id && form.id) {
        await vehicleService.assignDevice(form.id, form.device_id);
      }
      
      // Si se seleccionó un conductor, vincularlo
      if (form.driver_id && form.id) {
        await vehicleService.assignDriver(form.id, form.driver_id);
      }
      
    } catch (err) {
      setError('Error al guardar el vehículo');
      console.error('Error saving vehicle:', err);
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
        Información del Vehículo
      </Typography>
      
      <TextField
        name="name"
        label="Nombre"
        value={form.name || ''}
        onChange={handleChange}
        fullWidth
        margin="normal"
        required
      />
      
      <TextField
        name="plate"
        label="Placa"
        value={form.plate || ''}
        onChange={handleChange}
        fullWidth
        margin="normal"
        required
      />
      
      <TextField
        name="brand"
        label="Marca"
        value={form.brand || ''}
        onChange={handleChange}
        fullWidth
        margin="normal"
      />
      
      <TextField
        name="model"
        label="Modelo"
        value={form.model || ''}
        onChange={handleChange}
        fullWidth
        margin="normal"
      />
      
      <TextField
        name="year"
        label="Año"
        type="number"
        value={form.year || ''}
        onChange={handleChange}
        fullWidth
        margin="normal"
      />
      
      <FormControl fullWidth margin="normal">
        <InputLabel>Estado</InputLabel>
        <Select
          name="status"
          value={form.status || 'active'}
          onChange={handleSelectChange('status')}
          label="Estado"
        >
          <MenuItem value="active">Activo</MenuItem>
          <MenuItem value="maintenance">Mantenimiento</MenuItem>
          <MenuItem value="inactive">Inactivo</MenuItem>
        </Select>
      </FormControl>

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
        <InputLabel>Conductor Asignado</InputLabel>
        <Select
          name="driver_id"
          value={form.driver_id || ''}
          onChange={handleSelectChange('driver_id')}
          label="Conductor Asignado"
        >
          <MenuItem value="">Sin conductor</MenuItem>
          {availableDrivers.map((driver) => (
            <MenuItem key={driver.id} value={driver.id}>
              {driver.full_name} - Licencia: {driver.license}
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

export {}; 
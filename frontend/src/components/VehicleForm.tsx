import React, { useState, useEffect } from 'react';
import { Vehicle, Device, Driver } from '../types/unified';
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
import { useTranslation } from 'react-i18next';

interface Props {
  initialData?: Partial<Vehicle>;
  onSave: (data: Partial<Vehicle>) => void;
  onCancel: () => void;
}

// Extended form interface to handle temporary IDs for form state
interface VehicleFormData extends Omit<Partial<Vehicle>, 'device' | 'driver'> {
  device_id?: number; // Temporary field for form handling
  driver_id?: number; // Temporary field for form handling
}

export const VehicleForm: React.FC<Props> = ({ initialData = {}, onSave, onCancel }) => {
  const { t } = useTranslation();
  const [form, setForm] = useState<VehicleFormData>(() => {
    // Convert Vehicle data to form data, excluding device and driver objects
    const { device, driver, ...vehicleProps } = initialData;
    return {
      ...vehicleProps,
      // Extract IDs from objects if they exist
      device_id: device?.id,
      driver_id: driver?.id
    };
  });
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
      setError(t('vehicles.form.loadingOptions'));
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
    setLoading(true);
    setError(null);
    
    try {
      // Create the vehicle data without the temporary IDs
      const { device_id, driver_id, ...vehicleData } = form;
      
      // Find the selected device and driver objects
      const selectedDevice = device_id ? availableDevices.find(d => d.id === device_id) : null;
      const selectedDriver = driver_id ? availableDrivers.find(d => d.id === driver_id) : null;
      
      // Create the final vehicle object with proper references
      const finalVehicleData: Partial<Vehicle> = {
        ...vehicleData,
        device: selectedDevice || null,
        driver: selectedDriver || null
      };
      
      await onSave(finalVehicleData);
      
    } catch (err) {
      setError(t('vehicles.form.errorSaving'));
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
        {t('vehicles.form.vehicleInfo')}
      </Typography>
      
      <TextField
        name="plate"
        label={t('vehicles.plate')}
        value={form.plate || ''}
        onChange={handleChange}
        fullWidth
        margin="normal"
        required
      />
      
      <TextField
        name="make"
        label={t('vehicles.brand')}
        value={form.make || ''}
        onChange={handleChange}
        fullWidth
        margin="normal"
      />
      
      <TextField
        name="model"
        label={t('vehicles.model')}
        value={form.model || ''}
        onChange={handleChange}
        fullWidth
        margin="normal"
      />
      
      <TextField
        name="year"
        label={t('vehicles.year')}
        type="number"
        value={form.year || ''}
        onChange={handleChange}
        fullWidth
        margin="normal"
      />
      
      <FormControl fullWidth margin="normal">
        <InputLabel>{t('vehicles.form.status')}</InputLabel>
        <Select
          name="status"
          value={form.status || 'ACTIVE'}
          onChange={handleSelectChange('status')}
          label={t('vehicles.form.status')}
        >
          <MenuItem value="ACTIVE">{t('vehicles.form.active')}</MenuItem>
          <MenuItem value="MAINTENANCE">{t('vehicles.form.maintenance')}</MenuItem>
          <MenuItem value="INACTIVE">{t('vehicles.form.inactive')}</MenuItem>
          <MenuItem value="REPAIR">En Reparación</MenuItem>
        </Select>
      </FormControl>

      <Divider sx={{ my: 3 }} />
      
      <Typography variant="h6" gutterBottom>
        {t('vehicles.form.assignments')}
      </Typography>
      
      <FormControl fullWidth margin="normal">
        <InputLabel>{t('vehicles.form.gpsDevice')}</InputLabel>
        <Select
          name="device_id"
          value={form.device_id || ''}
          onChange={handleSelectChange('device_id')}
          label={t('vehicles.form.gpsDevice')}
        >
          <MenuItem value="">{t('vehicles.form.noDevice')}</MenuItem>
          {availableDevices.map((device) => (
            <MenuItem key={device.id} value={device.id}>
              {device.name || `${t('vehicles.form.device')} ${device.imei}`} - IMEI: {device.imei}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      
      <FormControl fullWidth margin="normal">
        <InputLabel>{t('vehicles.form.assignedDriver')}</InputLabel>
        <Select
          name="driver_id"
          value={form.driver_id || ''}
          onChange={handleSelectChange('driver_id')}
          label={t('vehicles.form.assignedDriver')}
        >
          <MenuItem value="">{t('vehicles.form.noDriver')}</MenuItem>
          {availableDrivers.map((driver) => (
            <MenuItem key={driver.id} value={driver.id}>
              {driver.name} {driver.last_name} - Licencia: {driver.license}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1, mt: 3 }}>
        <Button onClick={onCancel} disabled={loading}>
          {t('vehicles.form.cancel')}
        </Button>
        <Button 
          type="submit" 
          variant="contained" 
          disabled={loading}
        >
          {loading ? t('vehicles.form.saving') : t('vehicles.form.save')}
        </Button>
      </Box>
    </Box>
  );
};

export {}; 
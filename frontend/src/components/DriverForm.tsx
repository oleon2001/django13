import React, { useState } from 'react';
import { Driver } from '../types/unified';
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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      
      await onSave(form);
      
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
            name="is_active"
            checked={form.is_active || false}
            onChange={handleChange}
          />
        }
        label="Activo"
      />

      <Divider sx={{ my: 3 }} />
      
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
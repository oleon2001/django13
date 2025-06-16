import React, { useState } from 'react';
import { Vehicle } from '../types';
import { TextField, Button, Box } from '@mui/material';

interface Props {
  initialData?: Partial<Vehicle>;
  onSave: (data: Partial<Vehicle>) => void;
  onCancel: () => void;
}

export const VehicleForm: React.FC<Props> = ({ initialData = {}, onSave, onCancel }) => {
  const [form, setForm] = useState<Partial<Vehicle>>(initialData);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  return (
    <Box component="form" onSubmit={e => { e.preventDefault(); onSave(form); }}>
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
      <TextField
        name="status"
        label="Estado"
        value={form.status || ''}
        onChange={handleChange}
        fullWidth
        margin="normal"
      />
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1, mt: 2 }}>
        <Button onClick={onCancel}>Cancelar</Button>
        <Button type="submit" variant="contained">Guardar</Button>
      </Box>
    </Box>
  );
};

export {}; 
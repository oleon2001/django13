import React from 'react';
import {
  Box,
  Typography,
  Table as MuiTable,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
} from '@mui/material';
import { mockVehicles } from '../data/mockData';
// import { Vehicle, Column } from '../types'; // Ya no se necesita Column si definimos la tabla aquí
// import './Vehicles.css'; // Eliminar este import

const Vehicles: React.FC = () => {
  // const columns: Column<Vehicle>[] = [
  //   {
  //     header: 'ID',
  //     accessor: (vehicle: Vehicle) => vehicle.id,
  //   },
  //   {
  //     header: 'Nombre',
  //     accessor: (vehicle: Vehicle) => vehicle.device.name,
  //   },
  //   {
  //     header: 'Placa',
  //     accessor: (vehicle: Vehicle) => vehicle.plate,
  //   },
  //   {
  //     header: 'Modelo',
  //     accessor: (vehicle: Vehicle) => vehicle.model,
  //   },
  //   {
  //     header: 'Estado',
  //     accessor: (vehicle: Vehicle) => (
  //       <span className={`status status-${vehicle.status}`}>
  //         {vehicle.status === 'active' && 'Activo'}
  //         {vehicle.status === 'maintenance' && 'En Mantenimiento'}
  //         {vehicle.status === 'inactive' && 'Inactivo'}
  //       </span>
  //     ),
  //   },
  //   {
  //     header: 'Última Actualización',
  //     accessor: (vehicle: Vehicle) => new Date(vehicle.device.lastUpdate).toLocaleString(),
  //   },
  // ];

  const getStatusChipColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'maintenance': return 'warning';
      case 'inactive': return 'error';
      default: return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return 'Activo';
      case 'maintenance': return 'En Mantenimiento';
      case 'inactive': return 'Inactivo';
      default: return status;
    }
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom component="h1">
        Gestión de Vehículos
      </Typography>

      <TableContainer component={Paper}>
        <MuiTable sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Nombre Dispositivo</TableCell>
              <TableCell>Placa</TableCell>
              <TableCell>Modelo</TableCell>
              <TableCell>Estado</TableCell>
              <TableCell>Última Actualización</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {mockVehicles.map((vehicle) => (
              <TableRow
                key={vehicle.id}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell component="th" scope="row">
                  {vehicle.id}
                </TableCell>
                <TableCell>{vehicle.device.name}</TableCell>
                <TableCell>{vehicle.plate}</TableCell>
                <TableCell>{vehicle.model}</TableCell>
                <TableCell>
                  <Chip
                    label={getStatusText(vehicle.status)}
                    color={getStatusChipColor(vehicle.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{new Date(vehicle.device.lastUpdate).toLocaleString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </MuiTable>
      </TableContainer>
    </Box>
  );
};

export default Vehicles; 
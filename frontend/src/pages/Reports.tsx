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
} from '@mui/material';
import { mockReports } from '../data/mockData';
// import { Report, Column } from '../types'; // Ya no se necesita Column
// import './Reports.css'; // Eliminar este import

const Reports: React.FC = () => {
  // const columns: Column<Report>[] = [
  //   {
  //     header: 'ID',
  //     accessor: (report: Report) => report.id,
  //   },
  //   {
  //     header: 'Fecha',
  //     accessor: (report: Report) => report.createdAt,
  //   },
  //   {
  //     header: 'Tipo',
  //     accessor: (report: Report) => report.type,
  //   },
  //   {
  //     header: 'Distancia Total (km)',
  //     accessor: (report: Report) => report.data.totalDistance,
  //   },
  //   {
  //     header: 'Consumo Combustible (L)',
  //     accessor: (report: Report) => report.data.fuelConsumption,
  //   },
  //   {
  //     header: 'Velocidad Promedio (km/h)',
  //     accessor: (report: Report) => report.data.averageSpeed,
  //   },
  //   {
  //     header: 'Alertas',
  //     accessor: (report: Report) => report.data.alerts,
  //   },
  //   {
  //     header: 'Paradas',
  //     accessor: (report: Report) => report.data.stops,
  //   },
  //   {
  //     header: 'Duración (h)',
  //     accessor: (report: Report) => report.data.duration,
  //   },
  // ];

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom component="h1">
        Generación de Reportes
      </Typography>

      <TableContainer component={Paper}>
        <MuiTable sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Fecha</TableCell>
              <TableCell>Tipo</TableCell>
              <TableCell>Distancia Total (km)</TableCell>
              <TableCell>Consumo Combustible (L)</TableCell>
              <TableCell>Velocidad Promedio (km/h)</TableCell>
              <TableCell>Alertas</TableCell>
              <TableCell>Paradas</TableCell>
              <TableCell>Duración (h)</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {mockReports.map((report) => (
              <TableRow
                key={report.id}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell component="th" scope="row">
                  {report.id}
                </TableCell>
                <TableCell>{new Date(report.createdAt).toLocaleString()}</TableCell>
                <TableCell>{report.type}</TableCell>
                <TableCell>{report.data.totalDistance}</TableCell>
                <TableCell>{report.data.fuelConsumption}</TableCell>
                <TableCell>{report.data.averageSpeed}</TableCell>
                <TableCell>{report.data.alerts}</TableCell>
                <TableCell>{report.data.stops}</TableCell>
                <TableCell>{report.data.duration}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </MuiTable>
      </TableContainer>
    </Box>
  );
};

export default Reports; 
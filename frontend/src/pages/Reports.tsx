import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Button,
    Chip,
    CircularProgress,
    Alert,
} from '@mui/material';
import {
    Download as DownloadIcon,
    Refresh as RefreshIcon,
} from '@mui/icons-material';
import { reportService, Report } from '../services/reportService';

const Reports: React.FC = () => {
    const [reports, setReports] = useState<Report[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchReports();
    }, []);

    const fetchReports = async () => {
        try {
            setLoading(true);
            const data = await reportService.getAll();
            setReports(data);
            setError(null);
        } catch (err) {
            setError('Error loading reports');
            console.error('Error loading reports:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = (reportId: number) => {
        // TODO: Implement download functionality
        console.log('Download report:', reportId);
    };

    const handleRefresh = () => {
        fetchReports();
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed':
                return 'success';
            case 'processing':
                return 'warning';
            case 'failed':
                return 'error';
            default:
                return 'default';
        }
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4">
                    Reportes
                </Typography>
                <Button
                    variant="contained"
                    startIcon={<RefreshIcon />}
                    onClick={handleRefresh}
                >
                    Actualizar
                </Button>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Título</TableCell>
                            <TableCell>Tipo</TableCell>
                            <TableCell>Estado</TableCell>
                            <TableCell>Fecha de Creación</TableCell>
                            <TableCell>Acciones</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {reports.length > 0 ? (
                            reports.map((report) => (
                                <TableRow key={report.id}>
                                    <TableCell>{report.title}</TableCell>
                                    <TableCell>{report.type}</TableCell>
                                    <TableCell>
                                        <Chip
                                            label={report.status}
                                            color={getStatusColor(report.status)}
                                            size="small"
                                        />
                                    </TableCell>
                                    <TableCell>
                                        {new Date(report.createdAt).toLocaleString()}
                                    </TableCell>
                                    <TableCell>
                                        <Button
                                            size="small"
                                            startIcon={<DownloadIcon />}
                                            onClick={() => handleDownload(report.id)}
                                        >
                                            Descargar
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell colSpan={5} align="center">
                                    <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                                        No hay reportes disponibles en este momento.
                                        Los reportes se generarán automáticamente cuando haya datos de dispositivos GPS.
                                    </Typography>
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
        </Box>
    );
};

export default Reports; 
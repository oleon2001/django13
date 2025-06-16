import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    Grid,
    Card,
    CardContent,
    CardActions,
    Button,
    Chip,
    CircularProgress,
    Alert,
    TextField,
    InputAdornment,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Avatar,
    Divider,
    Stack,
    IconButton,
    LinearProgress,
} from '@mui/material';
import {
    Download as DownloadIcon,
    Refresh as RefreshIcon,
    Search as SearchIcon,
    Add as AddIcon,
    Assessment as AssessmentIcon,
    Schedule as ScheduleIcon,
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
    FilterList as FilterIcon,
    InsertChart as ChartIcon,
    DateRange as DateRangeIcon,
} from '@mui/icons-material';
import { reportService, Report } from '../services/reportService';

const Reports: React.FC = () => {
    const [reports, setReports] = useState<Report[]>([]);
    const [filteredReports, setFilteredReports] = useState<Report[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [typeFilter, setTypeFilter] = useState('all');
    const [openDialog, setOpenDialog] = useState(false);
    const [newReportType, setNewReportType] = useState('');

    useEffect(() => {
        fetchReports();
        // Auto-refresh every 30 seconds
        const interval = setInterval(fetchReports, 30000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        filterReports();
    }, [reports, searchTerm, statusFilter, typeFilter]);

    const fetchReports = async () => {
        try {
            setLoading(true);
            const data = await reportService.getAll();
            setReports(data);
            setError(null);
        } catch (err) {
            setError('Error al cargar los reportes');
            console.error('Error loading reports:', err);
        } finally {
            setLoading(false);
        }
    };

    const filterReports = () => {
        let filtered = reports;

        // Filter by search term
        if (searchTerm) {
            filtered = filtered.filter(report =>
                report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                report.type.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        // Filter by status
        if (statusFilter !== 'all') {
            filtered = filtered.filter(report => report.status === statusFilter);
        }

        // Filter by type
        if (typeFilter !== 'all') {
            filtered = filtered.filter(report => report.type === typeFilter);
        }

        setFilteredReports(filtered);
    };

    const handleDownload = async (reportId: number) => {
        try {
            const blob = await reportService.download(reportId);
            if (blob) {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `reporte_${reportId}.pdf`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            } else {
                setError('No se pudo descargar el reporte');
            }
        } catch (err) {
            setError('Error al descargar el reporte');
        }
    };

    const handleRefresh = () => {
        fetchReports();
    };

    const handleGenerateReport = () => {
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setNewReportType('');
    };

    const handleCreateReport = async () => {
        try {
            await reportService.create({ type: newReportType });
            handleCloseDialog();
            fetchReports();
        } catch (err) {
            setError('Error al generar el reporte');
        }
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

    const getStatusLabel = (status: string) => {
        switch (status) {
            case 'completed':
                return 'Completado';
            case 'processing':
                return 'Procesando';
            case 'failed':
                return 'Fallido';
            default:
                return status;
        }
    };

    const getTypeIcon = (type: string) => {
        switch (type) {
            case 'tracking':
                return <ChartIcon />;
            case 'summary':
                return <AssessmentIcon />;
            case 'daily':
                return <DateRangeIcon />;
            default:
                return <AssessmentIcon />;
        }
    };

    const getTypeLabel = (type: string) => {
        switch (type) {
            case 'tracking':
                return 'Seguimiento';
            case 'summary':
                return 'Resumen';
            case 'daily':
                return 'Diario';
            default:
                return type;
        }
    };

    const completedReports = reports.filter(r => r.status === 'completed').length;
    const processingReports = reports.filter(r => r.status === 'processing').length;
    const failedReports = reports.filter(r => r.status === 'failed').length;

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
                <CircularProgress size={60} />
            </Box>
        );
    }

    return (
        <Box sx={{ p: 3 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                    Reportes
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                    <IconButton onClick={handleRefresh} color="primary">
                        <RefreshIcon />
                    </IconButton>
                    <Button
                        variant="contained"
                        startIcon={<AddIcon />}
                        onClick={handleGenerateReport}
                        sx={{ borderRadius: 2 }}
                    >
                        Generar Reporte
                    </Button>
                </Box>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                    {error}
                </Alert>
            )}

            {/* Statistics Cards */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'primary.main', mx: 'auto', mb: 1 }}>
                                <AssessmentIcon />
                            </Avatar>
                            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                                {reports.length}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Total Reportes
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'success.main', mx: 'auto', mb: 1 }}>
                                <CheckCircleIcon />
                            </Avatar>
                            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                                {completedReports}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Completados
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'warning.main', mx: 'auto', mb: 1 }}>
                                <ScheduleIcon />
                            </Avatar>
                            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'warning.main' }}>
                                {processingReports}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Procesando
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'error.main', mx: 'auto', mb: 1 }}>
                                <ErrorIcon />
                            </Avatar>
                            <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'error.main' }}>
                                {failedReports}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Fallidos
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Filters */}
            <Paper sx={{ p: 2, mb: 3, borderRadius: 2 }}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={4}>
                        <TextField
                            fullWidth
                            placeholder="Buscar reportes..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <SearchIcon color="action" />
                                    </InputAdornment>
                                ),
                            }}
                            sx={{ borderRadius: 2 }}
                        />
                    </Grid>
                    <Grid item xs={12} md={3}>
                        <FormControl fullWidth>
                            <InputLabel>Estado</InputLabel>
                            <Select
                                value={statusFilter}
                                label="Estado"
                                onChange={(e) => setStatusFilter(e.target.value)}
                            >
                                <MenuItem value="all">Todos</MenuItem>
                                <MenuItem value="completed">Completados</MenuItem>
                                <MenuItem value="processing">Procesando</MenuItem>
                                <MenuItem value="failed">Fallidos</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} md={3}>
                        <FormControl fullWidth>
                            <InputLabel>Tipo</InputLabel>
                            <Select
                                value={typeFilter}
                                label="Tipo"
                                onChange={(e) => setTypeFilter(e.target.value)}
                            >
                                <MenuItem value="all">Todos</MenuItem>
                                <MenuItem value="tracking">Seguimiento</MenuItem>
                                <MenuItem value="summary">Resumen</MenuItem>
                                <MenuItem value="daily">Diario</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} md={2}>
                        <Typography variant="body2" color="text.secondary">
                            <FilterIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                            {filteredReports.length} de {reports.length}
                        </Typography>
                    </Grid>
                </Grid>
            </Paper>

            {/* Reports Cards */}
            {filteredReports.length > 0 ? (
                <Grid container spacing={3}>
                    {filteredReports.map((report) => (
                        <Grid item xs={12} sm={6} md={4} key={report.id}>
                            <Card sx={{ borderRadius: 3, boxShadow: 2, height: '100%' }}>
                                <CardContent>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <Avatar sx={{ bgcolor: 'primary.light', width: 32, height: 32 }}>
                                                {getTypeIcon(report.type)}
                                            </Avatar>
                                            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                                                {report.title}
                                            </Typography>
                                        </Box>
                                        <Chip
                                            label={getStatusLabel(report.status)}
                                            color={getStatusColor(report.status)}
                                            size="small"
                                            sx={{ borderRadius: 2 }}
                                        />
                                    </Box>
                                    
                                    <Divider sx={{ mb: 2 }} />
                                    
                                    <Stack spacing={1}>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <Typography variant="body2" color="text.secondary">
                                                Tipo:
                                            </Typography>
                                            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                {getTypeLabel(report.type)}
                                            </Typography>
                                        </Box>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <Typography variant="body2" color="text.secondary">
                                                Creado:
                                            </Typography>
                                            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                {new Date(report.createdAt).toLocaleDateString()}
                                            </Typography>
                                        </Box>
                                        {report.status === 'processing' && (
                                            <Box sx={{ mt: 1 }}>
                                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                                    Progreso:
                                                </Typography>
                                                <LinearProgress variant="indeterminate" sx={{ borderRadius: 1 }} />
                                            </Box>
                                        )}
                                    </Stack>
                                </CardContent>
                                <CardActions sx={{ justifyContent: 'flex-end', p: 2 }}>
                                    <Button
                                        size="small"
                                        startIcon={<DownloadIcon />}
                                        onClick={() => handleDownload(report.id)}
                                        disabled={report.status !== 'completed'}
                                        variant={report.status === 'completed' ? 'contained' : 'outlined'}
                                        sx={{ borderRadius: 2 }}
                                    >
                                        Descargar
                                    </Button>
                                </CardActions>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            ) : (
                <Paper sx={{ p: 6, textAlign: 'center', borderRadius: 3 }}>
                    <AssessmentIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                        {reports.length === 0 ? 'No hay reportes disponibles' : 'No se encontraron reportes'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        {reports.length === 0 
                            ? 'Los reportes se generarán automáticamente cuando haya datos de dispositivos GPS.'
                            : 'Intenta ajustar los filtros de búsqueda.'
                        }
                    </Typography>
                    {reports.length === 0 && (
                        <Button
                            variant="contained"
                            startIcon={<AddIcon />}
                            onClick={handleGenerateReport}
                            sx={{ borderRadius: 2 }}
                        >
                            Generar Primer Reporte
                        </Button>
                    )}
                </Paper>
            )}

            {/* Generate Report Dialog */}
            <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
                <DialogTitle>
                    Generar Nuevo Reporte
                </DialogTitle>
                <DialogContent>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        Selecciona el tipo de reporte que deseas generar:
                    </Typography>
                    <FormControl fullWidth sx={{ mb: 2 }}>
                        <InputLabel>Tipo de Reporte</InputLabel>
                        <Select
                            value={newReportType}
                            label="Tipo de Reporte"
                            onChange={(e) => setNewReportType(e.target.value)}
                        >
                            <MenuItem value="tracking">Reporte de Seguimiento</MenuItem>
                            <MenuItem value="summary">Reporte Resumen</MenuItem>
                            <MenuItem value="daily">Reporte Diario</MenuItem>
                        </Select>
                    </FormControl>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>Cancelar</Button>
                    <Button 
                        onClick={handleCreateReport} 
                        variant="contained"
                        disabled={!newReportType}
                        sx={{ borderRadius: 2 }}
                    >
                        Generar Reporte
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default Reports;
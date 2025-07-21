import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Container,
  Grid,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Switch,
  FormControlLabel,
  Tooltip,
  CircularProgress,
  Alert,
  Snackbar,
  Tabs,
  Tab,
  Chip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Map as MapIcon,
  Refresh as RefreshIcon,
  Analytics as AnalyticsIcon,
  Assessment as AssessmentIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { geofenceService, Geofence, GeofenceFilterParams } from '../../services/geofenceService';
import { GeofenceMap } from './GeofenceMap';
import { GeofenceMetricsDashboard } from './GeofenceMetricsDashboard';
import { ManualGeofenceChecker } from './ManualGeofenceChecker';
import GeofenceForm from './GeofenceForm';
import ConfirmationDialog from '../Modals/ConfirmationDialog';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`geofence-tabpanel-${index}`}
      aria-labelledby={`geofence-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const GeofenceManager: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  // Estados existentes
  const [geofences, setGeofences] = useState<Geofence[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedGeofence, setSelectedGeofence] = useState<Geofence | null>(null);
  const [isFormOpen, setIsFormOpen] = useState<boolean>(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState<boolean>(false);
  const [geofenceToDelete, setGeofenceToDelete] = useState<number | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });

  // Nuevos estados para tabs
  const [currentTab, setCurrentTab] = useState(0);
  const [selectedGeofenceForChecker, setSelectedGeofenceForChecker] = useState<Geofence | null>(null);

  // Definir showSnackbar primero para usarlo en loadGeofences
  const showSnackbar = useCallback((message: string, severity: 'success' | 'error' = 'success') => {
    setSnackbar({ open: true, message, severity });
  }, []);

  // Cargar geocercas usando useCallback para evitar recreación innecesaria
  const loadGeofences = useCallback(async (filters: GeofenceFilterParams = {}) => {
    try {
      setLoading(true);
      setError(null);
      const data = await geofenceService.getAll(filters);
      // Asegurar que data es un array
      if (Array.isArray(data)) {
        setGeofences(data);
      } else {
        console.warn('Expected array from geofenceService.getAll, got:', data);
        setGeofences([]);
      }
    } catch (err) {
      console.error('Error loading geofences:', err);
      setError(t('geofence.errors.loadError'));
      showSnackbar(t('geofence.errors.loadError'), 'error');
      // Asegurar que geofences sea un array aún en caso de error
      setGeofences([]);
    } finally {
      setLoading(false);
    }
  }, [t, showSnackbar]);

  // Cargar datos iniciales
  useEffect(() => {
    loadGeofences();
  }, [loadGeofences]);

  // Manejadores de eventos existentes
  const handleCreate = () => {
    setSelectedGeofence(null);
    setIsFormOpen(true);
  };

  const handleEdit = (geofence: Geofence) => {
    setSelectedGeofence(geofence);
    setIsFormOpen(true);
  };

  const handleView = (geofence: Geofence) => {
    setSelectedGeofenceForChecker(geofence);
    setCurrentTab(3); // Tab de verificación manual
  };

  const handleDeleteClick = (id: number) => {
    setGeofenceToDelete(id);
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!geofenceToDelete) return;
    
    try {
      await geofenceService.delete(geofenceToDelete);
      showSnackbar(t('geofence.messages.deleteSuccess'), 'success');
      loadGeofences();
    } catch (err) {
      console.error('Error deleting geofence:', err);
      showSnackbar(t('geofence.errors.deleteError'), 'error');
    } finally {
      setIsDeleteDialogOpen(false);
      setGeofenceToDelete(null);
    }
  };

  const handleStatusToggle = async (id: number, currentStatus: boolean) => {
    try {
      await geofenceService.update(id, { is_active: !currentStatus });
      showSnackbar(
        currentStatus 
          ? t('geofence.messages.deactivateSuccess')
          : t('geofence.messages.activateSuccess'),
        'success'
      );
      loadGeofences();
    } catch (err) {
      console.error('Error updating geofence status:', err);
      showSnackbar(t('geofence.errors.updateError'), 'error');
    }
  };

  const handleFormSubmit = async (data: any) => {
    try {
      if (selectedGeofence) {
        await geofenceService.update(selectedGeofence.id, data);
        showSnackbar(t('geofence.messages.updateSuccess'), 'success');
      } else {
        await geofenceService.create(data);
        showSnackbar(t('geofence.messages.createSuccess'), 'success');
      }
      setIsFormOpen(false);
      loadGeofences();
    } catch (err) {
      console.error('Error saving geofence:', err);
      showSnackbar(t('geofence.errors.saveError'), 'error');
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const getStatusChip = (isActive: boolean) => (
    <Chip
      label={isActive ? 'Activo' : 'Inactivo'}
      color={isActive ? 'success' : 'error'}
      size="small"
      variant="outlined"
    />
  );

  // Renderizado condicional para loading
  if (loading && geofences.length === 0 && currentTab !== 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          {t('geofence.title')}
        </Typography>
        <Box>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleCreate}
            sx={{ mr: 1 }}
          >
            {t('common.add')}
          </Button>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => loadGeofences()}
          >
            {t('common.refresh')}
          </Button>
        </Box>
      </Box>

      {/* Tabs Navigation */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={handleTabChange} aria-label="geofence tabs">
          <Tab 
            label="Dashboard de Métricas" 
            icon={<AnalyticsIcon />} 
            iconPosition="start"
            id="geofence-tab-0"
            aria-controls="geofence-tabpanel-0"
          />
          <Tab 
            label="Mapa y Lista" 
            icon={<MapIcon />} 
            iconPosition="start"
            id="geofence-tab-1"
            aria-controls="geofence-tabpanel-1"
          />
          <Tab 
            label="Analytics Detallados" 
            icon={<AssessmentIcon />} 
            iconPosition="start"
            id="geofence-tab-2"
            aria-controls="geofence-tabpanel-2"
          />
          <Tab 
            label="Verificación Manual" 
            icon={<RefreshIcon />} 
            iconPosition="start"
            id="geofence-tab-3"
            aria-controls="geofence-tabpanel-3"
          />
        </Tabs>
      </Box>

      {/* Tab Panels */}
      <TabPanel value={currentTab} index={0}>
        {/* Dashboard de Métricas */}
        <GeofenceMetricsDashboard />
      </TabPanel>

      <TabPanel value={currentTab} index={1}>
        {/* Vista original: Mapa y Lista */}
        <Grid container spacing={3}>
          {/* Mapa */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardHeader
                title={t('geofence.mapTitle')}
                avatar={<MapIcon color="primary" />}
              />
              <CardContent sx={{ height: '500px' }}>
                <GeofenceMap 
                  geofences={geofences} 
                  onGeofenceClick={(geofence) => navigate(`/geofences/${geofence.id}`)}
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Lista de geocercas */}
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardHeader
                title={t('geofence.listTitle')}
                subheader={`${geofences.length} geocercas encontradas`}
              />
              <CardContent sx={{ pt: 0, maxHeight: '500px', overflow: 'auto' }}>
                {error && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                  </Alert>
                )}

                {/* Asegurar que geofences es un array antes de usar .map() */}
                {!Array.isArray(geofences) || geofences.length === 0 ? (
                  <Alert severity="info">
                    {t('geofence.noGeofences')}
                  </Alert>
                ) : (
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Nombre</TableCell>
                          <TableCell>Estado</TableCell>
                          <TableCell>Acciones</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {geofences.map((geofence) => (
                          <TableRow key={geofence.id}>
                            <TableCell>
                              <Typography variant="body2" fontWeight={500}>
                                {geofence.name}
                              </Typography>
                              {geofence.description && (
                                <Typography variant="caption" color="text.secondary" display="block">
                                  {geofence.description}
                                </Typography>
                              )}
                            </TableCell>
                            <TableCell>
                              <FormControlLabel
                                control={
                                  <Switch
                                    checked={geofence.is_active}
                                    onChange={() => handleStatusToggle(geofence.id, geofence.is_active)}
                                    size="small"
                                  />
                                }
                                label=""
                                sx={{ m: 0 }}
                              />
                              {getStatusChip(geofence.is_active)}
                            </TableCell>
                            <TableCell>
                              <Box display="flex" gap={0.5}>
                                <Tooltip title="Ver detalles">
                                  <IconButton size="small" onClick={() => handleView(geofence)}>
                                    <ViewIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Editar">
                                  <IconButton size="small" onClick={() => handleEdit(geofence)}>
                                    <EditIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Eliminar">
                                  <IconButton size="small" onClick={() => handleDeleteClick(geofence.id)}>
                                    <DeleteIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              </Box>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={currentTab} index={2}>
        {/* Analytics Detallados - Placeholder por ahora */}
        <Alert severity="info" sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" gutterBottom>
            Analytics Detallados por Geocerca
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Esta funcionalidad estará disponible próximamente. Incluirá análisis detallados 
            de cada geocerca con gráficos de actividad, patrones de entrada/salida y más.
          </Typography>
        </Alert>
      </TabPanel>

      <TabPanel value={currentTab} index={3}>
        {/* Verificación Manual */}
        {selectedGeofenceForChecker ? (
          <ManualGeofenceChecker
            geofenceId={selectedGeofenceForChecker.id}
            geofenceName={selectedGeofenceForChecker.name}
            onResultsUpdate={(results) => {
              console.log('Manual check results:', results);
              showSnackbar(
                `Verificación completa: ${results.devices_checked} dispositivos verificados`,
                'success'
              );
            }}
          />
        ) : (
          <Alert severity="info" sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" gutterBottom>
              Verificación Manual de Geocercas
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Selecciona una geocerca desde la pestaña "Mapa y Lista" para realizar 
              una verificación manual de todos los dispositivos asociados.
            </Typography>
            <Button
              variant="outlined"
              onClick={() => setCurrentTab(1)}
              sx={{ mt: 2 }}
            >
              Ir a Mapa y Lista
            </Button>
          </Alert>
        )}
      </TabPanel>

      {/* Formulario de geocerca */}
      {isFormOpen && (
        <GeofenceForm
          open={isFormOpen}
          onClose={() => setIsFormOpen(false)}
          onSubmit={handleFormSubmit}
          initialData={selectedGeofence}
        />
      )}

      {/* Diálogo de confirmación de eliminación */}
      <ConfirmationDialog
        open={isDeleteDialogOpen}
        title={t('geofence.deleteConfirmTitle')}
        message={t('geofence.deleteConfirmMessage')}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setIsDeleteDialogOpen(false)}
      />

      {/* Snackbar para notificaciones */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default GeofenceManager;

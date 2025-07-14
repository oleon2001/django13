import React, { useState, useEffect } from 'react';
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
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Map as MapIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { geofenceService, Geofence, GeofenceFilterParams } from '../../services/geofenceService';
import { GeofenceMap } from './GeofenceMap';
import GeofenceForm from './GeofenceForm';
import ConfirmationDialog from '../Modals/ConfirmationDialog';

const GeofenceManager: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  // Estados
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

  // Cargar geocercas
  const loadGeofences = async (filters: GeofenceFilterParams = {}) => {
    try {
      setLoading(true);
      setError(null);
      const data = await geofenceService.getAll(filters);
      setGeofences(data);
    } catch (err) {
      console.error('Error loading geofences:', err);
      setError(t('geofence.errors.loadError'));
      showSnackbar(t('geofence.errors.loadError'), 'error');
    } finally {
      setLoading(false);
    }
  };

  // Cargar datos iniciales
  useEffect(() => {
    loadGeofences();
  }, []);

  // Manejadores de eventos
  const handleCreate = () => {
    setSelectedGeofence(null);
    setIsFormOpen(true);
  };

  const handleEdit = (geofence: Geofence) => {
    setSelectedGeofence(geofence);
    setIsFormOpen(true);
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

  const showSnackbar = (message: string, severity: 'success' | 'error' = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleSnackbarClose = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  // Renderizado condicional
  if (loading && geofences.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ my: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Encabezado */}
        <Grid item xs={12}>
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
        </Grid>

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
          <Card>
            <CardHeader
              title={t('geofence.listTitle')}
              subheader={`${geofences.length} ${t('geofence.itemsFound')}`}
              action={
                <Tooltip title={t('common.refresh')}>
                  <IconButton onClick={() => loadGeofences()}>
                    <RefreshIcon />
                  </IconButton>
                </Tooltip>
              }
            />
            <CardContent>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>{t('geofence.fields.name')}</TableCell>
                      <TableCell align="center">{t('geofence.fields.status')}</TableCell>
                      <TableCell align="right">{t('common.actions')}</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {geofences.length > 0 ? (
                      geofences.map((geofence) => (
                        <TableRow key={geofence.id} hover>
                          <TableCell>
                            <Typography variant="body2">{geofence.name}</Typography>
                            <Typography variant="caption" color="textSecondary">
                              {geofence.description || t('common.noDescription')}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <FormControlLabel
                              control={
                                <Switch
                                  checked={geofence.is_active}
                                  onChange={() => 
                                    handleStatusToggle(geofence.id, geofence.is_active)
                                  }
                                  color="primary"
                                  size="small"
                                />
                              }
                              label={geofence.is_active ? t('common.active') : t('common.inactive')}
                              labelPlacement="top"
                            />
                          </TableCell>
                          <TableCell align="right">
                            <Tooltip title={t('common.edit')}>
                              <IconButton 
                                size="small" 
                                onClick={() => handleEdit(geofence)}
                                color="primary"
                              >
                                <EditIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title={t('common.delete')}>
                              <IconButton 
                                size="small" 
                                onClick={() => handleDeleteClick(geofence.id)}
                                color="error"
                              >
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={3} align="center">
                          <Typography variant="body2" color="textSecondary">
                            {t('geofence.noGeofences')}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Formulario de geocerca */}
      <GeofenceForm
        open={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        onSubmit={handleFormSubmit}
        initialData={selectedGeofence}
      />

      {/* Diálogo de confirmación de eliminación */}
      <ConfirmationDialog
        open={isDeleteDialogOpen}
        title={t('geofence.deleteConfirmTitle')}
        message={t('geofence.deleteConfirmMessage')}
        onConfirm={handleDeleteConfirm}
        onCancel={() => {
          setIsDeleteDialogOpen(false);
          setGeofenceToDelete(null);
        }}
      />

      {/* Notificación */}
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

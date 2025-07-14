import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  FormControlLabel,
  Switch,
  Typography,
  Tabs,
  Tab,
  Box,
  Divider,
  Chip,
  CircularProgress,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useTranslation } from 'react-i18next';
import { Geofence, CreateGeofenceDTO, GeofenceType } from '../../types/geofence';
import { GeofenceMap } from './GeofenceMap';

// Tipos de geocercas disponibles
const GEOFENCE_TYPES: { value: GeofenceType; label: string }[] = [
  { value: 'circle', label: 'Círculo' },
  { value: 'polygon', label: 'Polígono' },
  { value: 'rectangle', label: 'Rectángulo' },
];

// Colores predefinidos para las geocercas
const COLOR_OPTIONS = [
  '#FF5252', // Rojo
  '#FF4081', // Rosa
  '#E040FB', // Púrpura
  '#7C4DFF', // Morado
  '#536DFE', // Azul
  '#448AFF', // Azul claro
  '#40C4FF', // Cian
  '#18FFFF', // Turquesa
  '#64FFDA', // Verde agua
  '#69F0AE', // Verde menta
  '#B2FF59', // Verde lima
  '#EEFF41', // Amarillo
  '#FFFF00', // Amarillo puro
  '#FFD740', // Ámbar
  '#FFAB40', // Naranja
  '#FF6E40', // Naranja oscuro
];

// Validación del formulario
const validationSchema = Yup.object({
  name: Yup.string().required('El nombre es requerido'),
  description: Yup.string(),
  type: Yup.string().oneOf(['circle', 'polygon', 'rectangle']).required('El tipo es requerido'),
  is_active: Yup.boolean(),
  color: Yup.string().required('El color es requerido'),
  stroke_width: Yup.number().min(1, 'El ancho debe ser al menos 1').max(10, 'El ancho máximo es 10'),
  stroke_color: Yup.string().required('El color del borde es requerido'),
  notify_on_entry: Yup.boolean(),
  notify_on_exit: Yup.boolean(),
  alert_on_entry: Yup.boolean(),
  alert_on_exit: Yup.boolean(),
  notification_cooldown: Yup.number().min(0, 'El tiempo de espera no puede ser negativo'),
});

interface GeofenceFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: CreateGeofenceDTO) => void;
  initialData?: Geofence | null;
  loading?: boolean;
}

const GeofenceForm: React.FC<GeofenceFormProps> = ({
  open,
  onClose,
  onSubmit,
  initialData,
  loading = false,
}) => {
  const { t } = useTranslation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  // Estados
  const [activeTab, setActiveTab] = useState(0);
  const [mapCenter, setMapCenter] = useState<[number, number]>([19.4326, -99.1332]); // CDMX por defecto
  const [drawingMode, setDrawingMode] = useState<GeofenceType>('circle');
  const [drawnGeometry, setDrawnGeometry] = useState<any>(null);
  
  // Inicializar el formulario con Formik
  const formik = useFormik({
    initialValues: {
      name: initialData?.name || '',
      description: initialData?.description || '',
      type: initialData?.geometry?.type || 'circle',
      is_active: initialData?.is_active ?? true,
      color: initialData?.color || '#3388ff',
      stroke_width: initialData?.stroke_width || 2,
      stroke_color: initialData?.stroke_color || '#3388ff',
      notify_on_entry: initialData?.notify_on_entry ?? true,
      notify_on_exit: initialData?.notify_on_exit ?? true,
      alert_on_entry: initialData?.alert_on_entry ?? false,
      alert_on_exit: initialData?.alert_on_exit ?? false,
      notification_cooldown: initialData?.notification_cooldown || 300, // 5 minutos por defecto
      devices: initialData?.devices || [],
      notify_emails: initialData?.notify_emails || [],
      notify_sms: initialData?.notify_sms || [],
    },
    validationSchema,
    onSubmit: (values) => {
      if (!drawnGeometry && !initialData) {
        formik.setFieldError('type', 'Debe dibujar la geocerca en el mapa');
        return;
      }

      const geometry = drawnGeometry || initialData?.geometry;
      
      if (!geometry) {
        formik.setFieldError('type', 'Geometría no válida');
        return;
      }

      const geofenceData: CreateGeofenceDTO = {
        ...values,
        geometry,
      };

      onSubmit(geofenceData);
    },
    enableReinitialize: true,
  });

  // Efecto para sincronizar el modo de dibujo con el tipo seleccionado
  useEffect(() => {
    setDrawingMode(formik.values.type as GeofenceType);
  }, [formik.values.type]);

  // Efecto para manejar la inicialización con datos existentes
  useEffect(() => {
    if (initialData && initialData.geometry) {
      // Centrar el mapa en la geocerca existente
      if (initialData.geometry.type === 'circle') {
        const [center] = initialData.geometry.coordinates as [L.LatLngExpression, number];
        if (Array.isArray(center)) {
          setMapCenter([center[0], center[1]]);
        } else if ('lat' in center && 'lng' in center) {
          setMapCenter([center.lat, center.lng]);
        }
      } else if (initialData.geometry.coordinates.length > 0) {
        // Para polígonos y rectángulos, usar el primer punto como centro
        const firstPoint = initialData.geometry.coordinates[0] as [number, number];
        if (firstPoint && firstPoint.length >= 2) {
          setMapCenter([firstPoint[0], firstPoint[1]]);
        }
      }
    }
  }, [initialData]);

  // Manejadores de eventos
  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleGeometryCreated = (geometry: any) => {
    setDrawnGeometry(geometry);
  };

  const handleCancel = () => {
    formik.resetForm();
    setDrawnGeometry(null);
    onClose();
  };

  // Renderizar pestañas del formulario
  const renderTabContent = () => {
    switch (activeTab) {
      case 0: // Información básica
        return (
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                id="name"
                name="name"
                label={t('geofence.fields.name')}
                value={formik.values.name}
                onChange={formik.handleChange}
                error={formik.touched.name && Boolean(formik.errors.name)}
                helperText={formik.touched.name && formik.errors.name}
                margin="normal"
                variant="outlined"
                size="small"
              />
              
              <TextField
                fullWidth
                id="description"
                name="description"
                label={t('geofence.fields.description')}
                value={formik.values.description}
                onChange={formik.handleChange}
                error={formik.touched.description && Boolean(formik.errors.description)}
                helperText={formik.touched.description && formik.errors.description}
                margin="normal"
                variant="outlined"
                size="small"
                multiline
                rows={3}
              />
              
              <FormControl fullWidth margin="normal" size="small">
                <InputLabel id="geofence-type-label">
                  {t('geofence.fields.type')}
                </InputLabel>
                <Select
                  labelId="geofence-type-label"
                  id="type"
                  name="type"
                  value={formik.values.type}
                  onChange={formik.handleChange}
                  label={t('geofence.fields.type')}
                  error={formik.touched.type && Boolean(formik.errors.type)}
                >
                  {GEOFENCE_TYPES.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
                {formik.touched.type && formik.errors.type && (
                  <Typography color="error" variant="caption" sx={{ display: 'block', mt: 1 }}>
                    {formik.errors.type}
                  </Typography>
                )}
              </FormControl>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={formik.values.is_active}
                    onChange={(e) => formik.setFieldValue('is_active', e.target.checked)}
                    name="is_active"
                    color="primary"
                  />
                }
                label={t('geofence.fields.is_active')}
                sx={{ mt: 2, display: 'block' }}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                {t('geofence.appearance')}
              </Typography>
              
              <Box display="flex" alignItems="center" mb={2}>
                <Typography variant="body2" sx={{ minWidth: 120 }}>
                  {t('geofence.fields.color')}:
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1} ml={2}>
                  {COLOR_OPTIONS.map((color) => (
                    <Box
                      key={color}
                      width={24}
                      height={24}
                      bgcolor={color}
                      borderRadius="50%"
                      border={formik.values.color === color ? '2px solid #000' : '1px solid #ccc'}
                      onClick={() => formik.setFieldValue('color', color)}
                      sx={{ cursor: 'pointer' }}
                    />
                  ))}
                </Box>
              </Box>
              
              <Box display="flex" alignItems="center" mb={2}>
                <Typography variant="body2" sx={{ minWidth: 120 }}>
                  {t('geofence.fields.stroke_color')}:
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1} ml={2}>
                  {COLOR_OPTIONS.map((color) => (
                    <Box
                      key={`stroke-${color}`}
                      width={24}
                      height={24}
                      bgcolor={color}
                      borderRadius="50%"
                      border={formik.values.stroke_color === color ? '2px solid #000' : '1px solid #ccc'}
                      onClick={() => formik.setFieldValue('stroke_color', color)}
                      sx={{ cursor: 'pointer' }}
                    />
                  ))}
                </Box>
              </Box>
              
              <TextField
                fullWidth
                id="stroke_width"
                name="stroke_width"
                label={t('geofence.fields.stroke_width')}
                type="number"
                value={formik.values.stroke_width}
                onChange={formik.handleChange}
                error={formik.touched.stroke_width && Boolean(formik.errors.stroke_width)}
                helperText={formik.touched.stroke_width && formik.errors.stroke_width}
                margin="normal"
                variant="outlined"
                size="small"
                InputProps={{
                  inputProps: { min: 1, max: 10, step: 1 },
                }}
              />
            </Grid>
          </Grid>
        );
        
      case 1: // Configuración de notificaciones
        return (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              {t('geofence.notification_settings')}
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formik.values.notify_on_entry}
                      onChange={(e) => formik.setFieldValue('notify_on_entry', e.target.checked)}
                      name="notify_on_entry"
                      color="primary"
                    />
                  }
                  label={t('geofence.fields.notify_on_entry')}
                  sx={{ display: 'block', mb: 2 }}
                />
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={formik.values.notify_on_exit}
                      onChange={(e) => formik.setFieldValue('notify_on_exit', e.target.checked)}
                      name="notify_on_exit"
                      color="primary"
                    />
                  }
                  label={t('geofence.fields.notify_on_exit')}
                  sx={{ display: 'block', mb: 2 }}
                />
                
                <TextField
                  fullWidth
                  id="notification_cooldown"
                  name="notification_cooldown"
                  label={t('geofence.fields.notification_cooldown')}
                  type="number"
                  value={formik.values.notification_cooldown}
                  onChange={formik.handleChange}
                  error={formik.touched.notification_cooldown && Boolean(formik.errors.notification_cooldown)}
                  helperText={
                    formik.touched.notification_cooldown && formik.errors.notification_cooldown
                      ? formik.errors.notification_cooldown
                      : t('geofence.help.notification_cooldown')
                  }
                  margin="normal"
                  variant="outlined"
                  size="small"
                  InputProps={{
                    endAdornment: <Typography variant="caption">segundos</Typography>,
                  }}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  {t('geofence.alert_settings')}
                </Typography>
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={formik.values.alert_on_entry}
                      onChange={(e) => formik.setFieldValue('alert_on_entry', e.target.checked)}
                      name="alert_on_entry"
                      color="secondary"
                    />
                  }
                  label={t('geofence.fields.alert_on_entry')}
                  sx={{ display: 'block', mb: 2 }}
                />
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={formik.values.alert_on_exit}
                      onChange={(e) => formik.setFieldValue('alert_on_exit', e.target.checked)}
                      name="alert_on_exit"
                      color="secondary"
                    />
                  }
                  label={t('geofence.fields.alert_on_exit')}
                  sx={{ display: 'block', mb: 2 }}
                />
              </Grid>
            </Grid>
            
            <Divider sx={{ my: 3 }} />
            
            <Typography variant="subtitle2" gutterBottom>
              {t('geofence.notification_recipients')}
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  id="notify_emails"
                  name="notify_emails"
                  label={t('geofence.fields.notify_emails')}
                  placeholder="email1@example.com, email2@example.com"
                  value={formik.values.notify_emails?.join(', ')}
                  onChange={(e) => {
                    const emails = e.target.value
                      .split(',')
                      .map((email) => email.trim())
                      .filter((email) => email);
                    formik.setFieldValue('notify_emails', emails);
                  }}
                  margin="normal"
                  variant="outlined"
                  size="small"
                  helperText={t('geofence.help.notify_emails')}
                />
                
                <Box mt={1}>
                  {formik.values.notify_emails?.map((email: string) => (
                    <Chip
                      key={email}
                      label={email}
                      onDelete={() => {
                        const filtered = formik.values.notify_emails?.filter((e: string) => e !== email) || [];
                        formik.setFieldValue('notify_emails', filtered);
                      }}
                      size="small"
                      sx={{ mr: 1, mb: 1 }}
                    />
                  ))}
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  id="notify_sms"
                  name="notify_sms"
                  label={t('geofence.fields.notify_sms')}
                  placeholder="+521234567890, +529876543210"
                  value={formik.values.notify_sms?.join(', ')}
                  onChange={(e) => {
                    const numbers = e.target.value
                      .split(',')
                      .map((num) => num.trim())
                      .filter((num) => num);
                    formik.setFieldValue('notify_sms', numbers);
                  }}
                  margin="normal"
                  variant="outlined"
                  size="small"
                  helperText={t('geofence.help.notify_sms')}
                />
                
                <Box mt={1}>
                  {formik.values.notify_sms?.map((number: string) => (
                    <Chip
                      key={number}
                      label={number}
                      onDelete={() => {
                        const filtered = formik.values.notify_sms?.filter((n: string) => n !== number) || [];
                        formik.setFieldValue('notify_sms', filtered);
                      }}
                      size="small"
                      sx={{ mr: 1, mb: 1 }}
                    />
                  ))}
                </Box>
              </Grid>
            </Grid>
          </Box>
        );
        
      case 2: // Mapa
        return (
          <Box sx={{ mt: 2, height: 400 }}>
            <Typography variant="subtitle2" gutterBottom>
              {t('geofence.draw_geofence')}
            </Typography>
            
            <GeofenceMap
              geofences={[]}
              center={mapCenter}
              height={350}
              onGeometryCreated={handleGeometryCreated}
              initialGeometry={initialData?.geometry}
            />
            
            <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mt: 1 }}>
              {t(`geofence.help.drawing_${drawingMode}`)}
            </Typography>
            
            {!drawnGeometry && !initialData?.geometry && (
              <Typography color="error" variant="caption" sx={{ display: 'block', mt: 1 }}>
                {t('geofence.errors.draw_required')}
              </Typography>
            )}
          </Box>
        );
        
      case 3: // Dispositivos
        return (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              {t('geofence.assigned_devices')}
            </Typography>
            
            <Typography variant="body2" color="textSecondary" paragraph>
              {t('geofence.help.assigned_devices')}
            </Typography>
            
            {/* Aquí iría la lista de dispositivos seleccionables */}
            <Box
              border={1}
              borderColor="divider"
              borderRadius={1}
              p={2}
              minHeight={200}
              display="flex"
              alignItems="center"
              justifyContent="center"
            >
              <Typography color="textSecondary">
                {t('geofence.no_devices_available')}
              </Typography>
            </Box>
          </Box>
        );
        
      default:
        return null;
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      fullScreen={isMobile}
      aria-labelledby="geofence-form-dialog-title"
    >
      <form onSubmit={formik.handleSubmit}>
        <DialogTitle id="geofence-form-dialog-title">
          {initialData ? t('geofence.edit_title') : t('geofence.create_title')}
        </DialogTitle>
        
        <DialogContent dividers>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
            variant="scrollable"
            scrollButtons="auto"
            aria-label="geofence form tabs"
          >
            <Tab label={t('geofence.tabs.basic_info')} />
            <Tab label={t('geofence.tabs.notifications')} />
            <Tab label={t('geofence.tabs.map')} />
            <Tab label={t('geofence.tabs.devices')} />
          </Tabs>
          
          <Box sx={{ py: 2 }}>
            {renderTabContent()}
          </Box>
        </DialogContent>
        
        <DialogActions sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Button 
            onClick={handleCancel} 
            color="inherit"
            disabled={loading}
          >
            {t('common.cancel')}
          </Button>
          
          {activeTab > 0 && (
            <Button 
              onClick={() => setActiveTab(activeTab - 1)}
              color="primary"
              disabled={loading}
            >
              {t('common.back')}
            </Button>
          )}
          
          {activeTab < 3 ? (
            <Button 
              onClick={() => setActiveTab(activeTab + 1)}
              color="primary"
              variant="outlined"
              disabled={loading}
            >
              {t('common.next')}
            </Button>
          ) : (
            <Button
              type="submit"
              color="primary"
              variant="contained"
              disabled={loading || (!drawnGeometry && !initialData?.geometry)}
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
            >
              {initialData ? t('common.update') : t('common.create')}
            </Button>
          )}
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default GeofenceForm;

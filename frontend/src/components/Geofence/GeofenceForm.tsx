import React, { useState, useEffect, useCallback } from 'react';
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
  Box,
  Divider,
  Chip,
  CircularProgress,
  useTheme,
  useMediaQuery,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
  Checkbox,
  Autocomplete,
  InputAdornment,
  Paper,
  Stack,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Fab,
  Zoom,
  Collapse,
  Alert,
} from '@mui/material';
import {
  LocationOn as LocationIcon,
  DevicesOther as DevicesIcon,
  Palette as PaletteIcon,
  Notifications as NotificationsIcon,
  Map as MapIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
  MyLocation as MyLocationIcon,
  Place as PlaceIcon,
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useTranslation } from 'react-i18next';
import { Geofence, CreateGeofenceDTO, GeofenceType } from '../../types/geofence';
import { Device } from '../../types';
import { deviceService } from '../../services/deviceService';
import { locationService, LocationSuggestion } from '../../services/locationService';
import GeofenceDrawingMap from './GeofenceDrawingMap';

// Tipos de geocercas disponibles
const GEOFENCE_TYPES: { value: GeofenceType; label: string; icon: string }[] = [
  { value: 'circle', label: 'Círculo', icon: '⭕' },
  { value: 'polygon', label: 'Polígono', icon: '🔷' },
  { value: 'rectangle', label: 'Rectángulo', icon: '▬' },
];

// Colores predefinidos con nombres
const COLOR_OPTIONS = [
  { color: '#FF5252', name: 'Rojo' },
  { color: '#E91E63', name: 'Rosa' },
  { color: '#9C27B0', name: 'Púrpura' },
  { color: '#673AB7', name: 'Morado' },
  { color: '#3F51B5', name: 'Índigo' },
  { color: '#2196F3', name: 'Azul' },
  { color: '#03A9F4', name: 'Azul claro' },
  { color: '#00BCD4', name: 'Cian' },
  { color: '#009688', name: 'Verde azulado' },
  { color: '#4CAF50', name: 'Verde' },
  { color: '#8BC34A', name: 'Verde lima' },
  { color: '#CDDC39', name: 'Lima' },
  { color: '#FFEB3B', name: 'Amarillo' },
  { color: '#FFC107', name: 'Ámbar' },
  { color: '#FF9800', name: 'Naranja' },
  { color: '#FF5722', name: 'Naranja oscuro' },
];

// Steps del wizard
const STEPS = [
  { label: 'Información Básica', icon: <LocationIcon /> },
  { label: 'Ubicación', icon: <MapIcon /> },
  { label: 'Dispositivos', icon: <DevicesIcon /> },
  { label: 'Notificaciones', icon: <NotificationsIcon /> },
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
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // Estados principales
  const [activeStep, setActiveStep] = useState(0);
  const [devices, setDevices] = useState<Device[]>([]);
  const [selectedDevices, setSelectedDevices] = useState<number[]>([]);
  const [devicesLoading, setDevicesLoading] = useState(false);
  const [mapCenter, setMapCenter] = useState<[number, number]>([19.4326, -99.1332]);
  const [drawnGeometry, setDrawnGeometry] = useState<any>(null);
  const [locationSearch, setLocationSearch] = useState('');
  const [locationSuggestions, setLocationSuggestions] = useState<LocationSuggestion[]>([]);
  const [isSearchingLocation, setIsSearchingLocation] = useState(false);
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);

  // Inicializar el formulario con Formik
  const formik = useFormik({
    initialValues: {
      name: initialData?.name || '',
      description: initialData?.description || '',
      type: (initialData?.geometry?.type as GeofenceType) || 'circle',
      is_active: initialData?.is_active ?? true,
      color: initialData?.color || '#2196F3',
      stroke_width: initialData?.stroke_width || 2,
      stroke_color: initialData?.stroke_color || '#2196F3',
      notify_on_entry: initialData?.notify_on_entry ?? true,
      notify_on_exit: initialData?.notify_on_exit ?? true,
      alert_on_entry: initialData?.alert_on_entry ?? false,
      alert_on_exit: initialData?.alert_on_exit ?? false,
      notification_cooldown: initialData?.notification_cooldown || 300,
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
        devices: selectedDevices,
      };

      onSubmit(geofenceData);
    },
    enableReinitialize: true,
  });

  // Cargar dispositivos al abrir el formulario
  useEffect(() => {
    if (open) {
      loadDevices();
      if (initialData?.devices) {
        setSelectedDevices(initialData.devices);
      }
    }
  }, [open]);

  // Búsqueda de ubicación con Google Places
  const searchLocation = useCallback(async (query: string) => {
    if (!query || query.length < 3) {
      setLocationSuggestions([]);
      return;
    }

    setIsSearchingLocation(true);
    
    try {
      const suggestions = await locationService.searchLocations(query);
      setLocationSuggestions(suggestions);
    } catch (error) {
      console.error('Error searching locations:', error);
      setLocationSuggestions([]);
    } finally {
      setIsSearchingLocation(false);
    }
  }, []);

  // Cargar dispositivos disponibles
  const loadDevices = async () => {
    try {
      setDevicesLoading(true);
      const deviceList = await deviceService.getAll();
      setDevices(deviceList || []);
    } catch (error) {
      console.error('Error loading devices:', error);
    } finally {
      setDevicesLoading(false);
    }
  };

  // Manejar selección de ubicación
  const handleLocationSelect = async (suggestion: LocationSuggestion) => {
    setLocationSearch(suggestion.description);
    setLocationSuggestions([]);
    
    try {
      const details = await locationService.getPlaceDetails(suggestion.place_id);
      if (details) {
        const { lat, lng } = details.geometry.location;
        setMapCenter([lat, lng]);
      }
    } catch (error) {
      console.error('Error getting place details:', error);
    }
  };

  // Obtener ubicación actual
  const getCurrentLocation = async () => {
    try {
      const location = await locationService.getCurrentLocation();
      if (location) {
        setMapCenter([location.lat, location.lng]);
        const address = await locationService.reverseGeocode(location.lat, location.lng);
        setLocationSearch(address);
      }
    } catch (error) {
      console.error('Error getting current location:', error);
    }
  };

  // Manejar selección de dispositivos
  const handleDeviceToggle = (deviceId: number) => {
    setSelectedDevices(prev => 
      prev.includes(deviceId)
        ? prev.filter(id => id !== deviceId)
        : [...prev, deviceId]
    );
  };

  // Manejar cambio de paso
  const handleNext = () => {
    if (activeStep === 1 && !drawnGeometry && !initialData) {
      formik.setFieldError('type', 'Debe dibujar la geocerca en el mapa');
      return;
    }
    setActiveStep(prev => prev + 1);
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handleGeometryCreated = (geometry: any) => {
    setDrawnGeometry(geometry);
  };

  const handleCancel = () => {
    formik.resetForm();
    setDrawnGeometry(null);
    setSelectedDevices([]);
    setActiveStep(0);
    setLocationSearch('');
    onClose();
  };

  // Renderizar el contenido de cada paso
  const renderStepContent = (step: number) => {
    switch (step) {
      case 0: // Información Básica
        return (
          <Card elevation={0} sx={{ backgroundColor: 'transparent' }}>
            <CardContent sx={{ p: 0 }}>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    id="name"
                    name="name"
                    label="Nombre de la geocerca"
                    placeholder="Ej. Zona Centro, Oficina Principal..."
                    value={formik.values.name}
                    onChange={formik.handleChange}
                    error={formik.touched.name && Boolean(formik.errors.name)}
                    helperText={formik.touched.name && formik.errors.name}
                    variant="outlined"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <LocationIcon color="primary" />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    id="description"
                    name="description"
                    label="Descripción (opcional)"
                    placeholder="Describe el propósito de esta geocerca..."
                    value={formik.values.description}
                    onChange={formik.handleChange}
                    error={formik.touched.description && Boolean(formik.errors.description)}
                    helperText={formik.touched.description && formik.errors.description}
                    variant="outlined"
                    multiline
                    rows={3}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <FormControl fullWidth variant="outlined">
                    <InputLabel>Tipo de geocerca</InputLabel>
                    <Select
                      id="type"
                      name="type"
                      value={formik.values.type}
                      onChange={formik.handleChange}
                      label="Tipo de geocerca"
                      error={formik.touched.type && Boolean(formik.errors.type)}
                    >
                      {GEOFENCE_TYPES.map((type) => (
                        <MenuItem key={type.value} value={type.value}>
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="h6">{type.icon}</Typography>
                            <Typography>{type.label}</Typography>
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formik.values.is_active}
                        onChange={(e) => formik.setFieldValue('is_active', e.target.checked)}
                        name="is_active"
                        color="primary"
                      />
                    }
                    label={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography>Geocerca activa</Typography>
                        {formik.values.is_active ? (
                          <Chip label="Activa" color="success" size="small" />
                        ) : (
                          <Chip label="Inactiva" color="default" size="small" />
                        )}
                      </Box>
                    }
                  />
                </Grid>

                {/* Configuración visual */}
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }}>
                    <Chip 
                      label="Apariencia" 
                      icon={<PaletteIcon />} 
                      color="primary" 
                      variant="outlined" 
                    />
                  </Divider>
                </Grid>

                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Color de relleno
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={1}>
                    {COLOR_OPTIONS.map((option) => (
                      <Tooltip key={option.color} title={option.name}>
                        <IconButton
                          onClick={() => formik.setFieldValue('color', option.color)}
                          sx={{
                            width: 40,
                            height: 40,
                            bgcolor: option.color,
                            border: formik.values.color === option.color ? '3px solid #000' : '1px solid #ccc',
                            '&:hover': {
                              transform: 'scale(1.1)',
                            },
                          }}
                        />
                      </Tooltip>
                    ))}
                  </Box>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Color del borde
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={1}>
                    {COLOR_OPTIONS.slice(0, 8).map((option) => (
                      <Tooltip key={`stroke-${option.color}`} title={option.name}>
                        <IconButton
                          onClick={() => formik.setFieldValue('stroke_color', option.color)}
                          sx={{
                            width: 32,
                            height: 32,
                            bgcolor: option.color,
                            border: formik.values.stroke_color === option.color ? '2px solid #000' : '1px solid #ccc',
                          }}
                        />
                      </Tooltip>
                    ))}
                  </Box>
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    id="stroke_width"
                    name="stroke_width"
                    label="Grosor del borde"
                    type="number"
                    value={formik.values.stroke_width}
                    onChange={formik.handleChange}
                    error={formik.touched.stroke_width && Boolean(formik.errors.stroke_width)}
                    helperText={formik.touched.stroke_width && formik.errors.stroke_width}
                    variant="outlined"
                    InputProps={{
                      inputProps: { min: 1, max: 10, step: 1 },
                      endAdornment: <InputAdornment position="end">px</InputAdornment>,
                    }}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        );

      case 1: // Ubicación
        return (
          <Card elevation={0} sx={{ backgroundColor: 'transparent' }}>
            <CardContent sx={{ p: 0 }}>
              <Grid container spacing={3}>
                {/* Búsqueda de ubicación */}
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                    <PlaceIcon color="primary" />
                    Buscar ubicación
                  </Typography>
                  
                  <Autocomplete
                    freeSolo
                    options={locationSuggestions}
                    getOptionLabel={(option) => 
                      typeof option === 'string' ? option : option.description
                    }
                    renderOption={(props, option) => (
                      <Box component="li" {...props}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                          <LocationIcon color="action" />
                          <Box>
                            <Typography variant="body1">
                              {option.structured_formatting.main_text}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {option.structured_formatting.secondary_text}
                            </Typography>
                          </Box>
                        </Box>
                      </Box>
                    )}
                    onInputChange={(event, newInputValue) => {
                      setLocationSearch(newInputValue);
                      searchLocation(newInputValue);
                    }}
                    onChange={(event, newValue) => {
                      if (typeof newValue !== 'string') {
                        handleLocationSelect(newValue as LocationSuggestion);
                      }
                    }}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        placeholder="Busca una dirección, ciudad o lugar..."
                        variant="outlined"
                        InputProps={{
                          ...params.InputProps,
                          startAdornment: (
                            <InputAdornment position="start">
                              <SearchIcon />
                            </InputAdornment>
                          ),
                          endAdornment: (
                            <InputAdornment position="end">
                              {isSearchingLocation ? (
                                <CircularProgress size={20} />
                              ) : (
                                <Tooltip title="Usar mi ubicación">
                                  <IconButton onClick={getCurrentLocation}>
                                    <MyLocationIcon />
                                  </IconButton>
                                </Tooltip>
                              )}
                            </InputAdornment>
                          ),
                        }}
                      />
                    )}
                  />
                </Grid>

                {/* Mapa para dibujar */}
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                    <MapIcon color="primary" />
                    Dibujar geocerca
                  </Typography>
                  
                  <Paper elevation={2} sx={{ p: 2, borderRadius: 2 }}>
                    <Alert severity="info" sx={{ mb: 2 }}>
                      <Typography variant="body2">
                        <strong>Instrucciones:</strong>
                        {formik.values.type === 'circle' && ' Haz clic y arrastra para crear un círculo'}
                        {formik.values.type === 'polygon' && ' Haz clic para agregar puntos, doble clic para finalizar'}
                        {formik.values.type === 'rectangle' && ' Haz clic y arrastra para crear un rectángulo'}
                      </Typography>
                    </Alert>
                    
                    <Box sx={{ height: 400, borderRadius: 1, overflow: 'hidden' }}>
                      <GeofenceDrawingMap
                        center={mapCenter}
                        height={400}
                        onGeometryCreated={handleGeometryCreated}
                        initialGeometry={initialData?.geometry}
                      />
                    </Box>
                    
                    {drawnGeometry && (
                      <Alert severity="success" sx={{ mt: 2 }}>
                        <Typography variant="body2">
                          ✅ Geocerca dibujada correctamente
                        </Typography>
                      </Alert>
                    )}
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        );

      case 2: // Dispositivos
        return (
          <Card elevation={0} sx={{ backgroundColor: 'transparent' }}>
            <CardContent sx={{ p: 0 }}>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                <DevicesIcon color="primary" />
                Seleccionar dispositivos
              </Typography>
              
              <Typography variant="body2" color="text.secondary" paragraph>
                Selecciona qué dispositivos serán monitoreados por esta geocerca
              </Typography>

              {devicesLoading ? (
                <Box display="flex" justifyContent="center" p={4}>
                  <CircularProgress />
                </Box>
              ) : devices.length === 0 ? (
                <Alert severity="info">
                  No hay dispositivos disponibles. 
                  <Button href="/devices" target="_blank" color="primary" sx={{ ml: 1 }}>
                    Ir a Dispositivos
                  </Button>
                </Alert>
              ) : (
                <Paper variant="outlined" sx={{ maxHeight: 400, overflow: 'auto' }}>
                  <List>
                    {devices.map((device, index) => (
                      <ListItem
                        key={device.imei || index}
                        divider={index < devices.length - 1}
                        button
                        onClick={() => handleDeviceToggle(device.imei)}
                      >
                        <ListItemAvatar>
                          <Avatar
                            sx={{
                              bgcolor: device.connection_status === 'ONLINE' ? 'success.main' : 'grey.400',
                            }}
                          >
                            <DevicesIcon />
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={
                            <Box display="flex" alignItems="center" gap={1}>
                              <Typography variant="subtitle1">
                                {device.name || `Dispositivo ${device.imei}`}
                              </Typography>
                              <Chip
                                label={device.connection_status || 'OFFLINE'}
                                size="small"
                                color={device.connection_status === 'ONLINE' ? 'success' : 'default'}
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="caption" display="block">
                                IMEI: {device.imei}
                              </Typography>
                              {device.position && (
                                <Typography variant="caption" color="text.secondary">
                                  Última posición: {device.position.latitude.toFixed(4)}, {device.position.longitude.toFixed(4)}
                                </Typography>
                              )}
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          <Checkbox
                            edge="end"
                            checked={selectedDevices.includes(device.imei)}
                            onChange={() => handleDeviceToggle(device.imei)}
                          />
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                </Paper>
              )}

              {selectedDevices.length > 0 && (
                <Alert severity="success" sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    ✅ {selectedDevices.length} dispositivo(s) seleccionado(s)
                  </Typography>
                </Alert>
              )}
            </CardContent>
          </Card>
        );

      case 3: // Notificaciones
        return (
          <Card elevation={0} sx={{ backgroundColor: 'transparent' }}>
            <CardContent sx={{ p: 0 }}>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                <NotificationsIcon color="primary" />
                Configurar notificaciones
              </Typography>

              <Grid container spacing={3}>
                {/* Notificaciones básicas */}
                <Grid item xs={12} md={6}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      Eventos de entrada y salida
                    </Typography>
                    
                    <FormControlLabel
                      control={
                        <Switch
                          checked={formik.values.notify_on_entry}
                          onChange={(e) => formik.setFieldValue('notify_on_entry', e.target.checked)}
                          name="notify_on_entry"
                          color="primary"
                        />
                      }
                      label="Notificar al entrar"
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
                      label="Notificar al salir"
                      sx={{ display: 'block' }}
                    />
                  </Paper>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      Tiempo entre notificaciones
                    </Typography>
                    
                    <TextField
                      fullWidth
                      id="notification_cooldown"
                      name="notification_cooldown"
                      label="Segundos de espera"
                      type="number"
                      value={formik.values.notification_cooldown}
                      onChange={formik.handleChange}
                      error={formik.touched.notification_cooldown && Boolean(formik.errors.notification_cooldown)}
                      helperText="Tiempo mínimo entre notificaciones del mismo evento"
                      variant="outlined"
                      InputProps={{
                        endAdornment: <InputAdornment position="end">seg</InputAdornment>,
                        inputProps: { min: 0, max: 3600 },
                      }}
                    />
                  </Paper>
                </Grid>

                {/* Opciones avanzadas */}
                <Grid item xs={12}>
                  <Button
                    variant="outlined"
                    onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
                    startIcon={showAdvancedOptions ? <RemoveIcon /> : <AddIcon />}
                    fullWidth
                  >
                    Opciones avanzadas de notificación
                  </Button>
                  
                  <Collapse in={showAdvancedOptions}>
                    <Box sx={{ mt: 2 }}>
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                          <TextField
                            fullWidth
                            id="notify_emails"
                            name="notify_emails"
                            label="Emails de notificación"
                            placeholder="email1@example.com, email2@example.com"
                            value={formik.values.notify_emails?.join(', ')}
                            onChange={(e) => {
                              const emails = e.target.value
                                .split(',')
                                .map((email) => email.trim())
                                .filter((email) => email);
                              formik.setFieldValue('notify_emails', emails);
                            }}
                            variant="outlined"
                            helperText="Separar múltiples emails con comas"
                          />
                        </Grid>
                        
                        <Grid item xs={12} md={6}>
                          <TextField
                            fullWidth
                            id="notify_sms"
                            name="notify_sms"
                            label="Números SMS"
                            placeholder="+521234567890, +529876543210"
                            value={formik.values.notify_sms?.join(', ')}
                            onChange={(e) => {
                              const numbers = e.target.value
                                .split(',')
                                .map((num) => num.trim())
                                .filter((num) => num);
                              formik.setFieldValue('notify_sms', numbers);
                            }}
                            variant="outlined"
                            helperText="Separar múltiples números con comas"
                          />
                        </Grid>
                      </Grid>
                    </Box>
                  </Collapse>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        );

      default:
        return null;
    }
  };

  const isStepComplete = (step: number) => {
    switch (step) {
      case 0:
        return formik.values.name && formik.values.type;
      case 1:
        return drawnGeometry || initialData?.geometry;
      case 2:
        return selectedDevices.length > 0;
      case 3:
        return true; // Las notificaciones son opcionales
      default:
        return false;
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      fullScreen={isMobile}
      PaperProps={{
        sx: {
          borderRadius: isMobile ? 0 : 3,
          minHeight: isMobile ? '100vh' : 600,
        },
      }}
    >
      <form onSubmit={formik.handleSubmit}>
        <DialogTitle sx={{ 
          background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
          color: 'white',
          textAlign: 'center',
          py: 3
        }}>
          <Typography variant="h5" component="h1" fontWeight="bold">
            {initialData ? '✏️ Editar Geocerca' : '✨ Crear Nueva Geocerca'}
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9, mt: 1 }}>
            {initialData ? 'Modifica la configuración de tu geocerca' : 'Configura una nueva área de monitoreo'}
          </Typography>
        </DialogTitle>
        
        <DialogContent sx={{ p: 0 }}>
          {/* Stepper horizontal en desktop, vertical en mobile */}
          <Box sx={{ p: 3, backgroundColor: 'grey.50' }}>
            <Stepper 
              activeStep={activeStep} 
              orientation={isMobile ? 'vertical' : 'horizontal'}
              sx={{ mb: 3 }}
            >
              {STEPS.map((step, index) => (
                <Step key={step.label} completed={isStepComplete(index)}>
                  <StepLabel
                    icon={
                      <Avatar
                        sx={{
                          bgcolor: activeStep === index 
                            ? 'primary.main' 
                            : isStepComplete(index) 
                              ? 'success.main' 
                              : 'grey.300',
                          color: 'white',
                          width: 40,
                          height: 40,
                        }}
                      >
                        {isStepComplete(index) ? <CheckCircleIcon /> : step.icon}
                      </Avatar>
                    }
                  >
                    <Typography variant="subtitle1" fontWeight="medium">
                      {step.label}
                    </Typography>
                  </StepLabel>
                  {isMobile && (
                    <StepContent>
                      <Box sx={{ mt: 2 }}>
                        {renderStepContent(index)}
                      </Box>
                    </StepContent>
                  )}
                </Step>
              ))}
            </Stepper>
          </Box>

          {/* Contenido del paso actual (solo en desktop) */}
          {!isMobile && (
            <Box sx={{ p: 3, minHeight: 400 }}>
              <Zoom in={true} timeout={300}>
                <Box>
                  {renderStepContent(activeStep)}
                </Box>
              </Zoom>
            </Box>
          )}
        </DialogContent>
        
        <DialogActions sx={{ 
          p: 3, 
          borderTop: 1, 
          borderColor: 'divider',
          backgroundColor: 'grey.50'
        }}>
          <Box display="flex" justifyContent="space-between" width="100%">
            <Button 
              onClick={handleCancel} 
              color="inherit"
              disabled={loading}
              startIcon={<ClearIcon />}
            >
              Cancelar
            </Button>
            
            <Box display="flex" gap={1}>
              {activeStep > 0 && (
                <Button 
                  onClick={handleBack}
                  color="primary"
                  disabled={loading}
                >
                  Anterior
                </Button>
              )}
              
              {activeStep < STEPS.length - 1 ? (
                <Button 
                  onClick={handleNext}
                  color="primary"
                  variant="contained"
                  disabled={loading || !isStepComplete(activeStep)}
                >
                  Siguiente
                </Button>
              ) : (
                <Button
                  type="submit"
                  color="primary"
                  variant="contained"
                  disabled={loading || !drawnGeometry && !initialData?.geometry}
                  startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
                  sx={{ minWidth: 120 }}
                >
                  {initialData ? 'Actualizar' : 'Crear Geocerca'}
                </Button>
              )}
            </Box>
          </Box>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default GeofenceForm;

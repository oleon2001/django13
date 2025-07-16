import React, { useState, useEffect } from 'react';
import {
  Alert,
  Badge,
  Box,
  Card,
  CardContent,
  Chip,
  Collapse,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Snackbar,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  LocationOn as LocationIcon,
  Notifications as NotificationsIcon,
  Logout as ExitIcon,
  Login as EntryIcon,
  Clear as ClearIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Map as MapIcon,
} from '@mui/icons-material';
import { useGeofenceWebSocket } from '../../hooks/useGeofenceWebSocket';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

interface GeofenceNotificationsProps {
  showInline?: boolean;
  maxItems?: number;
}

const GeofenceNotifications: React.FC<GeofenceNotificationsProps> = ({
  showInline = false,
  maxItems = 10
}) => {
  const {
    isConnected,
    lastEvent,
    lastNotification,
    lastAlert,
    events,
    clearEvents,
  } = useGeofenceWebSocket();

  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'info' | 'warning' | 'error' | 'success'>('info');
  const [alertDialogOpen, setAlertDialogOpen] = useState(false);
  const [currentAlert, setCurrentAlert] = useState<any>(null);
  const [expanded, setExpanded] = useState(false);

  // Handle new events
  useEffect(() => {
    if (lastEvent) {
      const message = `${lastEvent.device_name} ${lastEvent.event_type === 'ENTRY' ? 'entró en' : 'salió de'} ${lastEvent.geofence_name}`;
      setSnackbarMessage(message);
      setSnackbarSeverity(lastEvent.event_type === 'ENTRY' ? 'success' : 'warning');
      setSnackbarOpen(true);
    }
  }, [lastEvent]);

  // Handle notifications
  useEffect(() => {
    if (lastNotification) {
      setSnackbarMessage(lastNotification.message);
      setSnackbarSeverity('info');
      setSnackbarOpen(true);
    }
  }, [lastNotification]);

  // Handle alerts
  useEffect(() => {
    if (lastAlert) {
      setCurrentAlert(lastAlert);
      if (!lastAlert.auto_close) {
        setAlertDialogOpen(true);
      } else {
        setSnackbarMessage(lastAlert.message);
        setSnackbarSeverity(lastAlert.alert_level === 'warning' ? 'warning' : 'info');
        setSnackbarOpen(true);
      }
    }
  }, [lastAlert]);

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  const handleAlertDialogClose = () => {
    setAlertDialogOpen(false);
    setCurrentAlert(null);
  };

  const handleClearEvents = () => {
    clearEvents();
  };

  const handleToggleExpanded = () => {
    setExpanded(!expanded);
  };

  const openGoogleMaps = (lat: number, lng: number) => {
    const url = `https://www.google.com/maps?q=${lat},${lng}`;
    window.open(url, '_blank');
  };

  const getEventIcon = (eventType: 'ENTRY' | 'EXIT') => {
    return eventType === 'ENTRY' ? (
      <EntryIcon sx={{ color: 'success.main' }} />
    ) : (
      <ExitIcon sx={{ color: 'warning.main' }} />
    );
  };

  const getEventColor = (eventType: 'ENTRY' | 'EXIT') => {
    return eventType === 'ENTRY' ? 'success' : 'warning';
  };

  const formatEventTime = (timestamp: string) => {
    try {
      return format(new Date(timestamp), 'HH:mm:ss dd/MM', { locale: es });
    } catch (error) {
      return timestamp;
    }
  };

  if (showInline) {
    return (
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Badge 
                color={isConnected ? 'success' : 'error'} 
                variant="dot"
                sx={{ mr: 1 }}
              >
                <NotificationsIcon />
              </Badge>
              <Typography variant="h6">
                Eventos de Geocercas
              </Typography>
            </Box>
            <Box>
              <IconButton
                size="small"
                onClick={handleToggleExpanded}
                aria-label="expand"
              >
                {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
              {events.length > 0 && (
                <IconButton
                  size="small"
                  onClick={handleClearEvents}
                  aria-label="clear"
                >
                  <ClearIcon />
                </IconButton>
              )}
            </Box>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Chip
              size="small"
              label={isConnected ? 'Conectado' : 'Desconectado'}
              color={isConnected ? 'success' : 'error'}
            />
            <Chip
              size="small"
              label={`${events.length} eventos`}
              variant="outlined"
            />
          </Box>

          <Collapse in={expanded} timeout="auto" unmountOnExit>
            {events.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No hay eventos recientes
              </Typography>
            ) : (
              <List dense>
                {events.slice(0, maxItems).map((event, index) => (
                  <ListItem
                    key={`${event.id}-${index}`}
                    sx={{
                      border: 1,
                      borderColor: 'divider',
                      borderRadius: 1,
                      mb: 1,
                      '&:last-child': { mb: 0 }
                    }}
                    secondaryAction={
                      event.position && (
                        <IconButton
                          edge="end"
                          size="small"
                          onClick={() => openGoogleMaps(event.position[0], event.position[1])}
                          title="Ver en Google Maps"
                        >
                          <MapIcon />
                        </IconButton>
                      )
                    }
                  >
                    <ListItemIcon>
                      {getEventIcon(event.event_type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" component="span">
                            {event.device_name}
                          </Typography>
                          <Chip
                            size="small"
                            label={event.event_type === 'ENTRY' ? 'Entrada' : 'Salida'}
                            color={getEventColor(event.event_type)}
                          />
                          <Typography variant="body2" component="span">
                            {event.geofence_name}
                          </Typography>
                        </Box>
                      }
                      secondary={formatEventTime(event.timestamp)}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Collapse>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      {/* Snackbar para notificaciones */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbarSeverity}
          variant="filled"
          icon={<LocationIcon />}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>

      {/* Dialog para alertas importantes */}
      <Dialog
        open={alertDialogOpen}
        onClose={handleAlertDialogClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <LocationIcon color="warning" />
            {currentAlert?.title}
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            {currentAlert?.message}
          </Typography>
          {currentAlert?.data && (
            <Box>
              <Typography variant="body2" color="text.secondary">
                <strong>Dispositivo:</strong> {currentAlert.data.device_name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Geocerca:</strong> {currentAlert.data.geofence_name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Evento:</strong> {currentAlert.data.event_type === 'ENTRY' ? 'Entrada' : 'Salida'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Hora:</strong> {formatEventTime(currentAlert.data.timestamp)}
              </Typography>
              {currentAlert.data.position && (
                <Button
                  startIcon={<MapIcon />}
                  onClick={() => openGoogleMaps(currentAlert.data.position[0], currentAlert.data.position[1])}
                  sx={{ mt: 1 }}
                >
                  Ver ubicación
                </Button>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleAlertDialogClose} variant="contained">
            Entendido
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default GeofenceNotifications; 
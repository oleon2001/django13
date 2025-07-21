import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Typography,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Divider,
  Collapse,
  Tooltip,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  DevicesOther as DevicesIcon,
} from '@mui/icons-material';
import { geofenceService } from '../../services/geofenceService';
import { ManualGeofenceCheck, GeofenceEvent } from '../../types/geofence';

interface ManualGeofenceCheckerProps {
  geofenceId: number;
  geofenceName?: string;
  onResultsUpdate?: (results: ManualGeofenceCheck) => void;
}

interface EventListProps {
  events: GeofenceEvent[];
}

const EventList: React.FC<EventListProps> = ({ events }) => {
  const [expanded, setExpanded] = useState(false);

  if (!events || events.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        No se generaron eventos
      </Typography>
    );
  }

  const displayEvents = expanded ? events : events.slice(0, 3);

  return (
    <Box>
      <List dense>
        {displayEvents.map((event, index) => (
          <ListItem key={event.id || index} sx={{ pl: 0 }}>
            <ListItemIcon sx={{ minWidth: 32 }}>
              {event.event_type === 'ENTRY' ? (
                <CheckCircleIcon color="success" fontSize="small" />
              ) : (
                <WarningIcon color="warning" fontSize="small" />
              )}
            </ListItemIcon>
            <ListItemText
              primary={
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography variant="body2" fontWeight={500}>
                    {event.event_type === 'ENTRY' ? 'Entrada' : 'Salida'}
                  </Typography>
                  <Chip
                    label={event.event_type}
                    size="small"
                    color={event.event_type === 'ENTRY' ? 'success' : 'warning'}
                    variant="outlined"
                  />
                </Box>
              }
              secondary={
                <Typography variant="caption" color="text.secondary">
                  {new Date(event.timestamp).toLocaleString()}
                </Typography>
              }
            />
          </ListItem>
        ))}
      </List>
      
      {events.length > 3 && (
        <Button
          size="small"
          onClick={() => setExpanded(!expanded)}
          startIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          sx={{ mt: 1 }}
        >
          {expanded ? 'Mostrar menos' : `Ver ${events.length - 3} eventos más`}
        </Button>
      )}
    </Box>
  );
};

const DeviceResultCard: React.FC<{
  result: ManualGeofenceCheck['results'][0];
}> = ({ result }) => {
  const [expanded, setExpanded] = useState(false);
  
  const getStatusColor = (eventsGenerated: number) => {
    if (eventsGenerated > 0) return 'warning';
    return 'success';
  };

  const getStatusIcon = (eventsGenerated: number) => {
    if (eventsGenerated > 0) return <WarningIcon color="warning" />;
    return <CheckCircleIcon color="success" />;
  };

  const getStatusText = (eventsGenerated: number) => {
    if (eventsGenerated > 0) return `${eventsGenerated} evento(s) generado(s)`;
    return 'Sin cambios';
  };

  return (
    <Card variant="outlined" sx={{ mb: 2 }}>
      <CardContent sx={{ pb: 1 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
          <Box display="flex" alignItems="center" gap={1}>
            <DevicesIcon color="primary" fontSize="small" />
            <Typography variant="subtitle2" fontWeight={600}>
              {result.device_name || result.device_imei}
            </Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={1}>
            {getStatusIcon(result.events_generated)}
            <Chip
              label={getStatusText(result.events_generated)}
              size="small"
              color={getStatusColor(result.events_generated)}
              variant="outlined"
            />
          </Box>
        </Box>

        <Typography variant="body2" color="text.secondary" gutterBottom>
          IMEI: {result.device_imei}
        </Typography>

        {result.events_generated > 0 && (
          <Box>
            <Button
              size="small"
              onClick={() => setExpanded(!expanded)}
              startIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              sx={{ mt: 1, mb: expanded ? 1 : 0 }}
            >
              {expanded ? 'Ocultar eventos' : 'Ver eventos generados'}
            </Button>
            
            <Collapse in={expanded}>
              <EventList events={result.events} />
            </Collapse>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export const ManualGeofenceChecker: React.FC<ManualGeofenceCheckerProps> = ({
  geofenceId,
  geofenceName,
  onResultsUpdate,
}) => {
  const [checking, setChecking] = useState(false);
  const [results, setResults] = useState<ManualGeofenceCheck | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastCheckTime, setLastCheckTime] = useState<Date | null>(null);

  const handleManualCheck = async () => {
    setChecking(true);
    setError(null);
    
    try {
      const checkResults = await geofenceService.checkGeofenceDevices(geofenceId);
      setResults(checkResults);
      setLastCheckTime(new Date());
      
      // Notificar al componente padre si se proporciona callback
      if (onResultsUpdate) {
        onResultsUpdate(checkResults);
      }
      
    } catch (err) {
      console.error('Error in manual geofence check:', err);
      setError('Error al realizar la verificación manual. Intente nuevamente.');
    } finally {
      setChecking(false);
    }
  };

  const getTotalEventsGenerated = () => {
    if (!results) return 0;
    return results.results.reduce((sum, result) => sum + result.events_generated, 0);
  };

  const getDevicesWithEvents = () => {
    if (!results) return 0;
    return results.results.filter(result => result.events_generated > 0).length;
  };

  return (
    <Card>
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <RefreshIcon color="primary" />
            <Typography variant="h6">
              Verificación Manual de Geocerca
            </Typography>
          </Box>
        }
        subheader={geofenceName ? `Geocerca: ${geofenceName}` : undefined}
        action={
          <Tooltip title="Verificar dispositivos ahora">
            <Button
              variant="outlined"
              onClick={handleManualCheck}
              disabled={checking}
              startIcon={checking ? <CircularProgress size={20} /> : <RefreshIcon />}
              color="primary"
            >
              {checking ? 'Verificando...' : 'Verificar Ahora'}
            </Button>
          </Tooltip>
        }
      />
      
      <CardContent>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Esta función verifica manualmente todos los dispositivos asociados a la geocerca 
          para detectar eventos de entrada/salida en tiempo real.
        </Typography>

        {error && (
          <Alert severity="error" sx={{ my: 2 }}>
            {error}
          </Alert>
        )}

        {lastCheckTime && (
          <Typography variant="caption" color="text.secondary" display="block" mb={2}>
            Última verificación: {lastCheckTime.toLocaleString()}
          </Typography>
        )}

        {results && (
          <Box mt={3}>
            <Divider sx={{ mb: 2 }} />
            
            {/* Resumen de resultados */}
            <Box mb={3}>
              <Typography variant="h6" gutterBottom>
                Resultados de Verificación
              </Typography>
              
              <Box display="flex" gap={2} flexWrap="wrap" mb={2}>
                <Chip
                  icon={<DevicesIcon />}
                  label={`${results.devices_checked} dispositivos verificados`}
                  color="primary"
                  variant="outlined"
                />
                
                <Chip
                  icon={<InfoIcon />}
                  label={`${getTotalEventsGenerated()} eventos generados`}
                  color={getTotalEventsGenerated() > 0 ? 'warning' : 'success'}
                  variant="outlined"
                />
                
                {getDevicesWithEvents() > 0 && (
                  <Chip
                    icon={<WarningIcon />}
                    label={`${getDevicesWithEvents()} dispositivos con cambios`}
                    color="warning"
                    variant="outlined"
                  />
                )}
              </Box>

              {getTotalEventsGenerated() === 0 && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  ✅ Todos los dispositivos están en sus posiciones correctas. 
                  No se detectaron cambios de estado en la geocerca.
                </Alert>
              )}

              {getTotalEventsGenerated() > 0 && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  ⚠️ Se detectaron cambios de estado. {getDevicesWithEvents()} dispositivo(s) 
                  generaron eventos de entrada/salida.
                </Alert>
              )}
            </Box>

            {/* Lista detallada de resultados por dispositivo */}
            {results.results.length > 0 && (
              <Box>
                <Typography variant="subtitle1" gutterBottom fontWeight={600}>
                  Detalles por Dispositivo
                </Typography>
                
                {results.results.map((result) => (
                  <DeviceResultCard
                    key={result.device_imei}
                    result={result}
                  />
                ))}
              </Box>
            )}

            {results.devices_checked === 0 && (
              <Alert severity="info">
                No hay dispositivos asociados a esta geocerca para verificar.
              </Alert>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}; 
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Grid,
  Typography,
  CircularProgress,
  Alert,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  Warning as WarningIcon,
  Route as RouteIcon,
  Speed as SpeedIcon,
  Assessment as AssessmentIcon,
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
  LocationOn as LocationIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import { geofenceService } from '../../services/geofenceService';
import { BehaviorAnalysis } from '../../types/geofence';

interface DeviceBehaviorAnalysisProps {
  deviceId: string;
  deviceName?: string;
}

interface BehaviorScoreGaugeProps {
  score: number;
  size?: 'small' | 'medium' | 'large';
}

const BehaviorScoreGauge: React.FC<BehaviorScoreGaugeProps> = ({ score, size = 'medium' }) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    if (score >= 40) return 'error';
    return 'error';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excelente';
    if (score >= 60) return 'Bueno';
    if (score >= 40) return 'Regular';
    return 'Crítico';
  };

  const getScoreDescription = (score: number) => {
    if (score >= 80) return 'Cumplimiento óptimo de geocercas';
    if (score >= 60) return 'Cumplimiento satisfactorio';
    if (score >= 40) return 'Cumplimiento por debajo del promedio';
    return 'Requiere atención inmediata';
  };

  const gaugeSize = size === 'large' ? 120 : size === 'medium' ? 100 : 80;
  const strokeWidth = size === 'large' ? 8 : size === 'medium' ? 6 : 4;

  return (
    <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
      <Box position="relative" display="inline-flex">
        <CircularProgress
          variant="determinate"
          value={100}
          size={gaugeSize}
          thickness={strokeWidth}
          sx={{ color: 'grey.200' }}
        />
        <CircularProgress
          variant="determinate"
          value={score}
          size={gaugeSize}
          thickness={strokeWidth}
          color={getScoreColor(score)}
          sx={{
            position: 'absolute',
            left: 0,
            [`& .MuiCircularProgress-circle`]: {
              strokeLinecap: 'round',
            },
          }}
        />
        <Box
          sx={{
            top: 0,
            left: 0,
            bottom: 0,
            right: 0,
            position: 'absolute',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
          }}
        >
          <Typography
            variant={size === 'large' ? 'h4' : size === 'medium' ? 'h5' : 'h6'}
            component="div"
            color={`${getScoreColor(score)}.main`}
            fontWeight="bold"
          >
            {score.toFixed(0)}
          </Typography>
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ fontSize: size === 'large' ? '0.8rem' : '0.7rem' }}
          >
            /100
          </Typography>
        </Box>
      </Box>
      
      <Box textAlign="center">
        <Chip
          label={getScoreLabel(score)}
          color={getScoreColor(score)}
          size={size === 'large' ? 'medium' : 'small'}
          sx={{ mb: 1 }}
        />
        <Typography variant="caption" color="text.secondary" display="block">
          {getScoreDescription(score)}
        </Typography>
      </Box>
    </Box>
  );
};

const AnomaliesList: React.FC<{ 
  anomalies: BehaviorAnalysis['analysis']['anomalies_detected'] 
}> = ({ anomalies }) => {
  if (!anomalies || anomalies.length === 0) {
    return (
      <Alert severity="success" sx={{ textAlign: 'center' }}>
        <Typography variant="body2">
          🎉 No se detectaron anomalías en el comportamiento
        </Typography>
      </Alert>
    );
  }

  const getAnomalyColor = (confidence: number) => {
    if (confidence >= 0.8) return 'error';
    if (confidence >= 0.6) return 'warning';
    return 'info';
  };

  const getAnomalyIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'speed':
        return <SpeedIcon />;
      case 'location':
        return <LocationIcon />;
      case 'route':
        return <RouteIcon />;
      default:
        return <WarningIcon />;
    }
  };

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom color="error.main" fontWeight={600}>
        ⚠️ Anomalías Detectadas ({anomalies.length})
      </Typography>
      
      <List dense>
        {anomalies.slice(0, 5).map((anomaly, index) => (
          <ListItem key={index} divider={index < Math.min(anomalies.length, 5) - 1}>
            <ListItemIcon>
              {getAnomalyIcon(anomaly.anomaly_type)}
            </ListItemIcon>
            <ListItemText
              primary={
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography variant="body2" fontWeight={500}>
                    {anomaly.description}
                  </Typography>
                  <Chip
                    label={`${(anomaly.confidence_score * 100).toFixed(0)}%`}
                    size="small"
                    color={getAnomalyColor(anomaly.confidence_score)}
                    variant="outlined"
                  />
                </Box>
              }
              secondary={
                <Typography variant="caption" color="text.secondary">
                  {new Date(anomaly.timestamp).toLocaleString()} • 
                  Tipo: {anomaly.anomaly_type}
                </Typography>
              }
            />
          </ListItem>
        ))}
      </List>
      
      {anomalies.length > 5 && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          + {anomalies.length - 5} anomalías adicionales
        </Typography>
      )}
    </Box>
  );
};

const PeakHoursChart: React.FC<{ hours: number[] }> = ({ hours }) => {
  if (!hours || hours.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary" textAlign="center">
        No hay datos de horas pico disponibles
      </Typography>
    );
  }

  // Crear un array de 24 horas con la frecuencia de actividad
  const hourlyActivity = Array(24).fill(0);
  hours.forEach(hour => {
    if (hour >= 0 && hour < 24) {
      hourlyActivity[hour]++;
    }
  });

  const maxActivity = Math.max(...hourlyActivity);

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom fontWeight={600}>
        🕐 Patrones de Actividad por Hora
      </Typography>
      
      <Grid container spacing={0.5} sx={{ mt: 1 }}>
        {hourlyActivity.map((activity, hour) => {
          const intensity = maxActivity > 0 ? (activity / maxActivity) * 100 : 0;
          const isActive = activity > 0;
          
          return (
            <Grid item key={hour} xs={1}>
              <Tooltip title={`${hour}:00 - Actividad: ${activity}`}>
                <Box
                  sx={{
                    height: 40,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'flex-end',
                    alignItems: 'center',
                    cursor: 'pointer',
                  }}
                >
                  <Box
                    sx={{
                      width: '100%',
                      height: `${Math.max(intensity, 5)}%`,
                      backgroundColor: isActive ? 'primary.main' : 'grey.200',
                      borderRadius: '2px 2px 0 0',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        backgroundColor: isActive ? 'primary.dark' : 'grey.300',
                      },
                    }}
                  />
                  <Typography variant="caption" sx={{ fontSize: '0.6rem', mt: 0.5 }}>
                    {hour}
                  </Typography>
                </Box>
              </Tooltip>
            </Grid>
          );
        })}
      </Grid>
      
      <Box mt={2}>
        <Typography variant="caption" color="text.secondary">
          Horas con mayor actividad: {hours.slice(0, 3).join('h, ')}h
        </Typography>
      </Box>
    </Box>
  );
};

const ComplianceMetrics: React.FC<{ 
  metrics: BehaviorAnalysis['analysis']['compliance_metrics'] 
}> = ({ metrics }) => {
  const getComplianceColor = (rate: number) => {
    if (rate >= 0.8) return 'success';
    if (rate >= 0.6) return 'warning';
    return 'error';
  };

  const formatPercentage = (value: number) => `${(value * 100).toFixed(1)}%`;

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={4}>
        <Paper sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary" gutterBottom display="block">
            Adherencia a Geocercas
          </Typography>
          <Typography 
            variant="h5" 
            color={`${getComplianceColor(metrics.geofence_adherence_rate)}.main`}
            fontWeight="bold"
          >
            {formatPercentage(metrics.geofence_adherence_rate)}
          </Typography>
          <LinearProgress
            variant="determinate"
            value={metrics.geofence_adherence_rate * 100}
            color={getComplianceColor(metrics.geofence_adherence_rate)}
            sx={{ mt: 1 }}
          />
        </Paper>
      </Grid>
      
      <Grid item xs={12} sm={4}>
        <Paper sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary" gutterBottom display="block">
            Cumplimiento de Velocidad
          </Typography>
          <Typography 
            variant="h5" 
            color={`${getComplianceColor(metrics.speed_compliance_rate)}.main`}
            fontWeight="bold"
          >
            {formatPercentage(metrics.speed_compliance_rate)}
          </Typography>
          <LinearProgress
            variant="determinate"
            value={metrics.speed_compliance_rate * 100}
            color={getComplianceColor(metrics.speed_compliance_rate)}
            sx={{ mt: 1 }}
          />
        </Paper>
      </Grid>
      
      <Grid item xs={12} sm={4}>
        <Paper sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary" gutterBottom display="block">
            Eficiencia de Rutas
          </Typography>
          <Typography 
            variant="h5" 
            color={`${getComplianceColor(metrics.route_efficiency_score)}.main`}
            fontWeight="bold"
          >
            {formatPercentage(metrics.route_efficiency_score)}
          </Typography>
          <LinearProgress
            variant="determinate"
            value={metrics.route_efficiency_score * 100}
            color={getComplianceColor(metrics.route_efficiency_score)}
            sx={{ mt: 1 }}
          />
        </Paper>
      </Grid>
    </Grid>
  );
};

export const DeviceBehaviorAnalysis: React.FC<DeviceBehaviorAnalysisProps> = ({
  deviceId,
  deviceName,
}) => {
  const [analysis, setAnalysis] = useState<BehaviorAnalysis | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [analysisWindow, setAnalysisWindow] = useState<number>(7);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const loadAnalysis = async (showRefreshing = false) => {
    try {
      if (showRefreshing) setRefreshing(true);
      else setLoading(true);
      
      setError(null);
      const data = await geofenceService.getDeviceBehaviorAnalysis(deviceId, analysisWindow);
      setAnalysis(data);
    } catch (err) {
      console.error('Error loading device behavior analysis:', err);
      setError('Error al cargar el análisis comportamental del dispositivo');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadAnalysis();
  }, [deviceId, analysisWindow]);

  const handleRefresh = () => {
    loadAnalysis(true);
  };

  const handleAnalysisWindowChange = (event: any) => {
    setAnalysisWindow(event.target.value);
  };

  if (loading && !analysis) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
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

  if (!analysis) {
    return (
      <Alert severity="info" sx={{ my: 2 }}>
        No hay datos de análisis comportamental disponibles para este dispositivo
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" fontWeight="bold" gutterBottom>
            Análisis Comportamental ML
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {deviceName || analysis.device_name || analysis.device_imei} • 
            Período: {analysis.analysis_period_days} días
          </Typography>
        </Box>
        <Box display="flex" alignItems="center" gap={2}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Período</InputLabel>
            <Select
              value={analysisWindow}
              label="Período"
              onChange={handleAnalysisWindowChange}
            >
              <MenuItem value={1}>1 día</MenuItem>
              <MenuItem value={3}>3 días</MenuItem>
              <MenuItem value={7}>7 días</MenuItem>
              <MenuItem value={14}>14 días</MenuItem>
              <MenuItem value={30}>30 días</MenuItem>
            </Select>
          </FormControl>
          <Tooltip title="Actualizar análisis">
            <IconButton 
              onClick={handleRefresh}
              disabled={refreshing}
              color="primary"
            >
              {refreshing ? <CircularProgress size={20} /> : <RefreshIcon />}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Behavior Score */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="Puntuación Comportamental"
              avatar={<PsychologyIcon color="primary" />}
            />
            <CardContent>
              <BehaviorScoreGauge score={analysis.analysis.behavior_score} size="large" />
            </CardContent>
          </Card>
        </Grid>

        {/* Métricas de Cumplimiento */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader
              title="Métricas de Cumplimiento"
              avatar={<AssessmentIcon color="primary" />}
            />
            <CardContent>
              <ComplianceMetrics metrics={analysis.analysis.compliance_metrics} />
            </CardContent>
          </Card>
        </Grid>

        {/* Detección de Anomalías */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardHeader
              title="Detección de Anomalías"
              avatar={<WarningIcon color="primary" />}
            />
            <CardContent>
              <AnomaliesList anomalies={analysis.analysis.anomalies_detected} />
            </CardContent>
          </Card>
        </Grid>

        {/* Patrones de Actividad */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardHeader
              title="Patrones de Actividad"
              avatar={<TimelineIcon color="primary" />}
            />
            <CardContent>
              <PeakHoursChart hours={analysis.analysis.patterns.peak_hours} />
            </CardContent>
          </Card>
        </Grid>

        {/* Información adicional en acordeones */}
        <Grid item xs={12}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Rutas Frecuentes</Typography>
            </AccordionSummary>
            <AccordionDetails>
              {analysis.analysis.patterns.frequent_routes.length > 0 ? (
                <List>
                  {analysis.analysis.patterns.frequent_routes.slice(0, 5).map((route, index) => (
                    <ListItem key={route.route_id || index}>
                      <ListItemIcon>
                        <RouteIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`Ruta ${route.route_id || index + 1}`}
                        secondary={`Frecuencia: ${route.frequency} veces • ${route.coordinates.length} puntos`}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No se detectaron rutas frecuentes en este período
                </Typography>
              )}
            </AccordionDetails>
          </Accordion>

          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Patrones de Velocidad</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box>
                <Typography variant="body2" gutterBottom>
                  Tiempo típico de permanencia: {Math.round(analysis.analysis.patterns.typical_dwell_time / 60)} minutos
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" gutterBottom>
                  Velocidades promedio por período:
                </Typography>
                {Object.entries(analysis.analysis.patterns.average_speed_patterns).map(([period, speed]) => (
                  <Box key={period} display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2">{period}</Typography>
                    <Typography variant="body2" fontWeight={500}>{speed} km/h</Typography>
                  </Box>
                ))}
              </Box>
            </AccordionDetails>
          </Accordion>
        </Grid>
      </Grid>
    </Box>
  );
}; 
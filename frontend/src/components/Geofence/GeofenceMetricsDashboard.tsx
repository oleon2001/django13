import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Grid,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  LinearProgress,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  IconButton,
  Tooltip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Warning,
  Speed,
  Timer,
  DevicesOther,
  Refresh,
  Analytics,
} from '@mui/icons-material';
import { geofenceService } from '../../services/geofenceService';
import { GeofenceMetrics } from '../../types/geofence';

interface MetricCardProps {
  title: string;
  value: number | string;
  suffix?: string;
  color: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
  trend?: 'up' | 'down' | 'neutral';
  icon?: React.ReactNode;
  description?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  suffix = '',
  color,
  trend = 'neutral',
  icon,
  description,
}) => {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp color="success" fontSize="small" />;
      case 'down':
        return <TrendingDown color="error" fontSize="small" />;
      default:
        return null;
    }
  };

  const getColorProps = (colorName: string) => {
    const colorMap = {
      primary: { main: '#1976d2', light: '#e3f2fd' },
      secondary: { main: '#dc004e', light: '#fce4ec' },
      error: { main: '#d32f2f', light: '#ffebee' },
      warning: { main: '#ed6c02', light: '#fff3e0' },
      info: { main: '#0288d1', light: '#e1f5fe' },
      success: { main: '#2e7d32', light: '#e8f5e8' },
    };
    return colorMap[colorName as keyof typeof colorMap] || colorMap.primary;
  };

  const colors = getColorProps(color);

  return (
    <Card 
      sx={{ 
        height: '100%',
        background: `linear-gradient(135deg, ${colors.light} 0%, ${colors.light}dd 100%)`,
        border: `1px solid ${colors.main}22`,
        transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: 4,
        },
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
          <Typography variant="body2" color="text.secondary" fontWeight={500}>
            {title}
          </Typography>
          {icon && (
            <Box sx={{ color: colors.main }}>
              {icon}
            </Box>
          )}
        </Box>
        
        <Box display="flex" alignItems="baseline" mb={1}>
          <Typography variant="h4" component="div" fontWeight="bold" color={colors.main}>
            {value}
          </Typography>
          {suffix && (
            <Typography variant="h6" color="text.secondary" ml={0.5}>
              {suffix}
            </Typography>
          )}
          {getTrendIcon() && (
            <Box ml={1}>
              {getTrendIcon()}
            </Box>
          )}
        </Box>
        
        {description && (
          <Typography variant="caption" color="text.secondary">
            {description}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

const PerformanceScoreIndicator: React.FC<{ score: number }> = ({ score }) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excelente';
    if (score >= 60) return 'Bueno';
    if (score >= 40) return 'Regular';
    return 'Necesita Atención';
  };

  return (
    <Box>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
        <Typography variant="body2" color="text.secondary">
          Performance Score
        </Typography>
        <Chip 
          label={getScoreLabel(score)} 
          color={getScoreColor(score)}
          size="small"
        />
      </Box>
      <LinearProgress 
        variant="determinate" 
        value={score} 
        color={getScoreColor(score)}
        sx={{ height: 8, borderRadius: 4 }}
      />
      <Typography variant="caption" color="text.secondary" mt={1}>
        {score.toFixed(1)}/100
      </Typography>
    </Box>
  );
};

const ActiveDevicesList: React.FC<{ devices: GeofenceMetrics['most_active_devices'] }> = ({ devices }) => {
  if (!devices || devices.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary" textAlign="center" py={2}>
        No hay dispositivos activos
      </Typography>
    );
  }

  return (
    <List dense>
      {devices.slice(0, 5).map((device, index) => (
        <ListItem key={device.device_imei} divider={index < devices.length - 1}>
          <ListItemAvatar>
            <Avatar 
              sx={{ 
                width: 32, 
                height: 32, 
                bgcolor: index === 0 ? 'gold' : index === 1 ? 'silver' : index === 2 ? '#cd7f32' : 'grey.400',
                fontSize: '0.8rem'
              }}
            >
              {index + 1}
            </Avatar>
          </ListItemAvatar>
          <ListItemText
            primary={
              <Typography variant="body2" fontWeight={500}>
                {device.device_name || device.device_imei}
              </Typography>
            }
            secondary={
              <Typography variant="caption" color="text.secondary">
                {device.event_count} eventos
              </Typography>
            }
          />
        </ListItem>
      ))}
    </List>
  );
};

export const GeofenceMetricsDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<GeofenceMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [timeWindow, setTimeWindow] = useState<number>(24);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const loadMetrics = useCallback(async (showRefreshing = false) => {
    try {
      if (showRefreshing) setRefreshing(true);
      else setLoading(true);
      
      setError(null);
      const data = await geofenceService.getMetrics(timeWindow);
      setMetrics(data);
    } catch (err) {
      console.error('Error loading geofence metrics:', err);
      setError('Error al cargar las métricas de geocercas');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [timeWindow]);

  useEffect(() => {
    loadMetrics();
  }, [loadMetrics]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      loadMetrics(true);
    }, 30000);

    return () => clearInterval(interval);
  }, [loadMetrics]);

  const handleRefresh = () => {
    loadMetrics(true);
  };

  const handleTimeWindowChange = (event: any) => {
    setTimeWindow(event.target.value);
  };

  if (loading && !metrics) {
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

  if (!metrics) {
    return (
      <Alert severity="info" sx={{ my: 2 }}>
        No hay datos de métricas disponibles
      </Alert>
    );
  }

  const violationColor = metrics.violation_rate > 20 ? 'error' : metrics.violation_rate > 10 ? 'warning' : 'success';
  const eventsTotal = metrics.entry_events_24h + metrics.exit_events_24h;

  return (
    <Box>
      {/* Header con controles */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight="bold">
          Dashboard de Métricas - Geocercas
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Período</InputLabel>
            <Select
              value={timeWindow}
              label="Período"
              onChange={handleTimeWindowChange}
            >
              <MenuItem value={1}>1 hora</MenuItem>
              <MenuItem value={6}>6 horas</MenuItem>
              <MenuItem value={12}>12 horas</MenuItem>
              <MenuItem value={24}>24 horas</MenuItem>
              <MenuItem value={72}>3 días</MenuItem>
              <MenuItem value={168}>7 días</MenuItem>
            </Select>
          </FormControl>
          <Tooltip title="Actualizar datos">
            <IconButton 
              onClick={handleRefresh}
              disabled={refreshing}
              color="primary"
            >
              {refreshing ? <CircularProgress size={20} /> : <Refresh />}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Métricas principales */}
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Geocercas Totales"
            value={metrics.total_geofences}
            color="primary"
            icon={<Analytics />}
            description={`${metrics.active_geofences} activas`}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Eventos Totales"
            value={eventsTotal}
            color="info"
            icon={<DevicesOther />}
            description={`Últimas ${timeWindow}h`}
            trend={eventsTotal > 0 ? 'up' : 'neutral'}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Tasa de Violación"
            value={metrics.violation_rate.toFixed(1)}
            suffix="%"
            color={violationColor}
            icon={<Warning />}
            description="Porcentaje de violaciones"
            trend={metrics.violation_rate > 15 ? 'up' : 'down'}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Tiempo Promedio"
            value={Math.round(metrics.average_dwell_time / 60)}
            suffix=" min"
            color="secondary"
            icon={<Timer />}
            description="Permanencia en geocercas"
          />
        </Grid>

        {/* Performance Score */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="Puntuación de Rendimiento"
              avatar={<Speed color="primary" />}
            />
            <CardContent>
              <PerformanceScoreIndicator score={metrics.performance_score} />
            </CardContent>
          </Card>
        </Grid>

        {/* Dispositivos más activos */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardHeader 
              title="Dispositivos Más Activos"
              avatar={<DevicesOther color="primary" />}
            />
            <CardContent sx={{ pt: 0 }}>
              <ActiveDevicesList devices={metrics.most_active_devices} />
            </CardContent>
          </Card>
        </Grid>

        {/* Resumen de eventos */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Resumen de Actividad ({timeWindow}h)
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={4}>
                <Box textAlign="center">
                  <Typography variant="h4" color="success.main" fontWeight="bold">
                    {metrics.entry_events_24h}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Entradas a Geocercas
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box textAlign="center">
                  <Typography variant="h4" color="warning.main" fontWeight="bold">
                    {metrics.exit_events_24h}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Salidas de Geocercas
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box textAlign="center">
                  <Typography variant="h4" color="info.main" fontWeight="bold">
                    {metrics.most_active_devices.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Dispositivos Activos
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}; 
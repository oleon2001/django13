import React, { useState, useEffect, useRef } from 'react';
// Optimized MUI imports for better tree shaking
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Chip from '@mui/material/Chip';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import Alert from '@mui/material/Alert';
import Divider from '@mui/material/Divider';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemSecondaryAction from '@mui/material/ListItemSecondaryAction';
import Avatar from '@mui/material/Avatar';
import Badge from '@mui/material/Badge';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
// Optimized icon imports
import RefreshIcon from '@mui/icons-material/Refresh';
import GpsFixedIcon from '@mui/icons-material/GpsFixed';
import SpeedIcon from '@mui/icons-material/Speed';
import Battery80Icon from '@mui/icons-material/Battery80';
import SignalCellular4BarIcon from '@mui/icons-material/SignalCellular4Bar';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import CircularProgress from '@mui/material/CircularProgress';

import { useTranslation } from 'react-i18next';
import { Device } from '../types';
import { deviceService } from '../services/deviceService';
import DeviceMap from '../components/DeviceMap';

// Memoized status icon component for better performance
const StatusIcon = React.memo<{ status: string }>(({ status }) => {
  switch (status?.toLowerCase()) {
    case 'online':
      return <CheckCircleIcon color="success" />;
    case 'offline':
      return <ErrorIcon color="error" />;
    default:
      return <WarningIcon color="warning" />;
  }
});
StatusIcon.displayName = 'StatusIcon';

// Memoized device stats component
const DeviceStatsCard = React.memo<{
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
}>(({ title, value, icon, color }) => (
  <Card>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box>
          <Typography color="textSecondary" gutterBottom variant="body2">
            {title}
          </Typography>
          <Typography variant="h4" component="div" sx={{ color }}>
            {value}
          </Typography>
        </Box>
        <Avatar sx={{ bgcolor: color }}>
          {icon}
        </Avatar>
      </Box>
    </CardContent>
  </Card>
));
DeviceStatsCard.displayName = 'DeviceStatsCard';

// Memoized device list item component
const DeviceListItem = React.memo<{
  device: Device;
  isSelected: boolean;
  onSelect: (device: Device) => void;
  index: number;
  totalDevices: number;
}>(({ device, isSelected, onSelect, index, totalDevices }) => {
  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'online':
        return 'success';
      case 'offline':
        return 'error';
      default:
        return 'warning';
    }
  };

  return (
    <React.Fragment>
      <ListItem
        button
        selected={isSelected}
        onClick={() => onSelect(device)}
        sx={{
          '&.Mui-selected': {
            bgcolor: 'primary.light',
            '&:hover': {
              bgcolor: 'primary.light',
            },
          },
        }}
      >
        <ListItemIcon>
          <Badge
            color={getStatusColor(device.connection_status || 'OFFLINE')}
            variant="dot"
          >
            <DirectionsCarIcon />
          </Badge>
        </ListItemIcon>
        
        <ListItemText
          primary={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="subtitle2">
                {device.name || `Device ${device.imei}`}
              </Typography>
              <Chip
                label={device.connection_status || 'OFFLINE'}
                size="small"
                color={getStatusColor(device.connection_status || 'OFFLINE')}
                variant="outlined"
              />
            </Box>
          }
          secondary={
            <Box>
              <Typography variant="caption" display="block">
                IMEI: {device.imei}
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <SpeedIcon fontSize="small" />
                  <Typography variant="caption">
                    {device.speed || 0} km/h
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Battery80Icon fontSize="small" />
                  <Typography variant="caption">
                    {device.battery_level || 0}%
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <SignalCellular4BarIcon fontSize="small" />
                  <Typography variant="caption">
                    {device.signal_strength || 0}%
                  </Typography>
                </Box>
              </Box>
            </Box>
          }
        />
        
        <ListItemSecondaryAction>
          <Tooltip title="Ver en mapa">
            <IconButton
              edge="end"
              onClick={() => onSelect(device)}
            >
              <VisibilityIcon />
            </IconButton>
          </Tooltip>
        </ListItemSecondaryAction>
      </ListItem>
      {index < totalDevices - 1 && <Divider />}
    </React.Fragment>
  );
});
DeviceListItem.displayName = 'DeviceListItem';

const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const [devices, setDevices] = useState<Device[]>([]);
  const [realTimePositions, setRealTimePositions] = useState<any[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<Device | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [isRealTimeEnabled, setIsRealTimeEnabled] = useState(true);
  const stopPollingRef = useRef<(() => void) | null>(null);

  const fetchDevices = React.useCallback(async (showRefreshing = false) => {
    try {
      if (showRefreshing) setRefreshing(true);
      else setLoading(true);
      
      const data = await deviceService.getAll();
      setDevices(data);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError(t('devices.errorLoading'));
      console.error('Error loading devices:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [t]);

  useEffect(() => {
    fetchDevices();
  }, [fetchDevices]);

  // Real-time polling effect
  useEffect(() => {
    if (isRealTimeEnabled) {
      stopPollingRef.current = deviceService.startRealTimePolling(
        (positions) => {
          setRealTimePositions(positions);
          setLastUpdate(new Date());
          
          // Update devices with real-time positions
          setDevices(prevDevices => 
            prevDevices.map(device => {
              const realtimePos = positions.find(pos => pos.imei === device.imei);
              if (realtimePos) {
                return {
                  ...device,
                  latitude: realtimePos.position.latitude,
                  longitude: realtimePos.position.longitude,
                  speed: realtimePos.speed,
                  course: realtimePos.course,
                  altitude: realtimePos.altitude,
                  connection_status: realtimePos.connection_status,
                  lastUpdate: realtimePos.last_update,
                };
              }
              return device;
            })
          );
        },
        10000 // Poll every 10 seconds (optimized from 3s for better performance)
      );
    } else {
      if (stopPollingRef.current) {
        stopPollingRef.current();
        stopPollingRef.current = null;
      }
    }

    return () => {
      if (stopPollingRef.current) {
        stopPollingRef.current();
      }
    };
  }, [isRealTimeEnabled]);

  const handleDeviceSelect = React.useCallback((device: Device) => {
    setSelectedDevice(device);
  }, []);

  const handleRefresh = React.useCallback(() => {
    fetchDevices(true);
  }, [fetchDevices]);

  // Memoized calculations
  const deviceStats = React.useMemo(() => {
    const onlineDevices = devices.filter(d => d.connection_status === 'ONLINE').length;
    const offlineDevices = devices.filter(d => d.connection_status === 'OFFLINE').length;
    const totalDevices = devices.length;
    
    return { onlineDevices, offlineDevices, totalDevices };
  }, [devices]);

  if (loading && !refreshing) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="100vh"
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3, bgcolor: '#f5f5f5', minHeight: '100vh' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          {t('dashboard.title')}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={isRealTimeEnabled}
                onChange={(e) => setIsRealTimeEnabled(e.target.checked)}
                color="primary"
              />
            }
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {isRealTimeEnabled ? <PlayArrowIcon color="success" /> : <PauseIcon color="disabled" />}
                <Typography variant="body2">
                  {isRealTimeEnabled ? t('dashboard.realTime') : t('dashboard.paused')}
                </Typography>
              </Box>
            }
          />
          <Typography variant="body2" color="text.secondary">
            {t('dashboard.lastUpdate')}: {lastUpdate.toLocaleTimeString()}
          </Typography>
          <Typography variant="body2" color="primary">
            {t('dashboard.active')}: {realTimePositions.length}
          </Typography>
          <Tooltip title={t('dashboard.refresh')}>
            <IconButton 
              onClick={handleRefresh} 
              disabled={refreshing}
              color="primary"
            >
              <RefreshIcon sx={{ 
                animation: refreshing ? 'spin 1s linear infinite' : 'none' 
              }} />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={4}>
          <DeviceStatsCard
            title="Total Dispositivos"
            value={deviceStats.totalDevices}
            icon={<DirectionsCarIcon />}
            color="primary.main"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <DeviceStatsCard
            title="En Línea"
            value={deviceStats.onlineDevices}
            icon={<CheckCircleIcon />}
            color="success.main"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <DeviceStatsCard
            title="Fuera de Línea"
            value={deviceStats.offlineDevices}
            icon={<ErrorIcon />}
            color="error.main"
          />
        </Grid>
      </Grid>

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Device List */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
              <Typography variant="h6" component="h2">
                Dispositivos GPS
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {deviceStats.totalDevices} dispositivos registrados
              </Typography>
            </Box>
            
            <Box sx={{ flex: 1, overflow: 'auto' }}>
              {devices.length > 0 ? (
                <List>
                  {devices.map((device, index) => (
                    <DeviceListItem
                      key={device.imei}
                      device={device}
                      isSelected={selectedDevice?.imei === device.imei}
                      onSelect={handleDeviceSelect}
                      index={index}
                      totalDevices={devices.length}
                    />
                  ))}
                </List>
              ) : (
                <Box sx={{ p: 3, textAlign: 'center' }}>
                  <GpsFixedIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary">
                    No hay dispositivos
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Los dispositivos aparecerán aquí cuando se conecten
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Map */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ height: '600px', p: 2 }}>
            <Box sx={{ height: '100%' }}>
              <DeviceMap
                devices={devices}
                selectedDevice={selectedDevice}
                onDeviceSelect={handleDeviceSelect}
              />
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Device Details Panel */}
      {selectedDevice && (
        <Paper sx={{ mt: 3, p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Detalles del Dispositivo: {selectedDevice.name || `Device ${selectedDevice.imei}`}
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <List>
                <ListItem>
                  <ListItemIcon><DirectionsCarIcon /></ListItemIcon>
                  <ListItemText 
                    primary="IMEI" 
                    secondary={selectedDevice.imei} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><GpsFixedIcon /></ListItemIcon>
                  <ListItemText
                    primary="Ubicación" 
                    secondary={
                      selectedDevice.position?.latitude && selectedDevice.position?.longitude
                        ? `${selectedDevice.position.latitude.toFixed(6)}, ${selectedDevice.position.longitude.toFixed(6)}`
                        : 'No disponible'
                    }
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><SpeedIcon /></ListItemIcon>
                  <ListItemText
                    primary="Velocidad" 
                    secondary={`${selectedDevice.speed || 0} km/h`} 
                  />
                </ListItem>
              </List>
            </Grid>

            <Grid item xs={12} md={6}>
              <List>
                <ListItem>
                  <ListItemIcon><Battery80Icon /></ListItemIcon>
                  <ListItemText
                    primary="Batería" 
                    secondary={`${selectedDevice.battery_level || 0}%`} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><SignalCellular4BarIcon /></ListItemIcon>
                  <ListItemText 
                    primary="Señal" 
                    secondary={`${selectedDevice.signal_strength || 0}%`} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <StatusIcon status={selectedDevice.connection_status || 'OFFLINE'} />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Estado" 
                    secondary={selectedDevice.connection_status || 'OFFLINE'} 
                  />
                </ListItem>
              </List>
            </Grid>
          </Grid>
        </Paper>
      )}

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </Box>
  );
};

export default React.memo(Dashboard); 
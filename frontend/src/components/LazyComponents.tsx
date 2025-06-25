import React, { Suspense, lazy } from 'react';
import { CircularProgress, Box, Skeleton } from '@mui/material';
import EnhancedLoading from './EnhancedLoading';

// Optimized Loading component with skeleton
const LoadingSpinner: React.FC<{ message?: string; variant?: 'spinner' | 'skeleton' }> = ({ 
  message = 'Cargando...', 
  variant = 'spinner' 
}) => {
  if (variant === 'skeleton') {
    return (
      <Box sx={{ p: 3 }}>
        <Skeleton variant="rectangular" height={60} sx={{ mb: 2 }} />
        <Skeleton variant="rectangular" height={400} sx={{ mb: 2 }} />
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Skeleton variant="rectangular" width="30%" height={200} />
          <Skeleton variant="rectangular" width="70%" height={200} />
        </Box>
      </Box>
    );
  }

  return (
    <Box 
      display="flex" 
      flexDirection="column"
      justifyContent="center" 
      alignItems="center" 
      minHeight="60vh"
      gap={2}
    >
      <CircularProgress size={60} />
      <Box sx={{ color: 'text.secondary', fontSize: '1.1rem' }}>
        {message}
      </Box>
    </Box>
  );
};

// Lazy load main page components with webpack chunk names
export const LazyDashboard = lazy(() => 
  import(/* webpackChunkName: "dashboard" */ '../pages/Dashboard')
);

export const LazyMonitoring = lazy(() => 
  import(/* webpackChunkName: "monitoring" */ '../pages/Monitoring')
);

export const LazyGPS = lazy(() => 
  import(/* webpackChunkName: "gps" */ '../pages/GPS')
);

export const LazyTracking = lazy(() => 
  import(/* webpackChunkName: "tracking" */ '../pages/Tracking')
);

export const LazyVehicles = lazy(() => 
  import(/* webpackChunkName: "vehicles" */ '../pages/Vehicles')
);

export const LazyDrivers = lazy(() => 
  import(/* webpackChunkName: "drivers" */ '../pages/Drivers')
);

export const LazyParking = lazy(() => 
  import(/* webpackChunkName: "parking" */ '../pages/Parking')
);

export const LazySensors = lazy(() => 
  import(/* webpackChunkName: "sensors" */ '../pages/Sensors')
);

export const LazyReports = lazy(() => 
  import(/* webpackChunkName: "reports" */ '../pages/Reports')
);

export const LazySettings = lazy(() => 
  import(/* webpackChunkName: "settings" */ '../pages/Settings')
);

export const LazyDeviceManagement = lazy(() => 
  import(/* webpackChunkName: "device-management" */ '../pages/DeviceManagement')
);

export const LazyRoutesPage = lazy(() => 
  import(/* webpackChunkName: "routes" */ '../pages/Routes')
);

export const LazyGPSPage = lazy(() => 
  import(/* webpackChunkName: "gps-page" */ '../pages/GPSPage')
);

// Lazy load heavy components
export const LazyDeviceMap = lazy(() => 
  import(/* webpackChunkName: "device-map" */ './DeviceMap')
);

// High-Order Component for consistent loading
const withLazyLoading = <T extends object>(
  LazyComponent: React.LazyExoticComponent<React.ComponentType<T>>,
  loadingMessage: string,
  useSkeletonLoading = false
) => {
  return React.forwardRef<any, T>((props, ref) => (
    <Suspense 
      fallback={
        useSkeletonLoading ? (
          <LoadingSpinner 
            message={loadingMessage} 
            variant="skeleton"
          />
        ) : (
          <EnhancedLoading message={loadingMessage} />
        )
      }
    >
      <LazyComponent {...props} ref={ref} />
    </Suspense>
  ));
};

// Enhanced wrapper components with optimized loading
export const DashboardWithLoading = withLazyLoading(
  LazyDashboard, 
  'Cargando Dashboard...', 
  true
);

export const MonitoringWithLoading = withLazyLoading(
  LazyMonitoring, 
  'Cargando Monitoreo...', 
  true
);

export const GPSWithLoading = withLazyLoading(
  LazyGPS, 
  'Cargando GPS...', 
  true
);

export const TrackingWithLoading = withLazyLoading(
  LazyTracking, 
  'Cargando Seguimiento...'
);

export const VehiclesWithLoading = withLazyLoading(
  LazyVehicles, 
  'Cargando Vehículos...', 
  true
);

export const DriversWithLoading = withLazyLoading(
  LazyDrivers, 
  'Cargando Conductores...', 
  true
);

export const ParkingWithLoading = withLazyLoading(
  LazyParking, 
  'Cargando Estacionamiento...'
);

export const SensorsWithLoading = withLazyLoading(
  LazySensors, 
  'Cargando Sensores...'
);

export const ReportsWithLoading = withLazyLoading(
  LazyReports, 
  'Cargando Reportes...', 
  true
);

export const SettingsWithLoading = withLazyLoading(
  LazySettings, 
  'Cargando Configuración...'
);

export const DeviceManagementWithLoading = withLazyLoading(
  LazyDeviceManagement, 
  'Cargando Gestión de Dispositivos...', 
  true
);

export const RoutesPageWithLoading = withLazyLoading(
  LazyRoutesPage, 
  'Cargando Rutas...'
);

export const GPSPageWithLoading = withLazyLoading(
  LazyGPSPage, 
  'Cargando Página GPS...'
);

// Device Map Component with Enhanced Loading
export const DeviceMapWithLoading = withLazyLoading(
  LazyDeviceMap, 
  'Cargando Mapa de Dispositivos...', 
  true
);

// Preload components for better UX
export const preloadComponents = () => {
  // Preload most commonly used components
  import('../pages/Dashboard');
  import('../pages/Monitoring');
  import('../pages/GPS');
  import('../pages/Vehicles');
  import('./DeviceMap');
};

// Component for preloading on app start
export const ComponentPreloader: React.FC = () => {
  React.useEffect(() => {
    // Preload components after a short delay to not block initial render
    const timer = setTimeout(() => {
      preloadComponents();
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  return null;
};

export default {
  LoadingSpinner,
  DashboardWithLoading,
  MonitoringWithLoading,
  GPSWithLoading,
  TrackingWithLoading,
  VehiclesWithLoading,
  DriversWithLoading,
  ParkingWithLoading,
  SensorsWithLoading,
  ReportsWithLoading,
  SettingsWithLoading,
  DeviceManagementWithLoading,
  RoutesPageWithLoading,
  GPSPageWithLoading,
  DeviceMapWithLoading,
  ComponentPreloader,
  preloadComponents
}; 
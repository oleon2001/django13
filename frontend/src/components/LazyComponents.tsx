import React, { Suspense, lazy } from 'react';
import { CircularProgress, Box } from '@mui/material';

// Loading component for Suspense fallback
const LoadingSpinner: React.FC<{ message?: string }> = ({ message = 'Cargando...' }) => (
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

// Lazy load main page components
export const LazyDashboard = lazy(() => import('../pages/Dashboard'));
export const LazyMonitoring = lazy(() => import('../pages/Monitoring'));
export const LazyGPS = lazy(() => import('../pages/GPS'));
export const LazyTracking = lazy(() => import('../pages/Tracking'));
export const LazyVehicles = lazy(() => import('../pages/Vehicles'));
export const LazyDrivers = lazy(() => import('../pages/Drivers'));
export const LazyParking = lazy(() => import('../pages/Parking'));
export const LazySensors = lazy(() => import('../pages/Sensors'));
export const LazyReports = lazy(() => import('../pages/Reports'));
export const LazySettings = lazy(() => import('../pages/Settings'));
export const LazyDeviceManagement = lazy(() => import('../pages/DeviceManagement'));
export const LazyRoutesPage = lazy(() => import('../pages/Routes'));
export const LazyGPSPage = lazy(() => import('../pages/GPSPage'));

// Lazy load heavy components (only if they have default exports)
export const LazyDeviceMap = lazy(() => import('./DeviceMap'));

// Wrapper components with Suspense and custom loading messages
export const DashboardWithLoading: React.FC = () => (
  <Suspense fallback={<LoadingSpinner message="Cargando Dashboard..." />}>
    <LazyDashboard />
  </Suspense>
);

export const MonitoringWithLoading: React.FC = () => (
  <Suspense fallback={<LoadingSpinner message="Cargando Monitoreo..." />}>
    <LazyMonitoring />
  </Suspense>
);

export const GPSWithLoading: React.FC = () => (
  <Suspense fallback={<LoadingSpinner message="Cargando GPS..." />}>
    <LazyGPS />
  </Suspense>
);

export const TrackingWithLoading: React.FC = () => (
  <Suspense fallback={<LoadingSpinner message="Cargando Seguimiento..." />}>
    <LazyTracking />
  </Suspense>
);

export const VehiclesWithLoading: React.FC = () => (
  <Suspense fallback={<LoadingSpinner message="Cargando Vehículos..." />}>
    <LazyVehicles />
  </Suspense>
);

export const DriversWithLoading: React.FC = () => (
  <Suspense fallback={<LoadingSpinner message="Cargando Conductores..." />}>
    <LazyDrivers />
  </Suspense>
);

export const ParkingWithLoading: React.FC = () => (
  <Suspense fallback={<LoadingSpinner message="Cargando Estacionamiento..." />}>
    <LazyParking />
  </Suspense>
);

export const SensorsWithLoading: React.FC = () => (
  <Suspense fallback={<LoadingSpinner message="Cargando Sensores..." />}>
    <LazySensors />
  </Suspense>
);

export const ReportsWithLoading: React.FC = () => (
  <Suspense fallback={<LoadingSpinner message="Cargando Reportes..." />}>
    <LazyReports />
  </Suspense>
);

export const SettingsWithLoading: React.FC = () => (
  <Suspense fallback={<LoadingSpinner message="Cargando Configuración..." />}>
    <LazySettings />
  </Suspense>
);

export const DeviceManagementWithLoading: React.FC = () => (
  <Suspense fallback={<LoadingSpinner message="Cargando Gestión de Dispositivos..." />}>
    <LazyDeviceManagement />
  </Suspense>
);

export const RoutesPageWithLoading: React.FC = () => (
  <Suspense fallback={<LoadingSpinner message="Cargando Rutas..." />}>
    <LazyRoutesPage />
  </Suspense>
);

export const GPSPageWithLoading: React.FC = () => (
  <Suspense fallback={<LoadingSpinner message="Cargando Página GPS..." />}>
    <LazyGPSPage />
  </Suspense>
);

// Map component with loading
export const DeviceMapWithLoading: React.FC<any> = (props) => (
  <Suspense fallback={<LoadingSpinner message="Cargando Mapa..." />}>
    <LazyDeviceMap {...props} />
  </Suspense>
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

export {
  LoadingSpinner
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
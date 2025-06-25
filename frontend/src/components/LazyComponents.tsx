import React, { Suspense, lazy } from 'react';
import EnhancedLoading from './EnhancedLoading';

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

// Wrapper components with Suspense and enhanced loading animations
export const DashboardWithLoading: React.FC = () => (
  <Suspense fallback={
    <EnhancedLoading 
      module="dashboard" 
      message="Cargando Dashboard" 
      subMessage="Preparando vista general del sistema"
      variant="detailed"
    />
  }>
    <LazyDashboard />
  </Suspense>
);

export const MonitoringWithLoading: React.FC = () => (
  <Suspense fallback={
    <EnhancedLoading 
      module="monitoring" 
      message="Cargando Monitoreo" 
      subMessage="Iniciando supervisión en tiempo real"
      variant="detailed"
    />
  }>
    <LazyMonitoring />
  </Suspense>
);

export const GPSWithLoading: React.FC = () => (
  <Suspense fallback={
    <EnhancedLoading 
      module="gps" 
      message="Cargando GPS" 
      subMessage="Conectando con dispositivos GPS"
      variant="default"
    />
  }>
    <LazyGPS />
  </Suspense>
);

export const TrackingWithLoading: React.FC = () => (
  <Suspense fallback={
    <EnhancedLoading 
      module="tracking" 
      message="Cargando Seguimiento" 
      subMessage="Preparando sistema de rastreo"
      variant="default"
    />
  }>
    <LazyTracking />
  </Suspense>
);

export const VehiclesWithLoading: React.FC = () => (
  <Suspense fallback={
    <EnhancedLoading 
      module="vehicles" 
      message="Cargando Vehículos" 
      subMessage="Obteniendo información de la flota"
      variant="default"
    />
  }>
    <LazyVehicles />
  </Suspense>
);

export const DriversWithLoading: React.FC = () => (
  <Suspense fallback={
    <EnhancedLoading 
      module="drivers" 
      message="Cargando Conductores" 
      subMessage="Accediendo a datos de conductores"
      variant="default"
    />
  }>
    <LazyDrivers />
  </Suspense>
);

export const ParkingWithLoading: React.FC = () => (
  <Suspense fallback={
    <EnhancedLoading 
      module="parking" 
      message="Cargando Estacionamiento" 
      subMessage="Verificando espacios disponibles"
      variant="default"
    />
  }>
    <LazyParking />
  </Suspense>
);

export const SensorsWithLoading: React.FC = () => (
  <Suspense fallback={
    <EnhancedLoading 
      module="sensors" 
      message="Cargando Sensores" 
      subMessage="Conectando con sensores IoT"
      variant="default"
    />
  }>
    <LazySensors />
  </Suspense>
);

export const ReportsWithLoading: React.FC = () => (
  <Suspense fallback={
    <EnhancedLoading 
      module="reports" 
      message="Cargando Reportes" 
      subMessage="Generando análisis y estadísticas"
      variant="detailed"
    />
  }>
    <LazyReports />
  </Suspense>
);

export const SettingsWithLoading: React.FC = () => (
  <Suspense fallback={
    <EnhancedLoading 
      module="settings" 
      message="Cargando Configuración" 
      subMessage="Accediendo a preferencias del sistema"
      variant="default"
    />
  }>
    <LazySettings />
  </Suspense>
);

export const DeviceManagementWithLoading: React.FC = () => (
  <Suspense fallback={
    <EnhancedLoading 
      module="devices" 
      message="Cargando Gestión de Dispositivos" 
      subMessage="Verificando estado de dispositivos"
      variant="detailed"
    />
  }>
    <LazyDeviceManagement />
  </Suspense>
);

export const RoutesPageWithLoading: React.FC = () => (
  <Suspense fallback={
    <EnhancedLoading 
      module="routes" 
      message="Cargando Rutas" 
      subMessage="Calculando rutas optimizadas"
      variant="default"
    />
  }>
    <LazyRoutesPage />
  </Suspense>
);

export const GPSPageWithLoading: React.FC = () => (
  <Suspense fallback={
    <EnhancedLoading 
      module="gps" 
      message="Cargando Página GPS" 
      subMessage="Inicializando interfaz GPS"
      variant="default"
    />
  }>
    <LazyGPSPage />
  </Suspense>
);

// Map component with loading
export const DeviceMapWithLoading: React.FC<any> = (props) => (
  <Suspense fallback={
    <EnhancedLoading 
      module="gps" 
      message="Cargando Mapa" 
      subMessage="Renderizando ubicaciones de dispositivos"
      variant="minimal"
    />
  }>
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

// Legacy LoadingSpinner for backward compatibility
const LoadingSpinner: React.FC<{ message?: string }> = ({ message = 'Cargando...' }) => (
  <EnhancedLoading 
    message={message}
    variant="minimal"
  />
);

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